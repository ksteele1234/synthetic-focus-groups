# Synthetic Focus Groups — Unified App Intake (v0.2)

## 0) One-liner
A single app that **creates believable ICP personas** and **runs synthetic focus groups** end-to-end, producing a weighted, auditable insight brief (CSV/YAML/JSON/PDF/MD) in minutes.

## 1) Why this exists (problem → outcome)
- Real research is slow and costly; teams need directional insights fast with transparency.
- Outcome: < 5 minutes to first insight for a 6–10 persona study; exportable with caveats and traceability.

## 2) Scope for V1
**In**
- Persona system with templates, traits, style tuning, and **per-persona weights** (default 1.0, range 0.0–5.0).
- Study setup: objectives, prompts, constraints, brand guardrails.
- Moderator agent for turn-taking, follow-ups, timeboxing.
- Consistency agent for persona voice drift detection and selective regeneration.
- Safety agent (prompt lint + output moderation; PII/toxicity/jailbreak); audit events.
- Insights agent for topic clustering, quotes, sentiment, limitations; **weighted + unweighted** aggregates.
- **Exports**: CSV, YAML, JSON, and PDF/Markdown brief (schemas versioned).
- **Dashboard & Analysis**: study KPIs, theme drill-down, persona influence, sentiment timelines, cost simulator.
- Observability: tokens, latency, cost; audit trail.

**Out (V1)**
- Voice/real-time audio, multilingual output, human recruiting, multi-tenant org mgmt.

## 3) Users & jobs
- Research Lead / PM: design study, generate discussion, consume weighted insights.
- Founder / Marketer: rapid concept checks, iterate prompts.
- Compliance/Legal: verify disclosure, policy compliance, audit trail.

## 4) Success metrics
- **TTFI** ≤ 5 min (10 personas × 8 turns).
- **Persona consistency** ≥ 0.8 cosine sim vs. style embeddings.
- **Insight quality (human eval)** ≥ 80% agreement on top-5 themes.
- **Export completeness**: 100% required sections; **weighted + unweighted** present.
- **Guardrail coverage**: 100% prompts/responses screened & logged.

## 5) Key stories
1. Create/edit ICP personas; assign **weights** per study.
2. Configure study (objective, constraints, turns, cost cap), attach personas, run.
3. Ask follow-ups; personas stay “in-character”; drift triggers selective regen.
4. Generate **aggregate** and **per-persona** reports (weighted + unweighted).
5. Export datasets (CSV/YAML/JSON) and a PDF/MD executive brief.

## 6) Agent architecture
- **Conductor**: oversees DAG/state, budget/SLA, retries/fallbacks; passes weight map; logs decisions.
- **Persona Agent**: generates/validates personas; emits embedding + style vector.
- **Moderator Agent**: orchestrates turns, probes, topics tagging.
- **Consistency Agent**: detects voice drift; requests targeted regen.
- **Safety Agent**: prompt lint + moderation; writes `guardrail_event`s.
- **Insights Agent**: per-persona metrics → **weighted aggregate** (and unweighted baseline); compiles limitations.
- **Export Agent**: renders CSV/YAML/JSON/PDF/MD; writes checksums; stamps `schema_version`.

Execution: Conductor→Persona→Moderator↔Consistency↔Safety→Insights→Export (via queue/worker pool).

## 7) Architecture (boring-first)
Frontend: Next.js (or Streamlit if retained) — Persona Studio, Study Designer, Live Session, Insights, Exports, Dashboard.  
Backend: FastAPI + Postgres (JSONB); Workers: Celery/RQ; WebSocket for live updates.  
LLM: provider adapter; per-persona system prompts; temperature per role.  
Storage: Postgres + object store for logs/exports.

## 8) Data model (abridged)
- `persona{id, name, traits jsonb, style_vector bytea|null, created_at, updated_at}`
- `study{id, title, objective, constraints jsonb, status, created_by, created_at}`
- `study_persona{study_id, persona_id, role, params jsonb, weight numeric default 1.0}`
- `message{id, study_id, persona_id|null, role, content, tokens int|null, cost numeric|null, topics text[]|null, sentiment text|null, ts timestamptz}`
- `insight{id, study_id, schema_version text, aggregation_method text, weighting_enabled bool, aggregate jsonb, by_persona jsonb, limitations text}`
- `guardrail_event{id, study_id, type, severity, details jsonb, ts}`
- `export{id, study_id, schema_version text, formats text[], datasets text[], location text, checksum text, created_at}`

