# GUARDRAIL BINDINGS

STATUS: DRAFT
PROJECT: {{PROJECT_NAME}}
WORKCELL_ID: {{WORKCELL_ID}}

---

## Framework Guardrail Applicability

The following table lists all 7 ADAPT framework guardrails and their applicability to this workcell. Guardrails cannot be removed. They may be noted as MODIFIED (with Director approval and documented change) or WAIVED (with a Director exception recorded in `02_DIRECTOR_LANE/DECISION_LOG.md`).

| Guardrail ID | Guardrail Name | Applicability | Modification / Exception Reference | Notes |
|-------------|---------------|:------------:|-----------------------------------|-------|
| GR-01 | Source Truth Primacy | APPLIES / MODIFIED / WAIVED-WITH-EXCEPTION | {{DECISION_LOG_REF}} | {{NOTES}} |
| GR-02 | Mutation Authority Boundary | APPLIES / MODIFIED / WAIVED-WITH-EXCEPTION | {{DECISION_LOG_REF}} | {{NOTES}} |
| GR-03 | Handoff Completeness | APPLIES / MODIFIED / WAIVED-WITH-EXCEPTION | {{DECISION_LOG_REF}} | {{NOTES}} |
| GR-04 | QA Independence | APPLIES / MODIFIED / WAIVED-WITH-EXCEPTION | {{DECISION_LOG_REF}} | {{NOTES}} |
| GR-05 | Evidence Traceability | APPLIES / MODIFIED / WAIVED-WITH-EXCEPTION | {{DECISION_LOG_REF}} | {{NOTES}} |
| GR-06 | Context Economy | APPLIES / MODIFIED / WAIVED-WITH-EXCEPTION | {{DECISION_LOG_REF}} | {{NOTES}} |
| GR-07 | Director Authority | APPLIES / MODIFIED / WAIVED-WITH-EXCEPTION | {{DECISION_LOG_REF}} | {{NOTES}} |

**Applicability values:**
- `APPLIES` — guardrail applies without modification.
- `MODIFIED` — guardrail applies with a Director-approved modification; see Decision Log reference.
- `WAIVED-WITH-EXCEPTION` — guardrail is waived for a specific, time-limited condition; Director exception is mandatory and must be referenced.

---

## Workcell-Specific Guardrail Additions

List any guardrail constraints added specifically for this workcell beyond the 7 framework guardrails. These additions may be more restrictive than the framework defaults but may not be less restrictive.

| WCG-ID | Guardrail Description | Rationale | Effective Date |
|--------|----------------------|-----------|---------------|
| WCG-{{SEQUENCE}} | {{GUARDRAIL_DESCRIPTION}} | {{RATIONALE}} | {{DATE}} |

If no workcell-specific additions apply, state: "No workcell-specific guardrail additions. Framework guardrails apply as listed above."

---

## Enforcement Note

Guardrails cannot be removed from this binding document. Any attempt to remove, weaken, or override a guardrail binding without a Director-approved exception recorded in `DECISION_LOG.md` is itself a guardrail violation. Violations must be surfaced immediately to the Director Lane.
