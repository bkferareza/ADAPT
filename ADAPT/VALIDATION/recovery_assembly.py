"""Offline FW-0006 synthetic staging prototype; no filesystem writer.

stage(instance, evidence_root, packet) invokes preflight FIRST and returns an
in-memory JSON-compatible STAGED/NOT_APPLIED plan or a refusal. validate_plan
rebuilds the plan from original evidence and compares every byte/field.

Additional evidence `assembly` is a synthetic-v1 recovery-purpose selection and
budget record. All three original authority fixture records must bind its exact
path/hash as `assembly`. This extends, but does not change, preflight's format.
Selection uses canonical packet input paths; required prerequisites are selected
automatically. Optional history must be explicitly classified HISTORICAL_RECOVERY.
The declared XL byte ceiling is an additional synthetic task budget, not a new
framework tier. No real approval, release, adoption, locking or writes supported.
"""
import importlib.util
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location(
    "assembly_preflight", Path(__file__).with_name("recovery_preflight.py"))
pre = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pre)
op = pre.op
require = pre.require
LANE = "recovery Context Steward"
BUDGET = "15_COMMANDS_AND_DRIVERS/CONTEXT_BUDGET_POLICY.md"
TEMPLATES = {
    "CP": "08_TEMPLATES/CONTEXT_PACK_TEMPLATE.md",
    "CD": "08_TEMPLATES/CONTEXT_DELTA_TEMPLATE.md",
    "HO": "08_TEMPLATES/HANDOFF_TEMPLATE.md",
}
SECTIONS = {
    "CP": ("Scope Declaration", "Active Handoff Summary", "Source Truth Artifacts Included",
           "Relevant Decisions", "Relevant Contracts", "Gaps and Blockers",
           "Stale or Excluded Items", "Known Limitations", "Context Steward Note"),
    "CD": ("State Changes", "New Artifacts Produced", "Superseded Items",
           "Downstream Impact", "Context Steward Note"),
    "HO": ("Work Completed", "Evidence Attached", "Contracts Impacted", "Open Items",
           "Risks", "Blockers", "Next Action Suggested", "Context Delta Reference",
           "Placement Note"),
}


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"))


def fingerprint(value):
    return pre.digest(canonical(value).encode("utf-8"))


def cell(value):
    return str(value).replace("\r\n", "\n").replace("\r", "\n").replace(
        "\\", "&#92;").replace("|", "&#124;").replace("\n", "<br>")


def table(columns, rows):
    return "\n".join(["| " + " | ".join(columns) + " |",
                      "| " + " | ".join("---" for _ in columns) + " |"] +
                     ["| " + " | ".join(cell(v) for v in row) + " |" for row in rows])


