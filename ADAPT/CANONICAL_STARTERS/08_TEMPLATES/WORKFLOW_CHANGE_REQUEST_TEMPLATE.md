# WORKFLOW CHANGE REQUEST

STATUS: DRAFT
WCR-ID: {{WCR-ID}}
WORKCELL_ID: {{WORKCELL_ID}}
REQUESTED_BY: {{IDENTITY}}
DATE: {{DATE}}

---

## Change Description

{{CHANGE_DESCRIPTION}}

[Provide a concise, one- to two-sentence summary of the requested change. This summary will appear in the WORKFLOW_CHANGE_LOG.md.]

---

## Current Behavior

{{CURRENT_BEHAVIOR}}

[Describe what the current workflow does — reference the specific agent name and step in DEFAULT_AGENT_BLUEPRINT.md. Be precise: describe the behavior as it exists today, not the desired state.]

---

## Proposed Change

{{PROPOSED_CHANGE}}

[Describe what should change. Specify: which agent is affected, which section of the agent definition changes, what the new behavior is, and whether this replaces or adds to the default. Use before/after format if helpful.]

---

## Reason / Justification

{{JUSTIFICATION}}

[Explain why this change is necessary. Reference project constraints, tooling differences, scope decisions, or Director instructions if applicable. Generic justifications ("it would be better") are not sufficient.]

---

## Affected Agents

List all agents in DEFAULT_AGENT_BLUEPRINT.md whose definition, sequence position, or behavior is impacted by this change.

| Agent Name | Blueprint Section Affected | Impact Description |
|------------|---------------------------|-------------------|
| {{AGENT_NAME}} | {{SECTION}} | {{IMPACT}} |

---

## Guardrail Impact

Does this change touch any guardrail binding in `07_GUARDRAILS/GUARDRAIL_BINDINGS.md`?

**YES / NO**

If YES, list affected guardrails:

| Guardrail ID | Guardrail Name | Nature of Impact |
|-------------|---------------|-----------------|
| {{GUARDRAIL_ID}} | {{GUARDRAIL_NAME}} | {{IMPACT}} |

If a guardrail is affected, Director approval is mandatory before this change may be implemented.

---

## Director Outcome

**Decision:** PENDING / APPROVED / REJECTED

**Decision Date:** {{DIRECTOR_DECISION_DATE}}

**Decision Reference:** DECISION_LOG.md #{{DL-ID}}

### If Approved — Implementation Instructions

{{IMPLEMENTATION_INSTRUCTIONS}}

[Director records specific implementation instructions here. If conditions apply to the approval, they are stated explicitly.]

### If Rejected — Rejection Reason

{{REJECTION_REASON}}

[Director records the reason for rejection. Rejected requests remain in WORKFLOW_CHANGE_REQUESTS.md and are referenced in WORKFLOW_CHANGE_LOG.md with status REJECTED.]
