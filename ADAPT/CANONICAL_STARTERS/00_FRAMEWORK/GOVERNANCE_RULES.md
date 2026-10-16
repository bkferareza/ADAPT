# Governance Rules

STATUS: DRAFT
VERSION: {{ADAPT_VERSION}}
PROJECT: {{PROJECT_NAME}}

## Purpose

These rules govern all ADAPT lanes, roles, and AI executions within this instance. Compliance is mandatory. A rule violation detected at runtime must be reported and must halt execution of the violating action.

## Core Rules

### Rule 1 — Director Authority
The Director Lane has intake, routing, source-truth promotion, assignment, gap classification, blocker routing, and certification authority. Director does not have implementation or application source code mutation authority.

### Rule 2 — Mutation Authority
No AI agent may mutate application source files without explicit workcell mutation authority assigned by the Director. Mutation authority is scoped to the workcell's assigned lane (backend files, frontend files, pipeline config, etc.) and must not exceed that scope.

### Rule 3 — QA Independence
QA validation must be performed independently of development. The same human or AI that developed a feature cannot produce QA signoff for that feature without a Director-granted CONSTRAINED exception recorded in the Decision Log. Developer self-validation is never equivalent to QA signoff.

A CONSTRAINED exception relaxes who validates. It never relaxes what the evidence must
rest on — see Rule 13.

### Rule 4 — Source Truth Promotion
Source truth must be explicitly promoted and versioned before it can be used as ground truth. The promotion command is: `Promote {{DOCUMENT_NAME}} as {{SOURCE_TRUTH_VERSION}}`. Promotion requires Director authority and human approval. Unpromoted documents are reference material, not source truth.

### Rule 5 — Evidence Requirement
Claims, completions, and acceptances require evidence traceable to a source requirement
or contract. Unverified claims are not accepted work. See EVIDENCE_STANDARD_BY_ROLE.md in
15_COMMANDS_AND_DRIVERS/.

Evidence has one of three classes, and must be labelled with it:

- **GROUNDED** — produced mechanically and preserved with what produced it: raw command
  or test-runner output with the command that ran, a file hash with the file and
  algorithm, a build log, a captured runtime response. Grounded evidence can be
  re-checked by re-running or re-reading, without trusting whoever recorded it.
- **REVIEWED** — assessed by an actor other than the one whose claim it supports. Review
  catches impossible or inconsistent claims — tests reported passing in a repository
  with no test harness. It does not reliably catch a plausible fabrication, and it does
  not make evidence grounded.
- **ASSERTED** — a statement by the claimant, including an AI summary of evidence. An
  assertion is never evidence of its own truth.

A summary or interpretation must be labelled as such and must reference the grounded
evidence it summarizes. It never replaces it.

No claim may exceed the class of evidence supporting it. A validation result resting on
ASSERTED evidence is not a validation result.

### Rule 6 — Context Traceability
Context packs must reference specific source truth versions and active handoff identifiers. Missing or untraced context must be recorded as GAP-T11 Context Gap before execution proceeds. Stale context from prior cycles must not be passed as current.

Sole first-promotion qualification: SOURCE_AUTHORITY_POLICY.md, First-Promotion
Initial Context Basis. All eligibility, scope, expiry and recovery conditions
apply together. This never validates an ordinary unversioned context pack.

### Rule 7 — Handoff Completion
A lane must emit a handoff before stopping. Silent continuation past the next handoff boundary is forbidden. If a handoff cannot be emitted (missing state, blocked, incomplete evidence), the lane must stop and record a blocker.

Only the eligible Initial Director designation stage in ACTION_PROMPT_DIRECTOR.md
returns its recorded completion to the human without a lane handoff; it writes
only identity/designation evidence, then STOP. Ordinary handoffs are unchanged.

### Rule 8 — Human Approval Gates
Certain actions require explicit human approval before proceeding. See HUMAN_APPROVAL_GATES.md in 15_COMMANDS_AND_DRIVERS/. Required approval gates include: source truth promotion, workcell onboarding, milestone plan approval, code mutation scope approval, release certification, and guardrail override.

