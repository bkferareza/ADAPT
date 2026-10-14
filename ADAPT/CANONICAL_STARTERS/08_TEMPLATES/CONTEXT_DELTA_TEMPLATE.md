# CONTEXT DELTA

STATUS: DRAFT
CONTEXT_DELTA_ID: CD-{{SEQUENCE}}
WORKCELL_ID: {{WORKCELL_ID}}
PRECEDING_CONTEXT_PACK_ID: {{CP-ID}}
DATE: {{DATE}}

---

## State Changes

Changes to the framework state produced by this bounded action. Each row represents a discrete state transition.

| Item | Before | After | Artifact Updated |
|------|--------|-------|-----------------|
| {{ITEM_REFERENCE}} | {{BEFORE_STATE}} | {{AFTER_STATE}} | `{{ARTIFACT_PATH}}` |

[Be specific. "Before" and "After" should describe the actual state of the item — e.g., status transitions, version changes, decision outcomes, or file creation. Do not use vague descriptors like "incomplete" or "done".]

---

## New Artifacts Produced

List all new files or records created during this bounded action:

| Artifact | Type | Location | Traceability |
|----------|------|---------|-------------|
| {{ARTIFACT_NAME}} | EVIDENCE_REPORT / HANDOFF / GAP / BLOCKER / CONTRACT / OTHER | `{{ARTIFACT_PATH}}` | {{BI-ID}} / {{REQ-ID}} |

---

## Superseded Items

Items that are now stale or superseded as a result of this bounded action. The Context Steward must mark these as stale in the next context pack.

| Item | Superseded By | Reason |
|------|--------------|--------|
| {{SUPERSEDED_ITEM}} | {{REPLACEMENT_ARTIFACT}} | {{REASON}} |

If nothing is superseded, state: "No items superseded by this action."

---

## Downstream Impact

Context packs that must be rebuilt as a result of the state changes recorded above:

| Workcell | Reason Rebuild Required | Priority |
|----------|------------------------|---------|
| {{WORKCELL_ID}} | {{REASON}} | HIGH / MEDIUM / LOW |

If no downstream context packs are affected, state: "No downstream context pack rebuilds required."

---

## Context Steward Note

Context deltas are consumed by the Context Steward when assembling the next context pack. The Context Steward must review this delta before assembling any context pack for workcells listed in the Downstream Impact section above.
