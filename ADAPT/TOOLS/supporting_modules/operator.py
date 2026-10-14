"""Read-only ADAPT operator CLI; preview never grants execution authority."""

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
import fnmatch
import subprocess
import sys

# Avoid creating bytecode inside the experimental framework on ordinary invocation.
sys.dont_write_bytecode = True
TOOLS = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "adapt_state_reader", TOOLS / "supporting_modules/state_reader.py")
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)
MAX_BYTES = 2 * 1024 * 1024
CP = "02_DIRECTOR_LANE/PROJECT_CONTROL_PLANE.md"
SCHEMA = "15_COMMANDS_AND_DRIVERS/CONTROL_PLANE_SCHEMA.md"
REGISTRY = "02_DIRECTOR_LANE/WORKCELL_REGISTRY.md"
LANES = {"Director Lane", "QA Orchestrator", "Integrator Orchestrator",
         "Planning Orchestrator", "Context Steward", "Onboarding Orchestrator",
         "Janitor Orchestrator", "Challenge Lane"}
ENUMS = {
    "DeploymentMode": {"MODE_A_EXISTING_SOLUTION", "MODE_B_REQUIREMENTS_ONLY"},
    "RoutingMode": {"PROTECTED_DEFAULT", "DUAL_WRITE"},
    "InitializationMode": {"FULL_EXTERNAL_ADAPT_INSTANCE_SCAFFOLD"},
    "ExecutionReadiness": {"READY", "NOT_READY", "BLOCKED", "NEEDS_CONTEXT",
                           "NEEDS_APPROVAL", "NEEDS_PLANNING", "NEEDS_ONBOARDING"},
    "CurrentPhase": {"INITIALIZED", "SOURCE_TRUTH_LOADING", "SOURCE_TRUTH_READY",
                     "ONBOARDING", "PLANNING", "READY_FOR_ASSIGNMENT", "EXECUTION",
                     "INTEGRATION", "QA_VALIDATION", "CHALLENGE_REVIEW",
                     "CONSOLIDATION", "JANITOR_PASS", "READY_FOR_NEXT_CYCLE", "BLOCKED"},
    "Blocked": {"YES", "NO"},
}


class Problem(ValueError):
    def __init__(self, code, message, source=""):
        super().__init__(message)
        self.code, self.source = code, source


def diagnostic(code, status, message, source=""):
    # Status may also be UNVERIFIED, NOT_CHECKED, NOT_EXERCISED.
    return {"id": code, "status": status, "message": message, "source": source}


def root_path(value):
    path = Path(value).expanduser().resolve()
    if not path.is_dir():
        raise Problem("PATH_ROOT", "Explicit root must be an existing directory")
    return path


def bounded(root, reference):
    raw = reference.strip().strip("`").replace("\\", "/")
    relative = PurePosixPath(raw)
    if (not raw or relative.is_absolute() or ":" in raw or
            any(part in {"..", ".git"} for part in relative.parts)):
        raise Problem("PATH_BOUNDARY", "Reference must stay within its explicit root")
    path = (root / Path(*relative.parts)).resolve()
    if not path.is_relative_to(root):
        raise Problem("PATH_BOUNDARY", "Reference escapes its explicit root")
    if ".git" in path.relative_to(root).parts:
        raise Problem("PATH_BOUNDARY", "Git internals are not artifact references")
    return path


def text(root, reference):
    path = bounded(root, reference)
    if not path.is_file():
        raise Problem("ARTIFACT_MISSING", "Referenced artifact is missing", reference)
    if path.stat().st_size > MAX_BYTES:
        raise Problem("ARTIFACT_LIMIT", "Artifact exceeds 2 MiB read limit", reference)
    try:
        return path.read_text(encoding="utf-8-sig")
    except UnicodeError:
        raise Problem("ARTIFACT_ENCODING", "Artifact is not UTF-8", reference) from None


def state(root):
    text(root, CP)  # Enforce boundary/size before calling the sole CP parser.
    try:
        return reader.read_state(root)
    except (ValueError, UnicodeError):
        raise Problem("CP_STRUCTURE", "Malformed control-plane table", CP) from None


def section(document, heading):
    matches = list(re.finditer(r"^## " + re.escape(heading) + r"\s*$", document, re.M))
    if len(matches) != 1:
        raise Problem("ARTIFACT_STRUCTURE", "Missing or duplicate required section")
    tail = document[matches[0].end():]
    return re.split(r"^#{1,2} ", tail, maxsplit=1, flags=re.M)[0]


def split_row(line):
    # Shared Markdown helper only; control-plane parsing remains in State Reader.
    line = line.strip()
    pieces, start, slashes = [], 0, 0
    for i, char in enumerate(line):
        if char == "|" and slashes % 2 == 0:
            pieces.append(line[start:i])
            start = i + 1
        slashes = slashes + 1 if char == "\\" else 0
    pieces.append(line[start:])
    if len(pieces) < 3 or pieces[0] or pieces[-1]:
        raise Problem("ARTIFACT_TABLE", "Malformed Markdown row")
    return [p.strip().strip("`") for p in pieces[1:-1]]


