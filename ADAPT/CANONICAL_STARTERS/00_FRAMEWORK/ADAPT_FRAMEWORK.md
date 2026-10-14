# ADAPT Framework

STATUS: DRAFT
VERSION: {{ADAPT_VERSION}}
PROJECT: {{PROJECT_NAME}}
INITIALIZED: {{INITIALIZATION_DATE}}

## Purpose

This folder contains the ADAPT governance instance for {{PROJECT_NAME}}. ADAPT (Adaptive Delivery Protocol and Tracking) separates software delivery concerns into discrete governance lanes, each with defined authority, mutation scope, and evidence requirements.

## Operating Model

ADAPT runs on the Atomic Handoff Dispatch principle:
1. Recover current state
2. Locate active handoff or control plane
3. Validate authority
4. Estimate job size
5. Compute minimum safe context
6. Generate or attach Context Pack
7. Decide: execute, split, block, or route
8. Execute only if authorized and atomic
9. Produce evidence
10. Produce Context Delta
11. Emit next handoff
12. Update control plane
13. Stop

## Key Invariants

- Director routes work; Director does not implement.
- Workcells implement within their assigned scope; they do not assign themselves work.
- QA validates independently; developer self-validation is not QA signoff.
- Context Steward selects minimum safe context; Context Steward does not execute implementation.
- Handoffs must be emitted before a lane stops; silent continuation is forbidden.

## Folder Structure

```
ADAPT/
├── 00_FRAMEWORK/           — governance rules, role model, glossary
├── 01_SOURCE_TRUTH/        — requirements, business items, acceptance criteria
├── 02_DIRECTOR_LANE/       — intake, routing, control plane, gaps, blockers
├── 03_WORKCELLS/           — onboarded person-role workcells
├── 04_INTEGRATION/         — contracts, pipeline, merge readiness
├── 05_VALIDATION/          — QA strategy, test cases, defects, signoff
├── 06_HANDOFFS/            — active, consumed, archived handoffs
├── 07_GUARDRAILS/          — enforcement rules for each guardrail
├── 08_TEMPLATES/           — reusable templates for ADAPT artifacts
├── 09_CHALLENGE_LANE/      — challenge register and challenge reports
├── 10_CONTEXT_ECONOMY/     — context packs, deltas, budgets, stale context
├── 11_ONBOARDING/          — onboarding rules, role-to-workcell map
├── 12_JANITOR/             — stale artifact detection, cleanup, archival
├── 13_PLANNING/            — milestones, capacity, roadmaps, sequences
├── 14_MEMORY_BANK/         — reference index and notes (not live authority)
└── 15_COMMANDS_AND_DRIVERS/ — command registry, action prompts, routing
```

## References

- GOVERNANCE_RULES.md — operational governance rules
- 02_DIRECTOR_LANE/PROJECT_CONTROL_PLANE.md — current project state
- 15_COMMANDS_AND_DRIVERS/COMMAND_REGISTRY.md — supported ADAPT commands
