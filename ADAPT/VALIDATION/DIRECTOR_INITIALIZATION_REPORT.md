# ADAPT Director Initialization Correction Report

FINAL STATUS: **DIRECTOR_INITIALIZATION_CORRECTION_VALIDATED_LOCALLY**

This report is ASSERTED interpretation of the accompanying GROUNDED command outputs,
artifact hashes, before/after checkpoints and immutable original inputs. It is not
independent QA, release certification or genuine approval authentication.

## Framework

- Published baseline: ADAPT-FW-0004, f499d709dfdcda9fa2f869e6675bcc152d6f5bd4.
- Local successor candidate: ADAPT-FW-0005; Framework Learning FLC-004.
- Maintenance branch: fix/director-initialization-path. One authorized local
  maintenance commit contains this report; its resolved hash and final Git state
  are recorded in .adapt-local/maintenance/director-correction-20261016/delivery.json
  after committing, avoiding a recursive commit-hash claim in the committed file.
- Authority: actual Human Owner / Framework Maintainer POST-SCAFFOLD DIRECTOR
  INITIALIZATION CORRECTION instruction, preserved unchanged in the local evidence
  folder as MAINTAINER_APPROVAL.txt. It authorizes implementation, validation and
  one local commit, not merge, push or ADAPT-DEV adoption/initialization.

## Initialization Correction

The registered entry point remains exactly `Run Director intake` (registry row 4,
Director Lane routing, existing command syntax). No command, approval gate, runtime
API, control-plane field or identity schema field was added. The unregistered
INITIALIZE_DIRECTOR_IDENTITY command remains invalid.

ACTION_PROMPT_DIRECTOR.md defines the Initial Director designation stage. It checks
completed scaffold provenance, consistent INITIALIZED/NONE state, actual empty
workcell/handoff/context/history records, current Director Lane authority, a
separately supplied original explicit Human Owner designation and its reference,
SHA256 and applicability. Missing, conflicting, changed, ambiguous or untraceable
input stops execution. Account/Git/Driver claims are never designation evidence.
Existing named owners and recorded attempts cannot reuse the setup qualification.

Only the existing HUMAN_OWNER placeholder may be replaced in DIRECTOR_IDENTITY.md;
PROJECT, ROLE: Director, WORKCELL_TYPE: Director Lane, scaffold date and unrelated
bytes are preserved. Exactly one fresh DEC-NNN row records original human evidence,
AI operator distinction, state/history/contracts, scope, hashes, stage attempts,
identity delta, effective timestamp and next action. There is no new operator field
in identity and no invented signature or approval reference.

Minimum setup evidence replaces only the otherwise unreachable initial ordinary
pack/workcell-scope requirements. All thirteen master stages remain observable;
steps 9-12 use the same designation decision for evidence/delta, human completion
instead of a fabricated lane handoff, and verification that the control plane is
unchanged. No intake entry, CP-ID, CD-ID, workcell, handoff or control-field write
is authorized in this stage. Explicit corresponding qualifications align Rule 7,
Rule 11, context/handoff guardrails, context rules, stop rules and the mutation
matrix. All ordinary dispatch and approval requirements retain their scope.

On completion, qualification expires. Source truth remains NONE and phase remains
INITIALIZED. The next registered action is a separately invoked
`Promote {{DOCUMENT}} as {{SOURCE_TRUTH_VERSION}}` with exact source/hash, unused
version, Gate 1 approval, complete history and all existing first-promotion checks.
Gate 3, ordinary versioned context and normal workcell identity/scope/assignment
remain necessary for onboarding and implementation.

## Exact changed files

Paths below are relative to ADAPT/. No unrelated framework files changed.

