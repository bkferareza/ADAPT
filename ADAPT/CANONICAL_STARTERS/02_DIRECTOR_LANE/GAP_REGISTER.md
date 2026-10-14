# Gap Register

STATUS: DRAFT
PROJECT: {{PROJECT_NAME}}

## Purpose

Records all gaps identified during ADAPT execution. Gaps must be classified, routed, and resolved before the blocked work can proceed. Director owns the gap register.

## Gap Types

- **GAP-T10 Decision Gap:** A technical or architectural decision not yet made (e.g., choice of database, auth mechanism, deployment target)
- **GAP-T11 Context Gap:** Missing required context needed to execute safely (e.g., missing requirements section, unresolved ambiguity in source truth)
- **GAP-T12 Evidence Gap:** Required evidence cannot be produced (e.g., untestable acceptance criterion)
- **GAP-T13 Authority Gap:** No workcell or human has authority to make the required decision
- **GAP-T14 Framework Gap:** A governing ADAPT contract in this instance is contradictory, incomplete, or permits an ungoverned path. Not a solution-truth gap, an undecided choice (T10), missing context (T11), missing evidence (T12), or a missing authority holder (T13). The instance never edits its contract copy to resolve it; the Director escalates it to the Framework Maintainer (GOVERNANCE_RULES.md, Rule 14).

## Gap Register

| GAP-ID | Type | Severity | Title | Description | Raised By | Raised Date | Blocking Item | Routed To | Routed Date | Status | Resolution | Resolved Date |
|--------|------|----------|-------|-------------|-----------|-------------|---------------|-----------|-------------|--------|------------|---------------|
<!-- EXAMPLE: | GAP-T10-001 | GAP-T10 Decision Gap | BLOCKING | Database technology not selected | No database technology has been chosen. Backend cannot finalize schema design until this decision is made. | Director Lane | {{DATE}} | BI-002 Backend Data Model | Human Owner | {{DATE}} | OPEN | — | — | -->

## Severity Values

- BLOCKING: A named artifact cannot be produced at all until this gap is closed
- HIGH: Work may start but cannot complete or be certified
- MEDIUM: Work may complete; a decision is deferred
- LOW: Clarification only

## Status Values

- OPEN: Gap recorded; resolution pending
- IN_REVIEW: Under active discussion
- RESOLVED: Resolution accepted and recorded
- DEFERRED: Will not be resolved for current milestone; work adjusted
- SUPERSEDED: Made irrelevant by a subsequent decision

## Notes

Any lane may raise a gap. Only Director can classify and route it. A gap that cannot be resolved within the current milestone must be carried over via CARRY_OVER_REGISTER.md. GAP-IDs follow format GAP-T{{TYPE}}-{{SEQUENCE}} (e.g., GAP-T10-001).
