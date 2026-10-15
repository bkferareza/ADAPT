# ADAPT Bootstrap v2 Implementation and Release Evidence

Date: 2026-10-16 (Asia/Manila). External Framework Maintainer correction.
Source experiment: ADAPT-SELF-HOST-001. Finding: FRAMEWORK_BOOTSTRAP_CONTRACT_GAP.
This document is an ASSERTED implementation/validation interpretation; the raw
mechanically checkable records are linked below. It is not independent QA or
framework release certification, and is not a successful self-hosted development lane.

The implementation sections retain the local delivery record at `5e85373`.
The final acceptance and release gate section below supersedes its local-only
publication boundary and MODE_B-only coverage. Publication itself requires
successful remote-ref verification; this prepared evidence does not assert a push.

## Framework and authority

Original version: ADAPT-FW-0002, commit
`37f465782ef1fb69bc58da46bcc5969d6bea8220`.
Branch: `fix/initial-source-truth-bootstrap-v2`.
Corrected local version candidate: ADAPT-FW-0003.

The initial Human Owner BOOTSTRAP RECOVERY MILESTONE directive reaffirmed the
previously accepted bounded disposition: correct the generic first-promotion
context deadlock, validate, document through Framework Learning, and create a
local maintenance commit. Publication, merging main, ADAPT-DEV initialization/
adoption and other enhancements are excluded. This records that supplied human
authority; no historical signature or independent approval is fabricated.
The recovered implementation is non-authoritative reference material; this
patch is governed by the live contracts and current directive.

The confirmed conflict is grounded in the original baseline's
ACTION_PROMPT_MASTER Step 6, CONTEXT_RULES Rules 1-2, CONTEXT_GUARDRAIL missing/
unversioned-pack stop, and SCAFFOLD_WORKFLOW_AGENT's NONE / INITIALIZED completion
state. Promotion requires a pack whose registered source version does not yet
exist. The Human Owner supplied the accepted finding and experiment attribution;
no unavailable historical runtime trace or active instance state is reconstructed.

## Correction and affected contracts

The normative procedure is **First-Promotion Initial Context Basis** in canonical
SOURCE_AUTHORITY_POLICY.md. It qualifies the existing Promote command. No new
command, executing runtime capability, database or control plane is introduced.

All eligibility conditions are mandatory: valid canonical instance and frozen
framework; NONE / INITIALIZED; no previous promotion anywhere (including retained
archive/superseded history); no active implementation workcell, execution lane,
milestone, cycle or handoff; current human request for one exact document and
unused version; applicable traceable Gate 1 approval; readable complete source
bound to SHA256; identified Director authority; no unresolved eligibility conflict.

The initial basis records the request/approval, document identities/locations/hash,
version, frozen contract references/hashes, complete initial state, history checks,
Director identity/permissions, exact per-file/field writes, size/guardrails and
stage/completion evidence. It is not an ordinary context pack or general token.
Reservation in existing intake/decision records precedes source preservation and
other promotion writes. The Source Truth Agent performs the existing extraction,
duplicate comparison and verbatim checks; new/changed acceptance criteria are DRAFT.

Registration consumes the basis. Its only remaining use is the already-declared
completion evidence/state for that same promotion. The post-state is registered
SourceTruthVersion, SOURCE_TRUTH_READY / NEEDS_CONTEXT, and Director routing to
Context Steward. ActiveWorkcell, ActiveHandoff, ActiveMilestone and ActiveCycle
remain NONE. No invented identity, READY transition or implementation authority.

Context Steward uses its existing self-assembly rule against the registered version
and the addressed Director handoff. It processes the real CD-ID, assembles/indexes
an ordinary versioned pack, consumes its assembly request, emits the review delivery
handoff and stops. The pack's task is the active review handoff; consumed assembly
request is provenance. ActiveHandoff retains its existing workcell-binding semantics.
The Steward writes no Authority field; LastContextDelta never contains a CP-ID.
Further Director work requires ordinary context and lawful authority acquisition.