def table(document, heading, required):
    body = re.sub(r"<!--.*?-->", "", section(document, heading), flags=re.S)
    lines = [line for line in body.splitlines() if line.strip()]
    start = next((i for i, line in enumerate(lines) if line.lstrip().startswith("|")), len(lines))
    lines = lines[start:]
    if len(lines) < 2:
        raise Problem("ARTIFACT_TABLE", "Required table missing")
    header = split_row(lines[0])
    separator = split_row(lines[1])
    if (len(header) != len(set(header)) or not set(required) <= set(header) or
            len(separator) != len(header) or
            any(not re.fullmatch(r":?-{3,}:?", x) for x in separator)):
        raise Problem("ARTIFACT_TABLE", "Malformed table header or separator")
    rows = []
    ended = False
    for line in lines[2:]:
        if not line.lstrip().startswith("|"):
            ended = True
            continue
        if ended:
            raise Problem("ARTIFACT_TABLE", "Interrupted or multiple tables in section")
        row = split_row(line)
        if len(row) != len(header):
            raise Problem("ARTIFACT_TABLE", "Wrong table column count")
        rows.append(dict(zip(header, row)))
    return rows


def headers(document, keys):
    result = {}
    prefix = document.split("\n---", 1)[0]
    for key in keys:
        matches = re.findall(r"^" + re.escape(key) + r":[ \t]*(.*?)[ \t]*$", prefix, re.M)
        if len(matches) != 1 or not resolved(matches[0]):
            raise Problem("BIND_HEADER", "Missing, duplicate or unresolved binding header")
        result[key] = matches[0]
    return result


def resolved(value):
    return bool(value) and "{{" not in value and "}}" not in value


def registry(root):
    rows = table(text(root, REGISTRY), "Registry",
                 ["Workcell ID", "Role", "Human Owner", "Folder Path", "Status"])
    ids = [row["Workcell ID"] for row in rows]
    if len(ids) != len(set(ids)):
        raise Problem("REGISTRY_DUPLICATE", "Duplicate workcell ID", REGISTRY)
    return {row["Workcell ID"]: row for row in rows}


def handoff(root, value):
    declared_id = value if re.fullmatch(r"HO-\d+", value) else None
    if re.fullmatch(r"HO-\d+", value):
        value = "06_HANDOFFS/ACTIVE/" + value + ".md"
    path = bounded(root, value)
    active = bounded(root, "06_HANDOFFS/ACTIVE")
    if not path.is_relative_to(active) or path == active:
        raise Problem("HANDOFF_LOCATION", "Active handoff must be in ACTIVE/", CP)
    content = text(root, value)
    data = headers(content, ["STATUS", "HANDOFF_ID", "FROM_WORKCELL",
                             "TO_WORKCELL / TO_LANE", "SOURCE_TRUTH_VERSION",
                             "CONTEXT_PACK_REFERENCE"])
    if data["STATUS"] != "ACTIVE":
        raise Problem("HANDOFF_STATUS", "Bound handoff is not ACTIVE", value)
    if declared_id and data["HANDOFF_ID"] != declared_id:
        raise Problem("HANDOFF_BINDING", "Handoff ID does not match declared ID", value)
    if data["FROM_WORKCELL"] == data["TO_WORKCELL / TO_LANE"]:
        raise Problem("HANDOFF_SELF", "Self-addressed handoff violates handoff guardrail", value)
    return value, data, content


def required_inventory():
    inventory = json.loads((TOOLS / "supporting_modules/instance_inventory.json").read_text(encoding="utf-8"))
    return inventory["directories"], inventory["files"]


