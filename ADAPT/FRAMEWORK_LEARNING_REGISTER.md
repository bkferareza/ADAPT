# FRAMEWORK LEARNING REGISTER

Current Framework Version: ADAPT-FW-0004

## Purpose

The framework-level record of framework-learning candidates and the Framework Maintainer's disposition of each, and the single declaration of the current framework version. Scaffolding copies that version into every new instance as `VERSION:`.

## Authority and Scope

- Sole writer: the Framework Maintainer (GOVERNANCE_RULES.md, Rule 14). No instance actor writes this file.
- Framework-scoped. It lives at the framework root, outside CANONICAL_STARTERS, and is never copied into an instance.
- Not instance truth. An observation stays evidence in the instance where it arose. Only a candidate's Proposed Generic Change can become framework content, and only through a PROMOTED disposition and an authorized framework patch.
- Prospective. A promoted change reaches future scaffolds through the canonical starters. Existing instances are never rewritten automatically; recovery does not overwrite existing files (DEPLOYMENT_MODES.md). Any upgrade or backport is a separate, deliberate decision.

## Framework Version

- Format ADAPT-FW-NNNN, where NNNN is a zero-padded positive integer. Numeric order is framework order.
- Declared and advanced only by the Framework Maintainer: once per authorized framework patch containing one or more PROMOTED candidates, never once per file or per candidate.
- A label, once issued, is never reused or redefined.

## Pre-Register Hardening Baseline

ADAPT-FW-0001 is the first codified hardened baseline. Its controls, including those introduced by the hardening work that created this register, predate the register and have no candidate rows here. Their rationale and acceptance evidence are held in the Framework Maintainer's hardening records outside this framework. They are not reconstructed here as candidates, and no candidate ID, decision reference or evidence record is invented for them.

ADAPT-FW-0001 becomes an issued framework state when the first instance is scaffolded from it, and is never redefined after that. A control is kept while the failure or risk it addresses still exists. Every later change to a framework control, including the simplification or removal of a baseline control, is recorded here as a candidate before it is promoted.

## Raising a Candidate

A candidate is recorded only when it meets the framework-learning threshold in GOVERNANCE_RULES.md, Rule 14. It arrives by Director escalation of a GAP-T14 Framework Gap or a qualifying Memory Bank lesson.

Novelty Dimensions name what was materially new, one or more of: SOLUTION_OR_REPOSITORY, ROLE, WORK_TYPE, EXECUTION_PATH, VALIDATION_MECHANISM, DEPLOYMENT_OR_RUNTIME, GOVERNANCE_COMBINATION. GOVERNANCE_COMBINATION means a combination of authorities, gates, approvals, exceptions, or governance conditions exercised together in one flow that has not previously been exercised as that combination.

Evidence lists the references and their evidence class (GOVERNANCE_RULES.md, Rule 5). Solution-Specific Portion and Proposed Generic Change are always recorded separately.

## Dispositions

- `—` — pending; not yet disposed
- PROMOTED — the generic change is incorporated; requires Decision and Introduced In
- REJECTED_NON_GENERIC — valid but solution-specific; stays local
- REJECTED_INSUFFICIENT_EVIDENCE — not established; may be re-raised with more evidence
- ALREADY_COVERED — an existing control handles it; Decision names that control
- DEFERRED — valid but postponed; Decision gives the reason
- CONTRADICTED — stronger evidence shows the claim is wrong; Decision cites it

A disposed candidate is never deleted. Introduced In (an ADAPT-FW-NNNN label), Backport (ELIGIBLE or NOT_ELIGIBLE) and Upgrade Assessment (REQUIRED or NOT_REQUIRED) apply only to PROMOTED candidates and are `—` otherwise. Candidate IDs follow FLC-NNN.

## Candidates

FLC-003 records the Human Framework Maintainer's ONBOARDING LANE GOVERNANCE
CORRECTION directive (2026-10-16), following the read-only worklane audit and
first-workcell disposition for ADAPT-SELF-HOST-001. The confirmed conflict is
ONBOARDING_RULES Director identity precondition versus onboarding V-01's registry
dependency, combined with Rule 11 and master dispatch's missing onboarding lane
identity/scope basis. This is external maintenance, not an ADAPT-DEV workcell action.
The directive authorizes bounded implementation, focused and actual fresh-instance
validation, Framework Learning and a local maintenance commit only. Publication,
main merge, instance adoption and real workcell creation are not authorized.
ADAPT-FW-0004 is the next local candidate after issued ADAPT-FW-0003, advanced
once for this patch. PROMOTED means local incorporation; validation evidence and
limitations are in VALIDATION/ONBOARDING_REPORT.md and its linked raw records.

FLC-002 is raised from the Human Owner-confirmed FRAMEWORK_BOOTSTRAP_CONTRACT_GAP
in ADAPT-SELF-HOST-001. The initial Human Owner / Framework Maintainer directive,
ADAPT — BOOTSTRAP RECOVERY MILESTONE (2026-10-16), reaffirms the accepted bounded
correction and authorizes external framework implementation, validation and a
local maintenance commit only. No publication or instance adoption is authorized.
This records supplied human authority, not an AI self-approval or historical signature.