## 9) Reporting & weighting
**Per-persona**: theme scores (frequency×strength), sentiment (−1..1), top quotes.  
**Aggregate (weighted)**:
- Theme score: Σ(weightᵢ × theme_scoreᵢ) / Σ(weightᵢ)
- Sentiment: Σ(weightᵢ × sentimentᵢ) / Σ(weightᵢ)
- Agreement% (optional): Σ(weightᵢ × 1[persona supports theme]) / Σ(weightᵢ)

Output **both** weighted and unweighted. Tie-break on broader weighted coverage.

## 10) Exports
- **CSV**: `messages.csv`, `personas.csv` (incl. weight), `insights_aggregate.csv`, `insights_by_persona.csv`, `guardrails.csv`
- **YAML**: `study.yaml`, `personas.yaml`, `insights.yaml`
- **JSON**: `messages.json`, `insights.json`
- **PDF/MD**: executive brief

All exports include `schema_version`; checksums recorded; schemas in `/schemas`.

## 11) Dashboard & analysis
- Overview (runs by status; P50/P95 latency; cost; tokens)
- Persona Health (consistency score; drift alerts)
- Insights Quality (theme coherence; agreement)
- Guardrails (event rates/severity)
- Persona Influence (weights; what-if impact simulation)
- Theme explorer, quote browser, sentiment timelines, similarity matrix, cost simulator

## 12) API surface (excerpt)
- `POST /studies` → create
- `POST /studies/{id}/run` → run (params: turns, cost_cap, personas[])
- `PATCH /studies/{id}/personas/{persona_id}` → `{ "weight": 2.0 }`
- `GET /studies/{id}/insights?weighted=true`
- `POST /studies/{id}/report` → `{ "formats":["md","pdf","json"], "include":["aggregate","per_persona"], "weighting":{"enabled":true,"normalization":"none"} }`
- `POST /studies/{id}/export` → `{ "formats":["csv","yaml","json","pdf","md"], "datasets":["messages","personas","insights","guardrails"], "include_embeddings": false }`
- `GET /studies/{id}/exports` / `{export_id}`

## 13) Non-functional
- P95 per-turn latency targets; study export ≤ 30s (10×8).
- Budget guard: early-exit on cap; cost projection + live tracking.
- Auditability: 100% prompts/outputs + weight changes logged.
- Schema stability: breaking changes bump `schema_version` + converter.

## 14) Risks & mitigations
Persona collapse → memory embeddings + pre-commit style check.  
Hallucinated certainty → required “Limitations & Confidence.”  
Cost spikes → token/turn caps, early-exit.  
Overfitting → red-team corpus; regression tests.

## 15) Deliverables (spec-kit)
Functional spec, architecture spec, data model + migrations, milestone backlog, test plan (consistency, guardrails, exports).

## 16) Acceptance checklist (V1)
- [ ] Persona weights editable (UI/API); default 1.0.
- [ ] Aggregate + per-persona insights (weighted + unweighted) deterministic.
- [ ] Exports (CSV/YAML/JSON/PDF/MD) complete; checksums; schema validated.
- [ ] Dashboard toggles weighted/unweighted; updates theme rankings.
- [ ] Guardrail events recorded and visible; weight changes audited.
- [ ] 10×8 run meets time/cost targets; observability in place.

## 17) Open questions
- Keep Streamlit or move to Next.js now?
- Multi-tenant requirements for v1.1?
- Domain packs (healthcare/finance) with stricter guardrails?

## Storage Architecture

- Primary OLTP: PostgreSQL.
- Vector search: pgvector extension (initial provider), behind `VectorBackend` interface with provider registry.
- Access: async via `asyncpg`.
- Migrations: SQL files in `migrations/` (idempotent, replayable in CI).
- Env:
  - `DATABASE_URL=postgresql://user:pass@host:port/db`
  - `VECTOR_PROVIDER=pgvector` (pluggable later: pinecone, weaviate, milvus, qdrant)

### Why this shape
- Personas, Studies, Sessions, Messages, Insights are relational.
- Semantic search uses approximate nearest neighbor via pgvector.
- Exports (CSV/YAML/JSON) read from relational + vector results.