def doctor(root):
    findings = []
    def add(code, status, message, source=CP):
        findings.append(diagnostic(code, status, message, source))
    dirs, files = required_inventory()
    for path, directory in [(p, True) for p in dirs] + [(p, False) for p in files]:
        try:
            target = bounded(root, path)
            exists = target.is_dir() if directory else target.is_file()
            add("INSTANCE_DIR" if directory else "INSTANCE_FILE", "PASS" if exists else "FAIL",
                "Required artifact exists" if exists else "Required artifact missing", path)
        except Problem as error:
            add(error.code, "FAIL", str(error), path)
    try:
        values = state(root)
    except Problem as error:
        add(error.code, "FAIL", str(error), error.source)
        return {"diagnostics": findings}
    add("CP_STRUCTURE", "PASS", "All 21 fields parsed")
    try:
        schema_body = section(text(root, SCHEMA), "Schema")
        schema_fields = re.findall(r"^### (\w+)\s*$", schema_body, re.M)
        add("SCHEMA_COMPATIBILITY", "PASS" if schema_fields == list(reader.FIELDS) else "FAIL",
            "Instance schema matches supported 21-field inventory", SCHEMA)
    except Problem as error:
        add(error.code, "FAIL", str(error), SCHEMA)
    for field, value in values.items():
        if not resolved(value) and field != "Notes":
            add("CP_VALUE_UNRESOLVED", "UNVERIFIED", "Value is empty or a template placeholder: " + field)
        elif field in ENUMS:
            add("CP_ENUM", "PASS" if value in ENUMS[field] else "FAIL", "Recognized value: " + field)
    for field in ("ProjectName", "LastAction", "NextExpectedAction"):
        if not values[field]:
            add("CP_NONEMPTY", "FAIL", "Schema requires nonempty " + field)
    readiness = values["ExecutionReadiness"]
    if readiness in ENUMS["ExecutionReadiness"] and readiness != "READY":
        add("CP_PREREQUISITE", "WARN", "Recorded prerequisite state: " + readiness + "; no action authorized")
    if resolved(values["SourceTruthVersion"]):
        valid = values["SourceTruthVersion"] == "NONE" or re.fullmatch(r"SOURCE_TRUTH_V\d+(?:\.\d+)*", values["SourceTruthVersion"])
        add("CP_VERSION", "PASS" if valid else "FAIL", "Source-truth version format")
    if resolved(values["LastConsolidatedAt"]):
        from datetime import datetime
        try:
            if values["LastConsolidatedAt"] != "NEVER":
                datetime.fromisoformat(values["LastConsolidatedAt"].replace("Z", "+00:00"))
            add("CP_DATE", "PASS", "Consolidation date format")
        except ValueError:
            add("CP_DATE", "FAIL", "Invalid ISO consolidation date")
    checks = [
        ("CP-C01", ["Blocked", "ActiveBlockers"], values["Blocked"] == "YES", values["ActiveBlockers"] not in {"", "NONE"}),
        ("CP-C02", ["Blocked", "ActiveBlockers"], values["Blocked"] == "NO", values["ActiveBlockers"] == "NONE"),
        ("CP-C03", ["ExecutionReadiness", "ActiveMilestone", "SourceTruthVersion"], values["ExecutionReadiness"] == "READY", values["ActiveMilestone"] != "NONE" and values["SourceTruthVersion"] != "NONE"),
        ("CP-C04", ["CurrentPhase", "ActiveWorkcell", "ActiveHandoff"], values["CurrentPhase"] == "EXECUTION", values["ActiveWorkcell"] != "NONE" and values["ActiveHandoff"] != "NONE"),
        ("CP-C09", ["ActiveWorkcell", "ActiveHandoff"], values["ActiveWorkcell"] == "NONE", values["ActiveHandoff"] == "NONE"),
    ]
    for code, fields, applies, passed in checks:
        status = ("UNVERIFIED" if any(not resolved(values[f]) for f in fields) else
                  "NOT_EXERCISED" if not applies else "PASS" if passed else "FAIL")
        add(code, status, "Control-plane consistency rule", SCHEMA)
    try:
        cells = registry(root)
        authority = values["CurrentAuthority"]
        add("CP-C06", "UNVERIFIED" if not resolved(authority) else "NOT_EXERCISED" if authority == "NONE" else
            "PASS" if authority in cells or authority in LANES else "FAIL", "Authority is registered or recognized", REGISTRY)
        workcell = values["ActiveWorkcell"]
        if resolved(workcell) and workcell != "NONE":
            add("WORKCELL_BINDING", "PASS" if workcell in cells and cells[workcell]["Status"] == "ACTIVE" else "FAIL",
                "Active workcell registration", REGISTRY)
    except Problem as error:
        add(error.code, "FAIL", str(error), REGISTRY)
    active = values["ActiveHandoff"]
    if active == "NONE":
        add("CP-C05", "NOT_EXERCISED", "No declared active handoff", SCHEMA)
    elif not resolved(active):
        add("CP-C05", "UNVERIFIED", "Handoff binding unresolved", SCHEMA)
    else:
        try:
            ref, meta, _ = handoff(root, active)
            add("CP-C05", "PASS", "Declared active handoff exists", ref)
            add("HANDOFF_TARGET", "PASS" if meta["TO_WORKCELL / TO_LANE"] == values["ActiveWorkcell"] else "FAIL",
                "Handoff target matches active workcell (CP-C09)", ref)
        except Problem as error:
            add(error.code, "FAIL", str(error), error.source)
    for code, filename, heading, id_key, item_key, state_key, statuses in [
        ("CP-C10", "BLOCKER_REGISTER.md", "Blockers", "BLK-ID", "Blocked Item", "ActiveBlockers", {"OPEN", "RESOLVED", "DEFERRED"}),
        ("CP-C11", "GAP_REGISTER.md", "Gap Register", "GAP-ID", "Blocking Item", "ActiveGaps", {"OPEN", "IN_REVIEW", "RESOLVED", "DEFERRED", "SUPERSEDED"}),
    ]:
        ref = "02_DIRECTOR_LANE/" + filename
        try:
            rows = table(text(root, ref), heading, [id_key, item_key, "Status"])
            ids = [row[id_key] for row in rows]
            if len(ids) != len(set(ids)):
                raise Problem("REGISTER_STATE", "Duplicate IDs or unrecognized register status")
            if any(not resolved(row[id_key]) or not resolved(row["Status"]) for row in rows) or not resolved(values[state_key]):
                add(code, "UNVERIFIED", "Register or control-plane IDs unresolved", ref)
                continue
            if any(row["Status"] not in statuses for row in rows):
                raise Problem("REGISTER_STATE", "Unrecognized register status")
            opened = {row[id_key] for row in rows if row["Status"] == "OPEN"}
            mandatory = {row[id_key] for row in rows if row["Status"] == "OPEN" and
                         (code == "CP-C10" or bool(row[item_key]))}
            declared = set() if values[state_key] == "NONE" else {s.strip() for s in values[state_key].split(",")}
            passed = mandatory <= declared <= opened
            add(code, "PASS" if passed else "FAIL", "Declared IDs agree with register", ref)
        except Problem as error:
            add(error.code, "FAIL", str(error), ref)
    add("CP-C07", "NOT_CHECKED", "No cycle history evaluated", SCHEMA)
    try:
        routing_ref = "07_GUARDRAILS/SCOPE_GUARDRAIL.md"
        routing = re.findall(r"^RoutingMode:[ \t]*(.*)$", section(text(root, routing_ref), "Repository Routing"), re.M)
        if len(routing) != 1 or not resolved(routing[0]) or not resolved(values["RoutingMode"]):
            add("CP-C08", "UNVERIFIED", "Repository routing binding is unresolved", routing_ref)
        else:
            add("CP-C08", "PASS" if routing[0] == values["RoutingMode"] else "FAIL", "Repository routing declaration matches control plane", routing_ref)
    except Problem as error:
        add(error.code, "FAIL", str(error), "07_GUARDRAILS/SCOPE_GUARDRAIL.md")
    if resolved(values["ActiveWorkcell"]) and values["ActiveWorkcell"] != "NONE":
        try:
            binding_preview(root)
            add("ARTIFACT_BINDING", "PASS", "Identity, scope, context and action-prompt references resolve")
        except Problem as error:
            add(error.code, "FAIL", str(error), error.source)
    add("DOCTOR_LIMITS", "NOT_CHECKED", "Approval, evidence stage records, scope semantics and context freshness are not certified")
    return {"diagnostics": findings}


