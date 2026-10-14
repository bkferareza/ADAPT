# CONTROL_PLANE_SCHEMA.md
STATUS: DRAFT

## Purpose
Defines the exact schema for `ADAPT/02_DIRECTOR_LANE/PROJECT_CONTROL_PLANE.md`. Every field is listed with its type, allowed values, description, and update authority. Agents must read this schema before reading or writing the control plane to ensure they interpret and record fields correctly.

The control plane is the authoritative live state of the ADAPT instance. It is the first artifact read in every Atomic Handoff Dispatch cycle.

---

## Field Classes

Every field below belongs to exactly one class. The class determines who may write it. Where
a field's **Who Updates It** clause and its class appear to disagree, the class governs and
the clause is a defect.

**Identity** — `ProjectName`, `ProjectType`, `DeploymentMode`, `RoutingMode`,
`InitializationMode`. Written by the Director Lane at initialization and not during
execution. Changing one requires human approval and a `DECISION_LOG.md` entry.

**Authority** — `CurrentAuthority`, `ActiveWorkcell`, `ActiveHandoff`, `ActiveMilestone`,
`ActiveCycle`, `SourceTruthVersion`, `CurrentPhase`. Written by the Director Lane only,
subject to the explicit delegations below. A lane writing an authority field outside
those delegations is authorizing itself. A registry command issued directly by the human
operator authorizes the agent to record the authority the human granted; the agent must
name the issuing command when it does. An orchestrator beginning a governed activity may
set `CurrentPhase` to the phase naming that activity, and only that value. A workcell
completing its current bounded action may clear its own `ActiveHandoff` and set
`CurrentPhase` to `READY_FOR_ASSIGNMENT` when discharging that handoff. This workcell
delegation does not authorize changes to any other authority field. Neither delegation
permits setting `BLOCKED` or `READY_FOR_NEXT_CYCLE`, which are Director transitions.

**State** — `Blocked`, `ActiveBlockers`, `ActiveGaps`, `ExecutionReadiness`.
Written by the Director Lane, and by any lane that discovers the condition the field records.
A lane that hits a scope boundary writes `Blocked` itself; routing to the Director first
would leave the plane asserting a state that is not true. State writes are reconciled against
the registers by CP-C10 and CP-C11, so a lane that discovers a condition and fails to record
it leaves a detectable inconsistency rather than a silent one.

**Trace** — `LastAction`, `LastContextDelta`, `NextExpectedAction`, `LastConsolidatedAt`,
`Notes`. Written by whoever performed the activity the field records. Not by whoever wrote
the plane most recently. A lane that did not process a context delta does not write
`LastContextDelta`.

Twenty-one fields: five Identity, seven Authority, four State, five Trace.

## Schema

### ProjectName
- **Class:** Identity
- **Type:** String — free text
- **Allowed Values:** Any non-empty string (project name as established at initialization)
- **Description:** The human-readable name of the project governed by this ADAPT instance. Set once at initialization. Changes require Director approval and a new initialization note.
- **Who Updates It:** Director Lane at initialization. Not changed during normal execution cycles.

---

### ProjectType
- **Class:** Identity
- **Type:** String — constrained to recognized values
- **Allowed Values:** `Web App` / `Mobile App` / `API Service` / `Data Pipeline` / `Mixed` / free-form extension if none of the above apply (record justification in Notes)
- **Description:** The category of the project. Governs default lane availability assumptions (e.g., a pure API Service may not require a Frontend Workcell initially).
- **Who Updates It:** Director Lane at initialization. Not changed during normal execution cycles.

---

### DeploymentMode
- **Class:** Identity
- **Type:** Enum
- **Allowed Values:**
  - `MODE_A_EXISTING_SOLUTION` — ADAPT is applied to an existing codebase or partially built system
  - `MODE_B_REQUIREMENTS_ONLY` — ADAPT starts from requirements with no existing implementation
- **Description:** Controls which ADAPT modules and defaults are active. In MODE_A, the existing code, configuration and runtime behavior are OBSERVED_EVIDENCE of what the system currently does, not source truth. Where they diverge from promoted source truth, the divergence is recorded as an open question and changes nothing until a requirement change is explicitly promoted (see SOURCE_AUTHORITY_POLICY.md, Truth Classes). In MODE_B, implementation starts from scratch under ADAPT governance.
- **Who Updates It:** Director Lane at initialization. May only be changed with human approval and a recorded note in DECISION_LOG.md.

---

### RoutingMode
- **Class:** Identity
- **Type:** Enum
- **Allowed Values:**
  - `PROTECTED_DEFAULT` — the project repository is protected. No file in it may be
    written without explicit per-file authorization.
  - `DUAL_WRITE` — the project repository is writable for product code. ADAPT
    artifacts are written only to the ADAPT instance. Routing is decided by artifact
    class, not by access.
