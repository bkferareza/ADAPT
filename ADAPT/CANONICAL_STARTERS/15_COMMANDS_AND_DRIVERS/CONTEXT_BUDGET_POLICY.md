# CONTEXT_BUDGET_POLICY.md
STATUS: DRAFT

## Purpose
Defines the context size tiers that govern how much context the Context Steward may assemble for any given ADAPT action. The goal is minimum safe context: enough to execute correctly, not so much that the agent is overloaded with irrelevant history. Each tier specifies what is included, what is excluded, typical use cases, and whether Director or human approval is required.

---

## Tier Definitions

---

### XS — Extra Small

**Included Artifact Types**
- The single command or request being processed
- The one directly referenced artifact (one register entry, one template, one control plane field read)
- No cross-lane context

**Excluded Artifact Types**
- Full control plane (read only the specific fields needed)
- Full registers (read only the specific entry referenced)
- Any artifact not directly referenced by the command
- Handoff chain history
- Decision log entries (unless the single command references a specific decision ID)

**Typical Use Cases**
- Simple status queries (e.g., "what is the current source truth version?")
- Single-register updates (e.g., recording one intake item in INTAKE_REGISTER.md)
- Command routing decisions (classifying a command and emitting a routing handoff)
- Updating one control plane field

**Approval Required**
NO — XS actions may proceed without Director or human approval (subject to stop rules and approval gates).

**What to Do If XL Is Needed Instead of XS**
If the agent begins assembling context for what appeared to be an XS action but discovers the action actually requires more artifacts, stop context assembly, re-classify the job size, and proceed with the appropriate tier. Never understate job size to avoid an approval gate.

---

### S — Small

**Included Artifact Types**
- The active handoff
- One requirement or business item (REQ-ID or BI-ID) and its linked acceptance criteria (AC-IDs)
- One scope contract (SCOPE_CONTRACT.md for the active workcell)
- One template (from 08_TEMPLATES, if applicable)
- Relevant control plane fields (not the full document — the fields relevant to the task)

**Excluded Artifact Types**
- Full decision log history
- Full register history (prior cycles)
- Cross-lane artifacts (integration reports, QA reports) unless directly referenced in the handoff
- Context packs from prior cycles
- Archived handoffs

**Typical Use Cases**
- Single-BI analysis by a planning or workcell agent
- Template generation (e.g., creating one workcell file during onboarding)
- Onboarding initialization (starting the V-01 validation checks)
- Routing a single gap or blocker

**Approval Required**
NO — S actions may proceed without Director or human approval (subject to stop rules and approval gates).

---

### M — Medium

**Included Artifact Types**
- The active handoff
- All requirements and acceptance criteria relevant to the handoff's BI-ID scope (not all requirements — only those linked to the handoff)
- The workcell's scope contract
- Relevant decisions from DECISION_LOG.md (only entries referencing the BI-IDs or AC-IDs in scope — not the full log)
- One API or UI contract (if the handoff involves cross-lane contract reference)
- Active handoff chain: up to 3 prior handoffs in the sequence (to understand the task lineage)

**Excluded Artifact Types**
- Full decision log history beyond the relevant entries
- Integration reports (unless the handoff explicitly references one)
- QA reports (unless the handoff explicitly references one)
- Archived handoffs beyond 3 steps back
- Context packs from prior cycles
- Full source truth document (read only the referenced sections or extracted REQ-IDs, not the whole document)

**Typical Use Cases**
- Standard bounded implementation action by a Backend or Frontend workcell
- Single-lane work producing an evidence report
- Gap routing for a non-critical gap
- Context pack assembly for a typical workcell handoff

**Approval Required**
NO — M actions may proceed without Director or human approval (subject to stop rules and approval gates).

---

### L — Large

**Included Artifact Types**
- All M-tier artifacts
- Multi-lane context: handoffs from multiple workcells for the same BI-ID or milestone phase
- Integration report (IR-ID) if integration has completed
- QA validation context (relevant AC-IDs, test scope) if QA is involved
- Director awareness artifacts: control plane full read, ACCEPTED_WORK_REGISTER.md for the cycle, GAP_REGISTER.md (open items)
- Cross-lane contracts (all contracts relevant to the integration or QA scope)
- Dependency map entries relevant to the current scope

**Excluded Artifact Types**
- Full register history from prior cycles (except for ACCEPTED_WORK_REGISTER.md entries used for regression scope)
- Archived handoffs beyond the current cycle
- Source truth versions other than the current version

**Typical Use Cases**
- Integration review (Integrator Orchestrator assessing multiple lane handoffs)
- QA validation (QA Orchestrator with test plan, evidence, and integration context)
- Director consolidation for a cycle (reading all lane states)
- Planning review when multiple workcells are active

**Approval Required**
NO for the context assembly itself. However, the Director must be notified when an L-tier action begins (log the action in the control plane `LastAction` field with size=L). Some L-tier actions may trigger other approval gates (e.g., certifying release requires Gate 8).

---

### XL — Extra Large

**Included Artifact Types**
- All L-tier artifacts
- Full lane audit context: all handoffs, evidence reports, and decision entries for the full milestone scope
- Release review context: QA report, integration report, all AC-ID statuses, all certification records
- Major replan context: full planning submission, risk reports, dependency map, all workcell roadmaps, all capacity records
- Prior cycle consolidation summaries (from DECISION_LOG.md) to understand milestone history

**Excluded Artifact Types**
- Source truth versions other than the current version (unless a multi-version comparison is explicitly required)
- Archived handoffs from prior milestones (unless specifically referenced)

**Typical Use Cases**
- Full lane audit across a milestone boundary
- Release review before final certification
- Major replan affecting multiple milestones
- Post-mortem analysis of a full cycle

**Approval Required**
YES — Director approval required. Human approval required if the XL action involves release review or major replan.

The Context Steward must:
1. Flag the XL classification to the Director Lane.
2. Wait for Director (and human, if required) approval before assembling the context pack.
3. Record the approval in DECISION_LOG.md.

**What to Do If XL Is Needed But Approval Is Not Granted**
If XL approval is not granted:
1. The Director Lane and Context Steward must split the XL action into a sequence of L-size actions.
2. Each L-size action has its own handoff, context pack, execution, evidence, and context delta.
3. The split must be documented in DECISION_LOG.md: original XL action description, split rationale, list of substitute L-size actions in sequence.
4. The substitute L-size actions are executed in sequence, each following the full 13-step Atomic Handoff Dispatch protocol.

---

## Context Budget Enforcement Rules

**Rule CB-01 — Minimum Context Principle**
Assemble the minimum context that allows correct and safe execution. If an action can be completed at M tier, do not assemble L-tier context. The Context Steward must justify tier selection in the context pack header.

**Rule CB-02 — No Retroactive Tier Inflation**
An agent may not begin an XS or S action and then decide mid-execution that it needs XL context. If the agent discovers the action is larger than estimated, it must stop, re-size, and (if required) obtain approval before reassembling context.

**Rule CB-03 — Stale Context Is Not Budget**
Including stale artifacts in the context pack does not satisfy the context budget — stale artifacts do not count as valid context. A context pack with 10 stale artifacts is not an L-tier pack; it is a pack with a staleness problem.

**Rule CB-04 — XL Approval Is Non-Transferable**
An XL approval granted for a specific action does not automatically apply to the next XL action. Each XL action requires its own approval record.

**Rule CB-05 — Director Notification for L-Tier**
When a Context Steward assembles an L-tier context pack, it records `size=L` in the control plane `LastAction` field before delivering the pack. This is not an approval request — it is a notification. The Director reviews the notification as part of the next consolidation.