def binding_preview(root):
    values = state(root)
    if (any(not resolved(values[field]) or values[field] == "NONE" for field in
            ("ActiveHandoff", "SourceTruthVersion", "ActiveMilestone", "CurrentPhase")) or
            any(not resolved(values[field]) or values[field] not in allowed for field, allowed in ENUMS.items())):
        raise Problem("PREVIEW_STATE_UNVERIFIED", "Mandatory control-plane bindings are unresolved or unsupported", CP)
    workcell = values["ActiveWorkcell"]
    if not resolved(workcell) or workcell == "NONE" or values["CurrentAuthority"] != workcell:
        raise Problem("AUTHORITY_CONFLICT", "One registered workcell must match CurrentAuthority", CP)
    cells = registry(root)
    if workcell not in cells or cells[workcell]["Status"] != "ACTIVE":
        raise Problem("WORKCELL_UNKNOWN", "Bound workcell is not registered ACTIVE", REGISTRY)
    row = cells[workcell]
    if row["Role"] not in {"Backend Developer", "Frontend Developer"} or not resolved(row["Human Owner"]):
        raise Problem("ROLE_UNSUPPORTED", "Preview supports explicitly registered Backend/Frontend Developer identities only", REGISTRY)
    folder = row["Folder Path"].removeprefix("ADAPT/").rstrip("/")
    if not bounded(root, folder).is_relative_to(bounded(root, "03_WORKCELLS")):
        raise Problem("PATH_BOUNDARY", "Workcell folder must be inside 03_WORKCELLS", REGISTRY)
    identity_ref = folder + "/WORKCELL_IDENTITY.md"
    identity = text(root, identity_ref)
    if headers(identity, ["WORKCELL_ID"])["WORKCELL_ID"] != workcell:
        raise Problem("IDENTITY_CONFLICT", "Workcell identity header disagrees with registry", identity_ref)
    identity_rows = table(identity, "Identity Card", ["Field", "Value"])
    identity_values = {r["Field"]: r["Value"] for r in identity_rows}
    if len(identity_values) != len(identity_rows) or identity_values.get("HumanOwner") != row["Human Owner"] or identity_values.get("Role") != row["Role"]:
        raise Problem("IDENTITY_CONFLICT", "Identity card does not match registry", identity_ref)
    scope_ref = identity_values.get("ScopeContract", "")
    scope = text(root, scope_ref)
    if headers(scope, ["WORKCELL_ID"])["WORKCELL_ID"] != workcell:
        raise Problem("SCOPE_BINDING", "Scope contract belongs to another workcell", scope_ref)
    in_scope = section(scope, "In Scope")
    permissions = table(scope, "Mutation Authority", ["Permitted Path / Pattern", "File Types", "Restriction Notes"])
    if "{{" in in_scope or not re.search(r"^- \S", in_scope, re.M) or not permissions or any(
            not resolved(r["Permitted Path / Pattern"]) or not resolved(r["File Types"]) for r in permissions):
        raise Problem("SCOPE_INCOMPLETE", "Scope and mutation bindings must be explicit", scope_ref)
    handoff_ref, meta, _ = handoff(root, values["ActiveHandoff"])
    if meta["TO_WORKCELL / TO_LANE"] != workcell or meta["SOURCE_TRUTH_VERSION"] != values["SourceTruthVersion"]:
        raise Problem("HANDOFF_BINDING", "Handoff target or source truth conflicts with control plane", handoff_ref)
    context_ref = meta["CONTEXT_PACK_REFERENCE"]
    context_id = context_ref if re.fullmatch(r"CP-\d+", context_ref) else None
    if re.fullmatch(r"CP-\d+", context_ref):
        context_ref = "10_CONTEXT_ECONOMY/CONTEXT_PACKS/" + context_ref + ".md"
    context_document = text(root, context_ref)
    context = headers(context_document, ["WORKCELL_ID", "HANDOFF_ID", "SOURCE_TRUTH_VERSION"])
    if context != {"WORKCELL_ID": workcell, "HANDOFF_ID": meta["HANDOFF_ID"], "SOURCE_TRUTH_VERSION": values["SourceTruthVersion"]}:
        raise Problem("CONTEXT_BINDING", "Context pack does not match bound handoff", context_ref)
    if context_id and headers(context_document, ["CONTEXT_PACK_ID"])["CONTEXT_PACK_ID"] != context_id:
        raise Problem("CONTEXT_BINDING", "Context pack ID does not match reference", context_ref)
    # No work-item equivalence contract exists for the free-text handoff body.
    for key in ("ActiveBlockers", "ActiveGaps"):
        if values[key] != "NONE":
            raise Problem("BLOCKER_SCOPE_UNVERIFIED", "Cannot deterministically establish work-item blocker applicability", CP)
    for filename, heading, id_key, item_key in [
        ("BLOCKER_REGISTER.md", "Blockers", "BLK-ID", "Blocked Item"),
        ("GAP_REGISTER.md", "Gap Register", "GAP-ID", "Blocking Item"),
    ]:
        ref = "02_DIRECTOR_LANE/" + filename
        rows = table(text(root, ref), heading, [id_key, item_key, "Status"])
        allowed = {"OPEN", "RESOLVED", "DEFERRED"} if id_key == "BLK-ID" else {"OPEN", "IN_REVIEW", "RESOLVED", "DEFERRED", "SUPERSEDED"}
        if len({r[id_key] for r in rows}) != len(rows) or any(not resolved(r[id_key]) or r["Status"] not in allowed for r in rows):
            raise Problem("REGISTER_STATE", "Register binding is malformed or unresolved", ref)
        if any(r["Status"] == "OPEN" or not resolved(r["Status"]) for r in rows):
            raise Problem("BLOCKER_SCOPE_UNVERIFIED", "Open or unresolved register rows require scope review", ref)
    prompt_ref = "15_COMMANDS_AND_DRIVERS/ACTION_PROMPT_WORKCELL.md"
    blueprint_ref = folder + "/DEFAULT_AGENT_BLUEPRINT.md"
    text(root, prompt_ref)
    text(root, blueprint_ref)
    text(root, "15_COMMANDS_AND_DRIVERS/MUTATION_PERMISSION_MATRIX.md")
    return {
        "preview_only": True, "execution_authorized": False,
        "binding": {"workcell": workcell, "identity": row["Human Owner"], "role": row["Role"],
                    "handoff": meta["HANDOFF_ID"], "source_truth_version": values["SourceTruthVersion"]},
        "operator_preview": "Review this existing workcell/handoff binding with its action prompt. No execution invocation is generated.",
        "references": [CP, REGISTRY, identity_ref, scope_ref, handoff_ref, context_ref, prompt_ref, blueprint_ref,
                       "15_COMMANDS_AND_DRIVERS/MUTATION_PERMISSION_MATRIX.md"],
        "diagnostics": [diagnostic("PREVIEW_BINDING", "PASS", "Explicit identity, scope, handoff and context references agree"),
                        diagnostic("PREVIEW_AUTHORIZATION", "UNVERIFIED", "Approval, source-truth promotion, evidence stages, context freshness and task/scope semantics require operator review"),
                        diagnostic("NEXT_SELECTION_CONTRACT", "NOT_CHECKED", "Trace text is not authority; automatic next-action selection and executable invocation are unsupported")],
    }


