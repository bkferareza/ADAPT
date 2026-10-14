# Janitor Rules

STATUS: DRAFT
PROJECT: {{PROJECT_NAME}}

## Purpose

These rules govern all Janitor Lane operations within this ADAPT instance. The Janitor Lane keeps the ADAPT workspace clean and navigable without making product decisions or silently destroying information.

---

## Rule 1 — Archive, Mark, Summarize, Report — Never Silently Delete

Janitor archives, marks, summarizes, and reports. It does not silently delete artifacts. Every cleanup action must be visible and recoverable.

## Rule 2 — Source Truth Is Never Deleted

Source truth documents must never be deleted. They may be marked SUPERSEDED and moved to an archive folder, but the document must remain accessible and its version must remain recorded in SOURCE_TRUTH_VERSION_LOG.md.

## Rule 3 — Consumed Handoffs Require Director Confirmation Before Archiving

Consumed handoffs may be moved to ARCHIVE/ only after Director confirmation. Janitor must not autonomously archive handoffs without confirmation unless the handoff is already marked CONSUMED by the receiving workcell and more than one cycle has passed.

## Rule 4 — Orphan Tasks Routed to Director

Orphan tasks (tasks with no owning workcell, no BI-ID reference, or no active handoff) must be reported to the Director for routing. Janitor does not close, reassign, or discard them without Director instruction.

## Rule 5 — No Product Decisions

Janitor must not make product decisions. If a cleanup action would affect product behavior — including removing a decision from DECISION_LOG.md, altering a scope contract, or archiving an open acceptance criterion — Janitor must stop and route to the Director.

## Rule 6 — Compaction Must Preserve Decisions, Evidence, and Links

Compaction summaries must preserve all accepted decisions, evidence references, and authoritative links. Only raw history and verbose intermediate logs may be condensed. See COMPACTION_SUMMARIES.md.

## Rule 7 — Stale Context Packs Reported to Context Economy

Stale context packs must be reported via STALE_CONTEXT_REGISTER.md in 10_CONTEXT_ECONOMY/. Janitor does not rebuild context packs — it reports and flags. Rebuilding is the responsibility of the Context Steward.

## Rule 8 — All Cleanup Actions Recorded

All Janitor cleanup actions must be recorded in CLEANUP_REPORTS.md. An undocumented cleanup action is a governance violation.

## Rule 9 — Archive Candidates Require Director Review

Archive candidates require Director review before archiving unless they are clearly operational artifacts (consumed handoffs, superseded context packs). When in doubt, create an entry in ARCHIVE_CANDIDATES.md and wait for Director decision.

## Rule 10 — Open Blockers Cannot Be Closed Without Proof

The Janitor must not close open blockers without proof of resolution. Open blockers in BLOCKER_REGISTER.md remain OPEN until the Director or the responsible workcell provides resolution evidence.
