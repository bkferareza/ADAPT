# Source Truth Version Log

STATUS: DRAFT
VERSION: {{ADAPT_VERSION}}
PROJECT: {{PROJECT_NAME}}

## Purpose

Records every source truth promotion event. Provides an audit trail of what was accepted as authoritative ground truth and when.

## Version Log

| Version | Document Name | Document Type | Promoted By | Approval Date | Key Changes | Supersedes | Status |
|---------|--------------|---------------|-------------|---------------|-------------|------------|--------|
<!-- EXAMPLE: | SOURCE_TRUTH_V0.1 | {{SOURCE_DOCUMENT}} | Director Lane | {{DATE}} | Initial source truth — all requirements from project document | — | ACTIVE | -->

## Document Types

- Requirements Document
- Design Specification
- Architecture Decision Record (ADR)
- API Contract
- Business Requirements Document (BRD)
- User Story Set

## Status Values

- ACTIVE: Current authoritative version
- SUPERSEDED: Replaced by a newer version; retained for traceability
- ARCHIVED: Older version; preserved in archive

## Notes

Each promotion requires Director authority and human approval per HUMAN_APPROVAL_GATES.md. All workcell work must reference a specific source truth version. When a version is superseded, all open work against it must be re-validated.
