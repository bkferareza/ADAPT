# FW-0007 R3 correction and exact-image review package

Date: 2026-11-03 (Asia/Manila). Branch: `fw0007/human-communication-candidate`.
Current issued baseline: ADAPT-FW-0006. FLC-006: PENDING. FW-0007: NOT_ISSUED.

## Technical recommendation

R3 is corrected. R1 and R2 still pass unchanged in both modes. The bounded A-J
outcome matrix passes in MODE_A and MODE_B. Submit the refreshed exact candidate
and separate proposed FW-0007 image for final Human Framework Maintainer review.
This is a technical recommendation, not a human disposition or issuance decision.

## Cause and correction

The saved post-remediation R3 evidence showed an actual completed, audited repair
followed by an empty operation reference. Reference claim lookup raised before
outcome_available was set. The generic renderer then asserted CHANGES: None and
REPORTING: SUCCEEDED without evidence about the previous mutation.

The existing MaintenanceEntry now establishes uncertainty as soon as it selects
a consumed action, before reading its decision/reference/claim/outcome chain.
It retains the known operation reference and reference path, and retains a known
claim even if later reference validation fails. It validates the reference binding
and audits persisted completion before retaining any successful saved outcome.
Missing, incomplete, unreadable or unauditable evidence uses reporting_fallback
directly: RECOVERY UNKNOWN, REPORTING FAILED, CHANGES UNKNOWN, VALIDATION UNKNOWN.
No second renderer call, writer call or approval call occurs on that path.

The ordinary response explains that ADAPT could not verify the previous operation,
that the saved reference is incomplete or unreadable when that is the failed link,
that the earlier action may have changed files, and that no action was repeated.
It states that the operation remains stopped and the responsible human must inspect
available evidence. Known identifiers remain available without fabricated claims.
Re-entry leaves original reference, claim, outcome, journal and reporting bytes
untouched. It does not reconstruct, repair, retry, roll back or resume the operation.
No subsystem, dispatcher, writer, governance layer or approval mechanism was added.

## Bounded validation

- Focused interaction qualification: 58 tests passed.
- Final affected regression: 178 tests passed, zero failures/errors/skips.
- Proposed FW-0007 image: 14 tests passed, including both scaffold modes,
  R1/R2/R3, audited re-entry and actual structural/context operations.
- Wrong-version installation refusal: 1 test passed with both mode subcases.
- Every prior interaction test method remains unchanged; see test-preservation.json.

The final regression uses the prior bounded affected-suite selection: interaction,
supervision, plan review, scaffold/distribution, entry contracts, release and selected
operational approval, mutation, audit and replay checks. It adds only the R3 evidence
subcases and no-execution/rejection/audited-reentry boundaries. No unrelated historical
investigation or exhaustive writer fault review was repeated.

outcome-matrix-results.json maps A-J to the actual passing test IDs in both modes.
A covers evidenced no execution; B preserves refusal; C verifies actual replacement
then interruption/reporting failure; D preserves audited success; E covers empty,
unreadable and missing references; F covers missing claim/outcome/completion; G rejects
an altered journal at audit; H retains known success after renderer failure; I returns
minimal fallback text with both evidence lookup and renderer unavailable; J guards
writer and approval during completed re-entry. Assertions cover response text, outcome,
mutation/validation/reporting distinctions, identifiers/evidence and STOP behavior.

Every R3 evidence subcase first executes a real bounded structural repair on a new
disposable installed instance, proves changed bytes, audits success, and retains the
original reference/claim/outcome bytes in r3-original-evidence.json. It then damages
only disposable evidence, creates a fresh entry, guards writer/approval/renderer,
and checks the returned response plus unchanged instance and ledger inventories.
The normal renderer is available for the ordinary damaged-evidence cases; the dual
failure case makes it consistently unavailable and asserts it is never invoked.

Early development logs are retained. Two early runs encountered stale distribution
hashes while the baseline snapshot/source/manifest work was still in progress.
They are not qualification; later focused and final stable-source runs passed.
Original R1/R2 tests and previous reviews, tests and human usability evidence remain
preserved. No assertion was weakened.

## Exact review evidence and preservation

Evidence root: `.adapt-local/maintenance/fw0007-r3-20261103/`.
candidate-source.zip, SOURCE_INVENTORY.json and candidate-vs-head.patch bind the
complete current framework. r3-vs-reviewed-candidate.patch isolates this increment
from the prior R1/R2 reviewed candidate. The separate proposed-release-image/ADAPT,
proposed-fw0007-source.zip, PROPOSED_IMAGE_INVENTORY.json and proposed-version.patch
bind the coherent unissued FW-0007 preview. exact-review-receipt.json records hashes;
EVIDENCE_SHA256SUMS.json binds supporting root artifacts. Actual test logs and
disposable transcripts remain under this evidence root.

The branch retains its FW-0006 compatibility declaration. The isolated preview uses
the prior reviewed version-only delta for the register declaration, active version
comparisons and release metadata, with payload hashes recomputed. Both retain the
pending FLC-006 row. Final archives are refreshed after adding this review document;
tested executable/payload bytes are unchanged by that documentation refresh.
preservation.json verifies protected ADAPT-DEV files, previous FW-0007 evidence,
Git HEAD/tags, branch and the existing .gitignore amendment. Earlier packages remain
historical and are not overwritten. No protected repair or usability action was replayed.

## Limits and next human decision

Approvals in these tests are simulated technical evidence. Prior actual MODE_B
conversation acceptance is preserved; MODE_A real human usability remains NOT_TESTED.
Python 3.11.4 was executed; Python 3.10 syntax parsing is not Python 3.10 runtime or
cross-platform qualification. Existing local same-volume/exclusive-operator,
installation and approval assumptions remain. No new independent identity, QA,
power-loss, network-filesystem, resume or rollback guarantee is claimed.

BLK-001 remains HIGH/OPEN and ordinary execution remains gated. Human review is
required before further action when evidence is uncertain. The Human Framework
Maintainer must review this exact package and decide whether to accept R3 closure,
promote FLC-006 and authorize advancement to FW-0007. Proposed eventual disposition
remains PROMOTED / Introduced In FW-0007 / Backport ELIGIBLE / Upgrade Assessment
REQUIRED; none is recorded as a human decision. A disposition would require its own
incorporation and receipt refresh. Publication and existing-instance adoption remain
separate decisions. No merge, tag, publication or ADAPT-DEV modification occurred.

STOP.
