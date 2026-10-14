# VALIDATION REPORT

STATUS: DRAFT
VALIDATION_REPORT_ID: VR-{{SEQUENCE}}
QA_WORKCELL_ID: {{QA_WORKCELL_ID}}
SOURCE_TRUTH_VERSION: {{SOURCE_TRUTH_VERSION}}
SCOPE: {{VALIDATION_SCOPE}}
DATE: {{DATE}}
QA_INDEPENDENCE_STATUS: {{FULL / CONSTRAINED}}
ANCHORING: {{FULLY_ANCHORED / PARTIALLY_ANCHORED / UNANCHORED}}

---

> **QA Independence Note:** If QA_INDEPENDENCE_STATUS is CONSTRAINED, the nature of the constraint must be documented in `02_DIRECTOR_LANE/DECISION_LOG.md` and referenced here. A constrained independence status limits the probative value of this report and must be disclosed to the Director.

---

## Test Cases Executed

| TC-ID | AC-ID | Result | Evidence Reference |
|-------|-------|--------|-------------------|
| {{TC-ID}} | {{AC-ID}} | PASS / FAIL / BLOCKED / NOT_RUN | `{{EVIDENCE_PATH}}` |

[Every acceptance criterion in scope must have at least one corresponding test case. Untested acceptance criteria must appear with result NOT_RUN and a reason in the evidence reference column.]

**Three vocabularies, kept separate.** Test-case results are PASS / FAIL / BLOCKED /
NOT_RUN — what happened when one test case ran. Per-criterion recommendations are PASS /
CONDITIONAL_PASS / FAIL / VALIDATION_UNAVAILABLE — what QA recommends about one acceptance
criterion. Acceptance-criterion status — DRAFT / READY_FOR_TEST / PASSED / FAILED /
UNVERIFIED, in `ACCEPTANCE_CRITERIA.md` — has a named writer for each value in that file,
and is never written by this report. A test case's PASS is not a criterion's PASS, and neither is
PASSED.

---

## Defects Found

| DEF-ID | Severity | AC-ID | Status | Notes |
|--------|---------|-------|--------|-------|
| {{DEF-ID}} | CRITICAL / HIGH / MEDIUM / LOW | {{AC-ID}} | OPEN / RESOLVED / DEFERRED | {{DEFECT_NOTES}} |

If no defects were found, state: "No defects found."

**Severity definitions:**
- `CRITICAL` — acceptance criterion cannot be met; release is blocked
- `HIGH` — significant deviation from acceptance criterion; fix required before Director can approve
- `MEDIUM` — partial deviation; Director decides whether to approve with condition
- `LOW` — cosmetic or minor deviation; Director decides

---

## Coverage Summary

| Metric | Count |
|--------|-------|
| Acceptance criteria in scope | {{TOTAL_AC}} |
| Test cases executed | {{TOTAL_TC}} |
| Criteria recommended PASS | {{AC_PASS}} |
| Criteria recommended CONDITIONAL_PASS | {{AC_CONDITIONAL_PASS}} |
| Criteria recommended FAIL | {{AC_FAIL}} |
| Criteria recommended VALIDATION_UNAVAILABLE | {{AC_VALIDATION_UNAVAILABLE}} |
| Criteria without an outcome (tests BLOCKED) | {{AC_BLOCKED}} |
| Defects: CRITICAL | {{DEF_CRITICAL}} |
| Defects: HIGH | {{DEF_HIGH}} |
| Defects: MEDIUM | {{DEF_MEDIUM}} |
| Defects: LOW | {{DEF_LOW}} |

---

## Evidence

Validation evidence artifacts produced during this QA pass:

| Evidence ID | Description | Location |
|------------|-------------|---------|
| {{EVIDENCE_ID}} | {{EVIDENCE_DESCRIPTION}} | `05_VALIDATION/EVIDENCE/{{EVIDENCE_ID}}.md` |

---

## Residual Risks

Risks that testing could not eliminate:

| Risk | AC-IDs Affected | Likelihood | Recommendation |
|------|----------------|-----------|---------------|
| {{RISK_DESCRIPTION}} | {{AC-IDs}} | HIGH / MEDIUM / LOW | {{RECOMMENDATION}} |

If none, state: "No residual risks identified."

---

## Oracle and Anchoring

Mechanisms are those declared in `05_VALIDATION/QA_STRATEGY.md`, Validation Oracle. A
criterion is ANCHORED only when at least one of its test cases was executed by a declared
AVAILABLE mechanism and produced GROUNDED evidence (GOVERNANCE_RULES.md, Rule 5).
Otherwise it is UNANCHORED.

| AC-ID | Mechanism ID(s) | Evidence class | Anchored | Per-criterion recommendation |
|-------|-----------------|----------------|----------|------------------------------|
| {{AC-ID}} | {{VO-ID or NONE}} | GROUNDED / REVIEWED / ASSERTED | YES / NO | PASS / CONDITIONAL_PASS / FAIL / VALIDATION_UNAVAILABLE |

Report anchoring:
- FULLY_ANCHORED — every criterion in scope is anchored
- PARTIALLY_ANCHORED — some are. The QA Recommendation below covers anchored criteria
  only, and every unanchored criterion is listed above with VALIDATION_UNAVAILABLE
- UNANCHORED — none are. The QA Recommendation must be VALIDATION_UNAVAILABLE

An UNANCHORED criterion's per-criterion recommendation is always VALIDATION_UNAVAILABLE.
PASS, CONDITIONAL_PASS and FAIL each assert something about a criterion; none may be
issued without anchored evidence. A criterion that could not be validated is not a
criterion that failed.

---

## QA Recommendation

**Recommendation:** PASS / CONDITIONAL_PASS / FAIL / VALIDATION_UNAVAILABLE

| Value | Meaning |
|-------|---------|
| PASS | All acceptance criteria in scope are met. No defects outstanding. Director may approve. |
| CONDITIONAL_PASS | Minor issues outstanding. Director must review conditions below and decide whether to approve. |
| FAIL | One or more acceptance criteria are shown not met by anchored evidence. Defects must be resolved before re-validation. |
| VALIDATION_UNAVAILABLE | No declared mechanism produced grounded evidence for the criteria this recommendation covers. Nothing is asserted about whether they are met. The Director decides how to proceed. |

**Conditions (if CONDITIONAL_PASS):**

{{QA_CONDITIONS}}

[List specific conditions the Director must evaluate before approving. Reference DEF-IDs and AC-IDs.]

**QA Recommendation Rationale:**

{{RECOMMENDATION_RATIONALE}}

---

## Handoff to Director

The Director must decide the following based on this report:

- {{DIRECTOR_DECISION_ITEM_1}}
- {{DIRECTOR_DECISION_ITEM_2}}

[Specify the exact decisions required: approve for release, require defect resolution, grant conditional approval, or request re-validation. Do not leave this section generic — tailor it to the actual findings above.]

---

## QA Independence Note

This report is the product of QA validation under the independence status recorded in
its header. Where QA_INDEPENDENCE_STATUS is FULL, the QA workcell (`{{QA_WORKCELL_ID}}`)
is a distinct identity from every workcell that implemented the items validated here.
Where it is CONSTRAINED, the same human holds both roles under the exception referenced
above; this report is then not independent review, and only criteria anchored by GROUNDED
evidence carry verified status (GOVERNANCE_RULES.md, Rule 13).
