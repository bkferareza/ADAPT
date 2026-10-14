# Overextension Risk Reports

STATUS: DRAFT
PROJECT: {{PROJECT_NAME}}

## Purpose

This file records detected overextension and planning risks flagged by the Planning Lane. Planning must surface these reports to the Director before finalizing a milestone plan. The Director decides how to resolve the risk (reduce scope, add capacity, resequence, or accept risk).

## Risk Type Values

- Role Overload — a workcell is assigned more work than its available capacity for the milestone
- Late Integration — integration work is scheduled too late to allow adequate resolution time
- Late QA — QA work is scheduled too late to allow defect resolution within the milestone
- Unrealistic Concurrency — two or more items are scheduled in parallel but share a dependency or a workcell resource
- Role Coverage Gap — a required role has no active workcell onboarded for the milestone
- Dependency Chain Risk — a chain of dependencies creates a critical path with no buffer

## Reports

| OR-ID | Milestone | Risk Type | Affected Workcells | Description | Severity | Recommended Action | Director Decision | Notes |
|-------|-----------|-----------|-------------------|-------------|----------|--------------------|------------------|-------|
<!-- EXAMPLE: | OR-001 | MS-001 | Late QA | QA_CARLOS | QA is currently planned for the final 2 days of a 3-week milestone with 12 test cases in scope | HIGH | Move QA start to week 2; reduce final-week scope | Pending | Flagged during MS-001 plan review | -->
