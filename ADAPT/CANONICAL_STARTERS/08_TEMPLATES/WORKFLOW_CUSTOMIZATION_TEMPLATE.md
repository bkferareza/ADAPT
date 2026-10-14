# WORKFLOW CUSTOMIZATION

STATUS: DRAFT
PROJECT: {{PROJECT_NAME}}
WORKCELL_ID: {{WORKCELL_ID}}
WCR-ID: {{WCR-ID}}
REQUESTED_BY: {{IDENTITY}}
DATE_REQUESTED: {{DATE}}

---

## Description of Requested Customization

{{CUSTOMIZATION_DESCRIPTION}}

[Describe the specific change to the default workflow. Be precise about which step, sequence, or behavior is being customized. Reference the DEFAULT_AGENT_BLUEPRINT.md section being altered.]

---

## Justification

{{JUSTIFICATION}}

[Explain why the default workflow is insufficient for this workcell and why this customization is necessary. Reference project-specific constraints, tooling differences, or approved deviations if applicable.]

---

## Affected Agents

List all agents in DEFAULT_AGENT_BLUEPRINT.md that this customization modifies or reorders:

| Agent Name | Section Affected | Nature of Change |
|------------|-----------------|-----------------|
| {{AGENT_NAME}} | {{SECTION}} | {{CHANGE_NATURE}} |

---

## Behavior Change Type

- [ ] Adds to default behavior (default behavior is retained; new steps are added)
- [ ] Replaces default behavior (one or more default steps are replaced)
- [ ] Reorders default behavior (sequence is changed; no steps removed)
- [ ] Removes a default step (requires Director approval and documented justification)

---

## Guardrail Impact Assessment

Does this customization affect any guardrail binding in `07_GUARDRAILS/GUARDRAIL_BINDINGS.md`?

- [ ] NO — no guardrail binding is affected
- [ ] YES — the following guardrail bindings are affected:

| Guardrail ID | Guardrail Name | Nature of Impact |
|-------------|---------------|-----------------|
| {{GUARDRAIL_ID}} | {{GUARDRAIL_NAME}} | {{IMPACT_DESCRIPTION}} |

If YES, a Director exception must be recorded in `02_DIRECTOR_LANE/DECISION_LOG.md` before this customization may be applied.

---

## Director Review

**Outcome:** PENDING / APPROVED / REJECTED

**Director Notes:**

{{DIRECTOR_NOTES}}

[Director records rationale for approval or rejection here. If approved with conditions, conditions are stated explicitly.]

**Review Date:** {{DIRECTOR_REVIEW_DATE}}

---

## Implementation Status

**Status:** NOT_STARTED / IN_PROGRESS / APPLIED / SUPERSEDED

**Applied Date:** {{APPLIED_DATE}}

**Applied By:** {{APPLIED_BY}}

**Notes:**

{{IMPLEMENTATION_NOTES}}
