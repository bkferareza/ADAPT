# FRAMEWORK LEARNING REGISTER

Current Framework Version: ADAPT-FW-0006

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

## FW-0006 release incorporation

FLC-005 is PROMOTED under the final exact-revision Human Framework Maintainer
decision retained with review package FW0006-RELEASE-20261103. This advances the
single framework declaration to ADAPT-FW-0006. VALIDATION/FW0006_RELEASE.md binds
the candidate, corrected acceptance evidence, metadata patch and publication scope.
The dated scope/development records below retain their historical DEFERRED and
FW-0005 statements; this prospective disposition supersedes their release status.
Existing-instance adoption and every recovery action require separate approval.

## Candidates

FLC-005 final prospective scope correction, 2026-11-02 (Asia/Manila), under
Rule 14: the Human Framework Maintainer directs HUMAN_GOVERNED as the sole
recovery model and removes autonomous privileged recovery and mandatory operator
isolation/authentication infrastructure. This is an explicit scope-change decision,
not a waiver inferred from tests. Requirement C and SC-03/SC-07/SC-12 now test
normal-interaction human approval plus existing bounded execution safety, using
clearly labelled simulated decisions for engineering acceptance. Exact decision,
authority hash, historical requirement mapping, preserved safeguards and revised
A-O acceptance are in VALIDATION/FW0006_HUMAN_GOVERNED_SCOPE.md and local evidence
.adapt-local/maintenance/fw0006-human-governed-final/MAINTAINER_SCOPE_DECISION.json.
Historical registration, failed acceptance and journals remain unchanged. No
independent authentication, cryptographic provenance or malicious-agent resistance
is claimed. FLC-005 remains DEFERRED; effective framework remains ADAPT-FW-0005.
Final exact-revision promotion/publication and existing-instance adoption require
separate decisions. This direction authorizes implementation, validation and an
incremental candidate commit/push and draft PR update, not official release.


FLC-005 prospective scope correction, 2026-10-24 (Asia/Manila): the Human
Framework Maintainer explicitly removed provider-specific trust infrastructure
and retained human-supervised authorization and bounded recovery safety
requirements. This supersedes that development direction prospectively; prior
decisions and evidence remain preserved under .adapt-local/maintenance.
The supplied scope decision, exact mutation hashes, focused validation and finite
remaining-work checklist are recorded in
.adapt-local/maintenance/fw0006-scope-consolidation/MAINTAINER_SCOPE_DECISION.json
and REPORT.md. FLC-005 remains DEFERRED; effective version remains ADAPT-FW-0005.
No promotion, version advance, publication, adoption, operational recovery or
blocker resolution is authorized by this cleanup. SC-05 is not implemented here.

FLC-004 records the Human Owner / Framework Maintainer's POST-SCAFFOLD DIRECTOR
INITIALIZATION CORRECTION directive (2026-10-16) for ADAPT-SELF-HOST-001. The
confirmed FRAMEWORK_INITIALIZATION_PATH_GAP is evidenced by the frozen FW-0004
instance's unresolved Director owner and rejection of the unregistered standalone
initialization request. Its local preflight report and original human inputs
remain in the workspace's ignored .adapt-local storage; no instance data is
incorporated into generic contracts.

The directive authorizes bounded external implementation, focused/regression and
fresh-scaffold validation, Framework Learning and one local maintenance commit.
It does not authorize main merge, push, instance adoption or real Director
initialization. FLC-004 is PROMOTED as local incorporation only. ADAPT-FW-0005 is
the next local candidate after published ADAPT-FW-0004 at
f499d709dfdcda9fa2f869e6675bcc152d6f5bd4; no issued label is reused or historical
FLC disposition rewritten. The initial 27 focused cases, 128 regression tests and
actual disposable MODE_A sequence passed before advancing this candidate.
Final candidate-version acceptance, exact contract scope and limitations are
recorded in VALIDATION/DIRECTOR_INITIALIZATION_REPORT.md and its linked records.
Synthetic human inputs are fixtures, not real approvals or independent QA.

FLC-003 records the Human Framework Maintainer's ONBOARDING LANE GOVERNANCE
CORRECTION directive (2026-10-16), following the read-only worklane audit and
first-workcell disposition for ADAPT-SELF-HOST-001. The confirmed conflict is
ONBOARDING_RULES Director identity precondition versus onboarding V-01's registry
dependency, combined with Rule 11 and master dispatch's missing onboarding lane
identity/scope basis. This is external maintenance, not an ADAPT-DEV workcell action.
The initial directive authorized bounded implementation, focused and actual fresh-instance
validation, Framework Learning and a local maintenance commit only. Publication,
main merge, instance adoption and real workcell creation are not authorized.
ADAPT-FW-0004 is the next local candidate after issued ADAPT-FW-0003, advanced
once for this patch. PROMOTED initially recorded local incorporation; validation evidence and
limitations are in VALIDATION/ONBOARDING_REPORT.md and its linked raw records.

