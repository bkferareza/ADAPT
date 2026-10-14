# Context Rules

STATUS: DRAFT
PROJECT: {{PROJECT_NAME}}

## Purpose

These rules govern how context is assembled, used, validated, and retired within this ADAPT instance. All workcells and the Director must comply with these rules. The Context Steward is responsible for enforcing them during context pack assembly.

---

## Rule 1 — Context Pack Required

Every bounded ADAPT action requires a context pack assembled by the Context Steward. Ad-hoc context pulled directly from memory or training knowledge is not permitted as the basis for ADAPT actions.

## Rule 2 — Source Truth Version Reference

Context packs must reference a specific source truth version from SOURCE_TRUTH_VERSION_LOG.md. Unversioned context is not valid.

## Rule 3 — Scope Declaration

Context packs must declare scope explicitly: which items are included and which are excluded. An undeclared exclusion is a gap, not a valid omission.

## Rule 4 — Stale Context Detection

Stale context must be detected and excluded before use. See STALE_CONTEXT_REGISTER.md for known stale items. If a context pack includes a known stale item, it must be rebuilt before the action proceeds.

## Rule 5 — Size Classification

Context size must match the action type. Oversized context inflates token cost and risk; undersized context produces incomplete actions. See CONTEXT_BUDGETS.md for size tier definitions and selection guidance.

## Rule 6 — Invalidation on Version Supersession

Context packs must be invalidated when their source truth version is superseded. A context pack referencing a superseded source truth version must be marked SUPERSEDED in CONTEXT_INDEX.md and rebuilt before further use.

## Rule 7 — Gap Recording on Missing Context

Missing context must be recorded as GAP-T11 in the Gap Register. Missing context does not authorize inference from training knowledge. If a required artifact is not available, the action must be paused and the gap reported to the Director.

## Rule 8 — Context Steward Does Not Execute

The Context Steward does not execute implementation work. Its responsibility is limited to selecting, assembling, scoping, and validating context packs. Execution remains with the assigned workcell.

## Rule 9 — Context Delta on Completion

After an action is completed, the executing workcell must produce a Context Delta documenting what changed. The Context Delta must be attached to the outbound handoff so downstream lanes receive updated context.

## Rule 10 — Prior Cycle Context Not Valid Without Refresh

A context pack from a prior cycle is not valid for a new cycle without a refresh. Context packs do not carry over between milestones or cycles unless explicitly re-validated against the current source truth version.
