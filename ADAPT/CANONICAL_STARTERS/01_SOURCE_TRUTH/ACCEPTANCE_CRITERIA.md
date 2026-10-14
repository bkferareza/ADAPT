# Acceptance Criteria

STATUS: DRAFT
VERSION: {{ADAPT_VERSION}}
PROJECT: {{PROJECT_NAME}}
SOURCE_TRUTH_VERSION: {{SOURCE_TRUTH_VERSION}}

## Purpose

Acceptance criteria derived from requirements. Each criterion defines a verifiable condition that must be satisfied for the linked requirement to be considered done. QA test scenarios are derived from these criteria.

## Acceptance Criteria

| AC-ID | REQ-ID | Criterion | Test Type | Status | Verified By | Notes |
|-------|--------|-----------|-----------|--------|-------------|-------|
<!-- EXAMPLE: | AC-001 | REQ-001 | User can log in with valid email and password and receive a session token | Functional | READY_FOR_TEST | — | Happy path | -->

## Status Values

- DRAFT: Recorded by the Source Truth Agent when the criterion is created, or when its text changes on re-extraction. Written only by that agent.
- READY_FOR_TEST: Accepted by the Director — the criterion is named in a milestone plan approved under Gate 4. Written by the Director Lane when recording that approval, and only for criteria in DRAFT.
- PASSED: QA verified this criterion and the Director certified it. Only the Certification Agent writes this status.
- FAILED: A QA validation report recommended FAIL for this criterion, anchored on GROUNDED evidence with at least one linked DEF-ID, and the Certification Agent recorded it. Written only by the Certification Agent. It stays the status between validation cycles until a later Certification write replaces it; the criterion may be re-validated once every linked DEF-ID is RESOLVED.
- UNVERIFIED: No declared mechanism could validate this criterion, and a Gate 6 risk acceptance naming it is recorded in DECISION_LOG.md. Not PASSED and not FAILED — nothing is asserted about whether the criterion is met. Written only by the Certification Agent, only against that Gate 6 DEC-ID. Absence of validation alone never produces this status.

Blocked is not a stored status. A criterion is blocked while an OPEN entry in `02_DIRECTOR_LANE/BLOCKER_REGISTER.md` names its AC-ID; that register is the only record of the condition. Do not write it here.

## Test Type Values

Functional / Security / Performance / Accessibility / Integration / Regression / Edge Case

## Notes

Acceptance criteria are the primary input for QA test scenarios. They must be traceable to a source requirement (REQ-ID). AC-IDs follow format AC-NNN.