- CANONICAL_STARTERS/00_FRAMEWORK/GOVERNANCE_RULES.md
- CANONICAL_STARTERS/00_FRAMEWORK/ROLE_MODEL.md
- CANONICAL_STARTERS/07_GUARDRAILS/CONTEXT_GUARDRAIL.md
- CANONICAL_STARTERS/07_GUARDRAILS/HANDOFF_GUARDRAIL.md
- CANONICAL_STARTERS/10_CONTEXT_ECONOMY/CONTEXT_RULES.md
- CANONICAL_STARTERS/15_COMMANDS_AND_DRIVERS/ACTION_PROMPT_DIRECTOR.md
- CANONICAL_STARTERS/15_COMMANDS_AND_DRIVERS/ACTION_PROMPT_MASTER.md
- CANONICAL_STARTERS/15_COMMANDS_AND_DRIVERS/COMMAND_REGISTRY.md
- CANONICAL_STARTERS/15_COMMANDS_AND_DRIVERS/COMMAND_ROUTING_MATRIX.md
- CANONICAL_STARTERS/15_COMMANDS_AND_DRIVERS/MUTATION_PERMISSION_MATRIX.md
- CANONICAL_STARTERS/15_COMMANDS_AND_DRIVERS/STOP_RULES.md
- SCAFFOLD_WORKFLOW_AGENT.md
- FRAMEWORK_LEARNING_REGISTER.md
- TOOLS/tests/test_director_initialization.py
- VALIDATION/director_case.py
- VALIDATION/bootstrap_case.py
- VALIDATION/onboarding_case.py
- VALIDATION/DIRECTOR_INITIALIZATION_REPORT.md
- VALIDATION/DIRECTOR_INITIALIZATION_ACCEPTANCE.json
- VALIDATION/DIRECTOR_INITIALIZATION_TESTS.json
- VALIDATION/DIRECTOR_INITIALIZATION_GATE.json

The 12 affected contract/workflow files provide the normative stage and necessary
cross-references; FRAMEWORK_LEARNING_REGISTER.md records lineage. No change was
made to DIRECTOR_IDENTITY.md's canonical schema, first-promotion policy, human
approval gates, control-plane schema or official tooling distribution.
Validation helpers now support an actually unresolved fresh scaffold and preserve
previous decisions when allocating promotion/onboarding DEC-IDs. Previously their
fixed IDs/prepopulated synthetic owner could mask the initialization defect or
collide with the new designation record. These are test assets, not runtime tools.

## Validation

[DIRECTOR_INITIALIZATION_TESTS.json](DIRECTOR_INITIALIZATION_TESTS.json) captures
all three existing unittest suite commands, outputs and exit codes: 93 tooling
tests (including 27 new Director cases), 8 state-reader tests and 27 operator
toolkit tests: **128 passed**. The 27 focused cases cover the requested positive
checks and missing/conflicting designation, unresolved identities, wrong authority,
unsupported commands, product/control/intake writes, missing Gate 1, ordinary
implementation without identity/context, reassignment and qualification reuse.
Additional checks cover Driver spoofing, modified inputs/contracts, retained
history, active artifacts and incomplete scaffolds. Negative checks verify no
mutation after rejection. Existing bootstrap/onboarding/routing/context/mutation/
distribution tests all pass; 18 commands, 21 control fields and 15 STOP rules remain.

An initial test assertion counted the commented example source-version row as a
live promotion. It was corrected to inspect live table rows, and focused plus full
regression suites passed. Raw initial/corrected development results are retained
locally; no failed governing eligibility was bypassed.

[DIRECTOR_INITIALIZATION_ACCEPTANCE.json](DIRECTOR_INITIALIZATION_ACCEPTANCE.json)
records the final candidate-version actual disposable acceptance, not a scenario
marked passed from description alone:

1. Fresh MODE_A_EXISTING_SOLUTION / PROTECTED_DEFAULT scaffold using the official
   documented file workflow, canonical starters and official copy/verifier.
   Director owner remained unresolved, source truth NONE, phase INITIALIZED,
   no workcells/context packs/Gate 1 input. Initial artifacts and hashes retained.
2. Original explicitly labeled synthetic human designation supplied separately.
   Existing `Run Director intake` designation stage actually populated the owner
   and recorded DEC-001. Exactly two files changed; reverse/inverse hashes and
   unchanged control plane verified. No promotion executed in this dispatch.
