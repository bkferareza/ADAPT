# Merge Readiness

STATUS: DRAFT
PROJECT: {{PROJECT_NAME}}
MILESTONE: {{ACTIVE_MILESTONE}}
ASSESSED_BY: {{WORKCELL_ID}}
ASSESSED_DATE: {{DATE}}

## Purpose

Assessment of whether the current integrated state is ready for merge to the main branch or delivery target. Integrator produces this assessment.

## Readiness Checklist

| Item | Status | Evidence | Notes |
|------|--------|----------|-------|
| All API contracts accepted | {{STATUS}} | — | — |
| UI–Backend bindings verified | {{STATUS}} | — | — |
| Pipeline passing | {{STATUS}} | — | — |
| All active integration gaps resolved | {{STATUS}} | — | — |
| QA signoff received | {{STATUS}} | — | — |
| Director certification received | {{STATUS}} | — | — |
| No open HIGH-priority blockers | {{STATUS}} | — | — |

## Item Status Values

- READY: Condition satisfied
- NOT_READY: Condition not yet met
- BLOCKED: Cannot assess; blocker exists
- WAIVED: Intentionally waived by Director with documented reason

## Overall Readiness

OVERALL_STATUS: {{OVERALL_READINESS}}

## Notes

Merge readiness does not substitute for QA signoff or Director certification. All three are required before release.
