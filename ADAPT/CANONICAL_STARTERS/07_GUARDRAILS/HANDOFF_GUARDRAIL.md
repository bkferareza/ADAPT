# HANDOFF_GUARDRAIL

STATUS: DRAFT
PROJECT: {{PROJECT_NAME}}
GUARDRAIL_ID: {{GUARDRAIL_ID_HANDOFF}}

## Enforcement Rule

A lane must emit a handoff before stopping; silent continuation past the handoff boundary is forbidden.

## Trigger Conditions

- A bounded action reaches its natural completion point without a handoff artifact having been emitted and placed in 06_HANDOFFS/ACTIVE/
- The next handoff target lane or workcell is ambiguous or cannot be determined from the current LANE_ASSIGNMENT_MATRIX or active work state
- Work begins in a workcell but no active incoming handoff artifact exists in 06_HANDOFFS/ACTIVE/ authorizing that work to begin
- Multiple active handoff artifacts exist in 06_HANDOFFS/ACTIVE/ for the same business item and the same receiving lane, creating routing ambiguity
- A handoff artifact was emitted but was not built from the canonical HANDOFF_TEMPLATE.md, making it non-parseable or incomplete
- A lane attempts to continue executing additional work items after completing a bounded action without receiving a new handoff from the Director
- A handoff remains in 06_HANDOFFS/ACTIVE/ after the work it authorizes has completed, or after its receiving lane has emitted its own handoff
- An incoming handoff's evidence report has no Stage Record row for an agent defined in the emitting workcell's DEFAULT_AGENT_BLUEPRINT.md, or lists those agents out of order (the receiving lane reads that blueprint for this check only)
- An incoming handoff's evidence report records a stage with Attempts above 2
- A handoff's target lane or workcell is the same lane or workcell that emitted it

## Outcome Types

### PASS

A complete, well-formed handoff artifact has been produced using the HANDOFF_TEMPLATE.md, placed in 06_HANDOFFS/ACTIVE/, and references the correct target lane. The handoff contains all required fields: source lane, target lane, business item reference, current state, evidence references, and any blockers. Proceed to stop. The target lane may now act on the handoff.

### WARN

The handoff target is ambiguous — the correct receiving lane cannot be determined with certainty from available information. The AI agent must document the assumption it is making about the target, emit the handoff with the assumed target, and route to the Director for confirmation before the target lane begins work. The handoff is valid but must not be acted upon by the receiving lane until the Director confirms routing.

### STOP_REQUIRED

No handoff can be emitted — either the target is completely unknown, required fields cannot be populated (e.g., evidence is missing), or the lane is in a blocked state that prevents normal handoff completion. Stop immediately. Record a blocker in 02_DIRECTOR_LANE/BLOCKER_REGISTER.md. Emit a "BLOCKED" handoff artifact using the HANDOFF_TEMPLATE.md (with STATUS: BLOCKED) routed to the Director. Do not silently stop without any handoff artifact. For a receiving lane, an incomplete Stage Record, a stage with Attempts above 2, or a self-addressed handoff is always STOP_REQUIRED: do not begin the handed-off work; route to the Director.

## AI Behavior When Fired

| Outcome | AI Must | Record In | Route To |
|---------|---------|-----------|----------|
| PASS | Emit handoff artifact; stop current lane execution | 06_HANDOFFS/ACTIVE/ | Target lane (as declared in handoff) |
| WARN | Emit handoff with assumed target and documented assumption; stop; await Director confirmation | 06_HANDOFFS/ACTIVE/ (handoff with WARN notation); active work log | Director for routing confirmation |
| STOP_REQUIRED | STOP. Emit BLOCKED handoff artifact. Record blocker. Do not silently stop. | 02_DIRECTOR_LANE/BLOCKER_REGISTER.md; 06_HANDOFFS/ACTIVE/ (STATUS: BLOCKED) | Director lane |
| UNDISCHARGED | Report the handoff ID, its receiving lane, and the evidence its work completed. Do not move it yourself unless you are its receiving lane. | 02_DIRECTOR_LANE/BLOCKER_REGISTER.md if unresolved | Director lane |

## Discharge

A handoff leaves `ACTIVE/` when the lane it was addressed to completes the bounded action
it authorized. That lane moves it to `CONSUMED/` before emitting its own handoff. This is
the receiving lane's responsibility, not the Director's and not the Janitor's.

The Janitor moves handoffs from `CONSUMED/` to `ARCHIVE/` when their milestone closes. The
Janitor never moves a handoff out of `ACTIVE/`.

A handoff whose receiving lane cannot complete its action is not discharged. It stays in
`ACTIVE/` and a BLOCKED handoff is emitted alongside it.

Handoffs accumulating in `ACTIVE/` with no receiving lane acting on them is a governance
failure, not a neutral state. Any agent reading `ACTIVE/` and finding a handoff whose
authorized work has demonstrably completed must report it to the Director.

## Override Requirements

There is no override that permits silent stopping. A blocked lane must always emit a "BLOCKED" handoff artifact rather than stopping without a trace. The BLOCKED handoff serves as the override mechanism — it records the blocked state, the reason, and routes control to the Director, who then decides how to unblock and re-route.

Even if all handoff fields cannot be fully populated, a minimal BLOCKED handoff must be emitted with at minimum: source lane, block reason, and route-to: Director. This is a hard requirement with no exceptions.

## References

- `06_HANDOFFS/` — top-level handoff folder; contains ACTIVE/, CONSUMED/, and ARCHIVE/ subfolders
- `06_HANDOFFS/README.md` — the authoritative handoff lifecycle, including discharge
- `06_HANDOFFS/ACTIVE/` — where all active handoff artifacts are placed
- `08_TEMPLATES/HANDOFF_TEMPLATE.md` — canonical template that all handoff artifacts must be built from
- `02_DIRECTOR_LANE/LANE_ASSIGNMENT_MATRIX.md` — used to resolve ambiguous handoff targets
- `02_DIRECTOR_LANE/BLOCKER_REGISTER.md` — where handoff blockers are recorded
- `00_FRAMEWORK/GOVERNANCE_RULES.md` — framework-level handoff protocol rules
