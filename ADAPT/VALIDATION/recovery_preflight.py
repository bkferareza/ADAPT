"""Non-distributed FW-0006 offline prototype. No writer or operational authority.

API: validate(instance, evidence_root, packet) -> JSON-compatible findings.
packet is a dict with target, purpose, task, executor, inputs (canonical path,
sha256, class, reason, verified_at), evidence (name -> path/sha256), writes
(path, operation, fields, before_sha256, before, after), ids, completion,
failure_reason and freshness. Evidence paths are relative to an explicit external
directory. Evidence JSON records use the synthetic-v1 format exercised in the
focused tests; this is deliberately NOT a real approval/adoption wire format.

Only an internally consistent synthetic future installation can pass. Real human
authenticity, lawful release/adoption and concurrent-writer exclusion cannot be
established here. No installation override exists. Run CLI with python -B.
"""
import argparse
from datetime import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import stat
import sys

sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location(
    "recovery_existing_operator",
    Path(__file__).resolve().parents[1] / "TOOLS/supporting_modules/operator.py")
op = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(op)

PURPOSE = "RECOVERY_BOOTSTRAP_AUTHORIZATION"
GOVERNANCE = "00_FRAMEWORK/GOVERNANCE_RULES.md"
DIRECTOR = "02_DIRECTOR_LANE/DIRECTOR_IDENTITY.md"
VERSION_LOG = "01_SOURCE_TRUTH/SOURCE_TRUTH_VERSION_LOG.md"
INDEX = "10_CONTEXT_ECONOMY/CONTEXT_INDEX.md"
STALE = "10_CONTEXT_ECONOMY/STALE_CONTEXT_REGISTER.md"
BLOCKERS = "02_DIRECTOR_LANE/BLOCKER_REGISTER.md"
REQUIRED = {GOVERNANCE, DIRECTOR, VERSION_LOG, INDEX, STALE, BLOCKERS,
            op.CP, op.SCHEMA, "02_DIRECTOR_LANE/DECISION_LOG.md",
            "02_DIRECTOR_LANE/GAP_REGISTER.md",
            "02_DIRECTOR_LANE/WORKCELL_REGISTRY.md",
            "07_GUARDRAILS/SCOPE_GUARDRAIL.md",
            "07_GUARDRAILS/CONTEXT_GUARDRAIL.md",
            "10_CONTEXT_ECONOMY/CONTEXT_RULES.md",
            "08_TEMPLATES/CONTEXT_PACK_TEMPLATE.md",
            "08_TEMPLATES/CONTEXT_DELTA_TEMPLATE.md",
            "08_TEMPLATES/HANDOFF_TEMPLATE.md",
            "15_COMMANDS_AND_DRIVERS/MUTATION_PERMISSION_MATRIX.md"}
COMPLETION = {
    "pack_status": "DRAFT", "index_during": "STALE", "index_final": "ARCHIVED",
    "task_handoff": "NONE", "ordinary_context": "INVALID",
    "preserve_blockers_and_attempts": True, "consume_handoffs": False,
    "stop": True, "separate_blocker_resolution": True,
    "independent_current_context": True, "separate_operational_handback": True,
    "external_append_only_journal": True, "external_final_hash_manifest": True,
    "recheck_before_each_write": True, "exclude_concurrent_writers": True,
    "final_schema_and_reference_validation": True,
    "interruption": "PRESERVE_AND_STOP_REAUTHORIZE",
}


class Refusal(ValueError):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def require(condition, code, message):
    if not condition:
        raise Refusal(code, message)


def safe(root, reference):
    """Reuse bounded resolution, additionally reject aliases and all reparse paths."""
    require(isinstance(reference, str) and reference and
            not any(x in reference for x in ("\\", ":", "`")) and
            all(p not in {"", ".", ".."} for p in reference.split("/")),
            "PATH", "Expected normalized relative path")
    path = op.bounded(root, reference)
    current = root
    for part in reference.split("/"):
        current = current / part
        if current.exists() or current.is_symlink():
            info = current.lstat()
            require(not current.is_symlink() and
                    not getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT,
                    "PATH", "Symlink/reparse redirection is unsupported")
    return path


def raw(root, reference):
    path = safe(root, reference)
    require(path.is_file() and path.stat().st_size <= op.MAX_BYTES,
            "INPUT", "Missing or oversized input: " + reference)
    return path.read_bytes()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load_json(data):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, "AMBIGUOUS", "Duplicate JSON key")
            result[key] = value
        return result
    return json.loads(data, object_pairs_hook=unique)


