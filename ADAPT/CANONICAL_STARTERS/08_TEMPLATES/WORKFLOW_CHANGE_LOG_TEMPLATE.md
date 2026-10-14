# WORKFLOW CHANGE LOG

STATUS: DRAFT
WORKCELL_ID: {{WORKCELL_ID}}

---

## Change History

This log records all workflow change requests for this workcell — approved, applied, and rejected. Rejected requests are referenced here for audit completeness; the full request record remains in `WORKFLOW_CHANGE_REQUESTS.md`.

| WCR-ID | Change Description | Approved By | Approval Date | Applied Date | Status | Notes |
|--------|-------------------|-------------|--------------|-------------|--------|-------|
<!-- Example row — remove when populating with real entries:
| WCR-001 | Added pre-analysis schema validation step to Backend Requirement Analyst agent | Director_{{IDENTITY}} | {{DATE}} | {{DATE}} | APPLIED | References DECISION_LOG.md #DL-007 |
-->

---

## Status Values

| Status | Meaning |
|--------|---------|
| PENDING | Change request submitted; awaiting Director review |
| APPROVED | Director approved; awaiting implementation |
| APPLIED | Change implemented in EFFECTIVE_WORKFLOW.md |
| REJECTED | Director rejected; see WORKFLOW_CHANGE_REQUESTS.md for reason |
| SUPERSEDED | A later change request replaced this one before or after application |

---

## Log Maintenance Note

Rejected requests are referenced in this log with status REJECTED. The full request record, including the rejection reason, remains in `WORKFLOW_CHANGE_REQUESTS.md`. Do not delete rejected entries from either document.
