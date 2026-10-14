# HANDOFF

STATUS: DRAFT
HANDOFF_ID: {{HANDOFF_ID}}
FROM_WORKCELL: {{FROM_WORKCELL_ID}}
TO_WORKCELL / TO_LANE: {{TO_WORKCELL_ID}}
SOURCE_TRUTH_VERSION: {{SOURCE_TRUTH_VERSION}}
CONTEXT_PACK_REFERENCE: {{CONTEXT_PACK_ID}}
DATE_EMITTED: {{DATE}}

---

## Work Completed

{{WORK_COMPLETED}}

[Describe what was accomplished in this bounded action. Reference specific business items, files changed, and decisions made. Do not summarise what the role does in general — describe what was done in this specific execution.]

---

## Evidence Attached

| Evidence ID | Description | Location |
|------------|-------------|---------|
| {{ER-ID}} | {{EVIDENCE_DESCRIPTION}} | `03_WORKCELLS/{{FROM_WORKCELL_ID}}/EVIDENCE/{{ER-ID}}.md` |

---

## Contracts Impacted

List any API or integration contracts that were created or modified during this bounded action.

| Contract ID | Contract Name | Change Type | Location |
|------------|--------------|------------|---------|
| {{CONTRACT_ID}} | {{CONTRACT_NAME}} | CREATED / MODIFIED / DEPRECATED | `{{CONTRACT_PATH}}` |

If no contracts were impacted, state: "No contracts impacted."

---

## Open Items

Unresolved items that the receiving workcell or lane must handle before or during their next action:

- {{OPEN_ITEM_1}}
- {{OPEN_ITEM_2}}

If none, state: "No open items."

---

## Risks

Known risks to flag for the receiver:

- {{RISK_1}}
- {{RISK_2}}

If none, state: "No risks identified."

---

## Blockers

Blockers that the receiver must resolve before proceeding:

| BLK-ID | Description | Resolution Authority |
|--------|-------------|---------------------|
| {{BLK-ID}} | {{BLOCKER_DESCRIPTION}} | {{RESOLUTION_AUTHORITY}} |

If none, state: "No blockers."

---

## Next Action Suggested

{{NEXT_ACTION_SUGGESTION}}

[Describe the recommended next step for the receiving workcell or lane. This is a suggestion, not an instruction — the receiver's scope contract and Director authority govern what they do next.]

---

## Context Delta Reference

CONTEXT_DELTA_ID: {{CONTEXT_DELTA_ID}}

[Reference the context delta produced by this bounded action, if applicable. The Context Steward consumes this delta when assembling the next context pack.]

---

## Placement Note

This handoff must be placed in `06_HANDOFFS/ACTIVE/` and the control plane `ActiveHandoff` field must be updated to reference this HANDOFF_ID before the receiving workcell begins execution. Handoffs in `06_HANDOFFS/ARCHIVE/` are not active and must not be acted upon.