Promotion history permanently excludes bootstrap even if SourceTruthVersion is reset
to NONE. A partial reservation also excludes a fresh attempt. Changed approval,
document/hash, version or scope invalidates the attempt. Partial writes fail closed;
history/evidence is retained. Only evidence-backed reconciliation of the SAME
recorded attempt can use existing recovery authority and the one-correction limit.
This patch creates no new retry/recovery permission. Failed pack creation never
reopens bootstrap. Product, framework, QA, scope approval, standing delegation and
adjacent Director operations remain unauthorized under the initial basis.

Canonical paths below are relative to CANONICAL_STARTERS:

| Modified contract | Necessary impact; boundary retained |
|---|---|
| 00_FRAMEWORK/SOURCE_AUTHORITY_POLICY.md | One complete first-promotion procedure; eligibility, reservation, exact writes, expiry and recovery |
| 00_FRAMEWORK/GOVERNANCE_RULES.md | Narrow context qualification and recognized lane identity for these two actions only |
| 10_CONTEXT_ECONOMY/CONTEXT_RULES.md | Admit the initial basis while every ordinary pack still requires a registered version |
| 07_GUARDRAILS/CONTEXT_GUARDRAIL.md | Verify eligible first basis before ordinary triggers; no general override |
| 15_COMMANDS_AND_DRIVERS/ACTION_PROMPT_MASTER.md | Bind context steps/checklist and lane-only scope; preserve all thirteen stages, other stops and retry limits |
| 15_COMMANDS_AND_DRIVERS/ACTION_PROMPT_DIRECTOR.md | Bind Source Truth Agent to policy and name its control fields; no adjacent agent execution |
| 15_COMMANDS_AND_DRIVERS/ACTION_PROMPT_CONTEXT_STEWARD.md | Bind first ordinary assembly to the addressed handoff without fabricating workcell scope; correct CP indexing for this transition only |
| 15_COMMANDS_AND_DRIVERS/MUTATION_PERMISSION_MATRIX.md | Restrict otherwise broader Director permissions to the first-promotion allowlist |
| 15_COMMANDS_AND_DRIVERS/STOP_RULES.md | Qualify only first-promotion source/context prerequisites; all fifteen stop rules retained |

SCAFFOLD_WORKFLOW_AGENT.md clarifies pending candidate truth and frozen provenance;
its NONE / INITIALIZED state is unchanged. SCAFFOLD_TEST_RECORD.md records the
separate bounded test without closing the broader pending test. Framework Learning
and README record the local candidate and publication boundary.

CONTROL_PLANE_SCHEMA.md is unchanged: all required values and writer classes already
exist. COMMAND_REGISTRY.md remains eighteen commands: the existing active lane
handoff supplies row 9's input without a workcell binding. HUMAN_APPROVAL_GATES.md
already requires traceable Gate 1 approval, so it is unchanged. Output inventories,
all record column schemas, tool runtime, manifest and official distribution helper
are unchanged. No file was changed merely because it appeared in the input list.

## Validation categories and evidence

1. **Automated structural/conformance tests:** 25 focused unittest cases in
   `TOOLS/tests/test_bootstrap.py`, using disposable canonical-derived fixtures
   and the test-only read-only oracle in `VALIDATION/bootstrap_case.py`.
2. **Tooling regressions:** the existing 13 release/distribution, 8 state-reader
   and 27 operator-toolkit cases. Raw suite commands, outputs and child exit codes
   are in [BOOTSTRAP_V2_TESTS.json](BOOTSTRAP_V2_TESTS.json).
3. **Actual agent-guided scaffold workflow:** separate Codex-controlled stages
   against the current copied canonical instance, with output inspected at each
   boundary. Raw file artifacts, input/approval, commands, hashes/diffs, stage
   evidence and STOP decisions are in
   [BOOTSTRAP_V2_ACCEPTANCE.json](BOOTSTRAP_V2_ACCEPTANCE.json).
