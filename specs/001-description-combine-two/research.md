# Phase 0: Research Summary

This research phase documents the current state of the codebase and artifacts, focusing on reuse and minimal churn. All decisions are grounded in `reports/triage.csv`.

## Existing Code & Artifacts
- Database: Postgres + pgvector (see `migrations/0001_init.sql`, `src/vector/backend_pgvector.py`, `src/vector/registry.py`)
- Export formats: JSON schemas (`schemas/insights.schema.json`, `schemas/messages.schema.json`)
- Export logic: `src/export/enhanced_exporter.py`, `src/export/exporter.py`
- Aggregation: Persona weighting in `src/session/synthetic_runner.py`, `src/export/enhanced_exporter.py`
- Visualization: `src/visualizations/chart_generator.py`
- Migration: `tools/migrate.py`
- Repo health: `tools/audit_repo.py`, `tools/evaluate_repo.py`
- Tests: `tests/test_enhanced_integration.py`

## Keep/Refactor/Remove Decisions
- Keep: All files marked 'keep' in `reports/triage.csv`
- Refactor: `src/vector/backend_pgvector.py` (security), aggregation logic for persona weighting/schema compliance, dashboard logic for weighted aggregation
- Remove: `src/vector/__init__.py`, `tests/test_vector_pg.py` (dead code)

## Key Technical Constraints
- Must use Postgres + pgvector
- Export formats must match JSON schemas
- Persona weighting required in all aggregation
- Minimize code churn; prefer refactor over rewrite

## Dependency-Aware Sequence
1. Refactor security in vector backend
2. Update aggregation logic for persona weighting/schema compliance
3. Remove flagged dead code
4. Update dashboard logic
5. Expand tests
6. Validate exports
7. Run migration/audit tools

## Risks & Mitigations
- Security: Address findings in vector backend
- Schema drift: Validate exports against schemas
- Churn: Minimize by reusing existing code

---
