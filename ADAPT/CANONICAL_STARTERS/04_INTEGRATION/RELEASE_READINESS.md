# Release Readiness

STATUS: DRAFT
PROJECT: {{PROJECT_NAME}}
MILESTONE: {{ACTIVE_MILESTONE}}
RELEASE_TARGET: {{RELEASE_TARGET}}
ASSESSED_BY: Director Lane
ASSESSED_DATE: {{DATE}}

## Purpose

Director-level assessment of whether the current milestone is ready for release. Synthesizes merge readiness, QA signoff, accepted work, and open risks.

## Release Checklist

| Item | Status | Reference | Notes |
|------|--------|-----------|-------|
| All milestone business items accepted | {{STATUS}} | ACCEPTED_WORK_REGISTER.md | — |
| All acceptance criteria passed | {{STATUS}} | SIGNOFF_REGISTER.md | — |
| Merge readiness confirmed | {{STATUS}} | MERGE_READINESS.md | — |
| QA signoff received | {{STATUS}} | SIGNOFF_REGISTER.md | — |
| No open HIGH blockers | {{STATUS}} | BLOCKER_REGISTER.md | — |
| No unresolved HIGH gaps | {{STATUS}} | GAP_REGISTER.md | — |
| Director certification issued | {{STATUS}} | DECISION_LOG.md | — |
| Human approval received | {{STATUS}} | HUMAN_APPROVAL_GATES.md | — |

## Open Risks

<!-- Record any known risks that are accepted for release but not fully resolved -->
| RISK-ID | Description | Severity | Mitigation | Owner |
|---------|-------------|----------|------------|-------|
<!-- EXAMPLE: | RISK-001 | Performance under load not fully tested | MEDIUM | Load test scheduled for next cycle | QA Lane | -->

## OVERALL_RELEASE_STATUS: {{RELEASE_STATUS}}

## Notes

Release readiness requires human approval. Director cannot certify release unilaterally.
