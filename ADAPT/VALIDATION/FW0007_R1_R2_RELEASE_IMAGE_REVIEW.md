# FW-0007 R1/R2 correction and exact candidate review

Date: 2026-11-03 (Asia/Manila). Branch: `fw0007/human-communication-candidate`.
Issued baseline: ADAPT-FW-0006. FLC-006: PENDING. FW-0007: NOT_ISSUED.

## Correction

R1 and R2 were confirmed against the current local candidate and the preserved
Maintainer reproductions. The existing operational module now uses one small
`reporting_fallback` for immediate writer outcomes and audited saved completion
outcomes. No writer contract, approval authority, retry policy or dispatcher changed.

The entry retains the returned outcome before any later reporting or cleanup
failure. Its reporting exception path no longer requires RECOVERY_VALIDATED.
Interrupted recovery stays interrupted, refusal stays refused, and incomplete
evidence stays unknown. Returned writer fields, including reason, claim, hashes,
journal, final hashes and authority limitations, are retained. Reporting adds its
own failure fields and readable explanation. It never changes historical outcomes.

For interruption after actual replacement, the response says RECOVERY: INTERRUPTED
and REPORTING: FAILED, explains that the instance may have partially changed,
and requires evidence inspection before any further action. Unknown write extent
is CHANGES: UNKNOWN, never a no-change assertion. The persisted writer interruption,
pending result, claim, operation reference, journal and consumed decision remain
available. No automatic retry, resume or rollback occurs.

On completed-action re-entry, the entry first audits the writer's completion
evidence. The saved outcome then participates in the same fallback. A failed
renderer returns RECOVERY: SUCCEEDED and REPORTING: FAILED, explains that the
operation previously succeeded and its recorded validation passed, and says the
saved outcome remains authoritative and no replay is necessary. Entry status
remains BLOCKED / DECISION_ALREADY_CONSUMED, with recovery fields preserved.
Neither a writer invocation nor another approval is needed or attempted.

The exception path calls the fallback directly, never the failed renderer again.
Missing writer evidence and pre-execution renderer failure also return readable
unknown-state text. Validated success requires the writer's completion metadata;
a bare success label is insufficient. File validation evidence remains distinct
from overall recovery completion, interruption, reporting and execution readiness.
An unreadable or incomplete saved completion that fails audit returns unknown
mutation/validation with its known claim, without attempting recovery or rendering
a false no-change response.

## Validation evidence

Evidence root: `.adapt-local/maintenance/fw0007-r1-r2-20261103/`.
The machine-readable focused/final results and logs in that root are authoritative
for counts and individual test IDs; the review receipt binds the exact files.

Both MODE_A and MODE_B use separately installed disposable instances and simulated
approval. R1 executes the real writer, interrupts after replacement, verifies
changed bytes and persisted RECOVERY_INTERRUPTED, then raises reporting_check.
R2 completes and audits a real recovery, creates a fresh entry, makes the renderer
fail consistently, and guards writer/approval methods against replay. Tests inspect
the actual returned prose, writer fields and preserved files, rather than merely
checking that a report exists. Missing-outcome tests intentionally supply absent
evidence; no successful mutation is mocked.

Coverage also includes refusal followed by reporting failure, incomplete evidence,
normal reporting, natural-language approval, completed re-entry, authority and
withdrawal checks, ordinary STOP/replay guards, installed scaffold distribution,
manifest payload hashes, supervision, plan review and selected operational cases.
The affected regression follows the existing bounded qualification selection;
unrelated framework investigations and the exhaustive writer fault matrix are
outside this correction. The final affected suite is run once after stabilization.

An early before-fix test run reproduced R1 in both modes and R2 on its original
MODE_A installed fixture. Other early errors include the absent new helper and
fixtures copied while the source/manifest were being amended; that run is retained
as development evidence, not qualification. The historical Maintainer evidence
already independently reproduces both defects in both modes. Passing final-source
qualification supersedes these development-run failures without deleting them.
A development broad run was stopped before qualification to add this saved-audit
uncertainty check; its partial log is retained separately. The final affected
regression follows stabilization of that correction.

## Human usability and limitations

The actual prior MODE_B conversation remains accepted within its bounded scope:
details and CP terminology clarification, actual unconditional human approval,
validated sample repair and the operator's "next step clear" feedback. The original
session, outcome and evidence are preserved and were not replayed. This correction's
automated decisions establish technical behavior, not additional human acceptance.
MODE_A actual human usability remains NOT_TESTED. No new operator trial occurred.

Python 3.11.4 is the execution environment. The manifest minimum remains Python
3.10; syntax checks for the proposed image do not establish execution on Python
3.10 or other platforms. Local same-volume filesystem, exclusive operator and
the existing installation/approval bindings remain required. There is no new
identity authentication, network-filesystem support, power-loss recovery,
automatic retry, resume, rollback or independent QA claim.

## Exact source and proposed version review

`candidate-source.zip`, `SOURCE_INVENTORY.json`, `candidate-vs-head.patch` and
`r1-r2-vs-local-baseline.patch` bind the complete working candidate and the bounded
increment from the pre-existing local amendment. `exact-review-receipt.json` gives
their SHA256 hashes and the manifest/payload hashes. `EVIDENCE_SHA256SUMS.json`
binds the supporting root files. The pre-existing .gitignore amendment is excluded
from the candidate package and preserved. Historical reports retain their dated
findings; this review records the subsequent correction.

The branch retains the single FW-0006 declaration and the existing compatible
runtime checks. This is an unissued candidate, not a redefinition of the FW-0006
release. Review preparation additionally produces a separate, unissued proposed
FW-0007 image under `proposed-release-image/ADAPT`, archived as
`proposed-fw0007-source.zip`. It retains FLC-006 as pending. Its exact inventory,
version-only patch and distribution/operational compatibility results are retained
beside the working-candidate evidence. The preview is never installed into ADAPT-DEV.

The proposed atomic version delta is:

- Advance the single register declaration to ADAPT-FW-0007 once.
- Align the operational VERSION constant and the preflight/authority capability
  comparisons with FW-0007. Historical prose and evidence labels stay historical.
- Align manifest release_framework_version and recovery_capabilities.proposed_framework.
  Recompute every changed instance payload hash. The older tooling framework_version
  field describes the unchanged tooling-v1 baseline and remains FW-0002.
- Verify both new scaffold distributions and real bounded structural/context
  operations against that coherent version. Preserve refusal of wrong-version
  installation records; version text alone never grants authority.

Neither the preview nor its proposed patch records a human disposition or issues
a release. Actual decision evidence and its final register incorporation necessarily
require a final receipt refresh before publication; the exact pending proposal is
what this package presents for review.

## Proposed Maintainer disposition and next decision

Technical recommendation: R1 and R2 corrected; submit this exact candidate and
version preview for Maintainer review. Proposed FLC-006 disposition: PROMOTED,
Introduced In: ADAPT-FW-0007, Backport: ELIGIBLE, Upgrade Assessment: REQUIRED.
These are proposals only. The live FLC row remains pending with no invented
decision or introduction version. The Human Framework Maintainer must decide
whether to promote FLC-006 and authorize the proposed FW-0007 advancement.
Publication and existing-instance adoption are not authorized by this work order.

BLK-001 remains HIGH/OPEN. Ordinary execution remains BLOCKED. ADAPT-DEV,
historical journals/outcomes/usability evidence, Git HEAD and issued tags remain
unchanged, as checked in `preservation.json`. No merge, publication, protected
mutation, completed CONTEXT_INDEX replay or subsequent recovery was performed.

STOP after evidence preparation and the human-readable correction response.