The Human Owner / Framework Maintainer's subsequent FRAMEWORK V0004 RELEASE
directive (2026-10-16) explicitly authorizes publication of this validated patch
after final release checks, superseding the initial local-only limit. It also
authorizes read-only preparation of future controlled ADAPT-DEV adoption, not
actual adoption. No further version increment accompanies release documentation.
Original synthetic acceptance remains evidence at db4a00cefc65838be68b758ebbca867908d5da7a;
release reruns and the retained local gate are in VALIDATION/ONBOARDING_TESTS.json
and VALIDATION/ONBOARDING_GATE.json. No independent QA or Director dispatch
certification is implied. Publication completion requires remote verification;
this authorization record alone does not claim a completed push.

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

| FLC-004 | ADAPT-SELF-HOST-001; Human Owner-confirmed FRAMEWORK_INITIALIZATION_PATH_GAP, 2026-10-16 | GROUNDED: original contracts at f499d709dfdcda9fa2f869e6675bcc152d6f5bd4; VALIDATION/DIRECTOR_INITIALIZATION_ACCEPTANCE.json, VALIDATION/DIRECTOR_INITIALIZATION_TESTS.json, VALIDATION/DIRECTOR_INITIALIZATION_GATE.json; ASSERTED interpretation: VALIDATION/DIRECTOR_INITIALIZATION_REPORT.md | EXECUTION_PATH, GOVERNANCE_COMBINATION | Named human and frozen ADAPT-DEV state remain local; no instance adoption or real designation | Bounded initial Director designation through existing Run Director intake, exact identity/decision scope and traceable human input before first promotion; qualify initial lane/context/completion requirements only for that stage | PROMOTED | Human Owner acting as Framework Maintainer explicitly approved POST-SCAFFOLD DIRECTOR INITIALIZATION CORRECTION: bounded implementation, validation and one local maintenance commit only; no main merge, push, instance adoption or real initialization. Recorded supplied human authority, not AI self-approval or an invented signature. | ADAPT-FW-0005 | ELIGIBLE | REQUIRED |

| FLC-003 | ADAPT-SELF-HOST-001; read-only worklane audit and Maintainer disposition, 2026-10-16 | GROUNDED: original contracts at a9082ec9267927f68bf338813e0438fb0122d510; VALIDATION/ONBOARDING_ACCEPTANCE.json, VALIDATION/ONBOARDING_TESTS.json and VALIDATION/ONBOARDING_GATE.json; ASSERTED interpretation and limitations: VALIDATION/ONBOARDING_REPORT.md | EXECUTION_PATH, GOVERNANCE_COMBINATION | No frozen instance operational state incorporated; no instance adoption | Verify human Director designation from identity artifact; bind first and subsequent onboarding to existing lane authority, ordinary context, Gate 3 and exact pre-workcell governance scope | PROMOTED | Human Framework Maintainer ONBOARDING LANE GOVERNANCE CORRECTION approved implementation/local commit; subsequent FRAMEWORK V0004 RELEASE explicitly approves publication after final checks and read-only adoption preparation. No actual adoption or independent certification authorized. | ADAPT-FW-0004 | ELIGIBLE | REQUIRED |

