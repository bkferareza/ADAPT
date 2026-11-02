"""Bounded synthetic writer for FLC-005 development; never production authority.

execute(instance, evidence_root, packet, plan) consumes an unchanged staged plan.
Only fixtures below SYNTHETIC_ROOT are writable. Interrupted ownership is retained
indefinitely: this module has no resume, retry, rollback or lock override API.
audit(instance, journal, plan) independently checks durable records and bytes.

O_EXCL is the cross-process ownership primitive. fsync persists files; POSIX
directories are also fsynced. Windows stdlib cannot promise directory-entry
survival on power loss. No multi-file atomicity, hostile-OS exclusion, signed
journal authenticity, real human authentication or production durability claimed.
"""
import copy
from datetime import datetime, timezone
import importlib.util
import json
import os
from pathlib import Path
import socket
import stat
import uuid

_spec = importlib.util.spec_from_file_location(
    "runtime_assembly", Path(__file__).with_name("recovery_assembly.py"))
assembly = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(assembly)
pre, op = assembly.pre, assembly.op
require = pre.require
WORKSPACE = Path(__file__).resolve().parents[2]
MAINTENANCE = WORKSPACE / ".adapt-local/maintenance/fw0006-runtime"
SYNTHETIC_ROOT = MAINTENANCE / "synthetic"
ACCEPTANCE_ROOT = WORKSPACE / ".adapt-local/maintenance/fw0006-end-to-end/synthetic"
LOCK_ROOT = MAINTENANCE / "locks"


def _checked(path, boundary):
    path = Path(path).absolute()
    # A second fixed disposable boundary shared with the structural writer.
    # No caller flag or production target override; all checks below still run.
    if boundary == SYNTHETIC_ROOT and path.is_relative_to(ACCEPTANCE_ROOT):
        boundary = ACCEPTANCE_ROOT
    require(path == path.resolve() and path != boundary and
            path.is_relative_to(boundary), "BOUNDARY", "Outside fixed synthetic boundary")
    # Check ancestors too: resolve() alone need not expose every reparse type.
    for entry in (path, *path.parents):
        if entry.exists() or entry.is_symlink():
            info = entry.lstat()
            require(not entry.is_symlink() and not getattr(info, "st_file_attributes", 0) &
                    stat.FILE_ATTRIBUTE_REPARSE_POINT, "PATH", "Symlink/reparse point unsupported")
            require(not entry.is_file() or info.st_nlink == 1,
                    "ALIAS", "Hard-linked files unsupported")
    require("adapt-dev" not in [p.casefold() for p in path.parts],
            "BOUNDARY", "Protected instance target forbidden")
    return path


def _file(root, ref):
    path = pre.safe(root, ref)
    return _checked(path, SYNTHETIC_ROOT)


def _snapshot(root):
    result = {}
    aliases = set()
    for path in sorted(root.rglob("*")):
        _checked(path, SYNTHETIC_ROOT)
        if path.is_file():
            ref = path.relative_to(root).as_posix()
            require(ref.casefold() not in aliases, "ALIAS", "Canonical path alias")
            aliases.add(ref.casefold())
            result[ref] = pre.digest(path.read_bytes())
    return result


def _observed(root, expected):
    actual = _snapshot(root)
    return {**{p: "ABSENT" for p in expected}, **actual}


def _sync_directory(path):
    if os.name != "nt":
        descriptor = os.open(path, os.O_RDONLY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)


def _persist_new(path, data):
    # Exclusive create preserves any existing artifact, including failed runs.
    with path.open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    _sync_directory(path.parent)


def _encoded(value):
    return (assembly.canonical(value) + "\n").encode("utf-8")


def lock_path(instance):
    root = _checked(instance, SYNTHETIC_ROOT)
    return LOCK_ROOT / (pre.digest(str(root).casefold().encode()) + ".lock")


def _checkpoint(event, sequence):
    """Internal fault-injection seam; no execution mode or authorization bypass."""


def _plan_check(plan):
    require(assembly.fingerprint({k: v for k, v in plan.items() if k != "plan_sha256"}) ==
            plan["plan_sha256"], "PLAN", "Changed plan identity")


