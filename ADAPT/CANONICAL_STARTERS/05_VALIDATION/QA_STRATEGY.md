# QA Strategy

STATUS: DRAFT
PROJECT: {{PROJECT_NAME}}
SOURCE_TRUTH_VERSION: {{SOURCE_TRUTH_VERSION}}
MILESTONE: {{ACTIVE_MILESTONE}}

## Purpose

Defines the QA approach, independence model, test types, and coverage priorities for this ADAPT instance. QA validates against accepted source truth and acceptance criteria — not against developer assumptions.

## QA Independence Model

QA Independence Status: {{QA_INDEPENDENCE_STATUS}}

Valid values: FULL (separate human/AI) | CONSTRAINED (same human, Director exception granted) | BLOCKED (cannot proceed without exception)

Exception Reference (if CONSTRAINED): {{DIRECTOR_EXCEPTION_REFERENCE}}

## Validation Oracle

Oracle Declaration Status: UNDECLARED

Valid values: DECLARED (the Director has recorded which mechanisms can validate this
solution) | NONE (the Director has recorded that no independent mechanism exists) |
UNDECLARED (no decision recorded — QA must not begin)

Declaration Reference: NONE

| Mechanism ID | Type | Validates | Grounded evidence it produces | Availability | Notes |
|--------------|------|-----------|-------------------------------|--------------|-------|
<!-- EXAMPLE: | VO-01 | AUTOMATED_TESTS | Behaviour of the functions under functions/ | Test-runner output with the command that ran | AVAILABLE | Local only; no CI runs it | -->

Type values:
- AUTOMATED_TESTS — a test runner executes the solution's tests and reports results
- BUILD_OR_STATIC_CHECK — compilation, packaging, linting or schema validation
- RUNTIME_ENVIRONMENT — an environment where the solution runs and its behaviour can be
  exercised and captured
- REFERENCE_COMPARISON — output compared with a named reference: a legacy system, a
  production baseline, or an external result
- HUMAN_RUNTIME_VERIFICATION — a person exercises the running solution. It anchors
  validation only when the observation is captured (log, recording, screenshot); an
  uncaptured observation is REVIEWED or ASSERTED evidence, not GROUNDED

Availability values: AVAILABLE (usable now) | UNAVAILABLE (declared but not currently
usable — tests that depend on it are BLOCKED, not failed)

The declaration is a Director decision, recorded with a DEC-ID in Declaration Reference.
Repository discovery may observe that a mechanism appears to exist; that observation is
OBSERVED_EVIDENCE until the Director declares it. A mechanism is never declared by the
workcell whose work it would validate.

QA stopping on UNDECLARED raises a GAP-T10 Decision Gap routed to the Director. The
Director resolves it by recording the declaration — or the decision that no mechanism
exists — in DECISION_LOG.md and writing this section, including Declaration Reference. A
direct operator instruction is sufficient authorization. No other lane writes this section.

## Test Types Planned

| Test Type | Scope | Tools (if known) | Priority | Notes |
|-----------|-------|-------------------|----------|-------|
<!-- EXAMPLE: | Functional | Core user flows per acceptance criteria | {{TEST_TOOL}} | HIGH | All MUST_HAVE requirements | -->
<!-- EXAMPLE: | Regression | Previously passing scenarios | {{TEST_TOOL}} | HIGH | Run after each integration | -->
<!-- EXAMPLE: | Security | Auth flows, input validation | {{TEST_TOOL}} | HIGH | — | -->
<!-- EXAMPLE: | Performance | Key API endpoints | {{TEST_TOOL}} | MEDIUM | Load profile TBD | -->
<!-- EXAMPLE: | Accessibility | UI components | {{TEST_TOOL}} | MEDIUM | WCAG 2.1 AA target | -->

## Coverage Priorities

- Priority 1: Acceptance criteria for MUST_HAVE requirements
- Priority 2: Acceptance criteria for SHOULD_HAVE requirements
- Priority 3: Regression coverage for previously accepted work
- Priority 4: Edge cases and security scenarios

## QA Entry Criteria

QA begins only when:
1. Director has assigned QA work via handoff
2. Accepted source truth version is identified
3. Acceptance criteria are in READY_FOR_TEST status, or FAILED with every linked DEF-ID
  RESOLVED (re-validation)
4. Developer handoff with evidence has been received
5. Oracle Declaration Status is DECLARED or NONE. If it is UNDECLARED, QA does not
   begin; route to the Director.

## QA Exit Criteria

QA is complete when:
1. Every acceptance criterion in scope — READY_FOR_TEST, or FAILED under re-validation —
  has a per-criterion outcome in the QA validation report: PASS, CONDITIONAL_PASS, FAIL,
  or VALIDATION_UNAVAILABLE. QA does not write acceptance-criterion status.
2. All found defects are recorded in DEFECT_REGISTER.md
3. QA Evidence Certifier has reviewed completeness
4. QA Handoff Preparer has sent results to Director
