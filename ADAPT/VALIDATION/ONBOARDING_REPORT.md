# Onboarding lane correction — local validation

Date: 2026-10-16. External Human Framework Maintainer maintenance for
ADAPT-SELF-HOST-001, not an ADAPT-DEV workcell operation.
Baseline: ADAPT-FW-0003 at a9082ec9267927f68bf338813e0438fb0122d510.
Local successor candidate: ADAPT-FW-0004; Framework Learning FLC-003.
The supplied ONBOARDING LANE GOVERNANCE CORRECTION directive authorizes bounded
implementation, validation and local commit only. Main merge, publication,
instance adoption and real workcell creation are not authorized.

This report is ASSERTED interpretation of the linked GROUNDED records, not
independent QA certification. Genuine Human Owner approvals for test identities
and self-hosted development-lane success are not claimed.

## Conflict and necessary contract changes

ONBOARDING_RULES precondition 1 accepts a populated Director identity artifact.
Onboarding V-01 instead requires a Director in an initially empty workcell
registry. Rule 11 and master dispatch have no onboarding lane identity/scope
basis before a development workcell exists. Removing V-01 alone is insufficient.

Canonical paths below are relative to CANONICAL_STARTERS:

| Contract | Necessary correction; retained boundary |
|---|---|
| 15_COMMANDS_AND_DRIVERS/ACTION_PROMPT_ONBOARDING.md | Normative lane identity/scope basis; traceable human Director designation, exact command/Gate 3, ordinary context and explicit paths; V-01/V-03 aligned; named control writes |
| 11_ONBOARDING/ONBOARDING_RULES.md | Same Director verification; completion returns to Director without assignment; named control fields and schema precedence |
| 00_FRAMEWORK/GOVERNANCE_RULES.md | Rule 11 narrowly recognizes accountable lanes for this procedure; development still requires a registered workcell |
| 15_COMMANDS_AND_DRIVERS/ACTION_PROMPT_MASTER.md | Bounded onboarding scope replaces pre-existing development scope; ordinary context and all thirteen stages remain |
| 15_COMMANDS_AND_DRIVERS/ACTION_PROMPT_DIRECTOR.md | Exact intake, approval recording and routing only; ordinary task context required |
| 15_COMMANDS_AND_DRIVERS/ACTION_PROMPT_CONTEXT_STEWARD.md | Specific ordinary onboarding context without fictional workcell; CP-ID indexed, actual CD-ID retained |
| 15_COMMANDS_AND_DRIVERS/MUTATION_PERMISSION_MATRIX.md | Restrict onboarding/preparation to normative scope and existing schema permissions |

The onboarding prompt's old WC-identity-role example conflicted with the registry
and generated template's ROLE_ABBREVIATION_IDENTITY pattern. It now references
the existing registry format. The generic post-onboarding handoff instruction
now returns completion to Director, preserving separate assignment.
No command, runtime, manifest, distribution helper, gate, schema, protected
routing or STOP rule changed. Source-promotion bootstrap is unchanged.

## Governed behavior

Verify DIRECTOR_IDENTITY.md, matching project/role/lane, real human owner,
resolved fields and traceable human designation. An identity artifact alone
does not confer authority. An empty registry does not block this presence check.
Bind the executor to the recognized Onboarding Orchestrator, exact registered
command and actual invocation or lawful Director-issued ACTIVE handoff.
Require current registered source truth, ordinary task-specific context,
applicable Gate 3 human approval recorded by Director, and exact target/scope.
A Driver claim or AI assertion of approval is insufficient.

Scope permits only approved workcell artifacts, registry/map/report rows,
evidence/delta and required handoff lifecycle. All fifteen artifacts and full
role-specific blueprints pass quality checks before registration. The new
workcell has no assigned BI or execution mutation scope. Product/framework
changes, milestone execution, unauthorized customization, scope expansion,
QA certification and release approval remain unauthorized. First and subsequent
onboarding use the same procedure. Existing correction/STOP limits remain.
Partial generation never becomes final registration or fresh retry authority.

## Validation and reproduction

Raw suites: [ONBOARDING_TESTS.json](ONBOARDING_TESTS.json).
Actual workflow: [ONBOARDING_ACCEPTANCE.json](ONBOARDING_ACCEPTANCE.json).
Integrity gate: [ONBOARDING_GATE.json](ONBOARDING_GATE.json).

Run existing bootstrap, release/distribution and toolkit regressions plus focused
onboarding tests without rewriting the preceding release's evidence:

~~~text
python -B ADAPT/VALIDATION/run_onboarding_tests.py
~~~

Focused coverage includes first/second onboarding; missing/placeholder Director;
conflicting/untraced designation; wrong project/role; missing/mismatched Gate 3;
unauthorized executor/spoofed Driver; missing/stale ordinary context; missing
scope; duplicate/existing target; incomplete artifacts/blueprints; routing
mismatch; product mutation and implementation without assignment.

