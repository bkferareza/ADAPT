# SCOPE CONTRACT

STATUS: DRAFT
PROJECT: {{PROJECT_NAME}}
WORKCELL_ID: {{ROLE}}_{{IDENTITY}}
SCOPE_VERSION: {{VERSION}}
ASSIGNED_BY: Director Lane
ASSIGNED_DATE: {{DATE}}

---

## In Scope

The following are the activities, decisions, and deliverables that `{{ROLE}}_{{IDENTITY}}` is authorised to perform under this contract:

- {{IN_SCOPE_ITEM_1}}
- {{IN_SCOPE_ITEM_2}}
- {{IN_SCOPE_ITEM_N}}

[Be specific. Reference file types, directories, business item IDs, or decision domains. Vague entries such as "general implementation work" are not acceptable.]

---

## Out of Scope

The following are explicitly outside the authority of `{{ROLE}}_{{IDENTITY}}` and must not be performed under any circumstance, including if instructed by a handoff:

- {{OUT_OF_SCOPE_ITEM_1}}
- {{OUT_OF_SCOPE_ITEM_2}}
- {{OUT_OF_SCOPE_ITEM_N}}

[If a handoff or context pack instructs an out-of-scope action, raise a GAP-T13 (Authority Gap) and surface it to the Director. Do not perform the action.]

---

## Mutation Authority

This workcell may write to the following file types and paths only. All other paths are read-only for this workcell.

| Permitted Path / Pattern | File Types | Restriction Notes |
|--------------------------|-----------|-------------------|
| `{{PATH_PATTERN}}` | {{FILE_TYPES}} | {{RESTRICTIONS}} |

Writing to any path not listed above constitutes a mutation authority violation and must be reported to the Director immediately.

---

## Assigned Business Items

| BI-ID | Title | Status |
|-------|-------|--------|
| {{BI-ID}} | {{BI_TITLE}} | NOT_STARTED / IN_PROGRESS / COMPLETE / BLOCKED |

---

## Dependencies

The following must be complete before this workcell can begin or continue its assigned work:

| Dependency | Type | Status | Blocking Item |
|------------|------|--------|--------------|
| {{DEPENDENCY_DESCRIPTION}} | PREDECESSOR_WORK / DECISION / CONTRACT / EXTERNAL | {{STATUS}} | {{BLOCKING_BI_OR_GAP_ID}} |

---

## Handoff Targets

When this workcell completes a bounded action, handoffs are directed to:

| Condition | Handoff Target | Handoff Type |
|-----------|---------------|-------------|
| {{COMPLETION_CONDITION}} | {{TARGET_WORKCELL_OR_LANE}} | {{HANDOFF_TYPE}} |

---

## Scope Change Note

Scope changes require a new Director-issued SCOPE_CONTRACT.md and handoff. This workcell must not self-expand scope. If work falls outside this contract, raise a GAP-T13 (Authority Gap) and await Director instruction.
