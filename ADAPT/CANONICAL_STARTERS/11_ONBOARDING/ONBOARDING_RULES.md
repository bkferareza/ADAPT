# Onboarding Rules

STATUS: DRAFT
PROJECT: {{PROJECT_NAME}}

## Purpose

These rules govern how workcells are onboarded into this ADAPT instance. Onboarding is a formal process with defined prerequisites, a fixed sequence, and a quality gate. Partial or informal onboarding is not permitted.

---

## Onboarding Command Syntax

```
Onboard {{IDENTITY}} as {{ROLE}}
```

This command, issued to the Director, initiates the onboarding sequence.

---

## Pre-Onboarding Requirements

Before onboarding can begin, all of the following must be true:

1. The Director Lane must exist and be active (DIRECTOR_IDENTITY.md must be present and populated)
2. A source truth version must have been promoted in SOURCE_TRUTH_VERSION_LOG.md
3. The requested role must be defined in ROLE_MODEL.md — roles not listed in ROLE_MODEL.md cannot be onboarded

---

## What Onboarding Creates

Onboarding creates a workcell folder at:

```
ADAPT/03_WORKCELLS/{{ROLE}}_{{IDENTITY}}/
```

All 15 required files are generated within that folder during onboarding.

---

## Onboarding Sequence

1. Verify Director Lane exists and is active
2. Verify source truth version has been promoted
3. Verify the requested role is defined in ROLE_MODEL.md
4. Create the workcell folder at `ADAPT/03_WORKCELLS/{{ROLE}}_{{IDENTITY}}/`
5. Generate all 15 required workcell files (see below)
6. Register the workcell in WORKCELL_REGISTRY.md
7. Emit the first handoff from the Director to the new workcell

---

## Required Files Created at Onboarding

The following 15 files must be present upon completion of onboarding. Any file missing constitutes an incomplete onboarding:

1. `ACTION_PROMPT_{{ROLE}}_{{IDENTITY}}.md`
2. `WORKCELL_IDENTITY.md`
3. `SCOPE_CONTRACT.md`
4. `DEFAULT_AGENT_BLUEPRINT.md`
5. `WORKFLOW_CUSTOMIZATION.md`
6. `EFFECTIVE_WORKFLOW.md`
7. `GUARDRAIL_BINDINGS.md`
8. `WORKFLOW_CHANGE_REQUESTS.md`
9. `WORKFLOW_CHANGE_LOG.md`
10. `ROADMAP.md`
11. `TASK_REGISTER.md`
12. `EVIDENCE_LOG.md`
13. `HANDOFFS.md`
14. `BLOCKERS.md`
15. `CONTEXT_DELTAS.md`

---

## Post-Onboarding Steps

After the 15 files are generated and the quality check passes:

1. Update WORKCELL_REGISTRY.md with the new workcell entry
2. Update the project control plane (PROJECT_CONTROL_PLANE.md)
3. Record the completed onboarding in ONBOARDING_REPORTS.md

---

## Quality Check — Blueprint Depth

`DEFAULT_AGENT_BLUEPRINT.md` must contain full 8-section definitions for all agents required by the role. The 8 required sections per agent are defined in the framework agent blueprint standard.

If any agent definition is missing one or more of the 8 required sections, the onboarding agent must:

1. Report a `ROLE_AGENT_BLUEPRINT_DEPTH_FAILURE` to the Director
2. Halt onboarding — do not create the workcell folder or register the workcell
3. Await Director instruction before retrying

Onboarding is not complete until the quality check passes.