- **Description:** Controls where the scaffold and every subsequent workcell may
  write. Under `DUAL_WRITE`, the routing test is applied at write time: does this
  artifact ship, or does it describe how the work was done? Ships to the repository;
  describes to the instance. `SCOPE_GUARDRAIL.md` is populated from this value.
- **Who Updates It:** Director Lane at initialization. May only be changed with human
  approval and a recorded note in DECISION_LOG.md.

---

### InitializationMode
- **Class:** Identity
- **Type:** String
- **Allowed Values:** `FULL_EXTERNAL_ADAPT_INSTANCE_SCAFFOLD` — the only recognized mode. Written by START_HERE.md and SCAFFOLD_WORKFLOW_AGENT.md at initialization.
- **Description:** Records how this ADAPT instance was initialized. Used for traceability and to determine which canonical starters were applied.
- **Who Updates It:** Director Lane at initialization. Read-only after initialization unless re-scaffolding is explicitly approved.

---

### SourceTruthVersion
- **Class:** Authority
- **Type:** String
- **Allowed Values:** Any version label in the format `SOURCE_TRUTH_V{number}` (e.g., `SOURCE_TRUTH_V0.1`, `SOURCE_TRUTH_V1.0`) or `NONE` if not yet promoted
- **Description:** The version label of the currently accepted source truth. Must match an entry in SOURCE_TRUTH_VERSION_LOG.md. No work requiring source truth may proceed when this field is `NONE`.
- **Who Updates It:** Director Lane when a source truth promotion is approved and recorded.

---

### ActiveMilestone
- **Class:** Authority
- **Type:** String
- **Allowed Values:** Any milestone ID (e.g., `M01`, `M02`) or `NONE` if no milestone is active
- **Description:** The milestone currently under execution. Must match an approved milestone plan in DECISION_LOG.md. Only one milestone may be active at a time unless multi-milestone execution is explicitly approved.
- **Who Updates It:** Director Lane when a milestone plan is approved or when the active milestone is closed during consolidation.

---

### ActiveCycle
- **Class:** Authority
- **Type:** String
- **Allowed Values:** Any cycle number or label (e.g., `C01`, `M01-C02`, `SPRINT-03`) or `NONE`
- **Description:** The current execution cycle within the active milestone. Cycle granularity is defined during planning. Cycles are opened and closed by the Director during consolidation.
- **Who Updates It:** Director Lane at cycle open and cycle close.

---

### ActiveHandoff
- **Class:** Authority
- **Type:** String
- **Allowed Values:** Handoff file path (relative to ADAPT instance root) or handoff ID (e.g., `HO-0042`) or `NONE`
- **Description:** The currently active handoff artifact. This is the single authoritative task instruction for the current execution unit. Only one handoff may be active per workcell at a time. The emitting lane sets this field; the receiving lane consumes it.
- **Scope:** `ActiveHandoff` names the handoff bound to the workcell in `ActiveWorkcell`. It is not a pointer to the most recently emitted handoff. A handoff emitted to another lane — an escalation, a routing record, a blocker report — is placed in `06_HANDOFFS/ACTIVE/` and does **not** become `ActiveHandoff`. It is found by its receiving lane when that lane holds authority.
- **Who Updates It:** Set when a handoff is assigned to the workcell named in `ActiveWorkcell`. Cleared to `NONE` when that handoff is discharged to `CONSUMED/`. Where `ActiveWorkcell` is `NONE`, `ActiveHandoff` is `NONE`. Context Steward reads it to generate the context pack.
- **Never:** repoint this field to a handoff the current lane just emitted for someone else. That loses the workcell's binding and is not authorized by any step of the dispatch protocol.

---

### CurrentAuthority
- **Class:** Authority
- **Type:** String
- **Allowed Values:** Workcell ID (e.g., `WC-ANA-BACKEND`) or lane name (e.g., `Director Lane`, `QA Orchestrator`) or `NONE`
- **Description:** The identity or lane currently holding execution authority. Only the entity identified in this field may take actions that produce evidence or emit handoffs. Any other entity attempting to execute must stop and route to the Director.
- **Who Updates It:** Director Lane when routing or assigning work. Updated when a workcell receives or completes a handoff. An orchestrator reached by a registry command issued directly by the human operator sets this field to itself and records the issuing command in `INTAKE_REGISTER.md` — the authority comes from the human, not from the orchestrator claiming it.

---

