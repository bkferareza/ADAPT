"""SC-05 synthetic structural maintenance; no ordinary execution authority.

plan(instance, scope) reads raw evidence and returns exact byte images (hex).
execute(instance, evidence_root, scope, proposed) applies that plan once only.
scope is explicit HUMAN_SUPERVISED maintenance intent, not authenticated human
approval. Production, retry, rollback and resume are deliberately unsupported.
Only Notes -> Blockers relocation is supported. Uncertain Markdown is refused.
"""
import copy
from datetime import datetime
import importlib.util
import json
import os
from pathlib import Path
import re
import uuid

_spec = importlib.util.spec_from_file_location(
    "structural_runtime", Path(__file__).with_name("recovery_runtime.py"))
runtime = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(runtime)
pre, op = runtime.pre, runtime.op
require = pre.require
EVIDENCE_ROOT = runtime.WORKSPACE / ".adapt-local/maintenance/fw0006-structural-repair"
SYNTHETIC_ROOT = EVIDENCE_ROOT / "synthetic"
OPERATION = "RELOCATE_MISPLACED_BLOCKER_ROW"
COLUMNS = ["BLK-ID", "Severity", "Title", "Description", "Blocked Item",
           "Raised By", "Raised Date", "Assigned To", "Status", "Resolution", "Resolved Date"]


def _checked(path):
    boundary = (runtime.ACCEPTANCE_ROOT if Path(path).absolute().is_relative_to(
        runtime.ACCEPTANCE_ROOT) else SYNTHETIC_ROOT)
    return runtime._checked(path, boundary)


def _snapshot(root):
    return {p.relative_to(root).as_posix(): pre.digest(_checked(p).read_bytes())
            for p in sorted(root.rglob("*")) if _checked(p).is_file()}


def _fields(line):
    fields = op.split_row(line)
    require(len(fields) == 11 and all(fields) and
            all("{{" not in f and "}}" not in f for f in fields),
            "ROW", "Incomplete eleven-column record")
    require(re.fullmatch(r"BLK-\d{3,}", fields[0]) and
            fields[1] in {"CRITICAL", "HIGH", "MEDIUM", "LOW"} and
            fields[8] in {"OPEN", "RESOLVED", "DEFERRED"}, "ROW", "Invalid record enums")
    datetime.fromisoformat(fields[6])
    empty = {"NONE", "—", "-"}
    if fields[8] == "OPEN":
        require(fields[9] in empty and fields[10] in empty,
                "ROW", "OPEN record contains resolution data")
    elif fields[8] == "RESOLVED":
        require(fields[9] not in empty, "ROW", "Missing resolution")
        datetime.fromisoformat(fields[10])
    return fields


def _repair(data, blocker):
    document = data.decode("utf-8-sig")
    require("```" not in document and "~~~" not in document,
            "STRUCTURE", "Fenced Markdown unsupported")
    # Mask comments without changing offsets/line counts. Examples are not rows.
    require(document.count("<!--") == document.count("-->"), "STRUCTURE", "Unclosed comment")
    visible = re.sub(r"<!--.*?-->", lambda m: re.sub(r"[^\r\n]", " ", m[0]), document, flags=re.S)
    raw_lines = data.splitlines(keepends=True)
    lines = visible.splitlines()
    require(len(raw_lines) == len(lines), "STRUCTURE", "Unsupported line boundaries")
    headings = [(i, line.strip()) for i, line in enumerate(lines) if re.match(r"^#{1,6} ", line)]
    blocks = [i for i, h in headings if h == "## Blockers"]
    require(len(blocks) == 1, "STRUCTURE", "Missing/ambiguous Blockers section")
    start = blocks[0]
    end = next((i for i, h in headings if i > start and re.match(r"^#{1,2} ", h)), len(lines))
    table_lines = [i for i in range(start + 1, end) if lines[i].strip()]
    require(len(table_lines) >= 2 and op.split_row(lines[table_lines[0]]) == COLUMNS,
            "SCHEMA", "Expected canonical eleven-column header")
    normalized = "\n".join(document.splitlines())
    existing = op.table(normalized, "Blockers", COLUMNS)
    ids = [r["BLK-ID"] for r in existing]
    require(len(ids) == len(set(ids)), "DUPLICATE", "Duplicate canonical IDs")
    for row in existing:
        _fields("| " + " | ".join(row[c] for c in COLUMNS) + " |")
    token = re.compile(r"(?<![\w-])" + re.escape(blocker) + r"(?![\w-])")
    # Only table-like records count; prose references remain unrelated content.
    candidates = [i for i, line in enumerate(lines)
                  if line.lstrip().startswith("|") and token.search(line)]
    matches = []
    for i in candidates:
        fields = _fields(lines[i])
        require(fields[0] == blocker, "AMBIGUOUS", "Requested ID occurs in another record")
        matches.append((i, fields))
    require(len(matches) == 1, "DUPLICATE", "Expected exactly one requested blocker record")
    source, fields = matches[0]
    if start < source < end:
        require(blocker in ids, "STRUCTURE", "Canonical row not parsed")
        return data, fields, source, source
    owner = next((h for i, h in reversed(headings) if i < source), None)
    require(owner == "## Notes" and sum(h == "## Notes" for _, h in headings) == 1,
            "SECTION", "Only unambiguous Notes placement is repairable")
    require(blocker not in ids, "DUPLICATE", "Already present in Blockers")
    require(raw_lines[source].endswith(b"\n"), "STRUCTURE", "Unterminated row unsupported")
    destination = table_lines[1] + 1
    require(raw_lines[destination - 1].endswith(b"\n"), "STRUCTURE", "Unterminated separator")
    after = b"".join(raw_lines[:destination] + [raw_lines[source]] +
                     raw_lines[destination:source] + raw_lines[source + 1:]) if source >= destination else None
    require(after is not None, "SECTION", "Notes must follow canonical Blockers")
    repaired = op.table("\n".join(after.decode("utf-8-sig").splitlines()), "Blockers", COLUMNS)
    require([r for r in repaired if r["BLK-ID"] == blocker] == [dict(zip(COLUMNS, fields))],
            "SCHEMA", "Proposed repair failed register validation")
    return after, fields, source, destination


