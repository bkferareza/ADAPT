# Planning Rules

STATUS: DRAFT
PROJECT: {{PROJECT_NAME}}

## Purpose

These rules govern the Planning Lane within this ADAPT instance. The Planning Lane produces recommendations and sequences — it does not approve its own output or make product decisions.

---

## Rule 1 — Planning Recommends; Director Approves

Planning must not approve its own output. All planning outputs (milestone plans, roadmaps, capacity models, sequencing recommendations) must be submitted to the Director as a handoff. The Director decides what to approve.

## Rule 2 — Capacity Must Be Considered

Planning must not over-assign work. Each workcell's available capacity (see CAPACITY_MODEL.md) must be checked before assigning business items to a workcell for a milestone. Overextension must be flagged, not silently ignored.

## Rule 3 — QA and Integration Are Planned In, Not Dumped at the End

QA and Integration work must be planned into the milestone timeline with explicit sequencing. Planning must not produce a milestone plan that assigns all QA and Integration tasks to the final period of the milestone.

## Rule 4 — Read Source Truth, Gap Register, and Blocker Register First

Before making planning recommendations, Planning must read the current source truth version, the GAP_REGISTER.md, and the BLOCKER_REGISTER.md. Planning based on stale or incomplete information is a governance violation.

## Rule 5 — Account for Dependencies

Planning must account for dependencies between business items and workcells. See DEPENDENCY_MAP.md in 02_DIRECTOR_LANE/ and DEPENDENCY_SEQUENCES.md in this section. Work must not be scheduled in violation of a known dependency.

## Rule 6 — Milestones Must Have Verifiable Completion Criteria

Every milestone must have clear, verifiable completion criteria recorded in MILESTONE_REGISTER.md. A milestone without testable completion criteria cannot be approved by the Director.

## Rule 7 — Flag Overextension Risk

Planning must flag overextension risk when detected — see OVEREXTENSION_RISK_REPORTS.md. Overextension must be surfaced to the Director before the milestone plan is finalized.

## Rule 8 — Submit Outputs as Handoffs

Planning outputs must be submitted to the Director as a handoff (routed via 06_HANDOFFS/ACTIVE/). Planning does not publish its output directly to workcells without Director approval.

## Rule 9 — Approved Outputs Are Recorded in DECISION_LOG.md

Approved planning outputs are recorded by the Director in DECISION_LOG.md. Planning does not write to DECISION_LOG.md directly.

## Rule 10 — Planning Must Not Mutate Source Code or ADAPT Control Artifacts

Planning must not modify application source code, source truth documents, or ADAPT control artifacts (e.g., WORKCELL_REGISTRY.md, PROJECT_CONTROL_PLANE.md). Planning writes only to its own lane artifacts and to handoffs.