### ExecutionReadiness
- **Class:** State
- **Type:** Enum
- **Allowed Values:**
  - `READY` — all prerequisites met; next action may proceed
  - `NOT_READY` — prerequisites not yet met (check Notes or active gap/blocker)
  - `BLOCKED` — a blocker is preventing progress (check ActiveBlockers)
  - `NEEDS_CONTEXT` — context pack is missing or insufficient
  - `NEEDS_APPROVAL` — human approval is pending
  - `NEEDS_PLANNING` — no approved milestone plan exists
  - `NEEDS_ONBOARDING` — required workcell is not registered
- **Description:** Signals whether the ADAPT instance can proceed with the next action. Agents read this field first. If the value is anything other than `READY`, the agent must address the indicated prerequisite before continuing.
- **Who Updates It:** Director Lane and any orchestrator completing a prerequisite step. Context Steward may update to `NEEDS_CONTEXT`. Guardrail Orchestrators may update to `BLOCKED` or `NEEDS_APPROVAL`.

---

### CurrentPhase
- **Class:** Authority
- **Type:** Enum
- **Allowed Values:**
  - `INITIALIZED` — ADAPT scaffold created; no source truth yet
  - `SOURCE_TRUTH_LOADING` — source truth promotion in progress
  - `SOURCE_TRUTH_READY` — source truth promoted and available
  - `ONBOARDING` — workcell onboarding in progress
  - `PLANNING` — milestone planning in progress
  - `READY_FOR_ASSIGNMENT` — milestone plan approved, or a prior package's handoff discharged; no workcell is currently bound to an active handoff
  - `EXECUTION` — active workcell is executing under a handoff
  - `INTEGRATION` — integration review in progress
  - `QA_VALIDATION` — QA validation in progress
  - `CHALLENGE_REVIEW` — challenge review in progress
  - `CONSOLIDATION` — Director consolidation cycle in progress
  - `JANITOR_PASS` — janitor pass in progress
  - `READY_FOR_NEXT_CYCLE` — consolidation complete; awaiting next cycle authorization
  - `BLOCKED` — execution is blocked (check ActiveBlockers)
- **Description:** The current governance phase of the ADAPT instance. Drives which lanes and orchestrators are active. Agents use this field to determine if their actions are appropriate for the current phase. A phase value exists for the interval between plan approval (or package completion) and the next assignment, so EXECUTION continues to mean a workcell is genuinely and currently bound.
- **Who Updates It:** Director Lane when transitioning between phases. A workcell may set `READY_FOR_ASSIGNMENT` only when discharging its current bounded-action handoff. Orchestrators may update to a sub-phase value when beginning a governed activity.

---

### ActiveWorkcell
- **Class:** Authority
- **Type:** String
- **Allowed Values:** Workcell ID (e.g., `WC-ANA-BACKEND`) from WORKCELL_REGISTRY.md or `NONE`
- **Description:** The workcell currently executing under `Run atomic handoff dispatch`. Only one workcell should be active at a time per execution lane. If multiple workcells are running in parallel, each must have a separate, non-overlapping scope contract.
- **Who Updates It:** Director Lane when assigning a handoff to a workcell. The workcell clears this field (sets to `NONE` or the next assigned workcell) when it emits its completion handoff.

---

### Blocked
- **Class:** State
- **Type:** Boolean
- **Allowed Values:** `YES` / `NO`
- **Description:** Indicates whether the ADAPT instance is currently blocked from making progress. If `YES`, ActiveBlockers must list at least one BLK-ID. If `NO`, ActiveBlockers must be `NONE`. Inconsistency between these fields is a control plane error that triggers Stop Rule 14.
- **Who Updates It:** Director Lane and Blocker Routing Agent. `YES` whenever at least one blocker is OPEN in BLOCKER_REGISTER.md, whatever its severity; `NO` only when none is OPEN.

---

### ActiveBlockers
- **Class:** State
- **Type:** String
- **Allowed Values:** Comma-separated BLK-IDs (e.g., `BLK-001, BLK-003`) or `NONE`
- **Description:** The IDs of every blocker whose status in BLOCKER_REGISTER.md is OPEN. A RESOLVED or DEFERRED blocker is removed. Must be consistent with the Blocked field.
- **Who Updates It:** Director Lane and Blocker Routing Agent when adding or resolving blockers.

---

### ActiveGaps
- **Class:** State
- **Type:** String
- **Allowed Values:** Comma-separated GAP-IDs (e.g., `GAP-001, GAP-004`) or `NONE`
- **Description:** The IDs of all open (unresolved) gaps in GAP_REGISTER.md. Used by orchestrators to check whether a required piece of information or authority is currently missing.
- **Who Updates It:** Director Lane and Gap Routing Agent when opening or resolving gaps.

---

### LastAction
- **Class:** Trace
- **Type:** String — free text
- **Allowed Values:** Any non-empty description of the last completed ADAPT action
- **Description:** Human-readable summary of the most recent completed action. Used for state recovery at the start of a new session. Should reference the relevant artifact ID (e.g., handoff ID, evidence report ID, decision log entry).
- **Who Updates It:** The orchestrator or agent that completed the action. Updated at the end of every Atomic Handoff Dispatch cycle.

