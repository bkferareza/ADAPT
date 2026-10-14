# ADAPT Operator Tooling v1

Self-contained Python 3.9+ standard-library distribution. Git is required only
for evidence. New scaffolds copy this directory verbatim; no development
repository, experiments, absolute developer paths or network services are needed.
The operator commands are optional and read-only; distribution is mandatory.

```powershell
python TOOLS/adapt.py state --instance . --json
python TOOLS/adapt.py doctor --instance . --json
python TOOLS/adapt.py prompt next --instance . --json
python TOOLS/adapt.py evidence --instance . --repo ../PROJECT --file src/example.py --json
```

Run these inside the ADAPT directory, or provide explicit paths from elsewhere.
`--instance` directly contains `02_DIRECTOR_LANE`; `--repo` is the exact Git root.
`--file` is repeatable and repo-relative. Omit `--json` for human output.

## Inputs, outputs and permissions

| Command | Inputs | Outputs |
|---|---|---|
| state | Control-plane Markdown table | Exactly 21 strings in schema order; cell padding trimmed |
| doctor | Packaged inventory, instance schema, control plane, handoff and registers | Stable ID/status/message/source diagnostics; unchecked conditions explicit |
| prompt next | Recorded control-plane, registry, identity, scope, handoff, member action prompt, decisions, approvals, version log, context hashes and incoming evidence | Bound operator invocation preview or BLOCKED; never executes or grants approval |
| evidence | Explicit instance/repo roots and bounded declared files | Git root/branch/HEAD/status/changed paths, artifact existence and SHA256 hashes |

The decision contract is `15_COMMANDS_AND_DRIVERS/TOOLING_DECISION_CONTRACT.md` in
the instance. Populate its handoff binding table from existing authoritative
records only. Do not write binding rows to obtain a desired output. NextExpectedAction
and Next Action Suggested never choose or authorize execution. Supported previews
are Director-bound atomic dispatch to exact Backend Developer or Frontend
Developer identities. Other roles/commands/direct lane invocations are BLOCKED.

Context File Integrity declares bounded artifact hashes; mismatch is BLOCKED.
LastContextDelta must be NONE in the supported subset; later deltas require a
Context Steward review that v1 cannot deterministically establish.
Recorded ACTIVE decisions and approval references are checked as pointers, not
authenticated signatures. The invocation preview explicitly retains semantic
scope, adequacy, guardrail and human authenticity checks for the receiving agent.
Any open/unresolved blocker or gap is conservatively refused when work-item
applicability is unknown; this does not change Stop Rule 15's scoped behavior.

## Failure and evidence semantics

- Exit 0: output without a failed check, not readiness or certification.
- Exit 1: invalid/missing data, failed diagnostic, unsupported or BLOCKED preview.
- Exit 2: argparse usage error on stderr.

JSON failures contain stable diagnostic IDs with explicit source references.
PASS/WARN/FAIL describe checks. UNVERIFIED and applicability outcomes
NOT_CHECKED/NOT_EXERCISED are never implicit passes. Doctor checks required
inventory, the 21-field schema, enum/version/date values, active reference/binding
and CP-C01–06/09–11 where mechanically available. CP-C07 activity history and
semantic CP-C08 routing authorization are not certified. Templates and legitimate
instructional placeholders are retained; required live fields are populated at
scaffold completion. Doctor does not infer Lite module activation from absence.

Absolute artifact references, URLs, traversal and escaping symlinks fail. Each
artifact is limited to 2 MiB; references are bounded and never scan unrelated
roots. Evidence runs only rev-parse, status and branch queries, with optional
locks/fsmonitor/untracked cache disabled, submodule internals excluded and a
20-second timeout. No shell, hooks, fetch, commit, push, repairs or network calls.
No file contents, patches, credentials or raw process errors are dumped. Paths
and hashes themselves may be sensitive metadata; choose shared references carefully.

No hidden database/cache, no bytecode writes, no second control plane. Concurrent
writes and symlink races are not atomic. Git status size is not bounded; hashes
cover declared files only. Cross-platform absolute root output varies by OS.

## Distribution and evolution

MANIFEST.json names every shipped runtime/documentation file and its SHA256.
The source repository pins TOOLS to LF with .gitattributes so checkout newline
settings do not invalidate the distribution hashes.
supporting_modules/instance_inventory.json is a versioned structural inventory,
not a second state representation. New scaffolds execute the framework's narrow
copy/verifier; existing TOOLS targets are never overwritten automatically.

The sole implementations are supporting_modules/operator.py and state_reader.py.
Experimental entry paths in the development repository are compatibility shims.
Tests and the development distribution helper are not shipped to instances.
Changes require the existing Framework Maintainer process and explicit authorized
upgrade/backport for old instances. No command grants human approval, QA signoff,
release certification or action execution authority.
