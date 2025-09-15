# Implementation Plan: Combine Two Synthetic Focus Group Apps

**Branch**: `001-description-combine-two` | **Date**: September 14, 2025 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-description-combine-two/spec.md`

## Summary
The goal is to unify two synthetic focus group apps into a single, sleek, and distinctive platform for small marketing agencies. The app will enable rapid creation of believable ICP personas, run synthetic focus groups, and produce weighted, auditable insight briefs in multiple formats. Key features include persona templates, agent-driven moderation and consistency, robust data analysis tools, dashboards, and strict compliance with privacy and ethical standards. The technical approach leverages Python (FastAPI, Celery), React/TypeScript frontend, vector databases, and AI models (OpenAI GPT-4, Claude Sonnet).

## Technical Context
**Language/Version**: Python 3.11, TypeScript (React 18), SQL (PostgreSQL)  
**Primary Dependencies**: FastAPI, Celery, React, Tailwind CSS, Chroma/Pinecone, OpenAI GPT-4, Claude Sonnet  
**Storage**: PostgreSQL (metadata), Redis (caching), Chroma/Pinecone (vector)  
**Testing**: pytest, React Testing Library, integration tests  
**Target Platform**: Web (desktop/mobile), AWS/GCP cloud  
**Project Type**: Web (frontend + backend)  
**Performance Goals**: Session transcript generation <30 min, export ≤30s, P95 latency <200ms  
**Constraints**: No PII, schema versioning, auditability, cost guardrails, multi-tier pricing  
**Scale/Scope**: 100+ agencies, 10k+ users, multi-industry expansion  

## Constitution Check
**Simplicity**:
- Projects: 3 (api, frontend, tests)
- Using framework directly: Yes
- Single data model: Yes (DTOs only for serialization differences)
- Avoiding patterns: Yes (no unnecessary Repository/UoW)

**Architecture**:
- EVERY feature as library: Yes
- Libraries listed: persona, study, insights, export, moderation
- CLI per library: Planned
- Library docs: llms.txt format planned

**Testing (NON-NEGOTIABLE)**:
- RED-GREEN-Refactor cycle enforced: Yes
- Git commits show tests before implementation: Yes
- Order: Contract→Integration→E2E→Unit strictly followed
- Real dependencies used: Yes
- Integration tests for: new libraries, contract changes, shared schemas
- FORBIDDEN: Implementation before test, skipping RED phase

**Observability**:
- Structured logging included: Yes
- Frontend logs → backend: Yes (unified stream)
- Error context sufficient: Yes

**Versioning**:
- Version number assigned: Yes (MAJOR.MINOR.BUILD)
- BUILD increments on every change: Yes
- Breaking changes handled: Yes (parallel tests, migration plan)

## Project Structure
- /specs/001-description-combine-two/
  - spec.md
  - plan.md
  - research.md
  - data-model.md
  - contracts/
  - quickstart.md
  - tasks.md

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
4. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
5. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, or `GEMINI.md` for Gemini CLI).
6. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
7. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
8. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)
