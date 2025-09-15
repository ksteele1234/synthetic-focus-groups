# Schema Validation Guide

This guide provides instructions for validating exports against JSON schemas.

## Schemas
- `schemas/insights.schema.json`
- `schemas/messages.schema.json`

## Validation Steps
1. Export data using `src/export/enhanced_exporter.py` or `src/export/exporter.py`.
2. Use a JSON schema validation tool (e.g., `jsonschema` Python package) to validate exported files:
   ```python
   import json
   from jsonschema import validate, ValidationError

   with open('exported_file.json') as f:
       data = json.load(f)
   with open('schemas/insights.schema.json') as s:
       schema = json.load(s)
   try:
       validate(instance=data, schema=schema)
       print('Valid!')
   except ValidationError as e:
       print('Validation error:', e)
   ```
3. Repeat for all export formats and schemas.

## Automation
- Consider adding schema validation to your test suite (e.g., in `tests/test_enhanced_integration.py`).

---