### Rule 9 — Guardrail Enforcement
Before executing any bounded action, the AI must check the relevant guardrails in 07_GUARDRAILS/. A STOP_REQUIRED result halts execution of the bounded action. The AI must record the stop condition and route to the appropriate authority.

### Rule 10 — Memory Bank Restriction
Memory Bank documents in 14_MEMORY_BANK/ are reference-only. Memory Bank content must not be treated as live source authority. All authoritative state comes from the control plane, active handoffs, promoted source truth, and accepted contracts.

### Rule 11 — Workcell Identity
Every ADAPT execution must occur under a single, identified workcell identity. Executing under an ambiguous or missing identity is forbidden. See WORKCELL_ONBOARDING_CONTRACT.md for identity binding rules.

For only the eligible Initial Director designation stage of `Run Director intake`,
ACTION_PROMPT_DIRECTOR.md binds Director Lane to the actual Human Owner designation
before the identity is populated. That verified lane basis satisfies this rule
only for its two-file setup scope. It creates no workcell and authorizes no
other Director operation. A lane name or Driver assertion alone is insufficient.

For only the first promotion and its first ordinary context assembly under
SOURCE_AUTHORITY_POLICY.md, the identified Director Lane / Context Steward lane
identities satisfy this rule. No implementation workcell is created or implied.

For the existing Onboard command only, ACTION_PROMPT_ONBOARDING.md, Onboarding
lane identity and scope basis, governs identified Director intake/approval/routing,
Onboarding Orchestrator execution and associated Context Steward assembly.
Their verified lane identities satisfy this rule only within that bounded
procedure, with ordinary versioned context and Gate 3 intact. A claimed lane name
alone is insufficient. Development execution still requires an onboarded workcell,
its approved scope, effective workflow, assignment and handoff. No blanket lane
exception or product mutation authority is created.

### Rule 12 — No Workcell Self-Assignment
Workcells must not assign themselves new work. Work assignments come from the Director Lane via handoffs. A workcell that encounters unassigned work must record a gap or blocker and route to the Director.

### Rule 13 — Evidence Independence
The actor whose success depends on a claim must not be the sole producer and sole
authority for the evidence supporting that claim.

Where a second actor is available, the claim requires REVIEWED evidence at minimum, and
GROUNDED evidence wherever it concerns something mechanically checkable — tests, builds,
hashes, file contents, runtime output.

Where a second actor is not available — a CONSTRAINED exception under Rule 3, or a solo
operator — a mechanically checkable claim requires GROUNDED evidence. Independence that
cannot exist is replaced by evidence that does not depend on trusting the actor. If
grounded evidence cannot be produced — no harness, no environment, no captured output —
the claim is not made: it is recorded as unverified and routed to the Director. A claim
that is not mechanically checkable is recorded as the claimant's judgment, labelled
ASSERTED, and is not presented as verified.

This rule applies to every lane, not only QA.

### Rule 14 — Framework Evolution
The Framework Maintainer is a human authority outside every ADAPT instance, and the sole
authority to dispose framework-learning candidates, authorize changes to the generic
framework, authorize framework upgrades and backports, and declare or advance the
framework version recorded in the framework-root FRAMEWORK_LEARNING_REGISTER.md.

Framework-derived contract files in an instance — those in 00_FRAMEWORK/,
07_GUARDRAILS/, 08_TEMPLATES/ and 15_COMMANDS_AND_DRIVERS/ — change only through an
authorized framework upgrade or backport, recorded in that instance's DECISION_LOG.md.
No lane edits them to resolve a problem it encounters. Instance registers and state are
not affected by this rule.

Any lane may identify a framework-learning candidate. It qualifies when at least one of
these holds: a control failure occurred; a missing invariant was exposed; the situation
carries material governance or execution risk; or comparable friction recurred across at
least two independent cases. One control failure or missing invariant is sufficient. A
contract that is contradictory, incomplete, or permits an ungoverned path is raised as a
GAP-T14 Framework Gap; a qualifying lesson is routed from the Memory Bank. The Director
escalates either to the Framework Maintainer and never authorizes the change.

Promoted changes apply prospectively: future scaffolds inherit them from the canonical
starters, and existing instances are never rewritten automatically — recovery does not
overwrite existing files (DEPLOYMENT_MODES.md).