4. **Independent framework certification:** not performed. The subsequent release
   directive supplies conditional publication approval; adoption remains separate.

Reproduce automated suites with:

```text
python -B ADAPT/VALIDATION/run_bootstrap_tests.py
```

For the separately inspected acceptance stages, create a new external temporary
directory named `adapt-bootstrap-v2-*`, then invoke separately:

```text
python -B ADAPT/VALIDATION/bootstrap_case.py scaffold --disposable <DISPOSABLE>
python -B ADAPT/VALIDATION/bootstrap_case.py promote --disposable <DISPOSABLE>
python -B ADAPT/VALIDATION/bootstrap_case.py context --disposable <DISPOSABLE>
python -B ADAPT/VALIDATION/bootstrap_case.py verify --disposable <DISPOSABLE>
```

These fixed synthetic file actions are validation assets, not distributed ADAPT
tools or a general promotion engine. The scaffold stage follows START_HERE and
the live scaffold/output/onboarding/deployment contracts, copies all 112 canonical
starters, performs prescribed header/live-field population, extracts candidate
rows, records missing technical decisions, and executes the actual official
`distribute_tools.py` copy and `--verify` subprocesses. It produces the startup
report and stops. It does not call the unit-test fresh-instance fixture.

The next stage reads that actual state, verifies the initial basis, reserves the
attempt, preserves the exact source, reuses/quote-checks scaffold candidate IDs,
registers the first version and emits a canonical-template handoff. Codex inspects
the artifacts before activating Context Steward as a new bounded stage. That stage
uses the registered source, produces the ordinary pack and its canonical delivery,
and stops. The final stage tests reset/reuse and ordinary context rejection in
separate disposable clones. Synthetic approvals never represent Human Owner
decisions for a real instance. This flow is not evidence based solely on fixtures.

The positive case establishes SOURCE_TRUTH_V0.1, SOURCE_TRUTH_READY / NEEDS_CONTEXT,
AC-001 DRAFT, CP-0001 tied to active HO-0002 with consumed HO-0001 provenance,
and CD-0002 without any workcell/milestone/cycle binding. Product bytes remain
unchanged. The initial basis expires and subsequent context checks apply normally.

| Negative scope | Check/evidence |
|---|---|
| Missing/wrong approval, wrong gate, changed approval/request | Focused fixture rejection before any promotion write |
| Missing, altered, incomplete or unreadable source | Hash/completeness rejection; unreadability uses a labeled synthetic PermissionError |
| Unauthorized writer, adjacent Director action/register, product write | Identity/action/file allowlist rejection |
| Prior archived/superseded promotion or reset to NONE | History rejection; acceptance reset attack records STOP_REQUIRED |
| Repeated/partial attempt | Retained attempt marker rejection; child process exits after durable reservation with code 97 |
| Ordinary promotion without context | Structural and acceptance missing-pack rejection |
| Invalid workcell/handoff binding or active artifact | Binding/artifact rejection; existing tool suites cover malformed/ambiguous handoffs |
| Changed frozen contracts / uncertain history / loading phase | Fail-closed conformance checks |
| Ordinary stale source after transition | Separate stale clone rejected by ordinary integrity checks |

Existing tooling checks preserve state/doctor compatibility, read-only evidence,
fail-closed prompt-next, manifest verification, scaffold distribution, inventory,
source/context binding and retry limits. CLI inspection does not authorize bootstrap;
the agent follows the normative contracts. No tool enhancement was needed.

## Framework Learning and versioning

FLC-002 records EXECUTION_PATH / GOVERNANCE_COMBINATION, the supplied accepted
FRAMEWORK_BOOTSTRAP_CONTRACT_GAP and this generic correction. The maintainer's
current directive is its authority; no local Director or AI self-approves framework
evolution. GROUNDED baseline/artifact/test evidence is distinguished from this
ASSERTED interpretation. Instance-specific operational evidence remains separate.