def plan(instance, scope):
    """Read-only synthetic plan. Refusal raises; no CP/context/Director dependency."""
    root = _checked(instance)
    require(root.is_dir(), "TARGET", "Missing exact synthetic instance")
    require(set(scope) == {"governance", "human", "target", "path", "operation", "blocker", "before_sha256"}
            and scope["governance"] == "HUMAN_SUPERVISED" and op.resolved(scope["human"])
            and scope["human"] != "NONE" and scope["target"] == str(root)
            and scope["path"] == pre.BLOCKERS and scope["operation"] == OPERATION
            and re.fullmatch(r"BLK-\d{3,}", scope["blocker"]), "SCOPE", "Exact maintenance scope required")
    path = _checked(root / pre.BLOCKERS)
    require(path.stat().st_size <= op.MAX_BYTES, "LIMIT", "Register too large")
    before = path.read_bytes()
    require(pre.digest(before) == scope["before_sha256"], "BEFORE", "Changed before-image SHA256")
    after, fields, source, destination = _repair(before, scope["blocker"])
    body = {"status": "NO_REPAIR_REQUIRED" if before == after else "REPAIR_PLANNED",
            "scope": copy.deepcopy(scope), "before_image_hex": before.hex(), "after_image_hex": after.hex(),
            "before_sha256": pre.digest(before), "after_sha256": pre.digest(after),
            "fields": fields, "source_line": source + 1, "destination_line": destination + 1,
            "baseline": _snapshot(root), "operational_authority": False}
    return dict(body, plan_sha256=runtime.assembly.fingerprint(body))


def _checkpoint(event):
    """Internal fault injection seam; never an authorization override."""


