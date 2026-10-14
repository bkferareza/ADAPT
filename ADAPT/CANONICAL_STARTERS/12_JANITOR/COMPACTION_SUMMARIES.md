# Compaction Summaries

STATUS: DRAFT
PROJECT: {{PROJECT_NAME}}

## Purpose

This log records all context and history compaction summaries produced by the Janitor Lane. Compaction condenses verbose intermediate history into a navigable summary without removing authoritative content. Compaction must never remove accepted decisions, evidence references, or authoritative links — only raw history and verbose intermediate logs may be condensed.

## Compaction Standard

Before compacting, the Janitor must verify that all of the following are preserved in the output summary:

- All decisions accepted by the Director (reference to DECISION_LOG.md entry)
- All evidence references (reference to EVIDENCE_LOG.md or external evidence)
- All authoritative artifact links (live path to source truth, contracts, or scope documents)

If any of the above cannot be preserved, compaction must not proceed and must be reported to the Director.

## Log

| CS-ID | Date | Scope | Artifacts Compacted | Key Decisions Retained | Evidence Links Retained | Produced By | Notes |
|-------|------|-------|---------------------|----------------------|------------------------|-------------|-------|
<!-- EXAMPLE: | CS-001 | {{DATE}} | IMPL_ALICE CONTEXT_DELTAS.md cycles 1–3 | 3 context delta files (CP-001, CP-002, CP-003) | DEC-004, DEC-007 | EV-011, EV-015 | JANITOR | Summary written to IMPL_ALICE/CONTEXT_DELTAS_SUMMARY_CYCLE1-3.md | -->