def allocate_ids(instance, evidence_root, packet):
    """Read-only candidate IDs. Includes all inventory bytes/names and bound history.

    Callers must bind these candidates into authorization, run stage, and recheck
    at future write time. Merely referencing an ID consumes its numeric sequence;
    primary declarations must still be unique (index references are not definitions).
    """
    root, external = Path(instance).absolute(), Path(evidence_root).absolute()
    issued = {k: set() for k in ("CP", "CD", "SC", "HO")}
    definitions = set()
    for folder in ("10_CONTEXT_ECONOMY", "06_HANDOFFS"):
        for path in sorted(pre.safe(root, folder).rglob("*")):
            ref = path.relative_to(root).as_posix()
            pre.safe(root, ref)
            if not path.is_file():
                continue
            body = re.sub(r"<!--.*?-->", "", pre.raw(root, ref).decode("utf-8-sig"), flags=re.S)
            _issued(issued, body + "\n" + path.name)
            declared = pre.declared_ids(ref, body)
            if re.fullmatch(r"(?:CP|CD|HO)-\d+", path.stem):
                require(not declared or declared == [path.stem], "IDS", "Filename/header conflict")
                declared = [path.stem]
            if ref == pre.STALE:
                declared += re.findall(r"^\|\s*(SC-\d+)\s*\|", body, re.M)
            if ref == pre.INDEX:
                rows = re.findall(r"^\|\s*(CP-\d+)\s*\|", body, re.M)
                require(len(rows) == len(set(rows)), "IDS", "Duplicate index issuance")
            for identifier in declared:
                # Numeric aliases such as HO-01 and HO-001 are also collisions.
                kind, number = identifier.split("-")
                key = (kind, int(number))
                require(key not in definitions, "IDS", "Duplicate historical definition")
                definitions.add(key)
    external_definitions = set()
    for name, reference in sorted(packet["evidence"].items()):
        data = pre.raw(external, reference["path"])
        require(pre.digest(data) == reference["sha256"], "HASH", "Changed ID history evidence")
        # Bound interrupted history has its own target and synthetic provenance.
        if name.startswith("id_history"):
            record = pre.load_json(data)
            require(record["synthetic"] is True and record["target"] == packet["target"] and
                    record["purpose"] == pre.PURPOSE and
                    isinstance(record["issued_ids"], list), "IDS", "Unbound ID history")
            for identifier in record["issued_ids"]:
                require(re.fullmatch(r"(?:CP|CD|SC|HO)-\d+", identifier), "IDS", "Invalid history ID")
                kind, number = identifier.split("-")
                key = (kind, int(number))
                require(key not in external_definitions, "IDS", "Duplicate external issuance record")
                external_definitions.add(key)
                _issued(issued, identifier)
    result = {}
    for kind, numbers in issued.items():
        widths = {len(n) for n in numbers}
        require(len(widths) <= 1, "IDS", "Ambiguous sequence padding")
        number = max((int(n) for n in numbers), default=0) + 1
        result[kind] = kind + "-" + str(number).zfill(next(iter(widths), 3))
    return result


def _issued(issued, text):
    for kind, number in re.findall(r"\b(CP|CD|SC|HO)-(\d+)\b", text):
        issued[kind].add(number)


def _record(external, packet, name):
    ref = packet["evidence"][name]
    data = pre.raw(external, ref["path"])
    require(pre.digest(data) == ref["sha256"], "HASH", "Changed evidence: " + name)
    return pre.load_json(data)


def _document(root, kind, headers, bodies):
    template = pre.raw(root, TEMPLATES[kind]).decode("utf-8-sig").replace("\r\n", "\n")
    expected = list(SECTIONS[kind])
    require(re.findall(r"^## (.+)$", template, re.M) == expected,
            "SCHEMA", "Unsupported canonical template sections")
    prefix = template.split("\n---", 1)[0]
    keys = re.findall(r"^([A-Z_ /]+):", prefix, re.M)
    require(len(keys) == len(set(keys)) and set(keys) == set(headers),
            "SCHEMA", "Unsupported canonical template headers")
    output = template.splitlines()[0] + "\n\n"
    output += "\n".join(k + ": " + str(headers[k]) for k in keys)
    for heading in expected:
        output += "\n\n---\n\n## " + heading + "\n\n" + bodies[heading]
    op.headers(output, list(headers))
    for heading in expected:
        op.section(output, heading)
    return output + "\n"


def _append(root, ref, heading, columns, row):
    original = pre.raw(root, ref)
    text = original.decode("utf-8-sig")
    op.table(text, heading, columns)
    # Preserve existing bytes, comments and all other rows/sections exactly.
    start = re.search(r"^## " + re.escape(heading) + r"\s*$", text, re.M).end()
    following = re.search(r"^#{1,2} ", text[start:], re.M)
    end = start + following.start() if following else len(text)
    # A valid table may have trailing historical prose. Append to its row block,
    # preserving the prose rather than creating a second interrupted row block.
    visible = re.sub(r"<!--.*?-->", lambda match: re.sub(r"[^\r\n]", " ", match[0]),
                     text[start:end], flags=re.S)
    table_lines = list(re.finditer(r"(?m)^[ \t]*\|[^\r\n]*(?:\r?\n|$)", visible))
    if table_lines and visible[table_lines[-1].end():].strip():
        end = start + table_lines[-1].end()
    offset = len(text[:end].encode("utf-8")) + (3 if original.startswith(b"\xef\xbb\xbf") else 0)
    newline = b"\r\n" if b"\r\n" in original else b"\n"
    addition = newline + ("| " + " | ".join(cell(v) for v in row) + " |").encode("utf-8") + newline
    final = original[:offset] + addition + original[offset:]
    rows = op.table(final.decode("utf-8-sig"), heading, columns)
    require(rows[-1] == dict(zip(columns, (cell(v) for v in row))), "SCHEMA", "Register append mismatch")
    return final


