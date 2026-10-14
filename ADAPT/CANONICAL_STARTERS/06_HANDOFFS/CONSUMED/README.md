# Consumed Handoffs

STATUS: DRAFT
PROJECT: {{PROJECT_NAME}}

## Purpose

Contains handoffs that have been received and acted upon by their target lane. Consumed handoffs are retained here for audit and context delta tracing until the Janitor archives them.

## Usage

When a lane consumes a handoff from ACTIVE/:
1. Move the file here
2. Update the new handoff emitted to ACTIVE/

## Notes

Consumed handoffs must not be modified after consumption. They are the authoritative record of what was transferred at each step.
