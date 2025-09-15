# Quickstart Guide

## Setup
- Ensure Postgres + pgvector is running (see `migrations/0001_init.sql`)
- Run migration with `tools/migrate.py`

## Usage
- Use `src/session/synthetic_runner.py` for session orchestration
- Use `src/export/enhanced_exporter.py` for exporting results
- Validate exports against `schemas/insights.schema.json` and `schemas/messages.schema.json`
- Use dashboard in `src/visualizations/chart_generator.py` for analysis

## Testing
- Run integration tests: `tests/test_enhanced_integration.py`

## Audit & Health
- Run `tools/audit_repo.py` and `tools/evaluate_repo.py` to check code health

## Refactor Steps
- Address security in `src/vector/backend_pgvector.py`
- Update aggregation logic for persona weighting
- Remove flagged dead code

---
