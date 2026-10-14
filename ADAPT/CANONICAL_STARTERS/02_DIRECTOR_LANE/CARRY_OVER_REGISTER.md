# Carry-Over Register

STATUS: DRAFT
PROJECT: {{PROJECT_NAME}}
FROM_MILESTONE: {{PREVIOUS_MILESTONE}}
TO_MILESTONE: {{NEXT_MILESTONE}}

## Purpose

Records work items, gaps, and blockers that were not resolved in the current milestone and are carried over to the next. Director decides what carries over and why.

## Carry-Overs

| CO-ID | Type | Item ID | Title | Reason for Carry-Over | From Milestone | To Milestone | Priority in Next Cycle | Status |
|-------|------|---------|-------|-----------------------|----------------|--------------|------------------------|--------|
<!-- EXAMPLE: | CO-001 | Business Item | BI-007 | Reporting Dashboard | Dependency on BI-005 not resolved in time | {{MILESTONE_A}} | {{MILESTONE_B}} | MEDIUM | PENDING | -->

## Type Values

- Business Item
- Gap
- Blocker
- Open Question
- Acceptance Criterion

## Status Values

- PENDING: Will carry over; not yet started in next milestone
- ACTIVE: Picked up in next milestone
- RESOLVED: Resolved in a subsequent milestone
- DROPPED: Decided not to carry forward; reason in Notes