def declared_ids(reference, document):
    """Primary artifact metadata only; embedded snapshots/references still issue IDs.

    A pack's HANDOFF_ID and a handoff's delta reference are not declarations of
    another artifact. Keep full-document reference scanning for allocation bounds.
    """
    key = ("CONTEXT_PACK_ID" if reference.startswith("10_CONTEXT_ECONOMY/CONTEXT_PACKS/") else
           "CONTEXT_DELTA_ID" if reference.startswith("10_CONTEXT_ECONOMY/CONTEXT_DELTAS/") else
           "HANDOFF_ID" if reference.startswith("06_HANDOFFS/") else None)
    if key is None:
        return []
    metadata = re.split(r"(?m)^## |^---[ \t]*$", "\n".join(document.splitlines()), maxsplit=1)[0]
    values = re.findall(r"^" + key + r":[ \t]*(.*?)[ \t]*$", metadata, re.M)
    kind = {"CONTEXT_PACK_ID": "CP", "CONTEXT_DELTA_ID": "CD", "HANDOFF_ID": "HO"}[key]
    require(len(values) <= 1 and all(re.fullmatch(kind + r"-\d+", value) for value in values),
            "IDS", "Conflicting or invalid primary metadata ID")
    return values


def validate(instance, evidence_root, packet):
    """Read files only; deterministic first refusal, with no implicit partial pass."""
    findings = []
    result = {"status": "INVALID_PREFLIGHT", "findings": findings,
              "operational_authority": False, "human_authenticity": "UNVERIFIED",
              "distribution": "NON_DISTRIBUTED_PROTOTYPE"}
    try:
        root = Path(instance).absolute()
        external = Path(evidence_root).absolute()
        require(root == root.resolve() and external == external.resolve() and
                root.is_dir() and external.is_dir() and
                not external.is_relative_to(root) and not root.is_relative_to(external),
                "ROOT", "Exact disjoint canonical/evidence roots required")
        target = packet["target"]
        raw(root, op.CP)
        values = op.state(root)
        require(target == {"root": str(root), "identity": values["ProjectName"]},
                "TARGET", "Incorrect instance binding")
        require(packet["purpose"] == PURPOSE and op.resolved(packet["task"]) and
                op.resolved(packet["executor"]), "PURPOSE", "Bound Purpose B task/executor required")
        # Version text alone never establishes installed capability.
        raw(root, GOVERNANCE)
        installed_version = op.headers(op.text(root, GOVERNANCE), ["VERSION"])["VERSION"]
        if installed_version != "ADAPT-FW-0007" or not {"installation", "release", "adoption"} <= packet["evidence"].keys():
            raise Refusal("CAPABILITY", "No supported effective FW-0007 installation/adoption evidence")

        evidence = {}
        evidence_paths = set()
        for name, ref in packet["evidence"].items():
            path = safe(external, ref["path"])
            require(str(path).casefold() not in evidence_paths, "ALIAS", "Evidence alias collision")
            evidence_paths.add(str(path).casefold())
            data = raw(external, ref["path"])
            require(digest(data) == ref["sha256"], "HASH", "Changed evidence: " + name)
            evidence[name] = load_json(data)
        install = evidence["installation"]
        if install.get("format") != "synthetic-v1" or install.get("synthetic") is not True:
            raise Refusal("CAPABILITY", "Real release/adoption authentication is unsupported")
        require(install["target"] == target and install["version"] == installed_version and
                install["capabilities"] == ["rule14-entry", "purpose-b-assembly"] and
                install["effective"] is True, "CAPABILITY", "Inapplicable installed capability")
        for name in ("release", "adoption"):
            record = evidence[name]
            require(record["synthetic"] is True and record["target"] == target and
                    record["version"] == installed_version and record["effective"] is True and
                    record["maintainer"] == install["maintainer"] and
                    install[name] == packet["evidence"][name],
                    "CAPABILITY", "Missing/mismatched release or adoption chain")
        contracts = {GOVERNANCE, op.SCHEMA,
                     "15_COMMANDS_AND_DRIVERS/MUTATION_PERMISSION_MATRIX.md"}
        require(set(install["contracts"]) == contracts, "CAPABILITY", "Incomplete installed contract bindings")
        for path, sha in install["contracts"].items():
            require(digest(raw(root, path)) == sha, "CAPABILITY", "Installed contract hash mismatch")
        findings.append(op.diagnostic("CAPABILITY", "PASS", "Synthetic installed capability chain only"))
        require({"maintainer", "director", "authorization"} <= evidence.keys(),
                "AUTHORITY", "Original Maintainer, Director and authorization references required")
        require("designation" in evidence, "DIRECTOR", "Original Director designation required")

        # Every required/current inventory artifact must have a raw byte binding.
        inputs = {}
        aliases = set()
        for item in packet["inputs"]:
            path = safe(root, item["path"])
            alias = str(path).casefold()
            require(alias not in aliases, "ALIAS", "Duplicate canonical input/alias")
            aliases.add(alias)
            data = raw(root, item["path"])
            require(digest(data) == item["sha256"], "HASH", "Changed canonical input: " + item["path"])
            require(item["class"] in {"CURRENT_CANONICAL", "HISTORICAL_RECOVERY"} and
                    op.resolved(item["reason"]), "INPUT", "Input class/reason required")
            require(datetime.fromisoformat(item["verified_at"].replace("Z", "+00:00")).tzinfo is not None,
                    "INPUT", "Timezone-qualified verification time required")
            inputs[item["path"]] = item
        inventory = set(REQUIRED)
        for folder in ("10_CONTEXT_ECONOMY", "06_HANDOFFS"):
            for path in safe(root, folder).rglob("*"):
                safe(root, path.relative_to(root).as_posix())
                if path.is_file():
                    inventory.add(path.relative_to(root).as_posix())
        require(inventory <= inputs.keys(), "INPUT", "Canonical prerequisite/inventory missing")
        require(all(inputs[p]["class"] == "CURRENT_CANONICAL" for p in REQUIRED),
                "INPUT", "Required current state cannot come from historical packs")
        checks = op.doctor(root)["diagnostics"]
        require(not any(c["status"] in {"FAIL", "UNVERIFIED"} for c in checks),
                "STATE", "Existing deterministic tooling rejects canonical state")
        source_rows = op.table(op.text(root, VERSION_LOG), "Version Log", ["Version", "Document Name", "Status"])
        active = [r for r in source_rows if r["Status"] == "ACTIVE"]
        require(len(active) == 1 and active[0]["Version"] == values["SourceTruthVersion"] and
                active[0]["Document Name"] in inputs and
                inputs[active[0]["Document Name"]]["class"] == "CURRENT_CANONICAL",
                "SOURCE", "Unique registered current source/hash required")
        findings.append(op.diagnostic("STATE_AND_INPUTS", "PASS", "Current state parsed by existing reader/doctor; registered source and inventory hashes match"))

        binding = {key: packet[key] for key in ("target", "purpose", "task", "executor", "writes", "ids", "completion")}
        for name, role in (("maintainer", "Human Framework Maintainer"),
                           ("director", "Human Director"), ("authorization", "Bound Authorization")):
            record = evidence[name]
            require(record["synthetic"] is True and record["role"] == role and
                    record["binding"] == binding and record["inputs"] == packet["inputs"] and
                    record["original_input"] is True and op.resolved(record["human"]),
                    "AUTHORITY", "Missing original authority/scope binding: " + name)
        maintainer, director, auth = (evidence[n] for n in ("maintainer", "director", "authorization"))
        require(maintainer["human"] == install["maintainer"] and
                auth["maintainer"] == maintainer["human"] and auth["director"] == director["human"] and
                auth["executor"] == packet["executor"] and auth["capacity"] == "recovery Context Steward" and
                auth["canonical_assembly_approved"] is True and auth["gates"] == maintainer["gates"] == director["gates"] and
                bool(auth["gates"]) and all(v == "SYNTHETIC_APPROVED" for v in auth["gates"].values()),
                "AUTHORITY", "Explicit assembly delegation and applicable gates required")
        designation = evidence["designation"]
        require(designation == {"synthetic": True, "target": target, "human": director["human"],
                                "role": "Human Director", "original_input": True} and
                op.headers(op.text(root, DIRECTOR), ["HUMAN_OWNER"])["HUMAN_OWNER"] == director["human"],
                "DIRECTOR", "Missing designated Director provenance")
        findings.append(op.diagnostic("SYNTHETIC_AUTHORITY", "PASS", "Original-input fixture records bind both humans, designation, executor, gates and exact assembly scope"))

        _writes(root, packet, inputs, inventory, values)
        findings.append(op.diagnostic("WRITE_PLAN", "PASS", "Closed six-path plan, expected before-images and unused proposed IDs; nothing reserved or written"))
        failure = evidence["failure"]
        blockers = op.table(op.text(root, BLOCKERS), "Blockers", ["BLK-ID", "Status"])
        require(values["Blocked"] == "YES" and failure["target"] == target and
                failure["state"] == values and op.resolved(packet["failure_reason"]) and
                failure["ordinary_context_unavailable"] == packet["failure_reason"] and
                failure["attempts"] and failure["retry_limit"] > 0 and
                len(failure["attempts"]) >= failure["retry_limit"] and
                all(a["result"] == "FAILED" and a["evidence"] in evidence for a in failure["attempts"]) and
                all(evidence[a["evidence"]].get("synthetic") is True and
                    op.resolved(evidence[a["evidence"]].get("raw_diagnostic", "")) for a in failure["attempts"]) and
                len({a["evidence"] for a in failure["attempts"]}) == len(failure["attempts"]) and
                failure["blockers"] == {r["BLK-ID"]: r["Status"] for r in blockers} and
                "OPEN" in failure["blockers"].values(),
                "RETRIES", "Current blockers and raw exhausted retry history must be preserved")
        findings.append(op.diagnostic("RETRIES", "PASS", "Recorded exhausted attempts and OPEN blockers preserved"))
        completion = packet["completion"]
        require(all(type(completion.get(k)) is type(v) and completion[k] == v for k, v in COMPLETION.items()) and
                completion["return_to"] == [director["human"], maintainer["human"]],
                "COMPLETION", "Missing completion/STOP/handback conditions")
        for key in ("journal", "manifest", "return_destination"):
            safe(external, completion[key])
        require(len({completion[k].casefold() for k in ("journal", "manifest", "return_destination")}) == 3 and
                all(not safe(external, completion[k]).exists() for k in ("journal", "manifest", "return_destination")),
                "COMPLETION", "External output paths must be distinct and unused")
        require(packet["freshness"] == "STALE_ORDINARY_INVALID_RECOVERY_EVIDENCE_ONLY",
                "FRESHNESS", "No override of ordinary context freshness is supported")
        findings.append(op.diagnostic("COMPLETION_AND_FRESHNESS", "PASS", "Recovery-only archival, external evidence return, STOP and separate ordinary handback required"))
        result["status"] = "VALID_SYNTHETIC_PREFLIGHT"
        findings.append(op.diagnostic("SYNTHETIC_ONLY", "PASS", "Fixture consistency only; no human authentication or recovery approval"))
        findings.append(op.diagnostic("RUNTIME_LIMITS", "NOT_CHECKED", "No write-time locks, output assembly/schema validation, freshness certification or operational handback"))
    except (Refusal, op.Problem, OSError, ValueError, KeyError, TypeError, AttributeError) as error:
        code = getattr(error, "code", "MALFORMED_OR_MISSING")
        if code == "CAPABILITY":
            result["status"] = "UNSUPPORTED_CAPABILITY"
        findings.append(op.diagnostic(code, "FAIL", str(error)))
    return result