---

### LastContextDelta
- **Class:** Trace
- **Type:** String
- **Allowed Values:** CD-ID (e.g., `CD-0012`) or `NONE`
- **Description:** The ID of the most recently produced context delta. Used by the Context Steward to determine whether the active context pack is current. If the last context delta is more recent than the current context pack, the pack must be refreshed before execution.
- **Who Updates It:** Context Steward when processing a context delta.

---

### NextExpectedAction
- **Class:** Trace
- **Type:** String — free text
- **Allowed Values:** Any non-empty description of the next required action
- **Description:** Human-readable description of what should happen next. Set at the end of every Atomic Handoff Dispatch cycle by the completing orchestrator. Used for state recovery and to guide the next agent reading the control plane. It is trace only: no agent may treat it as authorization to execute.
- **Who Updates It:** The orchestrator or agent completing the current action. Must be set before stopping.

---

### LastConsolidatedAt
- **Class:** Trace
- **Type:** Datetime or date string
- **Allowed Values:** ISO 8601 date or datetime (e.g., `2025-11-14` or `2025-11-14T14:30:00Z`) or `NEVER`
- **Description:** The date and time of the last Director consolidation cycle. Used to determine cycle freshness and whether a consolidation is overdue.
- **Who Updates It:** Director Consolidation Agent at the end of each consolidation cycle.

---

### Notes
- **Class:** Trace
- **Type:** String — free text
- **Allowed Values:** Any text
- **Description:** Free-form notes for human or Director Lane use. May record deviations, special authorizations, context-window constraints, or anything not captured by other fields. Not machine-parsed by default.
- **Who Updates It:** Director Lane, human initiator, or any orchestrator needing to record an explanation that does not fit another field.

---

## Control Plane Consistency Rules

| Rule | Check |
|------|-------|
| CP-C01 | If `Blocked = YES` then `ActiveBlockers` must contain at least one BLK-ID |
| CP-C02 | If `Blocked = NO` then `ActiveBlockers` must be `NONE` |
| CP-C03 | If `ExecutionReadiness = READY` then `ActiveMilestone` must not be `NONE` and `SourceTruthVersion` must not be `NONE` |
| CP-C04 | If `CurrentPhase = EXECUTION` then `ActiveWorkcell` must not be `NONE` and `ActiveHandoff` must not be `NONE` |
| CP-C05 | If `ActiveHandoff` is not `NONE` then it must reference a file that exists in `06_HANDOFFS/ACTIVE/` |
| CP-C06 | If `CurrentAuthority` is not `NONE` then it must match an entry in WORKCELL_REGISTRY.md or be a recognized lane name |
| CP-C07 | `LastConsolidatedAt` must be updated whenever `Director consolidate cycle` completes |
| CP-C08 | `RoutingMode` must be populated, and `07_GUARDRAILS/SCOPE_GUARDRAIL.md` must contain a Repository Routing section recording the same value |
| CP-C09 | If `ActiveWorkcell` is `NONE` then `ActiveHandoff` must be `NONE`; if `ActiveHandoff` is not `NONE` then it must name a handoff whose target lane is `ActiveWorkcell` |
| CP-C10 | Every BLK-ID with status `OPEN` in `BLOCKER_REGISTER.md` must appear in `ActiveBlockers`, and every BLK-ID in `ActiveBlockers` must have status `OPEN` in `BLOCKER_REGISTER.md` |
| CP-C11 | Every GAP-ID with status `OPEN` and a non-empty Blocking Item in `GAP_REGISTER.md` must appear in `ActiveGaps`, and every GAP-ID in `ActiveGaps` must have status `OPEN` in `GAP_REGISTER.md` |

`CP-C01` and `CP-C02` check control-plane fields against each other. `CP-C10` and `CP-C11`
check them against the registers. A control plane can be internally consistent and still not
reflect what happened — a lane that raised a blocker and did not record it leaves
`Blocked = NO` beside an open BLK-ID, which reads identically to nothing being blocked. These
two rules make that divergence detectable.

A control plane that fails any of these checks is in an inconsistent state. Any agent detecting a consistency failure must stop, record the failure, and route to the Director (Stop Rule 14).

A rule whose antecedent is false is `NOT_EXERCISED`, not `PASS`. It is not a failure and
does not trigger Stop Rule 14, but it must be reported as `NOT_EXERCISED` rather than
counted among the passes. At scaffold completion most rules are `NOT_EXERCISED` by
design — an instance with no milestone, no handoff and no workcell cannot exercise the
rules that test them.
