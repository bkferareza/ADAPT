# Stale Artifact Register

STATUS: DRAFT
PROJECT: {{PROJECT_NAME}}

## Purpose

This register records ADAPT artifacts detected as stale by the Janitor Lane. A stale artifact is one that is no longer current, has been superseded, is orphaned (no owning workcell or active BI-ID), or is otherwise cluttering the ADAPT workspace. Detection does not authorize action — proposed actions require Director approval unless the artifact is an explicitly operational type (see JANITOR_RULES.md Rule 9).

## Proposed Action Values

- ARCHIVE — move to an archive folder; artifact is preserved but removed from active view
- MARK_SUPERSEDED — update the artifact's STATUS field to SUPERSEDED; do not move
- DELETE — permanent removal; requires explicit Director approval before execution
- COMPACT — condense verbose history into a summary; see COMPACTION_SUMMARIES.md
- REPORT_ONLY — no action taken; artifact flagged for Director awareness only

## Status Values

- DETECTED — artifact identified as stale; awaiting Director review or approval
- APPROVED — Director has approved the proposed action; not yet executed
- ACTIONED — proposed action has been executed and recorded in CLEANUP_REPORTS.md
- REJECTED — Director has reviewed and decided no action is warranted

## Register

| SA-ID | Artifact Path | Why Stale | Detected By | Detection Date | Proposed Action | Director Approval | Status | Notes |
|-------|--------------|-----------|-------------|----------------|-----------------|------------------|--------|-------|
<!-- EXAMPLE: | SA-001 | ADAPT/06_HANDOFFS/CONSUMED/HO-003.md | Handoff consumed two cycles ago; no longer needed in active view | JANITOR | {{DATE}} | ARCHIVE | Director — {{DATE}} | ACTIONED | Moved to ADAPT/06_HANDOFFS/ARCHIVE/ | -->
