# Task List: Combine Two Synthetic Focus Group Apps

## Vector Indexing & Search

**T001. Refactor security in vector backend**
- File: `src/vector/backend_pgvector.py`
- Action: Address credential handling, SQL injection, permissions per security audit.
- Acceptance: Security tests, code review, linter pass.

**T002. Verify existing vector registry**
- File: `src/vector/registry.py`
- Action: Confirm registry logic matches migration and backend.
- Acceptance: Verified existing.

**T003. Verify migration for pgvector**
- File: `migrations/0001_init.sql`
- Action: Confirm migration sets up pgvector correctly.
- Acceptance: Verified existing.

## Exports

**T004. Validate export logic against schemas**
- File: `src/export/enhanced_exporter.py`
- Action: Ensure all exports match `schemas/insights.schema.json` and `schemas/messages.schema.json`.
- Acceptance: Schema validation script, integration test.

**T005. Verify existing export logic**
- File: `src/export/enhanced_exporter.py`, `src/export/exporter.py`
- Action: Confirm export logic is modular and schema-aligned.
- Acceptance: Verified existing.

## Persona Weighting

**T006. Refactor aggregation for persona weighting**
- File: `src/session/synthetic_runner.py`, `src/export/enhanced_exporter.py`
- Action: Ensure persona weights are used in all aggregation tasks.
- Acceptance: Persona weighting test cases, integration test.

**T007. Verify existing persona management**
- File: `src/session/synthetic_runner.py`
- Action: Confirm persona management logic is modular and supports weighting.
- Acceptance: Verified existing.

## Dashboard

**T008. Refactor dashboard for weighted aggregation**
- File: `src/visualizations/chart_generator.py`
- Action: Update dashboard visualizations to reflect weighted aggregation and schema-aligned exports.
- Acceptance: Dashboard mockups, integration test.

**T009. Verify existing dashboard logic**
- File: `src/visualizations/chart_generator.py`
- Action: Confirm dashboard logic is modular and extensible.
- Acceptance: Verified existing.

## General

**T010. Remove dead code**
- File: `src/vector/__init__.py`, `tests/test_vector_pg.py`
- Action: Delete files flagged as dead code in triage.
- Acceptance: Files removed, linter pass.

**T011. Run migration and audit tools**
- File: `tools/migrate.py`, `tools/audit_repo.py`, `tools/evaluate_repo.py`
- Action: Run migration, audit, and evaluation scripts to confirm repo health.
- Acceptance: All scripts pass, no errors.

**T012. Expand and verify tests**
- File: `tests/test_enhanced_integration.py`
- Action: Add/verify tests for refactored logic, persona weighting, schema validation, security.
- Acceptance: All tests pass, coverage report.

---

## Parallel Execution Guidance

- T001, T004, T006, T008, T010, T011, T012 can be run in parallel [P] if they touch different files.
- T002, T003, T005, T007, T009 are “verified existing” and do not require action.

---

**Each task references concrete files/functions and includes acceptance checks. No tasks are created for work that already exists.**
