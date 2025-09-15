# Data Model

## Database
- **Postgres + pgvector**
  - Migration: `migrations/0001_init.sql`
  - Backend: `src/vector/backend_pgvector.py`, `src/vector/registry.py`

## Schemas
- **Insights**: `schemas/insights.schema.json`
- **Messages**: `schemas/messages.schema.json`

## Entities
- **Persona**: Weighted attributes, schema-aligned
- **Session**: Synthetic runner, aggregation logic
- **Export**: Enhanced exporter, schema compliance

## Aggregation
- Persona weighting included in all aggregation tasks (`src/session/synthetic_runner.py`, `src/export/enhanced_exporter.py`)

## Refactor Notes
- Ensure all aggregation logic uses persona weights
- Validate all exports against schemas

---