def _trace(root, write):
    data = pre.raw(root, op.CP)
    for field in write["fields"]:
        value = write["after"][field]
        # Preflight authorizes logical appended Notes; Markdown stores one cell.
        # Preserve literal pipes using Markdown escaping understood by State Reader.
        value = re.sub(r"(?<!\\)\|", r"\\|", value.replace("\r", "").replace("\n", "<br>"))
        pattern = rb"(?m)^(\|[ \t]*" + field.encode() + rb"[ \t]*\|)[^\r\n]*(\|[ \t]*\r?)$"
        data, count = re.subn(pattern, lambda m: m[1] + b" " + value.encode("utf-8") + b" " + m[2], data)
        require(count == 1, "SCHEMA", "Ambiguous control-plane trace row")
    before = op.state(root)
    parsed = {}
    for line in op.section(data.decode("utf-8-sig"), "Control Plane State").splitlines():
        if line.startswith("|"):
            key, value = op.reader.cells(line)
            if key in op.reader.FIELDS:
                require(key not in parsed, "SCHEMA", "Duplicate control-plane row")
                parsed[key] = value
    require(set(parsed) == set(before), "SCHEMA", "Missing control-plane fields")
    require(all(parsed[k] == before[k] for k in before if k not in write["fields"]),
            "WRITE_SCOPE", "Protected control-plane changes")
    return data