3. Separate synthetic Gate 1 source/hash/version approval supplied afterward.
   Existing FW-0004 bounded initial-promotion procedure actually preserved source,
   checked/extracted/reused candidate IDs, reserved DEC-002, registered
   SOURCE_TRUTH_V0.1 and routed to Context Steward. AC-001 remains DRAFT.
4. First ordinary CP-0001 actually assembled and indexed with registered source,
   exact input hashes, consumed request and canonical delivery. Ordinary context
   constraints are retained, not an extension of the designation qualification.
5. Separate visibly synthetic Gate 3/Director request, scoped approval/routing
   fixtures supplied under the existing onboarding acceptance architecture.
   Its ordinary CP-0002 was actually assembled, then Onboarding Orchestrator
   generated and checked all 15 PLANNER_TESTALPHA files before registration.
   DEC-003 preserved the existing designation/promotion rows. There was no
   implementation assignment or product mutation.
6. Final checks verify ordinary implementation remains STOP_REQUIRED without
   assignment, setup qualification cannot be reused, protected project bytes and
   its Git inventory are unchanged, and all three decision IDs remain unique.

Each stage was invoked and its artifacts inspected separately, with exact command
outputs, state, changed paths, hashes and inverse checks retained. The final
disposable phase is ONBOARDING with source truth SOURCE_TRUTH_V0.1, authority
Onboarding Orchestrator, ActiveWorkcell/ActiveHandoff NONE and readiness
NEEDS_CONTEXT. This is not a claim of READY implementation or completed planning.

Limitations: synthetic inputs are test assumptions, not actual Human Owner
approvals. The minimal greeting case does not establish arbitrary document
extraction correctness. Existing onboarding Director preparation/routing records
are supplied synthetic fixtures, not independently executed general Director
dispatch certification. Actual scaffold/designation/promotion/Context Steward/
onboarding artifact transitions were exercised; no independent QA or release
certification is claimed. No new blocking contract was found in this sequence.

## Framework Learning

FLC-004: Post-scaffold Director identity initialization and first operational
entry-point reachability. Disposition PROMOTED means local incorporation under the
actual supplied Maintainer instruction. Version lineage is issued FW-0004 to
local candidate FW-0005. FLC-001/002/003 records remain byte-for-byte unchanged.
Backport ELIGIBLE and Upgrade Assessment REQUIRED do not authorize adoption.

## Repository

Branch fix/director-initialization-path; baseline HEAD/main/origin main verified
at f499d709dfdcda9fa2f869e6675bcc152d6f5bd4. The single local maintenance commit's
resolved hash and final status are preserved in delivery.json and the local copy
of this report after commit. Main remains at the baseline; no merge or push.
The user-owned .gitignore change is preserved and excluded from this commit.
worktree.md and .git/info/exclude are unchanged. Historical validation records
are untouched. All temporary files, disposable instances and backups are inside
.adapt-local; test subprocess TEMP/TMP explicitly point there, with bytecode
writes disabled. No external output directory was created.

## ADAPT-DEV Integrity

All 132 ADAPT-DEV file hashes and the full directory inventory match the initial
protected snapshot. Effective FW-0004, original FW-0002 baseline, DEC-001,
Director placeholder, control plane, source history, trial records and tools
are unchanged. SourceTruthVersion remains NONE; CurrentPhase INITIALIZED;
CurrentAuthority Director Lane; ExecutionReadiness NEEDS_PLANNING;
ActiveWorkcell/ActiveHandoff NONE. Pending Governor Decision 001 remains at
BE79FBF1A70A9260F2B3F369DC945D935F0F7A3294D46B2ADCC2A3D99E338AC9.
Read-only state/doctor exit 0; expected prompt-next BLOCKED exit 1. No identity
initialization, source promotion, context pack, workcell or lifecycle step was
performed in ADAPT-DEV.

## Next Authority Boundary

No mandatory validation blocker remains; the local candidate is ready for release
review. Main merge/publication require separate explicit Framework Maintainer
release authorization. After publication, ADAPT-DEV adoption and actual Director
designation require separate deliberate authorization/operations. This instruction
does not grant them. STOP; no next milestone was executed.
