# Handoffs

STATUS: DRAFT
PROJECT: {{PROJECT_NAME}}

## Purpose

This folder manages handoff artifacts — structured transfers of work, evidence, and state between ADAPT lanes. Handoffs are the primary mechanism by which bounded actions are chained.

## Subfolders

- **ACTIVE/** — handoffs currently in transit (emitted but not yet consumed)
- **CONSUMED/** — handoffs that have been received and acted upon
- **ARCHIVE/** — handoffs from closed or superseded work items

## Handoff Lifecycle

1. A lane completes its bounded action and emits a handoff to ACTIVE/
2. The receiving lane reads the handoff, validates authority, and begins its bounded action
3. Upon completion, the handoff is moved to CONSUMED/ and the lane emits its own handoff
4. Consumed handoffs from closed milestones are archived to ARCHIVE/ by the Janitor

## Rules

- A lane must not begin work without an active handoff in ACTIVE/
- A lane must emit a new handoff before stopping (even if just to report a block)
- Silent continuation beyond the next handoff boundary is forbidden
- Handoffs must reference the source truth version and active context pack
