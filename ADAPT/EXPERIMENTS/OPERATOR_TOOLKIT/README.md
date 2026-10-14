# Experimental ADAPT Operator Toolkit v0.1

Python 3.9+ and Git for `evidence`; standard library only, no installation.
Run from any directory using the path to `adapt.py`. This remains experimental
under ADAPT-FW-0001. It is optional, not a canonical starter or mandatory step.

```powershell
python ADAPT/EXPERIMENTS/OPERATOR_TOOLKIT/adapt.py state --instance "D:\example_ADAPT_INSTANCE\ADAPT" --json
python ADAPT/EXPERIMENTS/OPERATOR_TOOLKIT/adapt.py doctor --instance "D:\example_ADAPT_INSTANCE\ADAPT" --json
python ADAPT/EXPERIMENTS/OPERATOR_TOOLKIT/adapt.py prompt next --instance "D:\example_ADAPT_INSTANCE\ADAPT"
python ADAPT/EXPERIMENTS/OPERATOR_TOOLKIT/adapt.py evidence --instance "D:\example_ADAPT_INSTANCE\ADAPT" --repo "D:\example_PROJECT" --file src/example.py --json
```

`--instance` is the directory directly containing `02_DIRECTOR_LANE`, not its
parent. `--repo` must be the actual Git root. `--file` is a repeatable,
explicit repo-relative path; it never follows references to unrelated roots.
All commands accept `--json`; without it they print concise human output.
No command writes an instance, framework, Git index or authority database.
No AI calls, repairs, result ingest, scaffolding, dispatch or network access.

## Command contracts

### state

Reads the bounded control-plane file and delegates to the existing State Reader.
Success JSON is exactly its 21 strings in schema order, without an envelope,
defaults or readiness inference. Existing State Reader CLI and tests are unchanged.
Malformed/missing files fail. Markdown cell padding is trimmed; strings,
placeholders and escapes are otherwise retained under the original parser limits.

### doctor

Returns `diagnostics`, each with stable `id`, `status`, `message`, and `source`.
Diagnostic IDs may repeat across artifacts; use `(id, source)` for inventory
findings. PASS, WARN and FAIL are severity outcomes; UNVERIFIED, NOT_CHECKED and
NOT_EXERCISED are evidence/applicability outcomes, never implicit passes.

Checks the full required instance inventory from the read-only framework
`SCAFFOLD_OUTPUT_CONTRACT.md`, including context and handoff directories; the
21-field schema; enums, source-version/date formats and required nonempty text;
CP-C01 through CP-C04; recognized authority/registry (CP-C06); active-handoff
location/existence (CP-C05) and target/workcell binding (CP-C09); and blocker/gap
register inclusion (CP-C10/11). Commented example rows are not live records.
Unknown or duplicate register IDs/statuses and malformed tables fail.
False rule antecedents are NOT_EXERCISED. Template placeholders remain
UNVERIFIED, including in canonical templates; templates are not invalid merely
because they contain placeholders.

Doctor is a structural subset, not certification. CP-C07 needs activity history;
CP-C08 needs routing-section interpretation. Both are explicitly unevaluated.
Source promotion, milestone approval, workcell role equivalence, stage records,
semantic scope, context freshness, task prerequisites and comprehensive referenced
artifact traversal remain unverified. Free-form ProjectType extensions are not
rejected or considered proof of justification. The inventory check targets the
full scaffold contract; it does not infer Lite/module activation from folder absence.
A zero exit code with UNVERIFIED findings does not mean the instance is ready.

### prompt next: supported binding-review subset

Outputs a deterministic **operator preview only**, with one bound identity/role,
handoff ID, source-version label and source artifact references. It never outputs
an execution invocation, substitutes an executing role, or grants approval.

Supported only when trace text exactly requests `Run atomic handoff dispatch`
and independent authoritative bindings agree: CurrentAuthority equals one ACTIVE
registered workcell; that identity card matches its registry role/owner; its
referenced scope contract belongs to it and has populated in-scope and mutation
rows; its ACTIVE, non-self-addressed handoff targets it; and its context pack
headers match the handoff/workcell/source version. A blueprint and action prompt
must exist. v0.1 supports exact Backend Developer and Frontend Developer roles;
aliases, lane invocation, Director, QA, Janitor, onboarding and integrations
requiring additional approvals remain unsupported. Handoff IDs of form HO-digits
map only to `06_HANDOFFS/ACTIVE/<ID>.md`; context IDs of form CP-digits map only to
`10_CONTEXT_ECONOMY/CONTEXT_PACKS/<ID>.md`. Otherwise supply explicit relative paths;
no directory search or guessed identity occurs.

The trace text is a requested preview filter, **not** the authorization source.
Missing/conflicting mandatory evidence produces diagnostics without a preview.
If any open or unresolved blocker/gap exists, applicability is UNVERIFIED and
the preview fails closed. Stop Rule 15 is work-item scoped: this conservative
tool limitation does not claim that every global blocker prevents every action.
The handoff body lacks a deterministic task-to-register work-item matching
contract, so the tool cannot distinguish unrelated blockers or remediation.

