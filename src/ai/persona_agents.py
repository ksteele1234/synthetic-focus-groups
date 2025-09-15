"""
Persona research and compilation agents.
- ResearchAgent builds a ResearchDossier using Perplexity and optional social quotes.
- PersonaCompilerAgent compiles validated personas with Claude and jsonschema repair loop.
"""
from __future__ import annotations

import os
import json
import uuid
from typing import Dict, Any, List, Optional, Tuple

from .agents import BaseAgent
from .perplexity_client import PerplexityClient
from .claude_client import ClaudeClient

# Load the detailed persona schema
try:
    from models.persona_schema import DETAILED_PERSONA_SCHEMA
except Exception:
    DETAILED_PERSONA_SCHEMA = {"type": "object"}

import jsonschema

# Optional: reuse WebPersonaBuilder for supplemental quotes
try:
    from research.web_persona_builder import WebPersonaBuilder
except Exception:
    WebPersonaBuilder = None


class ResearchAgent(BaseAgent):
    """Collects demographics/psychographics and citations using Perplexity; adds optional social quotes."""
    def __init__(self, perplexity: PerplexityClient, social_builder: Optional[WebPersonaBuilder] = None):
        super().__init__("Persona Research Agent", "Research")
        self.pplx = perplexity
        self.social_builder = social_builder

    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        topic = task.get("topic") or task.get("query") or "target market"
        region = task.get("region", "US")
        timeframe = task.get("timeframe", "last_36_months")
        include_social = task.get("include_social", True)

        plan = self._build_query_plan(topic, region, timeframe)
        findings = []
        for item in plan:
            res = self.pplx.ask(item["q"])  # returns {success, answer, citations, raw}
            findings.append({"bucket": item["bucket"], **res})

        demographics, psychographics, segments, citations = self._normalize(findings)

        quotes = []
        if include_social and self.social_builder:
            try:
                quotes = [q.to_dict() for q in self.social_builder.gather_quotes(topic, limit=12)]
            except Exception:
                quotes = []

        dossier = {
            "meta": {"topic": topic, "region": region, "timeframe": timeframe, "query_plan": plan},
            "demographics": demographics,
            "psychographics": psychographics,
            "segments": segments,
            "quotes": quotes,
            "citations": citations,
        }
        return {"success": True, "dossier": dossier}

    def _build_query_plan(self, topic: str, region: str, timeframe: str) -> List[Dict[str, str]]:
        return [
            {"bucket": "demographics", "q": f"{topic} audience {region} demographics site:pewresearch.org OR site:census.gov OR site:bls.gov 2019..2025"},
            {"bucket": "psychographics", "q": f"{topic} psychographics values motivations {region} survey site:pewresearch.org OR site:gallup.com 2019..2025"},
            {"bucket": "behaviors", "q": f"{topic} media consumption decision drivers {region} 2022..2025 report"},
            {"bucket": "pain_points", "q": f"{topic} pain points obstacles objections buyers {region} 2021..2025"},
            {"bucket": "benchmarks", "q": f"{topic} industry report demographics psychographics filetype:pdf {region} 2021..2025"},
        ]

    def _normalize(self, findings: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], Dict[str, Any], List[Dict[str, Any]], List[Dict[str, Any]]]:
        demographics: Dict[str, Any] = {}
        psychographics: Dict[str, Any] = {}
        segments: List[Dict[str, Any]] = []
        citations: List[Dict[str, Any]] = []
        for f in findings:
            if f.get("citations"):
                citations.extend(f["citations"])
            answer = (f.get("answer") or "").lower()
            bucket = f.get("bucket")
            if bucket == "demographics":
                # simple keyword-based hints
                for k in ["age", "gender", "income", "education", "location"]:
                    if k in answer and k not in demographics:
                        demographics[k] = f.get("answer")
            elif bucket in ("psychographics", "behaviors"):
                psychographics.setdefault("values", f.get("answer"))
            elif bucket in ("pain_points",):
                psychographics.setdefault("pain_points", f.get("answer"))
            elif bucket == "benchmarks":
                psychographics.setdefault("notes", f.get("answer"))
        return demographics, psychographics, segments, citations


class PersonaCompilerAgent(BaseAgent):
    """Compiles personas with Claude from a ResearchDossier, validates against schema, and repairs."""
    def __init__(self, claude: ClaudeClient, schema: Dict[str, Any] = None):
        super().__init__("Persona Compiler Agent", "Synthesis")
        self.claude = claude
        self.schema = schema or DETAILED_PERSONA_SCHEMA

    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        dossier = task["dossier"]
        n_personas = task.get("n_personas", 3)
        seed = task.get("few_shots", [])

        drafted = self._draft_personas(dossier, n_personas, seed)
        personas: List[Dict[str, Any]] = []
        errors: List[Dict[str, Any]] = []
        if isinstance(drafted, dict) and drafted.get("personas"):
            raw_list = drafted["personas"]
        elif isinstance(drafted, list):
            raw_list = drafted
        else:
            raw_list = []
        for p in raw_list:
            # ensure id and attach citations
            p.setdefault("id", str(uuid.uuid4()))
            p.setdefault("evidence_citations", dossier.get("citations", [])[:10])
            ok, err = self._validate(p)
            if ok:
                personas.append(p)
            else:
                repaired = self._repair_with_claude(p, err, dossier)
                ok2, err2 = self._validate(repaired)
                if ok2:
                    personas.append(repaired)
                else:
                    errors.append({"initial": err, "after_repair": err2})
        return {"success": len(personas) > 0, "personas": personas, "errors": errors}

    def _draft_personas(self, dossier: Dict[str, Any], n: int, few_shots: List[Dict[str, Any]]):
        system = (
            "You are a senior market researcher. Output JSON only. Do not speculate. "
            "If evidence is insufficient for any field, set it to '' or []."
        )
        # Include the reference persona style as a hint if available
        ref_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "docs", "samples", "persona_report_reference.md")
        ref_text = ""
        try:
            with open(os.path.abspath(ref_path), "r", encoding="utf-8") as f:
                ref_text = f.read()[:6000]
        except Exception:
            pass
        user = (
            "Grounding data (do not contradict):\n" + json.dumps(dossier, ensure_ascii=False) +
            "\n\nReference persona style (optional):\n" + ref_text +
            f"\n\nTask: Propose {n} distinct personas that STRICTLY match the provided schema's keys and types. "
            "Respond as {{\"personas\":[{{...}}]}}."
        )
        return self.claude.json_only(system, user, temperature=0.2, max_tokens=8000)

    def _validate(self, persona: Dict[str, Any]) -> Tuple[bool, List[str]]:
        try:
            jsonschema.validate(instance=persona, schema=self.schema)
            return True, []
        except jsonschema.ValidationError as e:
            return False, [str(e)]

    def _repair_with_claude(self, persona: Dict[str, Any], errors: List[str], dossier: Dict[str, Any]) -> Dict[str, Any]:
        system = "You fix JSON to pass schema without inventing unsupported facts. JSON only."
        user = (
            "Validation errors:\n" + json.dumps(errors) +
            "\n\nOriginal JSON:\n" + json.dumps(persona, ensure_ascii=False) +
            "\n\nGrounding data (do not add claims beyond these):\n" + json.dumps(dossier, ensure_ascii=False) +
            "\n\nFix minimally to pass validation. Unknowns should stay '' or []."
        )
        fixed = self.claude.json_only(system, user, temperature=0.1, max_tokens=3000)
        if isinstance(fixed, dict):
            return fixed
        return persona