def keyed(rows, key):
    result = {row[key]: row for row in rows}
    if len(result) != len(rows):
        raise Problem("ARTIFACT_DUPLICATE", "Duplicate authoritative table key")
    return result


def blueprint_agents(document):
    blocks = list(re.finditer(r"^## (.+)$", document, re.M))
    if not blocks:
        raise Problem("BLUEPRINT_STRUCTURE", "Blueprint has no agent definitions")
    agents = []
    required = {"Purpose", "Inputs", "Actions", "Outputs", "Boundaries", "Stop Conditions", "Evidence Produced", "Next Handoff"}
    for i, block in enumerate(blocks):
        body = document[block.end():blocks[i+1].start() if i+1 < len(blocks) else len(document)]
        sections = list(re.finditer(r"^### (.+)$", body, re.M))
        if not resolved(block[1]) or {s[1] for s in sections} != required or len(sections) != 8:
            raise Problem("BLUEPRINT_STRUCTURE", "Agent blueprint lacks eight required sections")
        for j, heading in enumerate(sections):
            content = body[heading.end():sections[j+1].start() if j+1 < len(sections) else len(body)].strip()
            if not resolved(content):
                raise Problem("BLUEPRINT_STRUCTURE", "Agent definition is unresolved")
        agents.append(block[1])
    if len(agents) != len(set(agents)):
        raise Problem("BLUEPRINT_STRUCTURE", "Duplicate agent definitions")
    return agents


