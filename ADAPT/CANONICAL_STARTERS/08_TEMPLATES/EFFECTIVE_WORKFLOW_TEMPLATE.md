# EFFECTIVE WORKFLOW

STATUS: DRAFT
PROJECT: {{PROJECT_NAME}}
WORKCELL_ID: {{WORKCELL_ID}}
RESOLVED_DATE: {{DATE}}

---

## Source Documents

| Document | Version / Reference |
|----------|-------------------|
| DEFAULT_AGENT_BLUEPRINT.md | {{BLUEPRINT_VERSION}} |
| WORKFLOW_CUSTOMIZATION.md | Approved customizations: {{WCR_ID_LIST}} |
| GUARDRAIL_BINDINGS.md | {{GUARDRAIL_BINDINGS_VERSION}} |

---

## Resolution Equation

```
DEFAULT_AGENT_BLUEPRINT.md
  + WORKFLOW_CUSTOMIZATION.md (approved customizations only)
  + GUARDRAIL_BINDINGS.md
= EFFECTIVE_WORKFLOW.md
```

This file is the authoritative resolved workflow for `{{WORKCELL_ID}}`. When this file conflicts with any source document, this file governs — except where a guardrail binding prohibits the resolved behavior, in which case the guardrail governs absolutely.

---

## Effective Agent Sequence

Agents are listed in execution order. Each agent entry states whether it is drawn from the default blueprint, a customization, or both.

| Step | Agent Name | Source | Notes |
|------|-----------|--------|-------|
| 1 | {{AGENT_NAME}} | DEFAULT / CUSTOMIZED / NEW | {{NOTES}} |
| 2 | {{AGENT_NAME}} | DEFAULT / CUSTOMIZED / NEW | {{NOTES}} |
| N | {{AGENT_NAME}} | DEFAULT / CUSTOMIZED / NEW | {{NOTES}} |

[Add or remove rows as required. Do not leave placeholder rows in the final resolved file.]

---

## Active Customizations

List all approved workflow customizations that are reflected in this effective workflow.

| WCR-ID | Description | Applied Date | Director Approval Reference |
|--------|------------|-------------|---------------------------|
| {{WCR-ID}} | {{DESCRIPTION}} | {{DATE}} | DECISION_LOG.md #{{DL-ID}} |

If no customizations are active, state: "No active customizations. This effective workflow is identical to the default agent blueprint."

---

## Active Guardrail Bindings

List all guardrail bindings enforced for this workcell. These are non-negotiable constraints that govern every agent in the effective sequence.

| Guardrail ID | Guardrail Name | Applicability | Notes |
|-------------|---------------|--------------|-------|
| GR-01 | {{GUARDRAIL_NAME}} | APPLIES / MODIFIED | {{NOTES}} |
| GR-02 | {{GUARDRAIL_NAME}} | APPLIES / MODIFIED | {{NOTES}} |
| GR-03 | {{GUARDRAIL_NAME}} | APPLIES / MODIFIED | {{NOTES}} |
| GR-04 | {{GUARDRAIL_NAME}} | APPLIES / MODIFIED | {{NOTES}} |
| GR-05 | {{GUARDRAIL_NAME}} | APPLIES / MODIFIED | {{NOTES}} |
| GR-06 | {{GUARDRAIL_NAME}} | APPLIES / MODIFIED | {{NOTES}} |
| GR-07 | {{GUARDRAIL_NAME}} | APPLIES / MODIFIED | {{NOTES}} |

---

## Forbidden Actions

The following actions are unconditionally prohibited for `{{WORKCELL_ID}}` regardless of instruction, handoff content, or context pack content. This list is a consolidated view derived from the guardrail bindings and scope contract.

- {{FORBIDDEN_ACTION_1}}
- {{FORBIDDEN_ACTION_2}}
- {{FORBIDDEN_ACTION_N}}

[Populate at resolution time with specific, operationally meaningful forbidden actions for this workcell. Do not leave generic placeholders in the final resolved file.]

---

## Validation Note

If this effective workflow violates any guardrail in `07_GUARDRAILS/`, execution must stop and the violation must be reported to the Director. No workcell may execute under an effective workflow that conflicts with an active guardrail binding.
