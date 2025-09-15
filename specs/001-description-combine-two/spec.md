# Feature Specification: Combine Two Synthetic Focus Group Apps

**Feature Branch**: `001-description-combine-two`  
**Created**: September 14, 2025  
**Status**: Draft  
**Input**: User description: "Combine two synthetic focus group apps into one, using insights from audit_repo.py and evaluate_repo.py. Reference background.md and spec/specs/000-intake/spec-intake.md for overview and requirements. Design must be sleek and distinctive."

## Execution Flow (main)
```
1. Parse user description from Input
	→ If empty: ERROR "No feature description provided"
2. Extract key concepts from description
	→ Identify: actors, actions, data, constraints
3. For each unclear aspect:
	→ Mark with [NEEDS CLARIFICATION: specific question]
4. Fill User Scenarios & Testing section
	→ If no clear user flow: ERROR "Cannot determine user scenarios"
5. Generate Functional Requirements
	→ Each requirement must be testable
	→ Mark ambiguous requirements
6. Identify Key Entities (if data involved)
7. Run Review Checklist
	→ If any [NEEDS CLARIFICATION]: WARN "Spec has uncertainties"
	→ If implementation details found: ERROR "Remove tech details"
8. Return: SUCCESS (spec ready for planning)
```

---

## User Scenarios & Testing *(mandatory)*

### Primary User Story
A marketing agency user logs in to the platform, creates or selects AI-generated ICP personas (with weights), sets up a synthetic focus group session, and receives actionable, weighted insights within minutes. The experience is visually sleek and distinctive, making it easy to manage studies, personas, and exports.

### Acceptance Scenarios
1. **Given** the user is logged in, **When** they create a new study and configure personas (with weights), **Then** the system generates a transcript and weighted/unweighted insights within 5–30 minutes.
2. **Given** the user has existing personas, **When** they bulk upload new personas or questions, **Then** the system integrates them and updates the persona library.
3. **Given** the user completes a session, **When** they request an export, **Then** the system provides CSV/YAML/JSON/PDF/MD files of insights and transcripts, including schema version and checksums.
4. **Given** a study is run, **When** guardrail events occur, **Then** all are logged and visible in the dashboard.

### Edge Cases
- What happens when a user uploads a malformed CSV/JSON file?
- How does the system handle AI model downtime or API errors?
- What if a session exceeds the expected time or fails to generate insights?
- How are persona voice drift and moderation handled during a session?

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: System MUST allow users to create, manage, and run synthetic focus group studies end-to-end.
- **FR-002**: System MUST support AI-generated ICP personas with templates, traits, style tuning, and per-persona weights.
- **FR-003**: Users MUST be able to bulk upload questions and personas via CSV/JSON.
- **FR-004**: System MUST generate session transcripts and actionable, weighted/unweighted insights within 5–30 minutes.
- **FR-005**: System MUST provide export functionality for transcripts and insights (CSV/YAML/JSON/PDF/MD), including schema version and checksums.
- **FR-006**: System MUST present a visually sleek and distinctive user interface.
- **FR-007**: System MUST integrate insights from audit_repo.py and evaluate_repo.py for code analysis and quality assurance.
- **FR-008**: System MUST ensure persona consistency and realistic group dynamics, including voice drift detection and selective regeneration.
- **FR-009**: System MUST handle errors gracefully, providing clear feedback to users.
- **FR-010**: System MUST comply with data privacy and ethical guidelines as outlined in background.md and spec-intake.md.
- **FR-011**: System MUST support multiple pricing tiers and session limits.
- **FR-012**: System MUST allow users to export session data in multiple formats, with weighted and unweighted aggregates.
- **FR-013**: System MUST provide onboarding and tutorial resources for new users.
- **FR-014**: System MUST support agency branding and white-label options.
- **FR-015**: System MUST log all major user actions and system events for audit purposes, including guardrail events and weight changes.
- **FR-016**: System MUST provide a dashboard for study KPIs, persona health, insights quality, guardrails, and persona influence.
- **FR-017**: System MUST support auditability and observability for all study runs and exports.
- **FR-018**: System MUST provide robust data analysis tools for exploring, visualizing, and interpreting study results, including theme drill-down, sentiment timelines, persona influence, and cost simulation.
- **FR-019**: System MUST offer interactive dashboards for users to monitor study KPIs, persona health, insights quality, guardrail events, and export usage, with filtering and drill-down capabilities.