def prompt_next(root):
    preview = binding_preview(root)
    values = state(root)
    fields = re.findall(r"^### (\w+)\s*$", section(text(root, SCHEMA), "Schema"), re.M)
    if fields != list(reader.FIELDS):
        raise Problem("SCHEMA_COMPATIBILITY", "Instance schema differs from supported schema", SCHEMA)
    if values["ExecutionReadiness"] != "READY" or values["CurrentPhase"] != "EXECUTION":
        raise Problem("PREVIEW_BLOCKED", "Dispatch preview requires recorded READY / EXECUTION binding", CP)
    if values["LastContextDelta"] != "NONE":
        raise Problem("CONTEXT_DELTA_UNVERIFIED", "v1 cannot establish freshness after a subsequent context delta; Context Steward review required", CP)
    ref, meta, handoff_document = handoff(root, values["ActiveHandoff"])
    if meta["FROM_WORKCELL"] != "Director Lane":
        raise Problem("PREVIEW_UNSUPPORTED_EMITTER", "v1 previews only explicitly Director-assigned incoming work", ref)
    active = bounded(root, "06_HANDOFFS/ACTIVE")
    candidates = sorted(active.glob("*.md"))
    if len(candidates) > 100:
        raise Problem("PREVIEW_LIMIT", "More than 100 ACTIVE artifacts; bounded selection unavailable")
    matches = 0
    for path in candidates:
        if path.name == "README.md":
            continue
        doc = text(root, path.relative_to(root).as_posix())
        status = headers(doc, ["STATUS"])["STATUS"]
        if status == "ACTIVE":
            target = headers(doc, ["TO_WORKCELL / TO_LANE"])["TO_WORKCELL / TO_LANE"]
            matches += target == values["ActiveWorkcell"]
    if matches != 1:
        raise Problem("HANDOFF_AMBIGUOUS", "Exactly one ACTIVE handoff must target the workcell", ref)
    binding_rows = table(handoff_document, "Operator Dispatch Binding", ["Field", "Value"])
    binding = {k: v["Value"] for k, v in keyed(binding_rows, "Field").items()}
    mandatory = {"Command", "WorkItem", "ScopeContract", "ScopeDecision", "MilestoneDecision",
                 "ApprovalReference", "ActionPrompt", "MutationPaths", "SourceTruthDocument",
                 "ContextPack", "EmittingBlueprint"}
    if set(binding) != mandatory or any(not resolved(value) for value in binding.values()):
        raise Problem("PREVIEW_BINDING_INCOMPLETE", "Missing, extra or unresolved dispatch binding fields", ref)
    if binding["Command"] != "Run atomic handoff dispatch":
        raise Problem("NEXT_SELECTION_UNSUPPORTED", "Only the registry's bound atomic dispatch is supported", ref)
    # References agree with the independently resolved identity and handoff.
    if binding["ScopeContract"] != preview["references"][3] or binding["ContextPack"] != preview["references"][5]:
        raise Problem("PREVIEW_REFERENCE_CONFLICT", "Binding scope/context conflicts with authoritative references", ref)
    scope_ref = binding["ScopeContract"]
    guard_ref = "07_GUARDRAILS/SCOPE_GUARDRAIL.md"
    routing = re.findall(r"^RoutingMode:[ \t]*(.*)$", section(text(root, guard_ref), "Repository Routing"), re.M)
    if routing != [values["RoutingMode"]]:
        raise Problem("ROUTING_BINDING", "Scope guardrail routing does not match control plane", guard_ref)
    scope = text(root, scope_ref)
    scope_headers = headers(scope, ["WORKCELL_ID", "ASSIGNED_BY", "SCOPE_VERSION"])
    if scope_headers["ASSIGNED_BY"] != "Director Lane":
        raise Problem("SCOPE_AUTHORITY", "Scope must record Director assignment", scope_ref)
    assigned = table(scope, "Assigned Business Items", ["BI-ID", "Status"])
    if not any(r["BI-ID"] == binding["WorkItem"] and r["Status"] in {"NOT_STARTED", "IN_PROGRESS"} for r in assigned):
        raise Problem("SCOPE_WORK_ITEM", "Bound work item is not assigned and actionable", scope_ref)
    permissions = table(scope, "Mutation Authority", ["Permitted Path / Pattern", "File Types", "Restriction Notes"])
    paths = [] if binding["MutationPaths"] == "NONE" else [p.strip() for p in binding["MutationPaths"].split(",")]
    if len(paths) != len(set(paths)):
        raise Problem("SCOPE_PATH", "Duplicate mutation paths", ref)
    for path in paths:
        # Validate syntax without reading project code or assuming a project root.
        if not path or ":" in path or "\\" in path or PurePosixPath(path).is_absolute() or ".." in PurePosixPath(path).parts:
            raise Problem("SCOPE_PATH", "Mutation path must be repo-relative", ref)
        # Anchor patterns at repo root and match per segment; '*' never crosses '/'.
        def permitted(pattern):
            parts = PurePosixPath(pattern).parts
            return (not PurePosixPath(pattern).is_absolute() and ":" not in pattern and
                    ".." not in parts and "**" not in parts and len(parts) == len(PurePosixPath(path).parts) and
                    all(fnmatch.fnmatchcase(value, rule) for value, rule in zip(PurePosixPath(path).parts, parts)))
        if not any(permitted(r["Permitted Path / Pattern"]) for r in permissions):
            raise Problem("MUTATION_PERMISSION", "Declared path is outside recorded mutation scope", scope_ref)
    decisions_ref = "02_DIRECTOR_LANE/DECISION_LOG.md"
    decisions = keyed(table(text(root, decisions_ref), "Decisions", ["DEC-ID", "Affects", "Status"]), "DEC-ID")
    for key, required in [("ScopeDecision", [values["ActiveWorkcell"], *paths]), ("MilestoneDecision", [values["ActiveMilestone"]])]:
        decision = decisions.get(binding[key])
        if not decision or decision["Status"] != "ACTIVE":
            raise Problem("APPROVAL_RECORD", "Referenced decision is not ACTIVE", decisions_ref)
        affects = {s.strip() for s in decision["Affects"].split(",")}
        if not set(required) <= affects:
            raise Problem("APPROVAL_BINDING", "Decision does not explicitly affect declared binding", decisions_ref)
    text(root, binding["ApprovalReference"])
    version_ref = "01_SOURCE_TRUTH/SOURCE_TRUTH_VERSION_LOG.md"
    versions = table(text(root, version_ref), "Version Log", ["Version", "Document Name", "Status"])
    if len([v for v in versions if v["Version"] == values["SourceTruthVersion"] and v["Status"] == "ACTIVE" and v["Document Name"] == binding["SourceTruthDocument"]]) != 1:
        raise Problem("SOURCE_PROMOTION", "Source document is not uniquely recorded ACTIVE under bound version", version_ref)
    text(root, binding["SourceTruthDocument"])
    member_ref = binding["ActionPrompt"]
    member = text(root, member_ref)
    if headers(member, ["WORKCELL_ID"])["WORKCELL_ID"] != values["ActiveWorkcell"]:
        raise Problem("MEMBER_BINDING", "Member prompt header conflicts with workcell", member_ref)
    protected = {k: r["Value"] for k, r in keyed(table(member, "PROTECTED BINDING", ["Field", "Value"]), "Field").items()}
    for field, expected in [("ActiveWorkcell", preview["binding"]["workcell"]), ("HumanOwner", preview["binding"]["identity"]), ("Role", preview["binding"]["role"])]:
        if protected.get(field) != expected:
            raise Problem("MEMBER_BINDING", "Protected member prompt disagrees with authoritative identity", member_ref)
    for field in ("SourceTruthRequired", "ActiveHandoffRequired", "ContextPackRequired", "EvidenceRequired", "StopAfterNextHandoff"):
        if protected.get(field) != "YES":
            raise Problem("MEMBER_SAFEGUARD", "Protected member prompt omits mandatory safeguard", member_ref)
    if not resolved(protected.get("Authority", "")) or not resolved(protected.get("MutationAuthority", "")):
        raise Problem("MEMBER_SAFEGUARD", "Protected authority/mutation scope is unresolved", member_ref)
    receiver_agents = blueprint_agents(text(root, preview["references"][7]))
    declared_suites = json.loads((TOOLS / "supporting_modules/instance_inventory.json").read_text(encoding="utf-8"))["role_agents"]
    if receiver_agents != declared_suites[preview["binding"]["role"]]:
        raise Problem("BLUEPRINT_STRUCTURE", "Receiver agent suite does not match its declared role")
    evidence_rows = table(handoff_document, "Evidence Attached", ["Evidence ID", "Location"])
    if not evidence_rows:
        raise Problem("EVIDENCE_STAGE", "Incoming handoff requires evidence", ref)
    emitter_blueprint = text(root, binding["EmittingBlueprint"])
    agents = blueprint_agents(emitter_blueprint)
    if agents != declared_suites["Director"]:
        raise Problem("BLUEPRINT_STRUCTURE", "Director emitting agent suite is incomplete", binding["EmittingBlueprint"])
    if not agents or any(not resolved(agent) for agent in agents):
        raise Problem("EVIDENCE_STAGE", "Emitting blueprint agent order is unavailable", binding["EmittingBlueprint"])
    for evidence in evidence_rows:
        report = text(root, evidence["Location"])
        stages = table(report, "Stage Record", ["Stage (agent)", "Attempts", "Result", "Evidence class", "Outputs / evidence"])
        if [r["Stage (agent)"] for r in stages] != agents or any(
                r["Attempts"] not in {"1", "2"} or r["Result"] not in {"COMPLETE", "NOT_APPLICABLE"} or
                r["Evidence class"] not in {"GROUNDED", "REVIEWED", "ASSERTED"} or not resolved(r["Outputs / evidence"]) for r in stages):
            raise Problem("EVIDENCE_STAGE", "Incoming stage evidence violates handoff guardrail", evidence["Location"])
    mandatory_refs = {ref, scope_ref, member_ref, preview["references"][2], preview["references"][7],
                      decisions_ref, binding["SourceTruthDocument"], binding["ApprovalReference"],
                      version_ref, binding["EmittingBlueprint"], guard_ref, *[r["Location"] for r in evidence_rows]}
    context_ref = binding["ContextPack"]
    integrity = table(text(root, context_ref), "File Integrity", ["Path", "SHA256"])
    recorded = keyed(integrity, "Path")
    if not mandatory_refs <= set(recorded) or len(recorded) > 100:
        raise Problem("CONTEXT_INTEGRITY", "Missing or excessive context-integrity references", context_ref)
    for path, row in recorded.items():
        file = bounded(root, path)
        text(root, path)  # Apply file boundary and size limits before hashing.
        if not re.fullmatch(r"[0-9a-f]{64}", row["SHA256"]) or hashlib.sha256(file.read_bytes()).hexdigest() != row["SHA256"]:
            raise Problem("CONTEXT_STALE", "Context snapshot hash does not match current artifact", context_ref)
    preview["invocation"] = {"command": "Run atomic handoff dispatch", "workcell": values["ActiveWorkcell"],
                             "identity": preview["binding"]["identity"], "role": preview["binding"]["role"],
                             "handoff": meta["HANDOFF_ID"], "action_prompt": member_ref, "scope": scope_ref,
                             "mutation_paths": paths, "context_pack": context_ref}
    preview["operator_preview"] = "Operator invocation preview only (not approval): Run atomic handoff dispatch under the bound identity, handoff, member prompt, scope and context below. Evaluate all semantic guardrails before execution."
    preview["references"] = sorted(set(preview["references"]) | mandatory_refs | {context_ref, "15_COMMANDS_AND_DRIVERS/TOOLING_DECISION_CONTRACT.md"})
    text(root, "15_COMMANDS_AND_DRIVERS/TOOLING_DECISION_CONTRACT.md")
    preview["diagnostics"] = [diagnostic("PREVIEW_BINDING", "PASS", "Recorded identity, decisions, scope, evidence and context-integrity bindings verified", ref),
                              diagnostic("PREVIEW_AUTHORIZATION", "UNVERIFIED", "Preview is not approval; human authenticity, semantic scope/adequacy and all execution guardrails remain agent/operator checks")]
    return preview