**Blocked capability:** automatic next-action selection and executable prompt
generation. The schema expressly says NextExpectedAction is trace, and the
handoff's Next Action Suggested is not an instruction. No deterministic mapping
from those texts to an approved command, job size, task scope, context freshness
or satisfied approval gates is defined. The toolkit delivers binding review;
the operator must perform those governance checks separately. Existence of a
scope/blueprint/context artifact does not establish its semantic completeness.
This subset does not complete autonomous next-invocation preparation.

### evidence

Returns Git root, branch (empty for detached HEAD), HEAD, sorted porcelain status
records, sorted changed paths, bounded artifact existence and SHA256 hashes.
Hashes the control plane, resolved active handoff and at most 100 explicit
`--file` references. Missing explicit files have `exists: false`; malformed
authoritative state or unsafe paths fail. Never dumps file contents, patches,
credentials, remote URLs or process error output. Paths and hashes may themselves
be sensitive metadata; choose explicit references for sharing accordingly.

Only four fixed read-only Git queries run: rev-parse root, status, branch and
rev-parse HEAD. No shell, hooks, fsmonitor process, fetch, pull, checkout, add,
commit, reset, clean or push. Optional index locks and untracked cache are
disabled; submodule internals are excluded. Git's normal local repository/config
reading still occurs. No content scanning of changed files is performed.

## Exit codes and bounds

- 0: output produced without FAIL; unverified checks can still remain.
- 1: invalid input, failed diagnostic or unsupported/ambiguous preview.
- 2: CLI usage error (argparse diagnostic on stderr).

JSON failure output uses the same diagnostic shape. Diagnostic errors do not
echo artifact contents. Paths may use platform separators; artifact references
normalize backslashes. Absolute references, traversal, `.git` references, URL/
drive references and symlinks resolving outside a supplied root fail. Roots
are explicit; there is no discovery in parent directories. Files read/hash are
limited to 2 MiB each; Git reads have a 20-second timeout. Concurrent writes,
symlink replacement races and Git status output size are not atomically bounded.
No persistent cache, timestamps or generated authority state is introduced.
Output ordering is stable for unchanged inputs on the same platform; absolute
root strings and Git path encoding can differ across platforms.

## Known framework inconsistencies and relevance

| Issue | Observed contract tension | Toolkit treatment |
|---|---|---|
| Placeholder preservation | Scaffold's populated-state requirements and blanket placeholder scan coexist with explicit preservation of template-level tokens | No blanket placeholder failures. State preserves text; doctor reports unresolved evidence; preview requires concrete binding fields only. |
| Janitor discharge ownership | Mutation matrix says Janitor can move consumed handoffs from ACTIVE to ARCHIVE; handoff guardrail assigns ACTIVE to CONSUMED to the receiving lane and denies Janitor ACTIVE moves | No lifecycle writes or Janitor invocation preview. |
| Onboarding control-plane authority | Onboarding action prompt allows directly issued command authority recording; schema allows explicit direct-command delegations, while matrix does not list the Onboarding Orchestrator as a role | No onboarding invocation selection or authority writes; direct command approval is not inferred. |
| Mutation-permission precedence | Schema class precedence and delegated state/trace writers coexist with matrix prohibitions on control-plane edits outside discharge | Report scope bindings only. Never reconcile permissions, authorize writes or patch either contract. |
| Lite stop-rule count | Lite documentation says 14 rules; STOP_RULES includes Rule 15, Execution While Blocked | Rule 15 informs conservative preview refusal. No Lite certification or rewriting rule counts. |

These are relevance assessments, not Framework Maintainer decisions. Some
delegations have explicit precedence already; their existence does not justify
silently reconciling the remaining matrix text or changing ADAPT-FW-0001.

## Validation and promotion

```powershell
python -B -m unittest discover -s ADAPT/EXPERIMENTS/STATE_READER/tests -p test_state_reader.py -v
python -B -m unittest discover -s ADAPT/EXPERIMENTS/OPERATOR_TOOLKIT/tests -p test_toolkit.py -v
```

Integration tests copy actual canonical starters into temporary directories,
populate only synthetic fixture binding evidence, create a temporary Git repo,
and exercise all four commands. They test repeatability, unchanged input/Git
bytes, malformed/missing artifacts, unknown identities, authority/context
conflicts, incomplete scope and unsafe paths. Fixture previews intentionally
leave semantic evidence unverified; they are not real-instance approval.

Promotion needs referenced/classified real-instance evidence of a generic
problem and benefit, reproducible accuracy/failure and nonmutation results,
novelty dimensions, and a qualifying Director escalation or Memory Bank lesson.
The Framework Maintainer must assess a candidate, record a PROMOTED disposition
with decision and introduced version, authorize a framework patch and consider
upgrade/backport eligibility. Deterministic next-selection also needs a new,
explicit decision/binding contract. No candidate, approval, promotion, version
change, framework certification or mandatory toolkit adoption is asserted here.
