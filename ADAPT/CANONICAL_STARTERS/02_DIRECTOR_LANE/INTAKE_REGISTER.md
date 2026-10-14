# Intake Register

STATUS: DRAFT
PROJECT: {{PROJECT_NAME}}

## Purpose

Records all incoming requests, commands, and work items that have been submitted to the Director Lane. Director classifies each intake item and routes it appropriately.

## Intake Items

| INT-ID | Received Date | Source | Request Summary | Classification | Routed To | Status | Notes |
|--------|---------------|--------|-----------------|----------------|-----------|--------|-------|
<!-- EXAMPLE: | INT-001 | {{DATE}} | Human Owner | Onboard Ana as Backend Developer | Onboarding Command | Onboarding Orchestrator | ROUTED | Workcell created at BACKEND_ANA/ | -->

## Classification Values

- Onboarding Command
- Planning Request
- Implementation Assignment
- Source Truth Promotion
- Gap Routing
- Blocker Escalation
- Challenge Request
- Consolidation Trigger
- Janitor Pass
- Human Approval Request

## Status Values

- RECEIVED: Logged, pending Director review
- CLASSIFIED: Director has assigned a classification
- ROUTED: Sent to the appropriate orchestrator or workcell
- COMPLETE: Intake item fully handled
- REJECTED: Not valid or out of scope; reason recorded in Notes
