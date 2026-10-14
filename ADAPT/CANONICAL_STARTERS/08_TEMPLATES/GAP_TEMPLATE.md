# GAP RECORD

STATUS: DRAFT
GAP_ID: GAP-T{{TYPE}}-{{SEQUENCE}}
GAP_TYPE: {{GAP_TYPE}}
RAISED_BY: {{WORKCELL_ID}}
RAISED_DATE: {{DATE}}
BLOCKING_ITEM: {{ITEM_ID}}

---

## Gap Type Reference

| Code | Type | Description |
|------|------|-------------|
| GAP-T10 | Decision Gap | A required decision is absent; implementation cannot proceed without it |
| GAP-T11 | Context Gap | Required context, source truth section, or artifact is missing or unresolvable |
| GAP-T12 | Evidence Gap | Expected evidence for a completed item is missing or insufficient |
| GAP-T13 | Authority Gap | An action required for progress falls outside this workcell's mutation authority |

---

## Title

{{GAP_TITLE}}

[One-line description of the gap. Example: "AC-043 acceptance criterion ambiguous — 'performant' undefined, no threshold stated."]

---

## Description

{{GAP_DESCRIPTION}}

[Full description of the gap — what is missing and why it matters. Reference the specific artifact, section, requirement ID, or decision that is absent or unclear. Be precise: the resolution authority must be able to act on this description without additional investigation.]

---

## Impact

{{GAP_IMPACT}}

[Describe what cannot proceed until this gap is resolved. Reference specific business items, acceptance criteria, or implementation steps that are blocked. Quantify where possible.]

---

## Resolution Authority

{{RESOLUTION_AUTHORITY}}

[Name the role or lane that must act to resolve this gap. For Decision Gaps: Director Lane. For Context Gaps: Context Steward or Director. For Evidence Gaps: the workcell that produced the incomplete evidence. For Authority Gaps: Director Lane.]

---

## Resolution Notes

{{RESOLUTION_NOTES}}

[Initially empty. Populated by the resolution authority when the gap is resolved. Must reference the specific decision, artifact, or action taken.]

---

## Resolution Date

{{RESOLUTION_DATE}}

[Initially empty. Populated when the gap status moves to RESOLVED.]

---

## Gap Status

**Status:** OPEN / IN_REVIEW / RESOLVED / DEFERRED / SUPERSEDED

**Status History:**

| Date | Status | Updated By | Notes |
|------|--------|-----------|-------|
| {{DATE}} | OPEN | {{WORKCELL_ID}} | Gap raised |