| FLC-001 | Tooling v1 consolidation, 2026-10-15; owner-raised framework gap review | GROUNDED: VALIDATION/TOOLING_V1_TEST_OUTPUT.txt, TOOLS/MANIFEST.json; ASSERTED summary: VALIDATION/TOOLING_V1_RELEASE.md | GOVERNANCE_COMBINATION, VALIDATION_MECHANISM | No client instance or solution-specific changes | Align placeholder validation, lifecycle ownership and schema write precedence; distribute read-only tools with explicit handoff-bound preview and reproducible copy verification | PROMOTED | Current repository-owner/Framework Maintainer directive: ADAPT — TOOLING V1 COMPLETION AND PUBLICATION; explicitly authorizes this scoped correction, promotion and publication after validation. Recorded on behalf of that human authority, not an AI/Director self-approval or historical signature. See VALIDATION/TOOLING_V1_RELEASE.md. | ADAPT-FW-0002 | ELIGIBLE | REQUIRED |
| FLC-002 | ADAPT-SELF-HOST-001; owner-confirmed FRAMEWORK_BOOTSTRAP_CONTRACT_GAP | GROUNDED: original contracts at 37f465782ef1fb69bc58da46bcc5969d6bea8220, VALIDATION/BOOTSTRAP_V2_ACCEPTANCE.json (original MODE_B and final MODE_A), VALIDATION/BOOTSTRAP_V2_TESTS.json, VALIDATION/BOOTSTRAP_V2_GATE.json; ASSERTED interpretation, affected contracts and limitations: VALIDATION/BOOTSTRAP_V2_REPORT.md | EXECUTION_PATH, GOVERNANCE_COMBINATION | No instance-specific operational state incorporated; frozen instance unchanged | Single-use first-promotion initial basis followed by ordinary versioned Context Steward assembly | PROMOTED | Human Owner / Framework Maintainer BOOTSTRAP RECOVERY MILESTONE approved local implementation; subsequent BOOTSTRAP V2 FINAL ACCEPTANCE AND RELEASE, 2026-10-16, explicitly authorizes publication after recorded MODE_A/MODE_B, regression, integrity and governance gates pass. Recorded on behalf of that human; no independent certification or adoption claimed. | ADAPT-FW-0003 | ELIGIBLE | REQUIRED |
| FLC-005 | ADAPT-SELF-HOST-001; BLOCKED_STATE_RECOVERY_ENTRY_DEADLOCK; current exceptional Human Director escalation, 2026-10-18 | GROUNDED bytes/hashes: .adapt-local/maintenance/fw0006-governance-bootstrap/evidence-manifest.json, ORIGINAL_HUMAN_REQUEST.txt, EXCEPTIONAL_DECISION.json, DIRECTOR_ESCALATION.json, MAINTAINER_RECEIPT.json; historical BLK-001 / Step 1 completion / Step 2 refusal; registration diagnosis, prospective entry/context contracts, recovery_preflight.py and focused tests referenced therein. ASSERTED qualification and remaining acceptance: .adapt-local/maintenance/fw0006-governance-bootstrap/REPORT.md; SC-01 through SC-12 remain proposed, not full runtime passes | EXECUTION_PATH, GOVERNANCE_COMBINATION | Historical local CRLF parser failure and repaired blocker register placement are supporting local evidence; named human, BLK-001 HIGH OPEN, HO-007 exhausted attempts and ADAPT-DEV state remain local and unchanged | Bounded Recovery Bootstrap and Blocked-State Framework Escalation Entry. Missing governance invariant / recovery execution-path deficiency: lawful bounded recovery and escalation independent of unavailable ordinary execution prerequisites; recovery-purpose authorization and context; canonical integrity/evidence; genuine Director-origin exceptional escalation; human approval and writer restrictions; existing blocker-resolution handback; no retry-history loss; mandatory FUTURE ADAPT SCAFFOLDS contracts, supported tooling, original approval traceability and regression protection SC-01 through SC-12 plus linked escalation-entry acceptance; ordinary guardrails/lifecycle preserved; no historical OPEN BLK-001 or ADAPT-DEV gaps in fresh scaffolds; separate existing-instance adoption and operational handback | PROMOTED | Final Human Framework Maintainer exact-revision decision recorded separately in .adapt-local/maintenance/fw0006-release-review-20261103/FINAL_MAINTAINER_DECISION.json; incorporation under revised HUMAN_GOVERNED scope and validated source/evidence inventory. No instance adoption or recovery operation is included. | ADAPT-FW-0006 | ELIGIBLE | REQUIRED |


## Prospective human-operability correction (2026-11-03)

The Human Framework Maintainer directive HUMAN COMMUNICATION AND APPROVAL
EXPERIENCE authorizes a bounded implementation and prospective preparation.
The current register was checked: FLC-001 through FLC-005 exist; FLC-006 is the
next candidate and is recorded below without promotion. Current Framework
Version remains ADAPT-FW-0006. No issued version or prior disposition changes.

| FLC-ID | Observed In | Evidence | Novelty Dimensions | Solution-Specific Portion | Proposed Generic Change | Disposition | Decision | Introduced In | Backport | Upgrade Assessment |
|---|---|---|---|---|---|---|---|---|---|---|
| FLC-006 | Maintainer-confirmed human approval interaction failure, 2026-11-03 | GROUNDED: current MaintenanceEntry technical review/callback, ACTION_PROMPT contracts; simulated acceptance in TOOLS/tests/test_recovery_human_interaction.py; limitations and exact review package in VALIDATION/HUMAN_COMMUNICATION_CORRECTION_REPORT.md | EXECUTION_PATH, GOVERNANCE_COMBINATION | ADAPT-DEV Context Index repair and separate local reporting-wrapper assertion remain local; no instance changes | Bounded Governor Feature B human interaction and ECON Human Operability slice: readable review/result, durable exact review pause/re-entry, plain response through existing supervised adapter, separate recovery/reporting outcomes | — | Pending Maintainer disposition and exact release review; implementation authorized by current directive, no publication or adoption | — | — | — |

Proposed next version: ADAPT-FW-0007, subject to an exact-image Maintainer
decision. Candidate source retains the FW-0006 runtime compatibility constant
and issued declaration while under development; it is not an issued FW-0006
replacement. Before publication, separately reviewed release metadata must
advance the declaration, runtime compatibility and manifest consistently and
qualify that exact image. No approval transfers to those unreviewed bytes.
Governor Feature A remains separate; full Feature B, ECON and FDRCB are pending.
