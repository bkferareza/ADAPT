# Capacity Model

STATUS: DRAFT
PROJECT: {{PROJECT_NAME}}
MILESTONE: {{ACTIVE_MILESTONE}}

## Purpose

This document models workcell capacities and constraints for the current milestone. It is maintained by the Planning Lane and reviewed by the Director before milestone plan approval. The capacity model is a planning aid, not a commitment register. Actual delivery commitments are recorded in MILESTONE_PLANS.md after Director approval.

## Notes

- Available Hours/Sprint is an estimate provided by the human owner of each workcell.
- Current Load is the total estimated effort of BI items currently assigned to the workcell for this milestone.
- Overextended is YES if Current Load exceeds Available Hours/Sprint; Planning must flag this in OVEREXTENSION_RISK_REPORTS.md.
- Director reviews capacity before approving any milestone plan.

## Model

| Workcell ID | Role | Human Owner | Available Hours/Sprint | Current Load | Overextended? | Notes |
|-------------|------|-------------|----------------------|--------------|---------------|-------|
<!-- EXAMPLE: | IMPL_ALICE | Implementation | Alice Reyes | 30 hrs | 28 hrs | No | Load is within capacity for MS-001 | -->