def _source_check(external, plan):
    for item in plan["evidence_manifest"]:
        require(pre.digest(_file(external, item["path"]).read_bytes()) == item["sha256"],
                "EVIDENCE", "Changed authority/source evidence")


def _final(root, plan, baseline, archival=False):
    expected = dict(baseline)
    for write in plan["write_set"]:
        expected[write["path"]] = write["proposed_final_sha256"]
    if archival:
        expected[pre.INDEX] = plan["operations"][1]["after_sha256"]
    require(_snapshot(root) == expected, "FINAL", "Final canonical inventory/hash mismatch")
    # Exact validated bytes already bind every template section and reference.
    # Parse the actual files too, using the existing deterministic readers.
    for kind in ("CP", "CD", "HO"):
        write = next(w for w in plan["write_set"] if Path(w["path"]).stem == plan["ids"][kind])
        text = _file(root, write["path"]).read_text(encoding="utf-8-sig")
        require(op.headers(text, ["STATUS"])["STATUS"] == "DRAFT", "SCHEMA", "Expected DRAFT")
        for heading in assembly.SECTIONS[kind]:
            op.section(text, heading)
        if kind == "CP":
            require(op.headers(text, ["HANDOFF_ID"])["HANDOFF_ID"] == "NONE", "REFERENCES", "Ordinary handoff activation")
        if kind == "CD":
            require(op.headers(text, ["PRECEDING_CONTEXT_PACK_ID"])["PRECEDING_CONTEXT_PACK_ID"] ==
                    plan["ids"]["CP"], "REFERENCES", "Incorrect delta CP")
        if kind == "HO":
            require(op.headers(text, ["CONTEXT_PACK_REFERENCE"])["CONTEXT_PACK_REFERENCE"] == plan["ids"]["CP"] and
                    "CONTEXT_DELTA_ID: " + plan["ids"]["CD"] in op.section(text, "Context Delta Reference"),
                    "REFERENCES", "Incorrect completion references")
    rows = op.table(op.text(root, pre.INDEX), "Index", ["CP-ID", "Status"])
    require(rows[-1]["CP-ID"] == plan["ids"]["CP"] and rows[-1]["Status"] ==
            ("STALE" if archival else "ARCHIVED"), "LIFECYCLE", "Invalid recovery lifecycle")
    rows = op.table(op.text(root, pre.STALE), "Register", ["SC-ID", "Status"])
    require(rows[-1]["SC-ID"] == plan["ids"]["SC"] and rows[-1]["Status"] == "OPEN",
            "LIFECYCLE", "Stale finding closed")
    require(op.state(root)["Blocked"] == "YES", "STATE", "Blocker state changed")
    diagnostics = op.doctor(root)["diagnostics"]
    require(not any(d["status"] in {"FAIL", "UNVERIFIED"} for d in diagnostics),
            "SCHEMA", "Final deterministic doctor refused")
    return {"schemas_and_references": "PASS", "exact_inventory_and_hashes": "PASS",
            "source_blockers_history_unrelated_handoffs": "UNCHANGED",
            "ordinary_context_activation": False, "doctor": diagnostics}


