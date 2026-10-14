# CONTEXT PACK

STATUS: DRAFT
CONTEXT_PACK_ID: CP-{{SEQUENCE}}
WORKCELL_ID: {{WORKCELL_ID}}
HANDOFF_ID: {{HANDOFF_ID}}
SOURCE_TRUTH_VERSION: {{SOURCE_TRUTH_VERSION}}
DATE_ASSEMBLED: {{DATE}}
CONTEXT_SIZE: {{XS / S / M / L / XL}}

---

## Scope Declaration

### Included in This Context Pack

{{SCOPE_INCLUDED}}

[List specifically what is included: which source truth sections, which handoff, which contracts, which decision log entries, which gaps and blockers. Be explicit — the consuming agent must know exactly what context is available.]

### Explicitly Excluded

{{SCOPE_EXCLUDED}}

[List what was considered and excluded, and why. This prevents consuming agents from requesting context that the Context Steward has already evaluated and determined to be out of scope or stale for this action.]

---

## Active Handoff Summary

| Field | Value |
|-------|-------|
| Handoff ID | {{HANDOFF_ID}} |
| From Workcell | {{FROM_WORKCELL_ID}} |
| Work Completed | {{WORK_COMPLETED_SUMMARY}} |
| Open Items | {{OPEN_ITEMS_SUMMARY}} |
| Blockers | {{BLOCKERS_SUMMARY}} |
| Next Action Suggested | {{NEXT_ACTION_SUGGESTION}} |

---

## Source Truth Artifacts Included

| Artifact | Section / File | Version | Relevance |
|----------|---------------|---------|-----------|
| {{ARTIFACT_NAME}} | `{{PATH_OR_SECTION}}` | {{VERSION}} | {{RELEVANCE}} |

---

## Relevant Decisions

Decisions from `02_DIRECTOR_LANE/DECISION_LOG.md` relevant to this action:

| Decision ID | Summary | Date | Impact on This Action |
|------------|---------|------|----------------------|
| {{DL-ID}} | {{DECISION_SUMMARY}} | {{DATE}} | {{IMPACT}} |

If no relevant decisions, state: "No decisions from the Decision Log are relevant to this action."

---

## Relevant Contracts

| Contract ID | Contract Name | Location | Relevance |
|------------|--------------|---------|-----------|
| {{CONTRACT_ID}} | {{CONTRACT_NAME}} | `{{CONTRACT_PATH}}` | {{RELEVANCE}} |

If no contracts are relevant, state: "No contracts are relevant to this action."

---

## Gaps and Blockers

Open gaps and blockers relevant to this action:

| ID | Type | Title | Status | Impact on This Action |
|----|------|-------|--------|----------------------|
| {{GAP_OR_BLK_ID}} | GAP-T10 / GAP-T11 / GAP-T12 / GAP-T13 / BLK | {{TITLE}} | OPEN / IN_REVIEW | {{IMPACT}} |

If none, state: "No open gaps or blockers are relevant to this action."

---

## Stale or Excluded Items

Items that were considered during context assembly but excluded as stale, superseded, or out of scope:

| Item | Reason for Exclusion |
|------|---------------------|
| {{ITEM_REFERENCE}} | {{EXCLUSION_REASON}} |

---

## Known Limitations

{{KNOWN_LIMITATIONS}}

[Document what this context pack does not cover. This may include: source truth sections not yet authored, decisions not yet made, contracts pending authorship, or gaps awaiting resolution. Consuming agents must not assume coverage of items not listed above.]

---

## Context Steward Note

This context pack was assembled by the Context Steward. Consuming agents must not load additional context outside this pack without a new Context Steward pass. Loading unvetted context outside this pack is a Context Economy guardrail violation.
