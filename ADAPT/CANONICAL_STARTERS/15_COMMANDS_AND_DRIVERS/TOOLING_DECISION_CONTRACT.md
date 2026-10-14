# Read-only Tooling Decision Contract

Tooling v1 is an optional interface to canonical artifacts. Distribution is
mandatory for new scaffolds; running it is optional. It neither authorizes work
nor replaces guardrails, approvals, evidence review, or the dispatch protocol.

## Deterministic preview selection

Only the registry command `Run atomic handoff dispatch` is previewed in v1.
It is selected from a Director-bound ACTIVE handoff, not NextExpectedAction or
Next Action Suggested. The latter remain trace/suggestion. Other commands and
direct lane invocation return BLOCKED; no identity or approval is guessed.

An ACTIVE workcell registry entry, matching control-plane CurrentAuthority and
ActiveWorkcell, matching identity owner/role and an ACTIVE incoming handoff are
required. Supported exact roles are Backend Developer and Frontend Developer.
The scope contract must belong to that workcell and explicitly list the task's
mutation paths; the task work item must appear in Assigned Business Items.
An ACTIVE decision must be referenced for the scope and milestone. Those
decisions must name their affected workcell/path or milestone, and a local
approval-record reference must exist. This verifies recorded evidence pointers,
not the authenticity of a human signature or approval of a new action.

## Handoff Operator Dispatch Binding

The emitting Director records this section in a handoff only after existing
governance requirements have been satisfied. These are references to existing
authority and evidence, never an independent authority database. Missing or
unresolved fields fail closed; v1 never populates them automatically.

Use the table in `08_TEMPLATES/OPERATOR_BINDING_TEMPLATE.md`. ScopeDecision and
MilestoneDecision reference ACTIVE DEC-ID rows in DECISION_LOG. ApprovalReference
is a bounded instance-relative record of the explicit approval; it does not
create an approval. ActionPrompt names the identity-bound member ACTION_PROMPT.md.
MutationPaths is a comma-separated list of repo-relative files or NONE for a
read-only task. WorkItem names one assigned BI-ID. SourceTruthDocument is a
bounded document listed ACTIVE under the current source version in the version
log. ContextPack must agree with CONTEXT_PACK_REFERENCE and its headers.

## Required checks before a preview

- All 21 fields parse and relevant values are supported. Phase is EXECUTION,
  readiness is READY and the active milestone/source version are populated.
  READY alone grants nothing.
- Registry, identity, protected member prompt and handoff target all agree.
- Handoff is from Director Lane, not self-addressed; exactly one ACTIVE handoff
  targets the workcell. A bounded scan of ACTIVE is allowed for this guardrail.
- Scope, ACTIVE decision rows and approval record exist and agree with binding.
  PROTECTED_DEFAULT additionally requires affected-file entries for each path.
- Context headers match; its File Integrity table declares current SHA256 for
  handoff, scope, identity, member prompt, blueprint, decisions and source document.
  No hash is substituted or invented by the operator CLI.
  If LastContextDelta is not NONE, v1 returns BLOCKED because delta applicability
  and refresh acceptance are not deterministically bound by this subset.
- Active registers agree with control-plane IDs. Open/unresolved rows cause
  BLOCKED when deterministic work-item applicability cannot be established;
  this conservative refusal is not a claim that unrelated blockers halt all work.
- Incoming evidence references are present and their Stage Records match the
  emitting blueprint with Attempts <= 2, or BLOCKED. The Director emitter may
  use its explicitly referenced Director blueprint; no blueprint is inferred.

The preview contains the exact registry command, bound identity/role/handoff,
scope/mutation paths and artifact references. It prominently says preview only,
not approval. The receiving agent must still evaluate semantic scope, context
adequacy, job size, all guardrails and approvals before any execution. A local
artifact's existence is not proof of authentic approval or complete governance.

## File Integrity table

Context packs used for tooling previews include `## File Integrity` with columns
`Path | SHA256`. Paths are bounded instance-relative files. The Context Steward
records actual hashes while assembling the pack. Hash disagreement, duplicate
paths or missing mandatory references returns BLOCKED. The table records context
traceability under Governance Rule 6 and does not change any writer permissions.

## Outcomes and permissions

State reads one control plane; doctor performs structural checks and reports
UNVERIFIED for unsupported semantic/history checks. Evidence runs only fixed,
local read-only Git queries and hashes bounded declared files. Prompt next reads
the above binding artifacts and emits a preview or BLOCKED. All commands have
zero instance/application mutation permission and no network access.
Exit codes: 0 output/preview produced, 1 failed or BLOCKED, 2 usage error.
Every unchecked condition remains explicitly unverified; no output is certification.