def _build(root, external, packet, *, operational=False, authority_reference=None):
    # Rendering only. Operational callers must run their independent eligibility
    # and authority checks; stage() retains its unmodified synthetic preflight.
    config = _record(external, packet, "assembly")
    require((config.get("format") == "operational-v1" if operational else
             config["synthetic"] is True and config["format"] == "synthetic-v1") and
            config["target"] == packet["target"] and config["purpose"] == pre.PURPOSE and
            config["lane"] == LANE and config["size"] == "XL" and
            op.resolved(config["size_reason"]) and type(config["max_bytes"]) is int and
            0 < config["max_bytes"] <= op.MAX_BYTES, "ASSEMBLY", "Bound recovery selection/budget required")
    for name in (() if operational else ("maintainer", "director", "authorization")):
        require(_record(external, packet, name)["assembly"] == packet["evidence"]["assembly"],
                "AUTHORITY", "Original authority must bind exact selection and budget")
    inputs = {item["path"]: item for item in packet["inputs"]}
    require(BUDGET in inputs and inputs[BUDGET]["class"] == "CURRENT_CANONICAL",
            "BUDGET", "Current budget policy must be hash-bound")
    require("### XL" in pre.raw(root, BUDGET).decode("utf-8-sig"), "BUDGET", "Missing existing XL tier")
    source_rows = op.table(op.text(root, pre.VERSION_LOG), "Version Log", ["Document Name", "Status"])
    source = next(r["Document Name"] for r in source_rows if r["Status"] == "ACTIVE")
    required = pre.REQUIRED | {source, BUDGET}
    selected = config["selected"]
    require(isinstance(selected, list) and len(selected) == len(set(selected)) and
            required <= set(selected) <= inputs.keys(), "SELECTION", "Missing/duplicate/unbound selection")
    require(all(inputs[p]["class"] == "HISTORICAL_RECOVERY" for p in set(selected) - required),
            "SELECTION", "Optional packs/handoffs are historical recovery evidence only")
    require(allocate_ids(root, external, packet) == packet["ids"], "IDS", "Consumed or partial ID collision")
    ids, values = packet["ids"], op.state(root)
    date = max(item["verified_at"] for item in packet["inputs"])[:10]
    auth = packet["evidence"]["authorization"]
    auth_ref = str(pre.safe(external, auth["path"])) + " SHA256=" + auth["sha256"]
    failure = _record(external, packet, "failure")
    blockers = failure["blockers"]
    refs = [{**inputs[p], "resolved_path": str(pre.safe(root, p)),
             "artifact_version": values["SourceTruthVersion"] if p == source else "observed snapshot",
             "use": "historical recovery evidence only" if inputs[p]["class"] == "HISTORICAL_RECOVERY"
             else "current canonical state"} for p in sorted(selected)]
    evidence_refs = [{"name": name, **ref, "resolved_path": str(pre.safe(external, ref["path"]))}
                     for name, ref in sorted(packet["evidence"].items())]
    binding = {"target": packet["target"], "purpose": packet["purpose"], "task": packet["task"],
               "executor": packet["executor"], "delegation": auth_ref, "gates": _record(external, packet, "authorization")["gates"],
               "failure_reason": packet["failure_reason"], "attempts": failure["attempts"],
               "authority_and_capability": evidence_refs, "allowlist": packet["writes"],
               "validation_criteria": packet["completion"], "return_destination": packet["completion"]["return_destination"],
               "budget": {k: config[k] for k in ("size", "size_reason", "max_bytes")}}
    if operational:
        require(bool(authority_reference), "AUTHORITY", "Controlled operation evidence reference required")
        binding["human_authority_delivery"] = {
            "operation_reference_path": authority_reference,
            "use": "Follow the consumed reference to the exact plan, installation/adoption, distinct human capacity decisions, journal and outcome. Task selection alone grants no authority."}
    # This exact prose is part of the hashed authorization itself. Its path is
    # sufficient here; the full authorization hash lives in external evidence.
    notes = "RECOVERY ONLY; NO ORDINARY EXECUTION AUTHORITY; " + packet["task"] + "; " + str(pre.safe(external, auth["path"]))
    excluded = sorted(set(inputs) - set(selected))
    pack_sections = {
        "Scope Declaration": "### Included in This Context Pack\n\n" + canonical(packet["writes"]) +
            "\n\n### Explicitly Excluded\n\nOrdinary execution, blocker closure, retry reset, source promotion, handoff consumption and operational handback.",
        "Active Handoff Summary": table(["Field", "Value"], [["Handoff ID", "NONE"],
            ["From Workcell", LANE], ["Work Completed", "Proposed bounded recovery assembly"],
            ["Open Items", "Pending handoffs are observed evidence only: " + values["ActiveHandoff"]],
            ["Blockers", canonical(blockers)], ["Next Action Suggested", "Return evidence to Director; STOP"],
            ["External authorization", auth_ref]]),
        "Source Truth Artifacts Included": table(["Artifact", "Section / File", "Version", "Relevance"],
            [[Path(source).name, source, values["SourceTruthVersion"], inputs[source]["reason"]]]),
        "Relevant Decisions": "Current recovery decision evidence (JSON-escaped pre-write snapshot):\n\n" + canonical(op.text(root, "02_DIRECTOR_LANE/DECISION_LOG.md")),
        "Relevant Contracts": table(["Contract ID", "Contract Name", "Location", "Relevance"],
            [["Rule 14", "Recovery contract", pre.GOVERNANCE, "Bounded recovery only"],
             ["Control plane", "Schema", op.SCHEMA, "Trace fields only"]]),
        "Gaps and Blockers": "Current snapshots; all statuses preserved.\n\n" + canonical({
            pre.BLOCKERS: op.text(root, pre.BLOCKERS),
            "02_DIRECTOR_LANE/GAP_REGISTER.md": op.text(root, "02_DIRECTOR_LANE/GAP_REGISTER.md")}),
        "Stale or Excluded Items": table(["Item", "Reason for Exclusion"],
            [[p, "Inventory checked; outside selected recovery purpose"] for p in excluded]) +
            "\n\nHistorical selection is evidence only; stale ordinary packs remain invalid.",
        "Known Limitations": ("Human consent is captured through the normal ADAPT interaction; identity is not independently authenticated. " if operational else "Synthetic evidence cannot authenticate humans. ") + "No ordinary context, blocker resolution or operational handback. " + config["size_reason"],
        "Context Steward Note": "Recovery assembly by " + packet["executor"] + " delegated as " + LANE +
            "; external task basis: " + auth_ref + ". No ordinary dispatch. STOP.",
    }
    pack = _document(root, "CP", {"STATUS": "DRAFT", "CONTEXT_PACK_ID": ids["CP"],
        "WORKCELL_ID": LANE, "HANDOFF_ID": "NONE", "SOURCE_TRUTH_VERSION": values["SourceTruthVersion"],
        "DATE_ASSEMBLED": date, "CONTEXT_SIZE": config["size"]}, pack_sections)
    pack += "\n## Recovery Basis\n\n" + canonical(binding) + "\n\n" + table(
        ["Resolved path", "Artifact ID/version", "SHA256", "Verified at", "Evidence class", "Inclusion reason", "Use"],
        [[r["resolved_path"], r["artifact_version"], r["sha256"], r["verified_at"], r["class"], r["reason"], r["use"]] for r in refs]) + "\n"
    pack += "\nSelected recovery evidence snapshots (JSON-escaped; historical entries are never current state):\n\n" + canonical(
        {p: pre.raw(root, p).decode("utf-8-sig") for p in sorted(selected)}) + "\n"
    require(len(pack.encode("utf-8")) <= config["max_bytes"], "BUDGET", "Recovery pack exceeds declared budget")
    paths = {kind: next(w["path"] for w in packet["writes"] if w["operation"] == "create" and
                       Path(w["path"]).stem == ids[kind]) for kind in ("CP", "CD", "HO")}
    delta = _document(root, "CD", {"STATUS": "DRAFT", "CONTEXT_DELTA_ID": ids["CD"], "WORKCELL_ID": LANE,
        "PRECEDING_CONTEXT_PACK_ID": ids["CP"], "DATE": date}, {
        "State Changes": "Proposed changes only; NOT_APPLIED.\n\n" + table(["Item", "Before", "After", "Artifact Updated"],
            [[w["path"], w["before_sha256"],
              "Proposed DRAFT document " + Path(w["path"]).stem if w["operation"] == "create"
              else canonical(w["after"]), w["path"]] for w in packet["writes"]]),
        "New Artifacts Produced": table(["Artifact", "Type", "Location", "Traceability"],
            [[ids[k], "HANDOFF" if k == "HO" else "OTHER", paths[k], auth_ref] for k in ("CP", "CD", "HO")]),
        "Superseded Items": "No items superseded by this action.",
        "Downstream Impact": "No downstream context pack rebuilds required. Ordinary context remains invalid; independent current context is required before operational handback.",
        "Context Steward Note": "Proposed recovery completion; blockers and exhausted attempts preserved. " + ids["CD"] + "; STOP.",
    })
    manifest_ref = str(pre.safe(external, packet["completion"]["manifest"]))
    handoff = _document(root, "HO", {"STATUS": "DRAFT", "HANDOFF_ID": ids["HO"], "FROM_WORKCELL": LANE,
        "TO_WORKCELL / TO_LANE": "Director Lane", "SOURCE_TRUTH_VERSION": values["SourceTruthVersion"],
        "CONTEXT_PACK_REFERENCE": ids["CP"], "DATE_EMITTED": date}, {
        "Work Completed": "Proposed bounded recovery assembly; STAGED / NOT_APPLIED. " + notes,
        "Evidence Attached": table(["Evidence ID", "Description", "Location"],
            [[ids["CD"], "Proposed context delta", paths["CD"]], ["External manifest", "Proposed final hashes; no self hashes in pack", manifest_ref]]),
        "Contracts Impacted": "No contracts impacted.",
        "Open Items": "Separate registered blocker resolution, independent current ordinary context and separately authorized operational handback remain mandatory. Return evidence to " + ", ".join(packet["completion"]["return_to"]) + ".",
        "Risks": ("Multi-file writes may partially complete; preserve evidence and STOP. " if operational else "Synthetic authority only. No production locking or transactional writes. ") + "Stale ordinary context remains invalid.",
        "Blockers": table(["BLK-ID", "Description", "Resolution Authority"],
            [[k, "Preserved " + v, "Separate registered procedure and Director sign-off"] for k, v in sorted(blockers.items())]),
        "Next Action Suggested": "Return exact manifest, diffs/hashes, validation evidence and " + paths["HO"] + " to responsible Human Director and Human Maintainer; STOP.",
        "Context Delta Reference": "CONTEXT_DELTA_ID: " + ids["CD"],
        "Placement Note": "Proposed placement in 06_HANDOFFS/ACTIVE/ is recovery evidence delivery only. Do not bind ActiveHandoff, consume pending handoffs or dispatch work. STOP.",
    })
    content = {paths["CP"]: pack.encode(), paths["CD"]: delta.encode(), paths["HO"]: handoff.encode()}
    columns = ["CP-ID", "Workcell", "Handoff ID", "Source Truth Version", "Size", "Date Assembled", "Status", "Notes"]
    row = [ids["CP"], LANE, "NONE", values["SourceTruthVersion"], config["size"], date, "ARCHIVED", notes]
    content[pre.INDEX] = _append(root, pre.INDEX, "Index", columns, row)
    interim = _append(root, pre.INDEX, "Index", columns, row[:6] + ["STALE", notes])
    content[pre.STALE] = _append(root, pre.STALE, "Register",
        ["SC-ID", "Context Pack ID", "Stale Item", "Why Stale", "Detected By", "Date Detected", "Impact", "Status", "Notes"],
        [ids["SC"], ids["CP"], "Recovery-only pack", packet["failure_reason"], LANE, date,
         "No ordinary execution authority", "OPEN", auth_ref])
    trace = next(w for w in packet["writes"] if w["path"] == op.CP)
    # Trace content is constrained to this task; preflight alone allows free prose.
    require(trace["after"]["LastAction"] == "Recovery assembly " + ids["CP"] and
            trace["after"]["Notes"] == values["Notes"] + "\n" + notes,
            "WRITE_SCOPE", "Trace prose must describe exactly this recovery task")
    content[op.CP] = _trace(root, trace)
    # Cross-artifact checks against the proposed bytes, never a temporary canonical tree.
    pack_headers = op.headers(pack, ["STATUS", "CONTEXT_PACK_ID", "WORKCELL_ID", "HANDOFF_ID", "SOURCE_TRUTH_VERSION"])
    delta_headers = op.headers(delta, ["CONTEXT_DELTA_ID", "PRECEDING_CONTEXT_PACK_ID", "WORKCELL_ID"])
    ho_headers = op.headers(handoff, ["HANDOFF_ID", "CONTEXT_PACK_REFERENCE", "TO_WORKCELL / TO_LANE", "SOURCE_TRUTH_VERSION"])
    require(pack_headers == {"STATUS": "DRAFT", "CONTEXT_PACK_ID": ids["CP"], "WORKCELL_ID": LANE,
                            "HANDOFF_ID": "NONE", "SOURCE_TRUTH_VERSION": values["SourceTruthVersion"]} and
            delta_headers == {"CONTEXT_DELTA_ID": ids["CD"], "PRECEDING_CONTEXT_PACK_ID": ids["CP"], "WORKCELL_ID": LANE} and
            ho_headers == {"HANDOFF_ID": ids["HO"], "CONTEXT_PACK_REFERENCE": ids["CP"],
                           "TO_WORKCELL / TO_LANE": "Director Lane", "SOURCE_TRUTH_VERSION": values["SourceTruthVersion"]},
            "REFERENCES", "Inconsistent proposed headers")
    require(op.section(handoff, "Context Delta Reference").strip().removesuffix("---").strip() == "CONTEXT_DELTA_ID: " + ids["CD"] and
            op.section(handoff, "Next Action Suggested").strip().removesuffix("---").strip().endswith("STOP."),
            "COMPLETION", "Missing completion delta or final STOP")
    source_table = op.table(pack, "Source Truth Artifacts Included", ["Section / File", "Version"])
    require(source_table[0]["Section / File"] == source and source_table[0]["Version"] == values["SourceTruthVersion"],
            "REFERENCES", "Unregistered staged source")
    for doc, heading, required_columns in ((delta, "State Changes", ["Item", "Before", "After", "Artifact Updated"]),
            (delta, "New Artifacts Produced", ["Artifact", "Type", "Location", "Traceability"]),
            (handoff, "Evidence Attached", ["Evidence ID", "Description", "Location"]),
            (handoff, "Blockers", ["BLK-ID", "Description", "Resolution Authority"])):
        op.table(doc, heading, required_columns)
    writes = []
    for write in sorted(packet["writes"], key=lambda w: w["path"]):
        ref = write["path"]
        final = content[ref]
        writes.append({"path": ref, "canonical_target": str(pre.safe(root, ref)),
            "operation": write["operation"], "permitted_fields": write["fields"],
            "expected_original_sha256": write["before_sha256"], "proposed_final_sha256": pre.digest(final),
            "authorization": {"root": str(external), **auth}, "source_evidence": refs + evidence_refs,
            "before_image_hex": None if write["operation"] == "create" else pre.raw(root, ref).hex(),
            "after_image_hex": final.hex()})
    by_path = {w["path"]: w for w in writes}
    order = [paths["CP"], pre.INDEX, pre.STALE, paths["CD"], paths["HO"], op.CP, pre.INDEX]
    operations = []
    for i, ref in enumerate(order):
        write = by_path[ref]
        before = interim if i == 6 else (None if write["before_image_hex"] is None else bytes.fromhex(write["before_image_hex"]))
        after = interim if i == 1 else bytes.fromhex(write["after_image_hex"])
        operations.append({"sequence": i + 1, "path": ref,
            "before_sha256": "ABSENT" if before is None else pre.digest(before),
            "after_sha256": pre.digest(after), "after_image_hex": after.hex(),
            "revalidate": "ALL_INPUTS_AND_ID_AVAILABILITY_OR_PRIOR_JOURNALED_AFTER_IMAGES"})
    return {"status": "STAGED", "application": "NOT_APPLIED", "synthetic_only": not operational,
        "operational_authority": False, "ids_reserved": False, "ids": ids,
        "input_manifest": packet["inputs"], "evidence_manifest": evidence_refs,
        "write_set": writes, "operations": operations,
        "journal": {"path": packet["completion"]["journal"], "mode": "APPEND_ONLY",
                    "records": [], "interruption": "PRESERVE_AND_STOP_REAUTHORIZE",
                    "production_locking": False, "automatic_retry_rollback_resume": False},
        "return": {"to": packet["completion"]["return_to"], "destination": packet["completion"]["return_destination"],
                   "manifest": packet["completion"]["manifest"], "handoff": paths["HO"], "final_action": "STOP"}}


