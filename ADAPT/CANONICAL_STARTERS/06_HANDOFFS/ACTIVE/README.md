# Active Handoffs

STATUS: DRAFT
PROJECT: {{PROJECT_NAME}}

## Purpose

Contains handoffs currently in transit. A handoff placed here is awaiting consumption by the receiving lane.

## Usage

When a lane completes a bounded action and emits a handoff:
1. Write the handoff file here using the naming convention: HANDOFF_{{FROM_ROLE}}_TO_{{TO_ROLE}}_{{SEQUENCE}}.md
2. Record the emitted handoff without repointing the current workcell's ActiveHandoff. The Director binds a handoff to its receiving ActiveWorkcell under CONTROL_PLANE_SCHEMA.md; an escalation or other outgoing handoff never replaces the emitter's current binding.
3. Stop

The receiving lane reads from this folder at the start of its bounded action.

## Current Active Handoffs

None — ADAPT instance just initialized.
