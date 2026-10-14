# Artifact Standards

STATUS: DRAFT
VERSION: {{ADAPT_VERSION}}
PROJECT: {{PROJECT_NAME}}

## Purpose

Defines the standards all ADAPT artifacts in this instance must meet. Non-compliant artifacts are flagged by the Janitor or Context Steward and must be corrected before use.

## Placeholder Standard

All project-specific values in templates and starters use {{DOUBLE_BRACE}} format.
- Correct: {{PROJECT_NAME}}, {{IDENTITY}}, {{ROLE}}, {{MILESTONE_ID}}, {{DATE}}
- Forbidden: <PROJECT_NAME>, <identity>, [placeholder], PLACEHOLDER

Unreplaced placeholders in live artifacts are treated as incomplete artifacts and must be flagged.

## Status Field Standard

Every ADAPT artifact must include a STATUS field. Valid values:
- DRAFT: created but not yet reviewed or in use
- ACTIVE: in current use as authoritative state
- SUPERSEDED: replaced by a newer version; retained for reference
- ARCHIVED: no longer active; moved to archive but preserved for history
- REMOVED: withdrawn from source truth by a recorded decision; retained for provenance and never deleted
- PENDING_REVIEW: created, awaiting Director or human review

Registers with their own status column — GAP_REGISTER, BLOCKER_REGISTER,
ACCEPTANCE_CRITERIA — use their own vocabulary for lifecycle state and this vocabulary for
artifact state. Where a register needs a value this list defines, it uses this list's
spelling.

## Register/Log Standard

Files that track records (registers, logs, indexes) must:
1. Include a fully populated header row
2. Include at least one commented-out example row showing correct column values
3. Start with zero live data rows until actual project data is added
4. Use consistent ID formats (REQ-NNN, BI-NNN, GAP-NNN, BLK-NNN, etc.)

## Evidence Standard

Evidence artifacts must:
- Be traceable to a source requirement, contract, or acceptance criterion
- Reference the source truth version they validate against
- Not be produced by the same human/AI that performed the work (QA evidence rule)
- Include the producing role and date

## Handoff Standard

Handoff artifacts must:
- Reference the source handoff they respond to (if applicable)
- Include the sending role/workcell and receiving role/workcell
- Include the evidence attached
- Include unresolved items and risks
- Be recorded in 06_HANDOFFS/ACTIVE/ while in transit

## Context Pack Standard

Context packs must:
- Declare their scope (what is included and explicitly excluded)
- Reference specific source truth versions
- Reference the active handoff they support
- Declare context size (XS/S/M/L/XL per CONTEXT_BUDGET_POLICY.md)
- Not include stale, superseded, or untraced artifacts

## Naming Conventions

- Workcell folders: {{ROLE}}_{{IDENTITY}}/ (e.g., BACKEND_ANA/)
- Handoff files: HANDOFF_{{FROM_ROLE}}_TO_{{TO_ROLE}}_{{SEQUENCE}}.md
- Gap records: GAP-{{TYPE}}-{{SEQUENCE}}.md (e.g., GAP-T10-001.md)
- Blocker records: BLK-{{SEQUENCE}}.md
- Context packs: CONTEXT_PACK_{{HANDOFF_ID}}_{{DATE}}.md
