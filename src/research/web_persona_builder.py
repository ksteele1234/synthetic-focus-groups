"""
Web persona builder: fetch first-hand quotes from Reddit (and stub for Quora) to construct evidence-backed personas.
Respects DEMO_MODE by providing offline sample quotes.
"""

from __future__ import annotations

import os
import time
import json
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

try:
    import requests
except ImportError:
    requests = None  # We will handle missing requests gracefully


@dataclass
class EvidenceQuote:
    source_type: str  # 'reddit' | 'quora'
    community: str
    published_at: str
    upvotes: int
    span: str  # the quoted text snippet
    url: str = ""
    stance: str = "other"
    topics: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_type": self.source_type,
            "community": self.community,
            "published_at": self.published_at,
            "upvotes": self.upvotes,
            "span": self.span,
            "url": self.url,
            "stance": self.stance,
            "topics": self.topics,
        }


class WebPersonaBuilder:
    """Build personas from web evidence (Reddit and Quora).
    Optionally calls a provider API for compliant web/Quora ingestion (RESEARCH_API_URL),
    and can LLM-synthesize richer personas when not in demo mode.
    """

    def __init__(self, user_agent: str = "FocusGroupResearchBot/1.0"):
        self.ua = user_agent
        self.demo_mode = os.environ.get("DEMO_MODE", "").lower() == "true"
        self.research_api_url = os.environ.get("RESEARCH_API_URL", "").strip() or None

    def gather_quotes(
        self,
        query: str,
        subreddits: Optional[List[str]] = None,
        min_upvotes: int = 5,
        limit: int = 20,
        time_filter: str = "year",
    ) -> List[EvidenceQuote]:
        """Gather first-hand quotes from Reddit. In demo mode, returns curated examples.
        Note: For production, consider official APIs or compliant data sources.
        """
        if self.demo_mode or requests is None:
            return self._demo_quotes(query)

        quotes: List[EvidenceQuote] = []
        headers = {"User-Agent": self.ua}
        subs = subreddits or ["marketing", "smallbusiness", "Entrepreneur", "SaaS"]

        # Use Reddit's public JSON search endpoint (rate-limited; may require API in production)
        for sub in subs:
            try:
                url = (
                    f"https://www.reddit.com/r/{sub}/search.json?q={requests.utils.quote(query)}"
                    f"&restrict_sr=1&sort=top&t={time_filter}&limit={limit}"
                )
                resp = requests.get(url, headers=headers, timeout=10)
                if resp.status_code != 200:
                    continue
                data = resp.json()
                for child in data.get("data", {}).get("children", []):
                    post = child.get("data", {})
                    selftext = post.get("selftext") or post.get("title") or ""
                    if not selftext:
                        continue
                    ups = int(post.get("ups") or 0)
                    if ups < min_upvotes:
                        continue
                    quotes.append(
                        EvidenceQuote(
                            source_type="reddit",
                            community=f"r/{sub}",
                            published_at=time.strftime(
                                "%Y-%m-%d", time.gmtime(int(post.get("created_utc", 0)))
                            ),
                            upvotes=ups,
                            span=selftext[:800],
                            url=f"https://www.reddit.com{post.get('permalink', '')}",
                            stance="other",
                            topics=[],
                        )
                    )
                    if len(quotes) >= limit:
                        break
                if len(quotes) >= limit:
                    break
            except Exception:
                # Be resilient; continue to next subreddit
                continue

        return quotes

    def gather_quora_quotes(self, query: str, limit: int = 10) -> List[EvidenceQuote]:
        """Quora evidence ingestion via provider API if configured, else demo-mode samples.
        Set RESEARCH_API_URL to a service that returns quotes: POST {url}/quotes {"provider":"quora","query":"...","limit":10}
        """
        if self.demo_mode:
            return self._demo_quotes(query)[:limit]
        if self.research_api_url and requests is not None:
            try:
                resp = requests.post(
                    f"{self.research_api_url.rstrip('/')}/quotes",
                    json={"provider": "quora", "query": query, "limit": limit},
                    headers={"User-Agent": self.ua},
                    timeout=15,
                )
                if resp.status_code == 200:
                    data = resp.json() or {}
                    items = data.get("quotes", [])
                    out: List[EvidenceQuote] = []
                    for it in items:
                        out.append(EvidenceQuote(
                            source_type="quora",
                            community=it.get("community", "quora"),
                            published_at=it.get("published_at", ""),
                            upvotes=int(it.get("upvotes", 0)),
                            span=it.get("span", ""),
                            url=it.get("url", ""),
                            stance=it.get("stance", "other"),
                            topics=it.get("topics", []),
                        ))
                    return out[:limit]
            except Exception:
                return []
        return []

    def build_persona_from_evidence(
        self,
        query: str,
        subreddits: Optional[List[str]] = None,
        min_upvotes: int = 5,
        limit: int = 20,
        use_llm: bool = True,
        additional_sources: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Synthesize a persona structure using gathered quotes as evidence.
        Returns a dict that maps well to the Persona dataclass fields, with an added
        `evidence_quotes` list for traceability.
        """
        quotes = self.gather_quotes(query, subreddits=subreddits, min_upvotes=min_upvotes, limit=limit)
        if not quotes:
            quotes = self.gather_quora_quotes(query, limit=limit)

        # Merge additional human-provided sources (external reports, PDFs summarized, etc.)
        extra = []
        for src in additional_sources or []:
            try:
                extra.append(EvidenceQuote(
                    source_type=src.get('source_type','external'),
                    community=src.get('community', src.get('title','external_report')),
                    published_at=src.get('published_at',''),
                    upvotes=int(src.get('weight', 1)),
                    span=src.get('snippet') or src.get('summary') or src.get('text', ''),
                    url=src.get('url',''),
                    stance=src.get('stance','other'),
                    topics=src.get('topics',[]),
                ))
            except Exception:
                continue
        quotes = quotes + extra

        # If allowed and not in demo mode, request an LLM to structure a detailed persona
        if use_llm and not self.demo_mode:
            try:
                from ai.openai_client import create_openai_client
                client = create_openai_client()
                if client is not None:
                    system = (
                        "You are a senior market researcher. Synthesize an evidence-backed buyer persona from quotes. "
                        "Output STRICT JSON matching this schema keys: name, age, gender, education, relationship_family, "
                        "occupation, annual_income, location, hobbies, community_involvement, personality_traits, values, "
                        "free_time_activities, lifestyle_description, major_struggles, obstacles, why_problems_exist, "
                        "deep_fears_business, deep_fears_personal, previous_software_tried, tangible_business_results, "
                        "tangible_personal_results, emotional_transformations, if_only_soundbites, big_picture_aspirations, "
                        "things_to_avoid, persona_summary, ideal_day_scenario."
                    )
                    evidence_str = json.dumps([q.to_dict() for q in quotes], ensure_ascii=False)
                    user = (
                        f"Research query: {query}\n\nHere are first-hand quotes with metadata: {evidence_str}\n\n"
                        "Synthesize a realistic persona reflecting the quotes. Only JSON, no commentary."
                    )
                    resp = client.chat_completion([
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ], temperature=0.3, max_tokens=800)
                    content = resp.choices[0].message.content
                    try:
                        persona_from_llm = json.loads(content)
                    except json.JSONDecodeError:
                        persona_from_llm = None
                    if isinstance(persona_from_llm, dict) and persona_from_llm.get("name"):
                        persona_from_llm["evidence_quotes"] = [q.to_dict() for q in quotes]
                        return persona_from_llm
            except Exception:
                pass

        # Simple heuristics to shape the persona profile
        pain_points = []
        goals = []
        values = []
        personality_traits = []

        text = "\n".join(q.span.lower() for q in quotes)
        if any(k in text for k in ["too expensive", "can't afford", "budget"]):
            pain_points.append("Budget constraints and price sensitivity")
        if any(k in text for k in ["integration", "copying data", "silos"]):
            pain_points.append("Integration gaps and data silos")
        if any(k in text for k in ["time", "hours", "save"]):
            goals.append("Save time through automation")
        if any(k in text for k in ["consistent", "brand voice", "quality"]):
            values.append("Consistency and quality")
        if any(k in text for k in ["practical", "efficient", "organized"]):
            personality_traits.append("practical")

        persona = {
            "name": f"Evidence-backed Persona ({query[:20]})",
            "age": 32,
            "gender": "",
            "education": "",
            "relationship_family": "",
            "occupation": "Target customer from online communities",
            "annual_income": "",
            "location": "",
            "hobbies": [],
            "community_involvement": [],
            "personality_traits": list(set(personality_traits)) or ["thoughtful", "practical"],
            "values": list(set(values)) or ["efficiency", "reliability"],
            "free_time_activities": "",
            "lifestyle_description": "",
            "major_struggles": list(set(pain_points)) or ["Workflow inefficiency", "Tool fragmentation"],
            "obstacles": [],
            "why_problems_exist": "Fragmented tools and limited budgets across communities",
            "deep_fears_business": ["Wasting resources on tools that don't work"],
            "deep_fears_personal": [],
            "fear_impact_spouse": "",
            "fear_impact_kids": "",
            "fear_impact_employees": "",
            "fear_impact_peers": "",
            "fear_impact_clients": "",
            "previous_agencies_tried": [],
            "previous_software_tried": [],
            "diy_approaches_tried": [],
            "why_agencies_failed": "",
            "why_software_failed": "",
            "why_diy_failed": "",
            "tangible_business_results": ["Reduce manual work", "Better attribution"],
            "tangible_personal_results": ["Work-life balance"],
            "emotional_transformations": ["Confidence in decisions"],
            "if_only_soundbites": ["If only my tools worked together and saved me time..."],
            "professional_recognition_goals": [],
            "financial_freedom_goals": [],
            "lifestyle_upgrade_goals": [],
            "family_legacy_goals": [],
            "big_picture_aspirations": "Run smoothly with less effort and more impact",
            "desired_reputation": ["Efficient", "Reliable"],
            "success_statements_from_others": [],
            "things_to_avoid": ["Overpaying for low-value tools"],
            "unwanted_quotes": [],
            "persona_summary": "Evidence-backed persona synthesized from community quotes.",
            "ideal_day_scenario": "Starts day reviewing a unified dashboard; automations handle routine tasks.",
            "evidence_quotes": [q.to_dict() for q in quotes],
        }
        return persona

    def _demo_quotes(self, query: str) -> List[EvidenceQuote]:
        return [
            EvidenceQuote(
                source_type="reddit",
                community="r/smallbusiness",
                published_at="2024-03-12",
                upvotes=124,
                span=(
                    "I'm constantly switching between different tools and it's chewing up hours every week. "
                    "If I could pay $30-50 a month for something that actually integrates and saves me time, I'd do it."
                ),
                url="https://www.reddit.com/r/smallbusiness/...",
                stance="pain",
                topics=["time", "integration", "pricing"],
            ),
            EvidenceQuote(
                source_type="reddit",
                community="r/marketing",
                published_at="2024-08-02",
                upvotes=98,
                span=(
                    "Our execs keep asking for ROI, but none of our platforms talk to each other. "
                    "Give me proper attribution and CRM integration and I'm in."
                ),
                url="https://www.reddit.com/r/marketing/...",
                stance="need",
                topics=["roi", "crm", "integration"],
            ),
        ]