The live version rule advances once per authorized patch containing promoted
generic candidates. ADAPT-FW-0003 is the next successor after the issued -0002;
the interrupted recovered attempt published no successor. PROMOTED here records
local incorporation, not publication, release certification or automatic adoption.
FLC-001 retains its original introduced version. Backport is ELIGIBLE subject to
Upgrade Assessment REQUIRED and a separate maintainer decision. The pending
publication review is not bypassed by this local version candidate.

## Integrity, repository boundary and limitations

This section describes the initial local delivery; final acceptance follows below.

The local commit includes only this scoped patch, deliberate validation source,
sanitized synthetic evidence and documentation. Disposable instances, temporary
logs, protected-path snapshots and recovery backups remain outside the repository.
worktree.md and .git/info/exclude retain their pre-milestone hashes. All 132 frozen
ADAPT-DEV files and its directory inventory are compared before/after; no instance
state, source truth, tools, workcells, pending document or baseline is adopted.
Live remote refs and local main remain at the original baseline. No merge or push.

This validation covers one minimal MODE_B source on Windows/Python 3.11. It does
not certify arbitrary extraction, MODE_A discovery, approval authenticity or history
completeness in every future instance; those semantic checks remain agent/human
responsibilities. No interrupted attempt is resumed under recovery authority.
There is no independent reviewer or QA signoff; grounded mechanics support the
solo operator's checkable claims under Rule 13. The original example-project test
remains pending. No broad framework certification or successful self-hosted
development lane is claimed. ADAPT-DEV remains governed by frozen ADAPT-FW-0002;
future controlled upgrade/adoption and its initialization are separate operations.

## Final MODE_A acceptance and release gate — 2026-10-16

The Human Owner / Framework Maintainer's BOOTSTRAP V2 FINAL ACCEPTANCE AND RELEASE
directive explicitly authorizes publication after the listed gates pass. The live
Framework Learning register and GOVERNANCE_RULES Rule 14 require that human
disposition and versioned generic incorporation, not another independent QA or
release signature. FLC-002 retains the original ADAPT-SELF-HOST-001 finding,
PROMOTED disposition and Introduced In ADAPT-FW-0003. This completion of the same
patch does not advance the version again. ADAPT-DEV did not govern this maintenance.

Codex executed the actual updated scaffold as separate inspected stages against
a fresh disposable existing-solution Git fixture outside the live repository:

```text
python -B ADAPT/VALIDATION/bootstrap_case.py scaffold --deployment MODE_A_EXISTING_SOLUTION --disposable <DISPOSABLE>
python -B ADAPT/VALIDATION/bootstrap_case.py promote --disposable <DISPOSABLE>
python -B ADAPT/VALIDATION/bootstrap_case.py negatives --disposable <DISPOSABLE>
python -B ADAPT/VALIDATION/bootstrap_case.py context --disposable <DISPOSABLE>
python -B ADAPT/VALIDATION/bootstrap_case.py verify --disposable <DISPOSABLE>
```

All stages exited 0. FULL_EXTERNAL_ADAPT_INSTANCE_SCAFFOLD / PROTECTED_DEFAULT
copied all 112 canonical starters, populated prescribed fields, distributed and
verified the official tools, and emitted the startup report. No scaffold contract
was repaired. Read-only MODE_A discovery recorded language, layout, documentation,
absent build configuration and a candidate unittest file. Observed code remains
OBSERVED_EVIDENCE / CANDIDATE_TRUTH in BI-002 and OQ-002. It was not promoted into
requirements, executed, or declared as a QA oracle. The source document alone
supplied the promotion requirement. Project bytes were unchanged after fixture setup.