### Additional Requirements and Clarifications (from reference docs)

#### Persona & Study Features
- Support persona templates, traits, style tuning, and per-persona weights (0.0–5.0).
- Study setup must include objectives, prompts, constraints, and brand guardrails.

#### Agents & Moderation
- Moderator agent for turn-taking, follow-ups, timeboxing.
- Consistency agent for persona voice drift detection and selective regeneration.
- Safety agent for prompt linting, output moderation, PII/toxicity/jailbreak detection, and audit events.

#### Insights & Reporting
- Insights agent for topic clustering, quotes, sentiment, limitations, weighted/unweighted aggregates.
- Exports must include CSV, YAML, JSON, PDF/Markdown brief, with versioned schemas and checksums.
- Narrative profile generation (King Kong style) with PDF export.
- Aggregate and per-persona reports (weighted + unweighted).

#### Dashboard & Analysis
- Dashboard must cover study KPIs, theme drill-down, persona influence, sentiment timelines, cost simulator, and observability (tokens, latency, cost, audit trail).
- Dashboard toggles weighted/unweighted, updates theme rankings.

#### Data Privacy & Ethics
- No PII collection; synthetic character policy; transparency; user education.
- Limitation disclaimers, ethical use guidelines, professional liability.

#### Validation & Quality Assurance
- Bias detection: demographic auditing, language analysis, diversity validation, expert review, continuous monitoring.
- Validation: expert validation, small-scale reality checks, client outcome tracking, statistical validation, peer review.
- Auditability: 100% prompts/outputs and weight changes logged.
- Guardrail coverage: 100% prompts/responses screened and logged.

#### User Experience & Support
- Bulk upload system for questions and personas (CSV/JSON).
- Professional web interface with agency branding.
- Session recording and playback functionality.
- User onboarding and tutorial system.
- Customer support infrastructure.

#### Business & Risk
- Payment processing and subscription management.
- Multiple pricing tiers and session limits.
- Risk mitigation: LLM cost escalation, vector database scaling, API rate limiting, quality degradation, market adoption, competitive response, customer churn, regulatory changes, customer support load, quality consistency, scaling challenges.

#### Technical & Non-functional
- Acceptance: Persona weights editable, aggregate and per-persona insights deterministic, dashboard toggles weighted/unweighted, guardrail events visible, time/cost targets met, observability in place.
- Schema stability: breaking changes bump schema version + converter.
- P95 per-turn latency targets; study export ≤ 30s (10×8).
- Budget guard: early-exit on cap; cost projection + live tracking.

### Key Entities
- **Persona**: Represents an AI-generated character profile with psychological attributes, industry context, style vector, and weight.
- **Study**: Represents a synthetic focus group event, including objectives, constraints, attached personas, session transcript, and insights.
- **User**: Represents a marketing agency or consultant using the platform, with access controls and study/session history.
- **Export**: Represents downloadable files (CSV, YAML, JSON, PDF, MD) containing session results and insights, with schema version and checksum.
- **Question Bank**: Repository of questions for focus group sessions, supporting bulk upload and management.
- **Guardrail Event**: Represents moderation, PII, toxicity, and policy compliance events during study runs.
- **Insight**: Represents weighted and unweighted aggregates, per-persona metrics, limitations, and agreement scores.

---

## Review & Acceptance Checklist
*GATE: Automated checks run during main() execution*

### Content Quality
- [ ] No implementation details (languages, frameworks, APIs)
- [ ] Focused on user value and business needs
- [ ] Written for non-technical stakeholders
- [ ] All mandatory sections completed

### Requirement Completeness
- [ ] No [NEEDS CLARIFICATION] markers remain
- [ ] Requirements are testable and unambiguous  
- [ ] Success criteria are measurable
- [ ] Scope is clearly bounded
- [ ] Dependencies and assumptions identified

---

## Execution Status
*Updated by main() during processing*

- [ ] User description parsed
- [ ] Key concepts extracted
- [ ] Ambiguities marked
- [ ] User scenarios defined
- [ ] Requirements generated
- [ ] Entities identified
- [ ] Review checklist passed

---