def stage(instance, evidence_root, packet):
    """No output path or writer: successful artifacts exist only as returned bytes."""
    preflight = pre.validate(instance, evidence_root, packet)
    refused = {"status": "REFUSED", "application": "NOT_APPLIED", "operational_authority": False,
               "preflight": preflight, "write_set": []}
    if preflight["status"] != "VALID_SYNTHETIC_PREFLIGHT":
        return refused
    try:
        result = _build(Path(instance).absolute(), Path(evidence_root).absolute(), packet)
        # Recheck the snapshot after assembling, catching observed concurrent changes.
        again = pre.validate(instance, evidence_root, packet)
        require(again == preflight, "REVALIDATION", "Inputs changed during staging")
        result["validation"] = {"preflight": preflight,
            "artifact_schema_and_references": "PASS", "budget_and_evidence": "PASS",
            "exact_scope_and_before_images": "PASS", "source_and_id_revalidation": "PASS",
            "canonical_writes": 0}
        result["journal"]["initial_record"] = {
            "event": "PLAN_VALIDATED", "inputs": result["input_manifest"],
            "planned_writes": [{k: w[k] for k in ("path", "expected_original_sha256", "proposed_final_sha256")}
                               for w in result["write_set"]], "validation": result["validation"]}
        result["journal"]["required_runtime_events"] = ["PLAN_VALIDATED", "BEFORE_WRITE_REVALIDATED",
            "WRITE_COMPLETED", "FINAL_VALIDATED", "INTERRUPTED_ON_ANY_INCOMPLETE_OR_INVALID_STATE"]
        result["journal"]["revalidation"] = (
            "Immediately before EACH operation: exclusive writer exclusion; original authority/capability evidence; "
            "all unchanged canonical inputs; prior journaled after-images; and unconsumed ID availability. "
            "Before archival: validate complete proposed schemas/references, unchanged inputs, "
            "OPEN stale findings and preserved ordinary state. After archival: verify all final hashes. "
            "Any discrepancy preserves evidence and STOP; no retry, rollback or resume.")
        result["plan_sha256"] = fingerprint(result)
        return result
    except (pre.Refusal, op.Problem, OSError, ValueError, KeyError, TypeError, AttributeError, StopIteration) as error:
        refused["finding"] = {"code": getattr(error, "code", "ASSEMBLY"), "message": str(error)}
        return refused


