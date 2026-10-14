# Signoff Register

STATUS: DRAFT
PROJECT: {{PROJECT_NAME}}
MILESTONE: {{ACTIVE_MILESTONE}}

## Purpose

Records QA signoff events and Director certification events. Signoffs confirm that work meets acceptance criteria and is ready for release consideration.

## Signoffs

| SO-ID | Type | Scope | Signed Off By | Date | Evidence Reference | Status | Notes |
|-------|------|-------|--------------|------|--------------------|--------|-------|
<!-- EXAMPLE: | SO-001 | QA Signoff | BI-001 User Login (AC-001, AC-002) | QA_CARLOS | {{DATE}} | VALIDATION_EVIDENCE.md VE-001, VE-002 | ACCEPTED | All criteria passed | -->

## Signoff Types

- QA Signoff: QA has validated all acceptance criteria for the scope; independent validation confirmed
- Director Certification: Director has confirmed all evidence, handoffs, and signoffs are complete for the scope
- Human Approval: Human owner has approved the scope for release

## Status Values

- ACCEPTED: Signoff received and recorded
- PENDING: Signoff requested; not yet received
- REJECTED: Signoff rejected; reason in Notes; must be re-evaluated

## Notes

A QA Signoff is not the same as a Director Certification. Both are required before release. A QA Signoff from the same human who developed the feature is only valid if Director has granted a CONSTRAINED QA independence exception.
