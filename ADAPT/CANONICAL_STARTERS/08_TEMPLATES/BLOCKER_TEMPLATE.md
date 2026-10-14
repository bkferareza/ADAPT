# BLOCKER RECORD

STATUS: DRAFT
BLK_ID: BLK-{{SEQUENCE}}
RAISED_BY: {{WORKCELL_ID}}
RAISED_DATE: {{DATE}}
BLOCKING_ITEM: {{ITEM_ID}}

---

## Title

{{BLOCKER_TITLE}}

[One-line description of the blocker. Example: "Integration test environment unavailable — downstream API contract validation cannot execute."]

---

## Description

{{BLOCKER_DESCRIPTION}}

[Describe the specific condition preventing progress. Reference the exact step, artifact, or dependency that is blocked. A blocker is a hard stop — not an inconvenience or a preference. If progress is possible through an alternative path, this should be a gap, not a blocker.]

---

## Root Cause

{{ROOT_CAUSE}}

[Known or suspected root cause of the blocker. If unknown, state "Unknown — further investigation required by {{RESOLUTION_AUTHORITY}}."]

---

## Impact

{{BLOCKER_IMPACT}}

[Describe what cannot proceed until this blocker is resolved. Reference specific business items, bounded actions, or handoffs that are halted. State whether other workcells are affected downstream.]

---

## Workaround Considered

{{WORKAROUND_CONSIDERED}}

[Describe any workaround that was considered and explain why it is or is not acceptable in an ADAPT context. In ADAPT, workarounds that bypass source truth, mutation authority, evidence requirements, or guardrail bindings are not acceptable regardless of urgency. If no workaround is viable, state that explicitly.]

---

## Resolution Authority

{{RESOLUTION_AUTHORITY}}

[Name the role, lane, or external party that must act to resolve this blocker. Blockers requiring external action (outside the ADAPT framework) must be escalated to the Director Lane.]

---

## Resolution Notes

{{RESOLUTION_NOTES}}

[Initially empty. Populated by the resolution authority when the blocker is resolved. Must describe the specific action taken and reference any artifacts produced.]

---

## Resolution Date

{{RESOLUTION_DATE}}

[Initially empty. Populated when the blocker status moves to RESOLVED.]

---

## Blocker Status

**Status:** OPEN / RESOLVED / DEFERRED

**Status History:**

| Date | Status | Updated By | Notes |
|------|--------|-----------|-------|
| {{DATE}} | OPEN | {{WORKCELL_ID}} | Blocker raised |