def audit(instance, journal, plan):
    """Read-only audit. Even a consistent partial prefix never authorizes resume."""
    result = {"status": "INVALID_JOURNAL", "action": "STOP_REAUTHORIZE",
              "automatic_resume": False, "operational_authority": False}
    try:
        root = _checked(instance, SYNTHETIC_ROOT)
        path = _checked(journal, SYNTHETIC_ROOT)
        _plan_check(plan)
        evidence_root = Path(plan["write_set"][0]["authorization"]["root"])
        require(path == _file(evidence_root, plan["journal"]["path"]), "JOURNAL", "Wrong journal path")
        _source_check(evidence_root, plan)
        data = path.read_bytes()
        require(data.endswith(b"\n"), "JOURNAL", "Truncated journal")
        records = [pre.load_json(line) for line in data.splitlines()]
        require(records and records[0]["event"] == "PLAN_VALIDATED", "JOURNAL", "Missing start")
        first = records[0]
        require(first["target"] == str(root) and first["input_manifest"] == plan["input_manifest"] and
                first["evidence_manifest"] == plan["evidence_manifest"] and first["ids"] == plan["ids"],
                "JOURNAL", "Incorrect source manifest/target")
        previous = plan["plan_sha256"]
        completed, pending, terminal = [], None, None
        expected = dict(first["baseline"])
        for w in plan["write_set"]:
            require(expected.get(w["path"], "ABSENT") == w["expected_original_sha256"],
                    "JOURNAL", "Baseline before-image mismatch")
            expected.setdefault(w["path"], "ABSENT")
        for item in plan["input_manifest"]:
            require(expected[item["path"]] == item["sha256"], "JOURNAL", "Baseline input mismatch")
        for index, record in enumerate(records):
            body = {k: v for k, v in record.items() if k != "record_sha256"}
            require(record["record_sha256"] == assembly.fingerprint(body) and record["journal_sequence"] == index and
                    record["previous_sha256"] == previous and record["plan_sha256"] == plan["plan_sha256"] and
                    record["execution_id"] == first["execution_id"] and terminal is None,
                    "JOURNAL", "Broken journal linkage/order/identity")
            previous = record["record_sha256"]
            event = record["event"]
            if index == 0:
                continue
            if event in {"BEFORE_WRITE_REVALIDATED", "WRITE_COMPLETED"}:
                require(len(completed) < len(plan["operations"]), "JOURNAL", "Extra operation")
                operation = plan["operations"][len(completed)]
                for key in ("sequence", "path", "before_sha256", "after_sha256"):
                    require(record[key] == operation[key], "JOURNAL", "Operation binding mismatch")
                if event == "BEFORE_WRITE_REVALIDATED":
                    require(pending is None and record["observed_before_sha256"] == operation["before_sha256"],
                            "JOURNAL", "Invalid intent")
                    pending = operation
                else:
                    require(pending == operation and record["observed_after_sha256"] == operation["after_sha256"],
                            "JOURNAL", "Missing intent or invalid completion")
                    completed.append(record["assembly_record"])
                    expected[operation["path"]] = operation["after_sha256"]
                    pending = None
            elif event == "FINAL_VALIDATED":
                require(pending is None and len(completed) == len(plan["operations"]) and
                        record["final_hashes"] == _snapshot(root), "JOURNAL", "Premature final event")
                for key, ref in (("manifest_sha256", plan["return"]["manifest"]),
                                 ("return_sha256", plan["return"]["destination"])):
                    require(pre.digest(_file(evidence_root, ref).read_bytes()) == record[key],
                            "JOURNAL", "Changed external completion evidence")
                terminal = event
            elif event == "INTERRUPTED_ON_ANY_INCOMPLETE_OR_INVALID_STATE":
                terminal = event
            else:
                require(False, "JOURNAL", "Unsupported event")
        observed = _observed(root, expected)
        projection = {p: observed[p] for p in {i["path"] for i in plan["input_manifest"]} |
                      {w["path"] for w in plan["write_set"]}}
        checked = assembly.inspect_journal(plan, completed, projection)
        agreement = observed == expected and checked["status"] != "REFUSED"
        result.update(status=("SYNTHETIC_EXECUTION_VALIDATED" if terminal == "FINAL_VALIDATED" and agreement
                              else "INTERRUPTED"), filesystem_agreement=agreement,
                      completed_operations=len(completed), pending_operation=pending,
                      assembly_inspection=checked, final_hashes=_snapshot(root),
                      execution_id=first["execution_id"], journal_head=previous)
        if terminal == "FINAL_VALIDATED":
            require(agreement, "JOURNAL", "Recorded and observed final bytes differ")
            _final(root, plan, first["baseline"])
    except (pre.Refusal, op.Problem, OSError, ValueError, KeyError, TypeError, StopIteration) as error:
        result.update(status="INVALID_JOURNAL", error=str(error))
    return result


