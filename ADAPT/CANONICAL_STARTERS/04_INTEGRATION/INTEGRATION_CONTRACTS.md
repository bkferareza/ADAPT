# Integration Contracts

STATUS: DRAFT
PROJECT: {{PROJECT_NAME}}
MILESTONE: {{ACTIVE_MILESTONE}}

## Purpose

Records all cross-lane integration contracts governing how components connect. An integration contract is accepted when both the producing lane (e.g., Backend) and consuming lane (e.g., Frontend) have agreed to its terms and the Integrator has reconciled any conflicts.

## Integration Contracts

| IC-ID | Contract Name | Producer Lane | Consumer Lane | Contract File/Reference | Version | Status | Reconciled By | Notes |
|-------|--------------|---------------|---------------|------------------------|---------|--------|---------------|-------|
<!-- EXAMPLE: | IC-001 | User Auth API Contract | Backend Workcell | Frontend Workcell | API_CONTRACTS.md §1 | V0.1 | ACCEPTED | Integrator Lane | Defines /auth/login endpoint | -->

## Status Values

- DRAFT: Proposed but not yet reviewed
- IN_REVIEW: Under reconciliation by Integrator
- ACCEPTED: Both lanes agree; contract is binding
- CONFLICT: Incompatibility found; resolution pending
- SUPERSEDED: Replaced by a newer version

## Notes

Contracts must be accepted before implementation begins against them. A workcell that discovers a contract conflict must escalate to the Integrator via handoff.
