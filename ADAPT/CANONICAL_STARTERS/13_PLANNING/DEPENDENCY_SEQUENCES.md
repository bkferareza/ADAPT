# Dependency Sequences

STATUS: DRAFT
PROJECT: {{PROJECT_NAME}}
MILESTONE: {{ACTIVE_MILESTONE}}

## Purpose

This file records sequenced dependency chains for planned work in the current milestone. Planning Lane populates this file as part of milestone plan preparation. All dependency chains must be reflected in WORKCELL_ROADMAPS.md sequencing. The Director reviews dependencies before approving milestone plans.

## Dependency Type Values

- Hard — successor cannot start until predecessor is complete; blocking
- Soft — successor can start before predecessor completes but may need rework if predecessor changes
- Integration — a formal integration contract or handoff must be completed between predecessor and successor
- QA Gate — QA must validate the predecessor artifact before successor work proceeds

## Status Values

- ACTIVE — dependency is in effect for the current milestone
- RESOLVED — predecessor is complete; successor is unblocked
- DEFERRED — dependency deferred with predecessor to a later milestone
- WAIVED — Director has waived this dependency with documented rationale

## Sequences

| SEQ-ID | Predecessor BI-ID | Successor BI-ID | Dependency Type | Estimated Gap | Status | Notes |
|--------|------------------|----------------|----------------|---------------|--------|-------|
<!-- EXAMPLE: | SEQ-001 | BI-001 | BI-003 | Hard | 1 day | ACTIVE | Schema (BI-001) must be finalized before seed data (BI-003) can be written | -->
