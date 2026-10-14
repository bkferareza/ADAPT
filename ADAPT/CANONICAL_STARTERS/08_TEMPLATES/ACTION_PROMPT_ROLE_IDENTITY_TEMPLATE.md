# ACTION PROMPT — {{ROLE}} — {{IDENTITY}}

STATUS: DRAFT
PROJECT: {{PROJECT_NAME}}
WORKCELL_ID: {{ROLE}}_{{IDENTITY}}

---

## PROTECTED BINDING
<!-- This section cannot be removed, weakened, or overridden. It is set at onboarding and governs all executions under this identity. -->

| Field | Value |
|-------|-------|
| ActiveWorkcell | {{ROLE}}_{{IDENTITY}} |
| HumanOwner | {{IDENTITY}} |
| Role | {{ROLE}} |
| WorkcellType | {{WORKCELL_TYPE}} |
| Authority | {{AUTHORITY_SCOPE}} |
| MutationAuthority | {{MUTATION_SCOPE}} |
| QAIndependenceStatus | {{QA_INDEPENDENCE_STATUS}} |
| SourceTruthRequired | YES |
| ActiveHandoffRequired | YES |
| ContextPackRequired | YES |
| EvidenceRequired | YES |
| StopAfterNextHandoff | YES |

---

## Pre-Execution Checklist

Before executing any bounded action, verify:
- [ ] Active handoff located in 06_HANDOFFS/ACTIVE/
- [ ] Source truth version identified and current
- [ ] Context pack assembled for this action
- [ ] Scope contract reviewed — action is within scope
- [ ] Mutation authority confirmed for any files to be modified
- [ ] Guardrails checked (07_GUARDRAILS/)
- [ ] No blocking conditions in BLOCKERS.md

---

## EDITABLE MEMBER WORKFLOW
<!-- This section may be customized. Changes must go through WORKFLOW_CHANGE_REQUEST process. -->
<!-- The following is prohibited: skipping source truth, context pack, evidence, or handoff; expanding mutation scope; bypassing QA independence; mutating another lane's files; overriding Director decisions; removing guardrail checks. -->

### Execution Sequence

{{MEMBER_DEFINED_EXECUTION_SEQUENCE}}

### Preferred Analysis Order

{{MEMBER_PREFERRED_ANALYSIS_ORDER}}

### Local Checklists

{{MEMBER_LOCAL_CHECKLISTS}}

### Personal Working Notes

{{MEMBER_WORKING_NOTES}}

---

## Execution Rule

This action prompt binds the AI runtime to the workcell identity above. All actions taken during this session are attributed to {{ROLE}}_{{IDENTITY}}.

One execution = one bounded action = one handoff emitted = STOP.

Do not continue past the next handoff boundary.