Final result: 101 tests passed, zero failed: 25 onboarding, 28 bootstrap,
13 release/distribution, 8 state-reader and 27 operator-toolkit cases.

Create a new external disposable directory named adapt-bootstrap-v2-* and invoke
these separately, inspecting artifacts at the stage boundaries:

~~~text
python -B ADAPT/VALIDATION/onboarding_case.py scaffold --disposable <DISPOSABLE>
python -B ADAPT/VALIDATION/onboarding_case.py promote --disposable <DISPOSABLE>
python -B ADAPT/VALIDATION/onboarding_case.py first-context --disposable <DISPOSABLE>
python -B ADAPT/VALIDATION/onboarding_case.py verify-bootstrap --disposable <DISPOSABLE>
python -B ADAPT/VALIDATION/onboarding_case.py inputs --disposable <DISPOSABLE>
python -B ADAPT/VALIDATION/onboarding_case.py context --disposable <DISPOSABLE>
python -B ADAPT/VALIDATION/onboarding_case.py route --disposable <DISPOSABLE>
python -B ADAPT/VALIDATION/onboarding_case.py negatives --disposable <DISPOSABLE>
python -B ADAPT/VALIDATION/onboarding_case.py onboard --disposable <DISPOSABLE>
~~~

Repeat inputs, context, route and onboard with --number 2 for the second identity.
These fixed validation actions are not distributed tools or a general engine.
Scaffolding reuses official canonical copying/population and the actual tooling
distribution helper. MODE_A discovery stays observed/candidate truth. The
synthetic source explicitly permits governance onboarding. No generated
framework contracts are manually repaired.

Codex performed the actual fresh MODE_A / PROTECTED_DEFAULT /
FULL_EXTERNAL_ADAPT_INSTANCE_SCAFFOLD sequence. First promotion registered
SOURCE_TRUTH_V0.1 and delivered CP-0001. Synthetic Planner TESTALPHA was registered
first and QA Engineer TESTBETA second, each with fifteen artifacts. CP-0002 and
CP-0003 are ordinary task-specific packs, not reused bootstrap bases. Steward
refresh records stale prior packs. Completion consumes incoming requests and
emits Director handoffs. ActiveWorkcell, ActiveHandoff, ActiveMilestone and
ActiveCycle remain NONE. Phase ONBOARDING / readiness NEEDS_CONTEXT is not
implementation readiness. Both workcells reject implementation without assignment.

Thirteen attacks on clones of the actual instance produced STOP_REQUIRED with
no writes by the rejecting check. These are acceptance scenarios, not extra
unit-test counts. Incomplete-generation setup occurs only in a disposable clone
and never registers a workcell. Four bootstrap reuse/context attacks also stopped.

Source SHA256:
f8db6770a3d953a8e644c1e496d53c847482f2e421229f9602d8b962668d7f27.
Raw evidence retains input bytes/hashes, commands/exits, before/after state,
exact changes and inverse verification, generated workcell artifacts and tool
diagnostics. Manifests/payloads are inspected before invocation; doctor stays
compatible and prompt next stays BLOCKED. Read-only results grant no authority.

## Limits and authority boundaries

Synthetic designation, Gate 3, Director decision/intake/request records and
Director routing transitions are supplied fixture inputs. They are not evidence
of a separately executed Director intake dispatch or genuine human approval for
those identities. Exercised operations are actual scaffold/promotion/first context,
ordinary onboarding context assembly, first onboarding and subsequent onboarding
from those inputs. Approval authenticity and semantic completeness remain
human/agent checks. No full Director preparation acceptance is claimed.

An initial helper inventory lookup error was corrected to use the authoritative
Planner/QA agent lists in WORKCELL_ONBOARDING_CONTRACT.md. Runtime inventory was
not expanded. Raw published-in-branch test records contain final successful runs.
Minimal synthetic Planner/QA cases do not certify every role, concurrency,
all recovery paths, or development/QA execution. Independent QA was not performed.
The broader original example-project test remains pending.

FLC-003 records EXECUTION_PATH / GOVERNANCE_COMBINATION and the supplied Maintainer
approval. PROMOTED means local incorporation. Version -0004 advances once for
this patch; -0003 remains the published baseline. FLC-002 and prior validation
records are preserved. Their historical hashes apply to their original commits.
Protected snapshots/disposable instances stay outside Git. Frozen ADAPT-DEV,
worktree.md and local exclude remain unchanged; no adoption or Governor promotion.

Release/publication and controlled ADAPT-DEV adoption require separate authority.
Future adoption must assess these seven contracts plus the prior bootstrap
correction, preserve instance history/state, and establish actual Director
ownership and applicable approvals. Registration never substitutes for assignment.