FLC-002 was incorporated locally under that supplied maintainer disposition.
ADAPT-FW-0003 is the next label after ADAPT-FW-0002, advanced once for this single
authorized patch. The interrupted, recovered attempt created no published
successor. No issued label or published lineage is redefined.

The Human Owner's subsequent BOOTSTRAP V2 FINAL ACCEPTANCE AND RELEASE directive
(2026-10-16) explicitly authorizes publication to GitHub main only after MODE_A
acceptance, existing MODE_B verification, regressions, integrity and governance
gates pass. This supplied conditional Framework Maintainer release decision
supersedes the earlier local-only delivery limit. No additional release approval
is required by this register or Rule 14; no AI self-approval, independent QA,
instance adoption or self-hosted development-lane success is implied. The gate
and both deployment modes are recorded in VALIDATION/BOOTSTRAP_V2_GATE.json,
VALIDATION/BOOTSTRAP_V2_ACCEPTANCE.json and VALIDATION/BOOTSTRAP_V2_REPORT.md.
Release completion is verified against remote refs; a prepared record alone
does not claim that a push has happened. No further version increment accompanies
this validation/documentation completion of the same FLC-002 patch.

| FLC-ID | Observed In | Evidence | Novelty Dimensions | Solution-Specific Portion | Proposed Generic Change | Disposition | Decision | Introduced In | Backport | Upgrade Assessment |
|---|---|---|---|---|---|---|---|---|---|---|

| FLC-003 | ADAPT-SELF-HOST-001; read-only worklane audit and Maintainer disposition, 2026-10-16 | GROUNDED: original contracts at a9082ec9267927f68bf338813e0438fb0122d510; VALIDATION/ONBOARDING_ACCEPTANCE.json and VALIDATION/ONBOARDING_TESTS.json; ASSERTED interpretation and limitations: VALIDATION/ONBOARDING_REPORT.md | EXECUTION_PATH, GOVERNANCE_COMBINATION | No frozen instance operational state incorporated; no instance adoption | Verify human Director designation from identity artifact; bind first and subsequent onboarding to existing lane authority, ordinary context, Gate 3 and exact pre-workcell governance scope | PROMOTED | Human Framework Maintainer ONBOARDING LANE GOVERNANCE CORRECTION explicitly authorizes this bounded external patch and local commit after validation; no publication, independent QA certification or adoption granted | ADAPT-FW-0004 | ELIGIBLE | REQUIRED |

| FLC-001 | Tooling v1 consolidation, 2026-10-15; owner-raised framework gap review | GROUNDED: VALIDATION/TOOLING_V1_TEST_OUTPUT.txt, TOOLS/MANIFEST.json; ASSERTED summary: VALIDATION/TOOLING_V1_RELEASE.md | GOVERNANCE_COMBINATION, VALIDATION_MECHANISM | No client instance or solution-specific changes | Align placeholder validation, lifecycle ownership and schema write precedence; distribute read-only tools with explicit handoff-bound preview and reproducible copy verification | PROMOTED | Current repository-owner/Framework Maintainer directive: ADAPT — TOOLING V1 COMPLETION AND PUBLICATION; explicitly authorizes this scoped correction, promotion and publication after validation. Recorded on behalf of that human authority, not an AI/Director self-approval or historical signature. See VALIDATION/TOOLING_V1_RELEASE.md. | ADAPT-FW-0002 | ELIGIBLE | REQUIRED |
| FLC-002 | ADAPT-SELF-HOST-001; owner-confirmed FRAMEWORK_BOOTSTRAP_CONTRACT_GAP | GROUNDED: original contracts at 37f465782ef1fb69bc58da46bcc5969d6bea8220, VALIDATION/BOOTSTRAP_V2_ACCEPTANCE.json (original MODE_B and final MODE_A), VALIDATION/BOOTSTRAP_V2_TESTS.json, VALIDATION/BOOTSTRAP_V2_GATE.json; ASSERTED interpretation, affected contracts and limitations: VALIDATION/BOOTSTRAP_V2_REPORT.md | EXECUTION_PATH, GOVERNANCE_COMBINATION | No instance-specific operational state incorporated; frozen instance unchanged | Single-use first-promotion initial basis followed by ordinary versioned Context Steward assembly | PROMOTED | Human Owner / Framework Maintainer BOOTSTRAP RECOVERY MILESTONE approved local implementation; subsequent BOOTSTRAP V2 FINAL ACCEPTANCE AND RELEASE, 2026-10-16, explicitly authorizes publication after recorded MODE_A/MODE_B, regression, integrity and governance gates pass. Recorded on behalf of that human; no independent certification or adoption claimed. | ADAPT-FW-0003 | ELIGIBLE | REQUIRED |