def _writes(root, packet, inputs, inventory, values):
    ids = packet["ids"]
    require(set(ids) == {"CP", "CD", "HO", "SC"}, "IDS", "Four independent ID sequences required")
    definitions = {}
    issued = {kind: set() for kind in ids}
    for ref in sorted(inventory):
        if not ref.startswith(("10_CONTEXT_ECONOMY/", "06_HANDOFFS/")):
            continue
        body = re.sub(r"<!--.*?-->", "", raw(root, ref).decode("utf-8-sig"), flags=re.S)
        for kind, number in re.findall(r"\b(CP|CD|HO|SC)-(\d+)\b", body + "\n" + Path(ref).name):
            issued[kind].add(number)
        # File names are primary issuance records; SC rows have no individual files.
        declared = declared_ids(ref, body)
        stem = Path(ref).stem
        if re.fullmatch(r"(?:CP|CD|HO)-\d+", stem):
            require(not declared or declared == [stem], "IDS", "Conflicting artifact filename/header IDs")
            declared = [stem]
        if ref == STALE:
            declared += re.findall(r"^\|\s*(SC-\d+)\s*\|", body, re.M)
        if ref == INDEX:
            index_ids = re.findall(r"^\|\s*(CP-\d+)\s*\|", body, re.M)
            require(len(index_ids) == len(set(index_ids)), "IDS", "Duplicate context index issuance rows")
        for identifier in declared:
            require(identifier not in definitions, "IDS", "Duplicate issued ID")
            definitions[identifier] = ref
    for kind, identifier in ids.items():
        require(isinstance(identifier, str) and re.fullmatch(kind + r"-\d+", identifier), "IDS", "Malformed proposed ID")
        numbers = issued[kind]
        number = identifier.split("-")[1]
        maximum = max((int(n) for n in numbers), default=0)
        padding = {len(n) for n in numbers}
        require(len(padding) <= 1 and int(number) == maximum + 1 and
                (not padding or len(number) == max(next(iter(padding)), len(str(maximum + 1)))) ,
                "IDS", "ID must be next unused sequence with unambiguous local padding")
    creates = {f"10_CONTEXT_ECONOMY/CONTEXT_PACKS/{ids['CP']}.md",
               f"10_CONTEXT_ECONOMY/CONTEXT_DELTAS/{ids['CD']}.md",
               f"06_HANDOFFS/ACTIVE/{ids['HO']}.md"}
    surfaces = {INDEX: ("append_row", {"row"}), STALE: ("append_open_row", {"row"}),
                op.CP: ("set_fields", {"LastContextDelta", "LastAction", "Notes"})}
    writes = packet["writes"]
    require(len(writes) == 6 and {w["path"] for w in writes} == creates | surfaces.keys(),
            "WRITE_SCOPE", "Prototype requires one complete six-path assembly plan")
    for write in writes:
        ref = write["path"]
        path = safe(root, ref)
        if ref in creates:
            require(write["operation"] == "create" and write["fields"] == ["document"] and
                    write["before_sha256"] == "ABSENT" and write["before"] is None and
                    not path.exists() and write["after"] == {"document": "STAGED_AT_WRITER_TIME"},
                    "BEFORE", "New artifacts require ABSENT before-images; no overwrite")
            continue
        operation, fields = surfaces[ref]
        require(write["operation"] == operation and set(write["fields"]) == fields and
                len(write["fields"]) == len(fields) and set(write["after"]) == fields and
                ref in inputs and write["before_sha256"] == inputs[ref]["sha256"],
                "WRITE_SCOPE", "Unpermitted path, field, operation or before hash")
        if ref == op.CP:
            require(write["before"] == {k: values[k] for k in fields} and
                    write["after"]["LastContextDelta"] == ids["CD"] and
                    op.resolved(write["after"]["LastAction"]) and
                    write["after"]["Notes"].startswith(values["Notes"] + "\n"),
                    "BEFORE", "Trace-only before values and appended Notes required")
        else:
            require(write["before"] == raw(root, ref).decode("utf-8-sig"), "BEFORE", "Expected register before-image mismatch")
            row = write["after"]["row"]
            if ref == INDEX:
                require(row == {"id": ids["CP"], "during": "STALE", "final": "ARCHIVED",
                                "handoff": "NONE", "source": values["SourceTruthVersion"],
                                "notes": "RECOVERY ONLY; NO ORDINARY EXECUTION AUTHORITY"},
                        "WRITE_SCOPE", "Recovery-only index append required")
            else:
                require(row == {"id": ids["SC"], "status": "OPEN", "pack": ids["CP"]},
                        "WRITE_SCOPE", "Only fresh OPEN stale row supported")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", required=True)
    parser.add_argument("--evidence-root", required=True)
    parser.add_argument("--packet", required=True, help="Packet path relative to evidence root")
    args = parser.parse_args(argv)
    try:
        packet = load_json(raw(Path(args.evidence_root).resolve(), args.packet))
    except (ValueError, OSError) as error:
        print(json.dumps({"status": "INVALID_PREFLIGHT", "operational_authority": False,
                          "findings": [op.diagnostic("PACKET", "FAIL", str(error))]}))
        return 1
    result = validate(args.instance, args.evidence_root, packet)
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "VALID_SYNTHETIC_PREFLIGHT" else 1


if __name__ == "__main__":
    sys.exit(main())