def execute(instance, evidence_root, packet, plan):
    """Execute once under synthetic ownership; return evidence and STOP."""
    result = {"status": "REFUSED", "operational_authority": False,
              "real_execution": "UNAUTHORIZED", "action": "STOP"}
    locked, journal_ready, append = False, False, None
    # Freeze caller-owned structures; never silently replace a changed plan.
    packet, plan = copy.deepcopy(packet), copy.deepcopy(plan)
    try:
        root = _checked(instance, SYNTHETIC_ROOT)
        external = _checked(evidence_root, SYNTHETIC_ROOT)
        require(root.is_dir() and external.is_dir() and not external.is_relative_to(root) and
                not root.is_relative_to(external), "BOUNDARY", "Disjoint fixture roots required")
        _snapshot(root)
        _snapshot(external)
        require(not lock_path(root).exists(), "LOCK", "Existing ownership; never steal or resume")
        _plan_check(plan)
        require(assembly.validate_plan(root, external, packet, plan)["valid"], "PLAN", "Staged plan no longer valid")
        require(assembly.allocate_ids(root, external, packet) == plan["ids"], "IDS", "IDs consumed")
        journal = _file(external, plan["journal"]["path"])
        manifest = _file(external, plan["return"]["manifest"])
        destination = _file(external, plan["return"]["destination"])
        for output in (journal, manifest, destination):
            require(not output.exists(), "HISTORY", "Existing execution evidence; no reuse")
            output.parent.mkdir(parents=True, exist_ok=True)
            _checked(output, SYNTHETIC_ROOT)
        LOCK_ROOT.mkdir(parents=True, exist_ok=True)
        ownership = lock_path(root)
        _checked(ownership, MAINTENANCE)
        execution_id = uuid.uuid4().hex
        owner = {"execution_id": execution_id, "pid": os.getpid(), "host": socket.gethostname(),
                 "acquired_at": datetime.now(timezone.utc).isoformat(),
                 "target": str(root), "plan_sha256": plan["plan_sha256"], "journal": str(journal),
                 "issued_ids": plan["ids"], "stale_policy": "NEVER_STEAL"}
        # Atomic create is the lock. Do not delete it on acquisition failure.
        descriptor = os.open(ownership, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        locked = True
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(_encoded(owner))
            stream.flush()
            os.fsync(stream.fileno())
        _sync_directory(ownership.parent)
        require(assembly.validate_plan(root, external, packet, plan)["valid"], "PLAN", "State changed before ownership")
        baseline = _snapshot(root)
        expected = dict(baseline)
        for w in plan["write_set"]:
            expected.setdefault(w["path"], "ABSENT")
        chain = {"head": plan["plan_sha256"], "sequence": 0, "bytes": b""}

        def append(event, **fields):
            body = {"event": event, "execution_id": execution_id, "plan_sha256": plan["plan_sha256"],
                    "journal_sequence": chain["sequence"], "previous_sha256": chain["head"],
                    "recorded_at": datetime.now(timezone.utc).isoformat(), **fields}
            record = {**body, "record_sha256": assembly.fingerprint(body)}
            require(_file(external, plan["journal"]["path"]).read_bytes() == chain["bytes"],
                    "JOURNAL", "Durable journal changed before append")
            encoded = _encoded(record)
            with journal.open("r+b") as stream:
                stream.seek(0, os.SEEK_END)
                stream.write(encoded)
                stream.flush()
                os.fsync(stream.fileno())
            chain.update(head=record["record_sha256"], sequence=chain["sequence"] + 1)
            chain["bytes"] += encoded

        _persist_new(journal, b"")
        journal_ready = True
        append("PLAN_VALIDATED", target=str(root), baseline=baseline, ids=plan["ids"],
               input_manifest=plan["input_manifest"], evidence_manifest=plan["evidence_manifest"], owner=owner)
        completed, prior = [], plan["plan_sha256"]
        for operation in plan["operations"]:
            sequence, ref = operation["sequence"], operation["path"]
            _checkpoint("before_intent", sequence)
            _source_check(external, plan)
            require(pre.load_json(ownership.read_bytes()) == owner, "LOCK", "Ownership changed")
            require(_observed(root, expected) == expected, "CONFLICT", "Canonical state changed")
            path = _file(root, ref)
            before = pre.digest(path.read_bytes()) if path.exists() else "ABSENT"
            require(before == operation["before_sha256"], "BEFORE", "Write-time before-image changed")
            if sequence == len(plan["operations"]):
                _final(root, plan, baseline, archival=True)
            fields = {k: operation[k] for k in ("sequence", "path", "before_sha256", "after_sha256")}
            append("BEFORE_WRITE_REVALIDATED", **fields, observed_before_sha256=before)
            _checkpoint("after_intent", sequence)
            # Repeat immediately after durable intent, before changing any bytes.
            _source_check(external, plan)
            require(_observed(root, expected) == expected and pre.load_json(ownership.read_bytes()) == owner,
                    "CONFLICT", "State/ownership changed after intent")
            require(_file(external, plan["journal"]["path"]).read_bytes() == chain["bytes"],
                    "JOURNAL", "Journal changed after intent")
            path = _file(root, ref)
            data = bytes.fromhex(operation["after_image_hex"])
            require(pre.digest(data) == operation["after_sha256"], "PLAN", "After bytes mismatch")
            if before == "ABSENT":
                _persist_new(path, data)
            else:
                temporary = path.with_name(path.name + "." + execution_id + ".pending")
                _persist_new(temporary, data)
                _file(root, ref)
                require(pre.digest(path.read_bytes()) == before, "BEFORE", "Changed before replacement")
                os.replace(temporary, path)
                _sync_directory(path.parent)
            _checkpoint("after_mutation", sequence)
            actual = pre.digest(_file(root, ref).read_bytes())
            require(actual == operation["after_sha256"], "AFTER", "Written bytes mismatch")
            body = {"plan_sha256": plan["plan_sha256"], "previous_sha256": prior,
                    **fields, "event": "WRITE_COMPLETED"}
            record = {**body, "record_sha256": assembly.fingerprint(body)}
            append("WRITE_COMPLETED", **fields, observed_after_sha256=actual, assembly_record=record)
            completed.append(record)
            prior = record["record_sha256"]
            expected[ref] = actual
            _checkpoint("after_completion", sequence)
        _source_check(external, plan)
        validation = _final(root, plan, baseline)
        observed = {p: expected[p] for p in {i["path"] for i in plan["input_manifest"]} |
                    {w["path"] for w in plan["write_set"]}}
        require(assembly.inspect_journal(plan, completed, observed)["status"] == "REPRESENTED_COMPLETE",
                "JOURNAL", "Existing journal auditor refused")
        # Prepare evidence first. A failure publishing evidence cannot yield success.
        result.update(status="SYNTHETIC_EXECUTION_VALIDATED", execution_id=execution_id,
                      plan_sha256=plan["plan_sha256"], validation=validation,
                      final_hashes=_snapshot(root), mutation_inventory=plan["write_set"],
                      journal=str(journal), lock_owner=owner,
                      durability="FILE_FSYNC; POSIX_DIRECTORY_FSYNC; WINDOWS_DIRECTORY_DURABILITY_UNPROVEN")
        manifest_evidence = {**result, "status": "SYNTHETIC_VALIDATION_EVIDENCE",
                             "completion_condition": "Valid only with FINAL_VALIDATED journal and passing audit"}
        _persist_new(manifest, _encoded(manifest_evidence))
        _persist_new(destination, _encoded({"execution_id": execution_id, "manifest": str(manifest),
                                          "return_to": plan["return"]["to"], "action": "STOP",
                                          "real_execution": "UNAUTHORIZED"}))
        append("FINAL_VALIDATED", final_hashes=result["final_hashes"], validation=validation,
               manifest_sha256=pre.digest(manifest.read_bytes()), return_sha256=pre.digest(destination.read_bytes()))
        checked = audit(root, journal, plan)
        require(checked["status"] == "SYNTHETIC_EXECUTION_VALIDATED", "JOURNAL", "Independent audit refused")
        result["audit"] = checked
        ownership.unlink()
        _sync_directory(ownership.parent)
        return result
    except Exception as error:
        result.update(status="INTERRUPTED" if locked else "REFUSED", error=str(error),
                      error_type=type(error).__name__, action="PRESERVE_AND_STOP_REAUTHORIZE")
        if locked and journal_ready:
            try:
                append("INTERRUPTED_ON_ANY_INCOMPLETE_OR_INVALID_STATE", error=str(error),
                       error_type=type(error).__name__, observed=_snapshot(root))
            except Exception as journal_error:
                result["journal_error"] = str(journal_error)
        return result