def git_read(repo, args):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0")
    try:
        result = subprocess.run(["git", "--no-optional-locks", "-c", "core.fsmonitor=false",
                                 "-c", "core.untrackedCache=false", "-C", str(repo), *args],
                                env=env, capture_output=True, timeout=20, check=False)
    except (OSError, subprocess.TimeoutExpired):
        raise Problem("GIT_UNAVAILABLE", "Git unavailable or read timed out") from None
    if result.returncode:
        raise Problem("GIT_READ", "Read-only Git query failed")
    return result.stdout.decode("utf-8", errors="surrogateescape")


def evidence(root, repo_value, references):
    repo = root_path(repo_value)
    actual_root = Path(git_read(repo, ["rev-parse", "--show-toplevel"]).strip()).resolve()
    if actual_root != repo:
        raise Problem("REPO_ROOT", "--repo must name the Git root, not a subdirectory")
    raw_status = git_read(repo, ["status", "--porcelain=v1", "-z", "--untracked-files=all", "--ignore-submodules=all"])
    entries, parts, i = [], raw_status.split("\0"), 0
    while i < len(parts) and parts[i]:
        item = parts[i]
        entry = {"status": item[:2], "path": item[3:]}
        if "R" in item[:2] or "C" in item[:2]:
            i += 1
            entry["original_path"] = parts[i]
        entries.append(entry)
        i += 1
    entries.sort(key=lambda e: (e["path"], e["status"]))
    if len(references) > 100:
        raise Problem("EVIDENCE_LIMIT", "At most 100 explicit repository file references")
    artifacts = []
    instance_refs = [CP]
    values = state(root)
    if resolved(values["ActiveHandoff"]) and values["ActiveHandoff"] != "NONE":
        ref, _, _ = handoff(root, values["ActiveHandoff"])
        instance_refs.append(ref)
    for base, origin, refs in [(root, "instance", instance_refs), (repo, "repo", references)]:
        for ref in sorted(set(refs)):
            path = bounded(base, ref)
            record = {"root": origin, "path": path.relative_to(base).as_posix(), "exists": path.is_file()}
            if path.is_file():
                if path.stat().st_size > MAX_BYTES:
                    raise Problem("EVIDENCE_LIMIT", "Referenced file exceeds 2 MiB")
                record["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
            artifacts.append(record)
    return {"git_root": str(repo), "branch": git_read(repo, ["branch", "--show-current"]).strip(),
            "head": git_read(repo, ["rev-parse", "HEAD"]).strip(), "working_tree": entries,
            "changed_paths": sorted({e["path"] for e in entries}), "artifacts": artifacts,
            "diagnostics": [diagnostic("REPO_EVIDENCE", "PASS", "Local Git metadata and bounded file hashes collected"),
                            diagnostic("EVIDENCE_GOVERNANCE", "NOT_CHECKED", "A clean tree is not governance evidence")],
            "limitations": ["No network or file-content output; paths and hashes are evidence, not certification.",
                            "No atomic snapshot against concurrent writes; submodule internals not inspected.",
                            "Only control plane, active handoff and explicit --file references hashed."]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("state", "doctor", "evidence", "prompt"):
        command = commands.add_parser(name)
        if name == "prompt":
            command.add_argument("selection", choices=["next"])
        command.add_argument("--instance", required=True)
        command.add_argument("--json", action="store_true")
        if name == "evidence":
            command.add_argument("--repo", required=True)
            command.add_argument("--file", action="append", default=[], help="Bounded repo-relative file to hash")
    args = parser.parse_args(argv)
    try:
        root = root_path(args.instance)
        result = (state(root) if args.command == "state" else doctor(root) if args.command == "doctor" else
                  prompt_next(root) if args.command == "prompt" else evidence(root, args.repo, args.file))
        exit_code = 1 if any(d["status"] == "FAIL" for d in result.get("diagnostics", [])) else 0
    except Problem as error:
        result = {"diagnostics": [diagnostic(error.code, "FAIL", str(error), error.source)]}
        if args.command == "prompt":
            result["result"] = "BLOCKED"
        exit_code = 1
    except OSError:
        result = {"diagnostics": [diagnostic("IO_READ", "FAIL", "Local file read failed")]}
        exit_code = 1
    if args.json:
        print(json.dumps(result, ensure_ascii=True, indent=2))
    elif args.command == "state" and exit_code == 0:
        for key, value in result.items():
            print(f"{key}: {value}")
    else:
        if "operator_preview" in result:
            print(result["operator_preview"])
            print("Binding: " + json.dumps(result["binding"], ensure_ascii=True))
            if "invocation" in result:
                print("Invocation preview: " + json.dumps(result["invocation"], ensure_ascii=True))
            print("References: " + ", ".join(result["references"]))
        if "git_root" in result:
            print(f"Repository: {result['git_root']}\nBranch: {result['branch']}\nHEAD: {result['head']}")
            for entry in result["working_tree"]:
                print(json.dumps(entry, ensure_ascii=True))
            for artifact in result["artifacts"]:
                print(json.dumps(artifact, ensure_ascii=True))
        for item in result.get("diagnostics", []):
            print(f"{item['status']} {item['id']}: {item['message']} [{item['source']}]")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