The explicitly synthetic Gate 1 approval binds the exact immutable source SHA256:
`cd74a7a29b244d249751d1fde629ea6400957b81d3bd7ba5540551c4d42c6ad2`.
Before/after artifact hashes, text and inverse-verified diffs are retained in
the existing acceptance JSON under `mode_a_release_acceptance`. Its input,
request, approval, frozen contract hashes and stage records are test evidence,
not fabricated Human Owner decisions for an operational instance.

The Director moved NONE / INITIALIZED through the reserved attempt to registered
SOURCE_TRUTH_V0.1 / SOURCE_TRUTH_READY / NEEDS_CONTEXT, preserving DRAFT criteria.
Registration consumed the initial basis. The addressed, active lane handoff
HO-0001 passed the Steward binding check. The Steward consumed it, assembled
ordinary CP-0001 referencing the registered version and active review HO-0002,
retained consumed HO-0001 provenance, and emitted CD-0002. All four active
workcell/handoff/milestone/cycle fields remain NONE. No implementation was authorized.

| Required negative case | Observed STOP reason |
|---|---|
| Missing approval | MISSING_APPROVAL |
| Invalid source hash | SOURCE_HASH |
| Unauthorized writer | WRITER |
| Duplicate / previous promotion | INITIAL_STATE |
| Reset registered version to NONE | PROMOTION_HISTORY |
| Invalid Context Steward handoff | STEWARD_HANDOFF_BINDING |
| Ordinary promotion without valid context | ORDINARY_CONTEXT_MISSING |
| Unauthorized adjacent action | ADJACENT_ACTION |

All eight were exercised against clones of the actual scaffold/promoted instance,
with no writes after rejection. Final verification also stopped repeated bootstrap,
reset reuse, missing ordinary context and stale ordinary source. The positive
ordinary pack passed integrity/context checks; its existence does not grant
Director authority. No required MODE_A scenario is classified NOT_EXERCISED.

The distributed MANIFEST and payload hashes were inspected before every CLI call.
Both at scaffold and after pack delivery, state, doctor and evidence exited 0;
prompt next exited 1 with BLOCKED because no active workcell/handoff binding exists.
The intermediate post-promotion doctor exited 0. Exact commands, diagnostics,
exit codes and manifest digests are in `subprocesses`. These read-only tools
neither execute nor authorize a lane-only bootstrap. Agent actions follow the
documented lane procedure; no tool rejection was bypassed. The unchanged Tooling v1
manifest's ADAPT-FW-0002 identifies its build origin, not the instance's version.

A second fresh MODE_B run passed scaffold, promotion, Steward delivery and final
ordinary/reuse checks with the updated harness (`mode_b_release_recheck`). The
original MODE_B evidence and original 73 passing tests remain retained. Final
regressions pass **76 tests**: 28 bootstrap, 13 existing release/distribution,
8 state-reader and 27 operator-toolkit tests, all child exit codes 0. The three
new tests cover Steward target/workcell binding and MODE_A candidate comparison.
No runtime, canonical contract, command, schema, writer class or distribution
capability changed during this final acceptance. The release gate records source,
evidence, documentation/link, whitespace and protected-file checks.

Limitations: two minimal synthetic cases on Windows/Python 3.11 do not certify
arbitrary source extraction, exhaustive history discovery or approval authenticity.
Those semantic checks remain agent/human duties. This is not independent QA or
full framework certification. The broader original example-project scaffold test
remains pending. No self-hosted development lane, ADAPT-DEV initialization or
adoption occurred. All 132 frozen instance files, directory inventory, worktree.md
and local exclude hashes are protected by before/after comparisons.

Controlled adoption impact, for a separately approved operation: assess the nine
canonical contract changes listed above against the frozen baseline; assess
scaffold provenance and the new framework version; retain instance state and
history and review the first-promotion eligibility and lane handoff requirements.
The Tooling v1 runtime/distribution is unchanged. Nothing here approves copying
contracts, restarting promotion, or changing the frozen instance.