def validate_plan(instance, evidence_root, packet, plan):
    """Rebuild schemas, refs, exact scope, hashes, IDs and before/after images."""
    expected = stage(instance, evidence_root, packet)
    return {"valid": expected["status"] == "STAGED" and canonical(expected) == canonical(plan),
            "application": "NOT_APPLIED", "operational_authority": False}


def inspect_journal(plan, records, observed):
    """Pure fixture auditor, never an execution/resume API.

    observed maps ALL packet inputs and proposed creates to SHA256 or ABSENT.
    Records are an immutable supplied append-only chain. A real append sink,
    durable writes, authenticity and exclusive locking remain runtime work.
    Even a consistent completed prefix is an interruption and must STOP.
    """
    result = {"status": "REFUSED", "action": "STOP_REAUTHORIZE", "automatic_resume": False,
              "application": "NOT_APPLIED", "operational_authority": False}
    try:
        unsigned = {k: v for k, v in plan.items() if k != "plan_sha256"}
        require(plan["status"] == "STAGED" and fingerprint(unsigned) == plan["plan_sha256"],
                "JOURNAL", "Changed plan")
        expected = {i["path"]: i["sha256"] for i in plan["input_manifest"]}
        expected.update({w["path"]: w["expected_original_sha256"] for w in plan["write_set"]})
        previous = plan["plan_sha256"]
        require(len(records) <= len(plan["operations"]), "JOURNAL", "Extra operation record")
        for i, record in enumerate(records):
            operation = plan["operations"][i]
            body = {"plan_sha256": plan["plan_sha256"], "previous_sha256": previous,
                    "sequence": operation["sequence"], "path": operation["path"],
                    "before_sha256": operation["before_sha256"], "after_sha256": operation["after_sha256"],
                    "event": "WRITE_COMPLETED"}
            require(record == {**body, "record_sha256": fingerprint(body)}, "JOURNAL", "Invalid, reordered or changed journal")
            require(expected[operation["path"]] == operation["before_sha256"], "JOURNAL", "Before chain mismatch")
            expected[operation["path"]] = operation["after_sha256"]
            previous = record["record_sha256"]
        require(observed == expected, "PARTIAL_STATE", "Unjournaled, missing or changed canonical bytes")
        if records:
            result["status"] = "INTERRUPTED" if len(records) < len(plan["operations"]) else "REPRESENTED_COMPLETE"
            result["action"] = "PRESERVE_AND_STOP_REAUTHORIZE"
        else:
            result["status"] = "PRISTINE_FIXTURE"
            result["action"] = "STOP_NO_WRITER"
    except (pre.Refusal, KeyError, TypeError, ValueError) as error:
        result["finding"] = {"code": getattr(error, "code", "JOURNAL"), "message": str(error)}
    return result
