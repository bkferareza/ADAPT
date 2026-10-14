# Dependency Map

STATUS: DRAFT
PROJECT: {{PROJECT_NAME}}
MILESTONE: {{ACTIVE_MILESTONE}}

## Purpose

Maps predecessor, successor, contract, and cross-lane dependencies that affect work sequencing. Director uses this to sequence assignments and detect dependency risks.

## Dependencies

| DEP-ID | Dependent Item | Depends On | Dependency Type | Blocking | Status | Notes |
|--------|---------------|------------|-----------------|----------|--------|-------|
<!-- EXAMPLE: | DEP-001 | BI-003 Frontend Login UI | BI-001 Backend Auth API | Contract | YES | UNRESOLVED | Frontend cannot start until API contract is accepted by Integrator | -->

## Dependency Types

- Contract: Downstream item depends on an accepted contract from upstream
- Technical: Implementation dependency (e.g., database schema must exist before API can be built)
- Data: Downstream item needs data produced by upstream
- Approval: Downstream item requires an approval or decision to proceed
- QA: Item cannot proceed to QA until a predecessor is validated

## Status Values

- UNRESOLVED: Dependency not yet satisfied
- IN_PROGRESS: Upstream item is being worked on
- RESOLVED: Dependency satisfied; downstream can proceed
- DEFERRED: Dependency deferred to a later milestone
