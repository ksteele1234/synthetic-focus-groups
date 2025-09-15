# Refactor Checklist

This checklist tracks specific refactor actions, files, and reasons (security, complexity, dead code) based on triage and requirements.

## Security
- [ ] Refactor `src/vector/backend_pgvector.py` to address security findings (credential handling, SQL injection, permissions).

## Complexity
- [ ] Consolidate duplicate logic in session/persona management modules (if found).
- [ ] Modularize aggregation logic for persona weighting in `src/session/synthetic_runner.py` and `src/export/enhanced_exporter.py`.

## Dead Code
- [ ] Remove `src/vector/__init__.py` (no domain match, no dependents).
- [ ] Remove `tests/test_vector_pg.py` (no domain match, no dependents).

## Schema Compliance
- [ ] Validate all exports against `schemas/insights.schema.json` and `schemas/messages.schema.json`.

---