def execute(instance, evidence_root, scope, proposed):
    """One bounded synthetic replacement, durable external evidence, then STOP.

    Ownership/evidence persist on success and failure: never retry the same root.
    A fresh separately authorized fixture is required for another experiment.
    """
    result = {"status": "REFUSED", "action": "STOP", "operational_authority": False}
    owned = False
    try:
        scope, proposed = copy.deepcopy(scope), copy.deepcopy(proposed)
        root, external = _checked(instance), _checked(evidence_root)
        require(external.is_dir() and not external.is_relative_to(root) and
                not root.is_relative_to(external), "BOUNDARY", "Disjoint external evidence required")
        ownership = _checked(root.parent / (root.name + ".structural.lock"))
        require(not ownership.exists(), "LOCK", "Existing ownership; no retry or resume")
        require(plan(root, scope) == proposed, "PLAN", "Changed or invalid repair plan")
        if proposed["status"] == "NO_REPAIR_REQUIRED":
            return dict(result, status="NO_REPAIR_REQUIRED")
        require(not ownership.is_relative_to(external), "BOUNDARY", "Ownership must be outside evidence")
        journal = _checked(external / "journal.jsonl")
        require(not journal.exists(), "HISTORY", "Evidence already exists")
        owner = {"target": str(root), "plan_sha256": proposed["plan_sha256"],
                 "execution_id": uuid.uuid4().hex, "journal": str(journal), "retry": "FORBIDDEN"}
        encoded_owner = runtime._encoded(owner)
        runtime._persist_new(ownership, encoded_owner)
        owned = True
        # Exact plan contains both original and proposed bytes and raw inventory.
        runtime._persist_new(_checked(external / "plan.json"), runtime._encoded(proposed))
        intent = runtime._encoded({"event": "BEFORE_WRITE_REVALIDATED", **owner,
                                   "before_sha256": proposed["before_sha256"],
                                   "after_sha256": proposed["after_sha256"]})
        runtime._persist_new(journal, intent)
        _checkpoint("after_intent")
        require(plan(root, scope) == proposed and ownership.read_bytes() == encoded_owner and
                journal.read_bytes() == intent, "CONFLICT", "Preconditions changed after durable intent")
        path = _checked(root / pre.BLOCKERS)
        temporary = _checked(path.with_name(path.name + "." + owner["execution_id"] + ".pending"))
        runtime._persist_new(temporary, bytes.fromhex(proposed["after_image_hex"]))
        _checkpoint("before_replace")
        expected = dict(proposed["baseline"])
        expected[temporary.relative_to(root).as_posix()] = proposed["after_sha256"]
        require(_snapshot(root) == expected and ownership.read_bytes() == encoded_owner and
                journal.read_bytes() == intent and
                _checked(external / "plan.json").read_bytes() == runtime._encoded(proposed),
                "CONFLICT", "Changed preconditions before replacement")
        _checked(path)
        os.replace(temporary, path)
        runtime._sync_directory(path.parent)
        _checkpoint("after_replace")
        expected.pop(temporary.relative_to(root).as_posix())
        expected[pre.BLOCKERS] = proposed["after_sha256"]
        require(_snapshot(root) == expected and path.read_bytes().hex() == proposed["after_image_hex"],
                "AFTER", "After-image or unrelated inventory mismatch")
        require(_repair(path.read_bytes(), scope["blocker"])[0] == path.read_bytes(),
                "SCHEMA", "Final structure invalid")
        require(journal.read_bytes() == intent, "JOURNAL", "Changed durable intent")
        with journal.open("ab") as stream:
            stream.write(runtime._encoded({"event": "SYNTHETIC_REPAIR_VALIDATED", **owner,
                                          "final_hashes": expected}))
            stream.flush()
            os.fsync(stream.fileno())
        return dict(result, status="SYNTHETIC_REPAIR_VALIDATED", journal=str(journal),
                    before_sha256=proposed["before_sha256"], after_sha256=proposed["after_sha256"])
    except (pre.Refusal, op.Problem, OSError, ValueError, KeyError, TypeError) as error:
        return dict(result, status="INTERRUPTED" if owned else "REFUSED", error=str(error),
                    continuation="STOP_REAUTHORIZE")


def audit(instance, evidence_root):
    """Read-only detection of partial/uncertain execution; never resumes."""
    result = {"status": "INTERRUPTED", "action": "STOP_REAUTHORIZE", "operational_authority": False}
    try:
        root, external = _checked(instance), _checked(evidence_root)
        proposed = json.loads(_checked(external / "plan.json").read_bytes())
        owner = json.loads(_checked(root.parent / (root.name + ".structural.lock")).read_bytes())
        data = _checked(external / "journal.jsonl").read_bytes()
        require(data.endswith(b"\n"), "JOURNAL", "Partial journal")
        records = [json.loads(line) for line in data.splitlines()]
        body = {k: v for k, v in proposed.items() if k != "plan_sha256"}
        require(runtime.assembly.fingerprint(body) == proposed["plan_sha256"] and
                owner["target"] == str(root) and owner["journal"] == str(external / "journal.jsonl") and
                owner["plan_sha256"] == proposed["plan_sha256"], "JOURNAL", "Identity mismatch")
        require(len(records) == 2 and records[0] == {"event": "BEFORE_WRITE_REVALIDATED", **owner,
                "before_sha256": proposed["before_sha256"], "after_sha256": proposed["after_sha256"]},
                "JOURNAL", "Missing/malformed completion")
        expected = dict(proposed["baseline"], **{pre.BLOCKERS: proposed["after_sha256"]})
        require(records[1] == {"event": "SYNTHETIC_REPAIR_VALIDATED", **owner, "final_hashes": expected}
                and _snapshot(root) == expected, "AFTER", "Completion/filesystem mismatch")
        after, fields, _, _ = _repair(bytes.fromhex(proposed["before_image_hex"]), proposed["scope"]["blocker"])
        require(pre.digest(after) == proposed["after_sha256"] and fields == proposed["fields"] and
                _checked(root / pre.BLOCKERS).read_bytes() == after, "PLAN", "Invalid repair bytes")
        return dict(result, status="SYNTHETIC_REPAIR_VALIDATED")
    except (pre.Refusal, op.Problem, OSError, ValueError, KeyError, TypeError) as error:
        return dict(result, error=str(error))
