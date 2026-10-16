"""Test-only conformance oracle and fixed synthetic agent acceptance file actions.

Not distributed to instances. This is not a production promotion engine, human
approval verifier or general scaffold command. Codex invokes separate stages
after reading contracts and inspecting the preceding stage's actual artifacts.
"""
import argparse
from datetime import datetime, timezone, timedelta
import difflib
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

FRAMEWORK = Path(__file__).resolve().parents[1]
CP = "02_DIRECTOR_LANE/PROJECT_CONTROL_PLANE.md"
LOG = "01_SOURCE_TRUTH/SOURCE_TRUTH_VERSION_LOG.md"
INTAKE = "02_DIRECTOR_LANE/INTAKE_REGISTER.md"
DEC = "02_DIRECTOR_LANE/DECISION_LOG.md"
SOURCE = "02_DIRECTOR_LANE/SYNTHETIC_SOURCE.txt"
PRESERVED = "01_SOURCE_TRUTH/SYNTHETIC_SOURCE.txt"
APPROVAL = "02_DIRECTOR_LANE/SYNTHETIC_APPROVAL.json"
REQUEST = "02_DIRECTOR_LANE/SYNTHETIC_REQUEST.txt"
ER = "02_DIRECTOR_LANE/ER-0001.md"
CD = "10_CONTEXT_ECONOMY/CONTEXT_DELTAS/CD-0001.md"
HO = "06_HANDOFFS/ACTIVE/HO-0001.md"
CONSUMED = "06_HANDOFFS/CONSUMED/HO-0001.md"
DELIVERY = "06_HANDOFFS/ACTIVE/HO-0002.md"
PACK = "10_CONTEXT_ECONOMY/CONTEXT_PACKS/CP-0001.md"
VERSION = "SOURCE_TRUTH_V0.1"
DATE = "2026-10-16"
QUOTE = "A reader can view the greeting."
DOCUMENT = ("# Bootstrap Acceptance\nPurpose: synthetic first-promotion test only.\n"
            "Project type: Web App. Domain: greeting viewer. User: reader.\n"
            "## Requirement and acceptance condition\n" + QUOTE + "\n"
            "## Boundaries\nNo product code, workcells, milestone acceptance or QA signoff.\n"
            "Language, framework, database, authentication and deployment are undecided.\n"
            "Suggested module: greeting viewer. No integration requested.\n"
            "Risk: this minimal case does not validate arbitrary document extraction.\n")
CONTRACTS = ["00_FRAMEWORK/" + x + ".md" for x in ("SOURCE_AUTHORITY_POLICY", "GOVERNANCE_RULES")]
CONTRACTS += ["10_CONTEXT_ECONOMY/CONTEXT_RULES.md", "10_CONTEXT_ECONOMY/CONTEXT_BUDGETS.md"]
CONTRACTS += ["07_GUARDRAILS/" + x + "_GUARDRAIL.md" for x in ("CONTEXT", "SCOPE", "MUTATION", "HANDOFF", "EVIDENCE", "CONTRACT", "QA_INDEPENDENCE")]
CONTRACTS += ["15_COMMANDS_AND_DRIVERS/" + x + ".md" for x in ("ACTION_PROMPT_MASTER", "ACTION_PROMPT_DIRECTOR", "ACTION_PROMPT_CONTEXT_STEWARD", "COMMAND_REGISTRY", "CONTROL_PLANE_SCHEMA", "MUTATION_PERMISSION_MATRIX", "HUMAN_APPROVAL_GATES", "STOP_RULES", "CONTEXT_BUDGET_POLICY", "EVIDENCE_STANDARD_BY_ROLE")]
CONTRACTS += ["08_TEMPLATES/" + x + "_TEMPLATE.md" for x in ("HANDOFF", "CONTEXT_PACK", "CONTEXT_DELTA", "EVIDENCE_REPORT")]
REGISTERS = ["01_SOURCE_TRUTH/" + x + ".md" for x in ("REQUIREMENTS_INDEX", "BUSINESS_ITEMS", "ACCEPTANCE_CRITERIA", "REQUIREMENT_SECTION_MAP")]
WRITES = [CP, LOG, INTAKE, DEC, PRESERVED, ER, CD, HO, *REGISTERS]


class Stop(ValueError):
    pass


def need(condition, reason):
    if not condition:
        raise Stop(reason)


def read(root, ref):
    return (root / ref).read_text(encoding="utf-8")


def write(root, ref, text):
    target = root / ref
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8", newline="\n")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(root):
    return {p.relative_to(root).as_posix(): sha(p) for p in sorted(root.rglob("*")) if p.is_file()}


def state(root):
    values = dict(re.findall(r"^\| (\w+) \| ([^|]*?) \|$", read(root, CP), re.M))
    values.pop("Field", None)
    return values


def set_state(root, **values):
    content = read(root, CP)
    for key, value in values.items():
        content, count = re.subn(r"^\| " + key + r" \| .*? \|$", f"| {key} | {value} |", content, flags=re.M)
        need(count == 1, "STATE_FIELD")
    write(root, CP, content)


def append(root, ref, content):
    write(root, ref, read(root, ref) + content)


def put_row(root, ref, identifier, cells):
    content = read(root, ref)
    row = "| " + " | ".join(cells) + " |"
    existing = re.compile(r"^\| " + re.escape(identifier) + r" \|.*$", re.M)
    if existing.search(content):
        content = existing.sub(lambda _: row, content)
    else:
        need("\n<!-- EXAMPLE:" in content, "TABLE_MARKER")
        content = content.replace("\n<!-- EXAMPLE:", "\n" + row + "\n<!-- EXAMPLE:", 1)
    write(root, ref, content)


def real_rows(path):
    return "\n".join(line for line in path.read_text(encoding="utf-8").splitlines() if line.startswith("| "))


def next_decision_id(root):
    used = [int(n) for n in re.findall(r'^\| DEC-(\d+) \|', real_rows(root / DEC), re.M)]
    return f"DEC-{max(used, default=0)+1:03}"


def fresh(root, basis):
    """Read-only checks for this explicitly synthetic case; semantic checks are agent assessments."""
    values = state(root)
    need(values == basis["state"], "STATE_CHANGED")
    need(values["SourceTruthVersion"] == "NONE" and values["CurrentPhase"] == "INITIALIZED", "INITIAL_STATE")
    need(all(values[k] == "NONE" for k in ("ActiveWorkcell", "ActiveHandoff", "ActiveMilestone", "ActiveCycle")), "ACTIVE_BINDING")
    need(values["Blocked"] == "NO" and values["ActiveBlockers"] == "NONE" and values["ExecutionReadiness"] == "NEEDS_PLANNING", "STATE_INCONSISTENT")
    need(basis["writer"] == values["CurrentAuthority"] == "Director Lane", "WRITER")
    need(basis["action"] == "first promotion", "ADJACENT_ACTION")
    need("{{DIRECTOR_IDENTITY}}" not in read(root, "02_DIRECTOR_LANE/DIRECTOR_IDENTITY.md"), "DIRECTOR_IDENTITY")
    need(basis["history_complete"] and not basis["uncertainties"], "HISTORY_UNCERTAIN")
    need(re.fullmatch(r"ADAPT-FW-\d{4}", basis["framework_version"]) and basis["framework_reference"], "BASELINE")
    for ref, digest in basis["contracts"].items():
        need((root / ref).is_file() and sha(root / ref) == digest, "CONTRACT_CHANGED")
    for path in root.rglob("*.md"):
        rel = path.relative_to(root).as_posix()
        if rel.startswith(("00_FRAMEWORK/", "07_GUARDRAILS/", "08_TEMPLATES/", "15_COMMANDS_AND_DRIVERS/", "TOOLS/")):
            continue
        need(not re.search(r"^\| SOURCE_TRUTH_V\d", real_rows(path), re.M), "PROMOTION_HISTORY")
        need("BOOTSTRAP_ATTEMPT:" not in path.read_text(encoding="utf-8"), "RECORDED_ATTEMPT")
    for directory in ("03_WORKCELLS", "06_HANDOFFS/ACTIVE"):
        need(not any(p.is_file() and p.name not in {"README.md", "ROLE_WORKCELL_BLUEPRINTS.md"} for p in (root / directory).rglob("*")), "ACTIVE_ARTIFACT")
    need((root / APPROVAL).is_file(), "MISSING_APPROVAL")
    need(sha(root / APPROVAL) == basis["approval_sha256"] and sha(root / REQUEST) == basis["request_sha256"], "BINDING_CHANGED")
    approval = json.loads(read(root, APPROVAL))
    need(approval.get("synthetic_fixture_only") is True, "SYNTHETIC_LABEL")
    need(approval.get("approved") is True and approval.get("gate") == 1, "GATE_1")
    need(approval.get("document") == SOURCE and approval.get("version") == basis["version"] and approval.get("sha256") == basis["source_sha256"], "APPROVAL_SCOPE")
    need(SOURCE in read(root, REQUEST) and basis["version"] in read(root, REQUEST), "REQUEST_SCOPE")
    need((root / SOURCE).is_file(), "SOURCE_MISSING")
    try:
        data = (root / SOURCE).read_bytes()
    except OSError as error:
        raise Stop("SOURCE_UNREADABLE") from error
    need(data.strip() and basis["source_complete"], "SOURCE_INCOMPLETE")
    need(hashlib.sha256(data).hexdigest() == basis["source_sha256"], "SOURCE_HASH")
    need(re.fullmatch(r"SOURCE_TRUTH_V\d+\.\d+", basis["version"]), "VERSION_LABEL")
    need(set(basis["allowed_writes"]) <= set(WRITES), "MUTATION_BOUNDARY")
    return "PASS_INITIAL_BASIS"


def inputs(root, populate_director=True):
    """Only synthetic input artifacts, never approvals for real instances."""
    write(root, SOURCE, DOCUMENT)
    identity = "02_DIRECTOR_LANE/DIRECTOR_IDENTITY.md"
    if populate_director:
        write(root, identity, read(root, identity).replace("{{DIRECTOR_IDENTITY}}", "SYNTHETIC TEST OWNER"))
    version = re.search(r"Current Framework Version: (\S+)", read(FRAMEWORK, "FRAMEWORK_LEARNING_REGISTER.md"))[1]
    write(root, REQUEST, f"SYNTHETIC FIXTURE ONLY: Promote {SOURCE} as {VERSION}.\nScope: first promotion only; SHA256 {sha(root / SOURCE)}.\n")
    approval = {"synthetic_fixture_only": True, "approved": True, "gate": 1, "document": SOURCE, "version": VERSION,
                "sha256": sha(root / SOURCE), "scope": "first promotion", "reference": "SYNTHETIC-GATE1-001; not a real Human Owner decision"}
    write(root, APPROVAL, json.dumps(approval, indent=2) + "\n")
    return {"state": state(root), "framework_version": version,
            "framework_reference": "maintainer working patch over 37f465782ef1fb69bc58da46bcc5969d6bea8220; exact source hashes in startup evidence",
            "contracts": {ref: sha(root / ref) for ref in CONTRACTS}, "writer": "Director Lane", "action": "first promotion",
            "history_complete": True, "uncertainties": [], "source_complete": True, "version": VERSION,
            "source_sha256": sha(root / SOURCE), "request_sha256": sha(root / REQUEST), "approval_sha256": sha(root / APPROVAL),
            "allowed_writes": WRITES, "identity": identity,
            "history_check": "Entire source version log; intake/decision records; all retained archive/superseded rows; workcell/handoff/milestone/cycle artifacts inspected. No promotion or attempt; commented templates excluded.",
            "size": "M; one requirement and its governance/provenance; no implementation"}


def ordinary(root, pack_ref=PACK):
    need(pack_ref is not None and (root / pack_ref).is_file(), "ORDINARY_CONTEXT_MISSING")
    pack = read(root, pack_ref)
    need("SOURCE_TRUTH_VERSION: " + state(root)["SourceTruthVersion"] in pack, "ORDINARY_VERSION")
    need("HANDOFF_ID: HO-0002" in pack and (root / DELIVERY).is_file(), "ORDINARY_HANDOFF")
    need("ASSEMBLED_BY: Context Steward" in pack and "## Scope Declaration" in pack, "ORDINARY_PROVENANCE")
    hashes = dict(re.findall(r"^\| ([^|]+?) \| ([a-f0-9]{64}) \|$", pack, re.M))
    need({PRESERVED, LOG, APPROVAL, ER, CONSUMED, DELIVERY} <= hashes.keys(), "ORDINARY_INTEGRITY")
    for ref, digest in hashes.items():
        need((root / ref).is_file() and sha(root / ref) == digest, "ORDINARY_STALE")
    return "PASS_ORDINARY_CONTEXT"


def command(base, args, expected=0):
    result = subprocess.run([str(a) for a in args], cwd=base, capture_output=True, text=True)
    journal = json.loads((base / "commands.json").read_text()) if (base / "commands.json").exists() else []
    journal.append({"command": [str(a) for a in args], "exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr})
    write(base, "commands.json", json.dumps(journal, indent=2) + "\n")
    need(result.returncode == expected, "SUBPROCESS: " + result.stdout + result.stderr)
    return result.stdout


def cli(base, root, *args, expected=0):
    manifest = json.loads(read(root, "TOOLS/MANIFEST.json"))
    need(all(sha(root / "TOOLS" / name) == digest for name, digest in manifest["files"].items()), "TOOL_MANIFEST")
    before = snapshot(root)
    value = command(base, [sys.executable, "-B", root / "TOOLS/adapt.py", *args, "--instance", root, "--json"], expected)
    need(before == snapshot(root), "TOOL_MUTATED_INSTANCE")
    journal = json.loads(read(base, "commands.json"))
    journal[-1].update(manifest_inspected_before_invocation=True, manifest_sha256=sha(root / "TOOLS/MANIFEST.json"), tool_bypass=False,
                       limitations="Read-only inspection/preview; exit 0 is not execution authority. Lane-only bootstrap is agent-guided, not executed by these tools.")
    write(base, "commands.json", json.dumps(journal, indent=2) + "\n")
    return json.loads(value)


def checkpoint(base, root, name, before):
    after = snapshot(root)
    changes = []
    for ref in sorted(before.keys() | after.keys()):
        if before.get(ref) == after.get(ref):
            continue
        original = base / ("before-" + name) / ref
        old = original.read_bytes().decode("utf-8") if original.is_file() else ""
        new = (root / ref).read_bytes().decode("utf-8") if (root / ref).is_file() else ""
        a, b = old.splitlines(True), new.splitlines(True)
        reverse = b.copy()
        for tag, i, j, k, l in reversed(difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_opcodes()):
            if tag != "equal":
                reverse[k:l] = a[i:j]
        need("".join(reverse) == old, "INVERSE_DIFF")
        changes.append({"path": ref, "before_sha256": before.get(ref, "NONE"), "after_sha256": after.get(ref, "NONE"),
                        "before": old, "after": new, "diff": "".join(difflib.unified_diff(a, b)), "inverse_verified": True})
    write(base, name + ".json", json.dumps({"state": state(root), "before": before, "after": after, "changes": changes}, indent=2) + "\n")


def scaffold(base, deployment="MODE_B_REQUIREMENTS_ONLY", prepare_promotion=True):
    """Codex scaffold file actions, independent of the unittest fresh-instance fixture."""
    root = base / "acceptance/ADAPT"
    need(not root.exists(), "NO_OVERWRITE")
    project = base / "project"
    project.mkdir()
    write(project, "REQUIREMENTS.txt", DOCUMENT)
    if deployment == "MODE_A_EXISTING_SOLUTION":
        # Establish the disposable existing solution BEFORE the read-only scaffold.
        write(project, "src/greeting.py", "def greeting():\n    return 'Hello'\n")
        write(project, "tests/test_greeting.py", "import unittest\nfrom src.greeting import greeting\n\nclass GreetingTest(unittest.TestCase):\n    def test_greeting(self):\n        self.assertEqual(greeting(), 'Hello')\n")
        write(project, "README.md", "# Synthetic existing solution\nPython greeting function; unittest test source exists. This is a disposable fixture, not a real product.\n")
    # Isolated Git metadata supports the distributed read-only evidence command.
    command(base, ["git", "init", project])
    command(base, ["git", "-C", project, "add", "."])
    command(base, ["git", "-C", project, "-c", "user.name=Synthetic Fixture", "-c", "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false", "commit", "-m", "synthetic test input"])
    write(base, "project-before.json", json.dumps(snapshot(project)))
    discovery = None
    if deployment == "MODE_A_EXISTING_SOLUTION":
        discovery = {"deployment": deployment, "read_only": True,
                     "files": {p.relative_to(project).as_posix(): sha(p) for p in project.rglob("*") if p.is_file() and ".git" not in p.relative_to(project).parts},
                     "observations": {"language": "Python (.py source)", "platform_framework": "Python; no application framework declared in fixture files",
                                      "build": "No build configuration or dependency manifest present", "validation_candidate": "tests/test_greeting.py imports unittest; presence observed, tests not run or declared as QA oracle",
                                      "layout": "src/ and tests/", "documentation": "README.md and REQUIREMENTS.txt", "requirements_origin": "Explicit REQUIREMENTS.txt; no ticket reference found",
                                      "code_observation": "src/greeting.py contains return 'Hello'; no runtime behavior or intended requirement inferred"},
                     "truth_class": "OBSERVED_EVIDENCE; any derived interpretation stays CANDIDATE_TRUTH", "qa_oracle": "UNDECLARED"}
        need(snapshot(project) == json.loads(read(base, "project-before.json")), "DISCOVERY_MUTATED_PROJECT")
        write(base, "discovery.json", json.dumps(discovery, indent=2))
    shutil.copytree(FRAMEWORK / "CANONICAL_STARTERS", root)
    for directory in ("CONTEXT_PACKS", "CONTEXT_DELTAS", "CONTEXT_SUMMARIES"):
        (root / "10_CONTEXT_ECONOMY" / directory).mkdir()
    version = re.search(r"Current Framework Version: (\S+)", read(FRAMEWORK, "FRAMEWORK_LEARNING_REGISTER.md"))[1]
    excluded = {"00_FRAMEWORK/ARTIFACT_STANDARDS.md", "15_COMMANDS_AND_DRIVERS/COMMAND_SYNTAX.md"}
    for file in root.rglob("*.md"):
        if file.relative_to(root).as_posix() in excluded:
            continue
        lines = file.read_text(encoding="utf-8").splitlines(True)
        for i in range(min(8, len(lines))):
            for key, token, value in (("PROJECT", "PROJECT_NAME", "Bootstrap Acceptance"), ("VERSION", "ADAPT_VERSION", version), ("INITIALIZED", "INITIALIZATION_DATE", DATE), ("LAST_UPDATED", "DATE", DATE)):
                if lines[i].startswith(key + ":"):
                    lines[i] = lines[i].replace("{{" + token + "}}", value)
        write(root, file.relative_to(root), "".join(lines))
    set_state(root, ProjectName="Bootstrap Acceptance", ProjectType="Web App", DeploymentMode=deployment, RoutingMode="PROTECTED_DEFAULT", InitializationMode="FULL_EXTERNAL_ADAPT_INSTANCE_SCAFFOLD", SourceTruthVersion="NONE", ActiveMilestone="NONE", ActiveCycle="NONE", ActiveHandoff="NONE", CurrentAuthority="Director Lane", ExecutionReadiness="NEEDS_PLANNING", CurrentPhase="INITIALIZED", ActiveWorkcell="NONE", Blocked="NO", ActiveBlockers="NONE", ActiveGaps="GAP-T10-001", LastAction="Synthetic scaffold " + DATE + "; STARTUP.md", LastContextDelta="NONE", NextExpectedAction="Run Director intake", LastConsolidatedAt="NEVER", Notes="SYNTHETIC ONLY; current maintainer acceptance directive authorizes this disposable scaffold; project/REQUIREMENTS.txt; no product writes; STARTUP.md records frozen provenance")
    guard = "07_GUARDRAILS/SCOPE_GUARDRAIL.md"
    write(root, guard, read(root, guard).replace("{{ROUTING_MODE}}", "PROTECTED_DEFAULT"))
    for ref in REGISTERS:
        write(root, ref, read(root, ref).replace("SOURCE_TRUTH_VERSION: {{SOURCE_TRUTH_VERSION}}", "SOURCE_TRUTH_VERSION: NONE"))
    extract(root, promoted=False)
    put_row(root, "01_SOURCE_TRUTH/OPEN_QUESTIONS.md", "OQ-001", ["OQ-001", "Which language, framework, database, authentication and deployment?", "Director Lane", "MEDIUM", "project/REQUIREMENTS.txt", "NONE", "OPEN", "NONE", "NONE"])
    put_row(root, "02_DIRECTOR_LANE/GAP_REGISTER.md", "GAP-T10-001", ["GAP-T10-001", "GAP-T10 Decision Gap", "MEDIUM", "Technical choices pending", "Source explicitly leaves technical choices undecided", "Director Lane", DATE, "future implementation only", "Human Owner", DATE, "OPEN", "NONE", "NONE"])
    if discovery:
        summary = "; ".join(f"{key}: {value}" for key, value in discovery["observations"].items())
        provenance = "project/ fixture files; SHA256 pins and read-only discovery in STARTUP.md"
        put_row(root, "01_SOURCE_TRUTH/BUSINESS_ITEMS.md", "BI-002", ["BI-002", "Existing solution discovery", summary, "NONE (candidate observation only)", "Discovery", "LOW", "DRAFT", "OBSERVED_EVIDENCE; any interpretation CANDIDATE_TRUTH; not a promoted requirement; " + provenance])
        put_row(root, "01_SOURCE_TRUTH/OPEN_QUESTIONS.md", "OQ-002", ["OQ-002", "OBSERVED_EVIDENCE: " + summary + "; which mechanism will the Director declare?", "Director Lane", "MEDIUM", provenance, "NONE; QA oracle remains UNDECLARED", "OPEN", "NONE", "NONE"])
    append(root, LOG, "\nScaffold pending input: project/REQUIREMENTS.txt. Candidate only; this note is not a promotion event.\n")
    append(root, "11_ONBOARDING/ONBOARDING_REPORTS.md", "\nSynthetic initialization under maintainer acceptance directive; no person-owned workcells; see STARTUP.md.\n")
    for flags in ([], ["--verify"]):
        command(base, [sys.executable, "-B", FRAMEWORK / "VALIDATION/distribute_tools.py", "--framework", FRAMEWORK, "--instance", root, *flags])
    # Director-initialization acceptance must stop at the real unresolved scaffold;
    # older bootstrap cases retain their explicitly pre-designated input fixture.
    basis = inputs(root) if prepare_promotion else None
    source_pins = {"CANONICAL_STARTERS/" + ref: sha(FRAMEWORK / "CANONICAL_STARTERS" / ref) for ref in CONTRACTS}
    for ref in ("START_HERE.md", "SCAFFOLD_WORKFLOW_AGENT.md", "SCAFFOLD_OUTPUT_CONTRACT.md", "WORKCELL_ONBOARDING_CONTRACT.md", "DEPLOYMENT_MODES.md", "FRAMEWORK_LEARNING_REGISTER.md"):
        source_pins[ref] = sha(FRAMEWORK / ref)
    inventory = json.loads(read(FRAMEWORK, "TOOLS/supporting_modules/instance_inventory.json"))
    need(all((root / p).is_file() for p in inventory["files"]) and all((root / p).is_dir() for p in inventory["directories"]), "INVENTORY")
    live_survivors, template_count = [], 0
    for file in root.rglob("*.md"):
        for i, line in enumerate(read(root, file.relative_to(root)).splitlines()):
            tokens = re.findall(r"\{\{[^}]+\}\}", line)
            template_count += len(tokens)
            if file.relative_to(root).as_posix() not in excluded and i < 8 and re.match(r"^(PROJECT|VERSION|INITIALIZED|LAST_UPDATED):", line) and any(t in line for t in ("{{PROJECT_NAME}}", "{{ADAPT_VERSION}}", "{{INITIALIZATION_DATE}}", "{{DATE}}")):
                live_survivors.append(file.relative_to(root).as_posix())
    need(not live_survivors, "POPULATION_FAILURE")
    startup = {"framework": "<FRAMEWORK>", "project": "<DISPOSABLE>/project", "instance": "<DISPOSABLE>/acceptance/ADAPT", "document": "project/REQUIREMENTS.txt", "project_name": "Bootstrap Acceptance", "mode": deployment, "routing": "PROTECTED_DEFAULT (explicit test input)", "project_source_mutation": "NO", "canonical_files": len(list((FRAMEWORK / "CANONICAL_STARTERS").rglob("*.md"))), "missing": [], "governance_directories": 16, "tool_files": 7, "instance_survivors": live_survivors, "template_survivors": template_count, "questions": ["OQ-001", "OQ-002"] if discovery else ["OQ-001"], "gaps": ["GAP-T10-001"], "blockers": [], "state": state(root), "version": version, "frozen_source_hashes": source_pins, "discovery": discovery, "next_command": "Run Director intake", "status": "SCAFFOLDED; STOP", "approval_notice": "Synthetic Gate 1 input is for the later promotion; not exercised during scaffold."}
    write(root, "STARTUP.md", "# ADAPT Startup / Initialization Report\nSYNTHETIC ONLY\n```json\n" + json.dumps(startup, indent=2) + "\n```\n")
    if basis is not None:
        write(base, "basis.json", json.dumps(basis, indent=2))
    write(base, "scaffold.json", json.dumps({"startup": startup, "hashes": snapshot(root)}, indent=2))
    for args, expected in ((("state",), 0), (("doctor",), 0), (("prompt", "next"), 1), (("evidence", "--repo", project), 0)):
        cli(base, root, *args, expected=expected)
    need(snapshot(project) == json.loads(read(base, "project-before.json")), "PROJECT_MUTATED")
    print(json.dumps({"stage": "scaffold", "version": version, "source": basis["source_sha256"] if basis else "NONE (no promotion input yet)", "state": state(root)}))


def extract(root, promoted):
    version = VERSION if promoted else "NONE"
    path = PRESERVED if promoted else "project/REQUIREMENTS.txt"
    counts = [sum(1 for line in real_rows(root / ref).splitlines() if re.match(r"^\| (REQ|BI|AC)-\d+ \|", line)) for ref in REGISTERS[:3]]
    note = ("verbatim: " + QUOTE + "; match; duplicate comparisons REQ/BI/AC=" + "/".join(map(str, counts)) + "; reused existing ID; no overlap with unrelated discovery candidates" if promoted else "CANDIDATE_TRUTH; pending promotion")
    put_row(root, REGISTERS[0], "REQ-001", ["REQ-001", "Requirement and acceptance condition", QUOTE, "MUST_HAVE", path, version, "ACTIVE" if promoted else "DRAFT", note])
    put_row(root, REGISTERS[1], "BI-001", ["BI-001", "Greeting view", QUOTE, "REQ-001", "Greeting", "MUST_HAVE", "DRAFT", note + "; " + version])
    put_row(root, REGISTERS[2], "AC-001", ["AC-001", "REQ-001", QUOTE, "Functional", "DRAFT", "NONE", "BI-001; " + note + "; " + version])
    put_row(root, REGISTERS[3], "REQ-001", ["REQ-001", path, "Requirement and acceptance condition", "5", "Requirement and acceptance condition", QUOTE, note])
    if promoted:
        for ref in REGISTERS:
            write(root, ref, read(root, ref).replace("SOURCE_TRUTH_VERSION: NONE", "SOURCE_TRUTH_VERSION: " + VERSION))


def handoff(root, identifier, target, er, delta, pack, completed, scope):
    value = read(root, "08_TEMPLATES/HANDOFF_TEMPLATE.md")
    fields = {"HANDOFF_ID": identifier, "FROM_WORKCELL_ID": "NONE", "TO_WORKCELL_ID": target, "SOURCE_TRUTH_VERSION": VERSION, "CONTEXT_PACK_ID": pack, "DATE": DATE, "WORK_COMPLETED": completed, "ER-ID": Path(er).stem, "EVIDENCE_DESCRIPTION": er, "CONTRACT_ID": "NONE", "CONTRACT_NAME": "None impacted", "CONTRACT_PATH": "NONE", "OPEN_ITEM_1": "OQ-001 / GAP-T10-001: future implementation only", "OPEN_ITEM_2": "No other open items", "RISK_1": "Minimal synthetic case only", "RISK_2": "No independent QA", "BLK-ID": "NONE", "BLOCKER_DESCRIPTION": "No blockers to context assembly", "RESOLUTION_AUTHORITY": "NONE", "NEXT_ACTION_SUGGESTION": scope, "CONTEXT_DELTA_ID": delta}
    for key, replacement in fields.items():
        value = value.replace("{{" + key + "}}", replacement)
    value = value.replace("STATUS: DRAFT", "STATUS: ACTIVE", 1).replace("`03_WORKCELLS/NONE/EVIDENCE/" + Path(er).name + "`", "`" + er + "`")
    value = value.replace("| NONE | None impacted | CREATED / MODIFIED / DEPRECATED | `NONE` |", "No contracts impacted.")
    value = value.replace("FROM_WORKCELL: NONE", "FROM_WORKCELL: NONE\nFROM_LANE: " + ("Director Lane" if target == "Context Steward" else "Context Steward"))
    need("{{" not in value, "HANDOFF_UNFILLED")
    return value + "\n## Explicit routing / delivery scope\n" + scope + "\n"


def promote(base, root, basis):
    print(fresh(root, basis))
    decision_id = next_decision_id(root)
    before = snapshot(root)
    shutil.copytree(root, base / "before-promote")
    append(root, INTAKE, "\n| INT-001 | " + DATE + " | SYNTHETIC-GATE1-001 | Promote SYNTHETIC_SOURCE.txt as SOURCE_TRUTH_V0.1 | Source Truth Promotion | Director Lane | RECEIVED | BOOTSTRAP_ATTEMPT: BT-001; ER-0001; synthetic only |\n")
    append(root, DEC, "\n| " + decision_id + " | Reserve first-promotion attempt BT-001 | Governed initial basis | Director recording synthetic approval | " + DATE + " | SOURCE_TRUTH_V0.1 | No fresh retry | ACTIVE | BOOTSTRAP_ATTEMPT: BT-001; binding in ER-0001; fixture only |\n")
    write(root, ER, "# ER-0001\nWORKCELL_ID: NONE\nLANE: Director Lane\nSYNTHETIC ONLY\n## Initial Context Basis\n```json\n" + json.dumps(dict(basis, before_hashes=before), indent=2) + "\n```\n")
    set_state(root, CurrentPhase="SOURCE_TRUTH_LOADING", ExecutionReadiness="NOT_READY")
    shutil.copyfile(root / SOURCE, root / PRESERVED)
    extract(root, promoted=True)
    need(sha(root / SOURCE) == sha(root / PRESERVED) == basis["source_sha256"], "SOURCE_HASH_BEFORE_REGISTRATION")
    stamp = datetime.now(timezone(timedelta(hours=8))).isoformat()
    put_row(root, LOG, VERSION, [VERSION, PRESERVED, "Requirements Document", "Director Lane", DATE, "Initial promotion; " + ER + "; SHA256 " + basis["source_sha256"] + "; SYNTHETIC-GATE1-001; " + stamp + "; REQ-001, BI-001, AC-001", "NONE", "ACTIVE"])
    append(root, LOG, "\nScaffold pending-input note above is historical; fulfilled by the ACTIVE row and ER-0001.\n")
    write(root, CD, "# CD-0001\nCONTEXT_DELTA_ID: CD-0001\nWORKCELL_ID: NONE\nLANE: Director Lane\nPRECEDING_CONTEXT_PACK_ID: NONE (initial basis, ER-0001)\n## State Changes\nNONE -> SOURCE_TRUTH_V0.1; INITIALIZED -> SOURCE_TRUTH_READY; readiness NEEDS_CONTEXT.\nREQ-001, BI-001, AC-001 reused with verbatim matches; AC-001 DRAFT. New preserved source, evidence and handoff.\n## Downstream Impact\nContext Steward must create first ordinary versioned pack; no prior packs to supersede. No implementation authorized.\n")
    suites = json.loads(read(FRAMEWORK, "TOOLS/supporting_modules/instance_inventory.json"))["role_agents"]["Director"]
    stages = "\n## Stage Record\n| # | Stage | Inputs | Outputs / evidence | Evidence class | Attempts | Result |\n|---|---|---|---|---|---|---|\n"
    for i, agent in enumerate(suites, 1):
        engaged = i <= 2
        stages += f"| {i} | {agent} | Request/source/basis if engaged | " + ("INT-001, " + decision_id + ", extraction, version log, hashes; zero new duplicate IDs" if engaged else "Not engaged: no assignment, dependency mapping, routing, certification or cycle work authorized") + f" | GROUNDED | 1 | {'COMPLETE' if engaged else 'NOT_APPLICABLE'} |\n"
    append(root, ER, stages + "\n## Dispatch and guardrails\nSteps 1-3: state/current synthetic request/Director identity. Step 4 M; 5-6 verified initial basis; 7-8 promotion only; 9 evidence; 10 CD-0001; 11 canonical HO-0001; 12 named policy fields; 13 STOP.\nContext PASS on initial basis; scope/mutation permit only declared instance artifacts. Source/approval/hash match; evidence traces BT-001 and contracts, extraction REQ-001/BI-001/AC-001. Handoff/evidence checks pass at completion. Contract and QA independence triggers not exercised (no implementation or QA). No override.\n## Integrity\nExternal promote checkpoint seals every changed file including this report with before/after hashes, exact diffs and inverse checks. All actual paths equal the initial allowlist.\n## Limitations\nSynthetic approval only; no independent QA, release certification or self-hosted lane success.\n")
    write(root, HO, handoff(root, "HO-0001", "Context Steward", ER, CD, "NONE (initial basis, ER-0001)", "First synthetic promotion registered; REQ-001/BI-001/AC-001 quote verified.", "Director routing: assemble first ordinary pack for promotion review only using registered source, logs, approval, contracts, ER-0001 and CD-0001; no implementation. Retain consumed HO-0001 provenance and deliver review pack under HO-0002."))
    set_state(root, SourceTruthVersion=VERSION, CurrentPhase="SOURCE_TRUTH_READY", ExecutionReadiness="NEEDS_CONTEXT", CurrentAuthority="Context Steward", LastAction="First promotion complete; ER-0001", LastContextDelta="CD-0001", NextExpectedAction="Context Steward assembly under HO-0001")
    after = snapshot(root)
    need({p for p in before.keys() | after.keys() if before.get(p) != after.get(p)} == set(WRITES), "ACTUAL_WRITE_SCOPE")
    need("| DRAFT |" in real_rows(root / REGISTERS[2]) and "| " + VERSION + " |" in real_rows(root / LOG), "PROMOTION_RECORD")
    need(all(state(root)[k] == v for k, v in basis["state"].items() if k not in {"SourceTruthVersion", "CurrentPhase", "ExecutionReadiness", "CurrentAuthority", "LastAction", "LastContextDelta", "NextExpectedAction"}), "CONTROL_FIELD_SCOPE")
    cli(base, root, "doctor")
    checkpoint(base, root, "promote", before)
    print("PASS_PROMOTION; STOP")


def steward_request(root, basis):
    """Read-only conformance check for the exact Director-routed assembly request."""
    need(state(root)["SourceTruthVersion"] == VERSION and state(root)["CurrentAuthority"] == "Context Steward", "STEWARD_AUTHORITY")
    need(all(state(root)[key] == "NONE" for key in ("ActiveWorkcell", "ActiveHandoff", "ActiveMilestone", "ActiveCycle")), "STEWARD_BINDING")
    need((root / HO).is_file(), "STEWARD_HANDOFF_MISSING")
    document = read(root, HO)
    for key, expected in (("STATUS", "ACTIVE"), ("HANDOFF_ID", "HO-0001"), ("FROM_LANE", "Director Lane"), ("TO_WORKCELL / TO_LANE", "Context Steward"), ("SOURCE_TRUTH_VERSION", VERSION)):
        matches = re.findall(r"^" + re.escape(key) + r":\s*([^\r\n]+)$", document, re.M)
        need(matches == [expected], "STEWARD_HANDOFF_BINDING")
    need(ER in document and CD in document and (root / ER).is_file() and (root / CD).is_file(), "STEWARD_HANDOFF_EVIDENCE")
    need(state(root)["CurrentPhase"] == "SOURCE_TRUTH_READY" and sha(root / PRESERVED) == basis["source_sha256"], "PROMOTION_INCOMPLETE")
    need(sha(root / APPROVAL) == basis["approval_sha256"] and "BOOTSTRAP_ATTEMPT:" in read(root, DEC), "PROMOTION_BINDING")
    return "PASS_STEWARD_REQUEST"


def context(base, root, basis):
    print(steward_request(root, basis))
    reservations = re.findall(r'^\| (DEC-\d+) \|.*BOOTSTRAP_ATTEMPT: BT-001', real_rows(root / DEC), re.M)
    need(len(reservations) == 1, "PROMOTION_DECISION_REFERENCE")
    before = snapshot(root)
    shutil.copytree(root, base / "before-context")
    append(root, CD, "\nContext Steward processed CD-0001; no prior packs exist to invalidate; CP-0001 follows this delta.\n")
    write(root, CONSUMED, read(root, HO).replace("STATUS: ACTIVE", "STATUS: CONSUMED", 1))
    (root / HO).unlink()
    er2 = "10_CONTEXT_ECONOMY/CONTEXT_SUMMARIES/ER-0002.md"
    cd2 = "10_CONTEXT_ECONOMY/CONTEXT_DELTAS/CD-0002.md"
    write(root, cd2, "# CD-0002\nCONTEXT_DELTA_ID: CD-0002\nWORKCELL_ID: NONE\nLANE: Context Steward\nPRECEDING_CONTEXT_PACK_ID: CP-0001\nCP-0001 created and indexed; CD-0001 processed; HO-0001 consumed, HO-0002 delivered. No source or authority changes. No prior packs superseded. Delivery delta reviewed for CP-0001; no required-input change.\n")
    agents = re.findall(r"^### \d+\. (.+)$", read(root, "15_COMMANDS_AND_DRIVERS/ACTION_PROMPT_CONTEXT_STEWARD.md"), re.M)
    write(root, er2, "# ER-0002\nWORKCELL_ID: NONE\nLANE: Context Steward\nSOURCE_TRUTH_VERSION: " + VERSION + "\n## Stage Record\n| # | Stage | Inputs | Outputs / evidence | Evidence class | Attempts | Result |\n|---|---|---|---|---|---|---|\n" + "".join(f"| {i} | {agent} | HO-0001, registered source, CD-0001, contracts | CP-0001 / CD-0002 / HO-0002; traceable hashes | GROUNDED | 1 | COMPLETE |\n" for i, agent in enumerate(agents, 1)) + "\n## Dispatch\nState/authority/routed request verified; M sizing; self-assembly against registered version; selection and hashes; CD-0001 processing; evidence/delta; canonical delivery after discharge; Trace-only control update; STOP. Staleness PROCEED_AS_IS after CD-0002 delivery review.\n## Integrity\nExternal context checkpoint seals exact changes and inverse hashes, including this report. No product work, Authority writes, acceptance, QA signoff or release certification.\n")
    delivery = handoff(root, "HO-0002", "Director Lane", er2, "CD-0002", "CP-0001", "First ordinary pack delivered for promotion review; HO-0001 consumed.", "CP-0001 is for promotion review only. Director must lawfully acquire authority before acting. No implementation authorized; GAP-T10-001 concerns future implementation. M size; hashes and CD-0002 delivery impact reviewed; no staleness.")
    refs = [PRESERVED, LOG, INTAKE, DEC, APPROVAL, REQUEST, ER, CD, CONSUMED, *REGISTERS, *CONTRACTS, "01_SOURCE_TRUTH/OPEN_QUESTIONS.md", "02_DIRECTOR_LANE/GAP_REGISTER.md", "02_DIRECTOR_LANE/BLOCKER_REGISTER.md"]
    pack = "# CONTEXT PACK\nSTATUS: ACTIVE\nCONTEXT_PACK_ID: CP-0001\nWORKCELL_ID: NONE\nLANE: Director promotion review\nHANDOFF_ID: HO-0002\nSOURCE_TRUTH_VERSION: " + VERSION + "\nDATE_ASSEMBLED: " + DATE + "\nCONTEXT_SIZE: M\nASSEMBLED_BY: Context Steward\n## Scope Declaration\nReview the first promotion only. No implementation, scope approval or adjacent execution.\n## Authoritative State at assembly\n" + json.dumps(state(root), indent=2) + "\n## Active Task\n" + delivery + "\n## Assembly Request Provenance\n" + CONSUMED + "\n## Source Truth\n" + PRESERVED + "; REQ-001 / BI-001 / AC-001 (DRAFT), verbatim matches.\n## Decisions / Gaps / Blockers\nDEC-001 reservation; synthetic Gate 1. OQ-001 / GAP-T10-001 concerns future implementation only; no blocker to assembly.\n## Exclusions\nProduct source, unrelated history, Memory Bank authority, implementation and QA excluded. No prior promoted version/pack exists.\n## Staleness and Delivery Delta Review\nCD-0001 processed; CD-0002 delivery impact reviewed, no required-input change. PROCEED_AS_IS. LastContextDelta becomes CD-0002; authority/readiness unchanged.\n## Known Limitations\nMinimal synthetic source only; no arbitrary extraction or independent certification.\n## File Integrity\n| Path | SHA256 |\n|---|---|\n" + "".join(f"| {ref} | {sha(root / ref)} |\n" for ref in refs) + "| " + DELIVERY + " | " + hashlib.sha256(delivery.encode()).hexdigest() + " |\n"
    required = "\n## Scope Contract Summary\nIdentified Context Steward assembles for Director Lane review under the explicit HO-0001 routing. ActiveWorkcell and ActiveHandoff NONE. Review scope only; no product mutation, new scope approval or execution authority. SOURCE_AUTHORITY_POLICY governs this lane-only transition.\n## Required Artifacts\n| Path | Inclusion reason | Staleness |\n|---|---|---|\n"
    for ref in refs:
        reason = "Frozen governing rule/template" if ref in CONTRACTS else "Promotion/source/approval provenance or current scoped register"
        required += f"| {ref} | {reason} | CURRENT; SHA256 verified below |\n"
    required += "\n## Relevant Decisions\nDEC-001 reserves this first attempt under the synthetic Gate 1 evidence; no implementation or scope approval.\n## Open Gaps and Blockers\nOQ-001 / GAP-T10-001: undecided technical choices block future implementation only. No blocker to this assembly.\n## Constraints\nUse SOURCE_TRUTH_V0.1 only. AC-001 remains DRAFT; no implementation, milestone acceptance, QA signoff or adjacent execution. Director must lawfully acquire authority before review.\n"
    pack = pack.replace("\n## File Integrity", required + "\n## File Integrity")
    pack = pack.replace("DEC-001 reservation", reservations[0] + " reservation").replace("DEC-001 reserves", reservations[0] + " reserves")
    if state(root)["DeploymentMode"] == "MODE_A_EXISTING_SOLUTION":
        pack += "\n## Existing solution discovery limitation\nOQ-002 and BI-002 retain OBSERVED_EVIDENCE / CANDIDATE_TRUTH only. No observed code behavior was promoted. QA oracle remains UNDECLARED; no QA action is authorized.\n"
    write(root, PACK, pack)
    put_row(root, "10_CONTEXT_ECONOMY/CONTEXT_INDEX.md", "CP-0001", ["CP-0001", "NONE (Director Lane review)", "HO-0002", VERSION, "M", DATE, "ACTIVE", "Context Steward; consumed HO-0001 provenance; no implementation"])
    write(root, DELIVERY, delivery)
    set_state(root, LastAction="CP-0001 delivered; ER-0002", LastContextDelta="CD-0002", NextExpectedAction="Director to acquire lawful authority and review HO-0002")
    need(all(state(root)[k] == v for k, v in before_state(base, "context").items() if k not in {"LastAction", "LastContextDelta", "NextExpectedAction"}), "STEWARD_FIELD_SCOPE")
    print(ordinary(root))
    for args, expected in ((("state",), 0), (("doctor",), 0), (("prompt", "next"), 1), (("evidence", "--repo", base / "project"), 0)):
        cli(base, root, *args, expected=expected)
    checkpoint(base, root, "context", before)
    print("PASS_CONTEXT; STOP")


def before_state(base, name):
    return state(base / ("before-" + name))


def negative_cases(base, root, basis):
    """Agent checks of attacked clones derived from the actual scaffold/promotion."""
    accepted_before = snapshot(root)
    records = []
    def attempt(name, source, setup, check):
        clone = base / ("negative-" + name) / "ADAPT"
        shutil.copytree(source, clone)
        setup(clone)
        before = snapshot(clone)
        try:
            check(clone)
        except Stop as error:
            records.append({"case": name, "result": "PASS", "guardrail_outcome": "STOP_REQUIRED", "reason": str(error),
                            "derived_from": source.relative_to(base).as_posix(), "no_writes_after_stop": before == snapshot(clone)})
        else:
            raise AssertionError("Expected negative STOP: " + name)
        need(before == snapshot(clone), "NEGATIVE_CHECK_WROTE_FILES")
    initial = base / "before-promote"
    attempt("missing-approval", initial, lambda c: (c / APPROVAL).unlink(), lambda c: fresh(c, basis))
    attempt("invalid-source-hash", initial, lambda c: append(c, SOURCE, "altered"), lambda c: fresh(c, basis))
    attempt("unauthorized-writer", initial, lambda c: None, lambda c: fresh(c, dict(basis, writer="Backend Workcell")))
    attempt("duplicate-or-previous-promotion", root, lambda c: None, lambda c: fresh(c, dict(basis, state=state(c))))
    def reset(c):
        set_state(c, SourceTruthVersion="NONE", CurrentPhase="INITIALIZED", CurrentAuthority="Director Lane", ExecutionReadiness="NEEDS_PLANNING", LastContextDelta="NONE")
    attempt("reset-version-to-none", root, reset, lambda c: fresh(c, dict(basis, state=state(c))))
    def wrong_handoff(c):
        write(c, HO, read(c, HO).replace("TO_WORKCELL / TO_LANE: Context Steward", "TO_WORKCELL / TO_LANE: Backend Workcell"))
    attempt("invalid-context-steward-handoff", root, wrong_handoff, lambda c: steward_request(c, basis))
    attempt("ordinary-promotion-without-context", root, lambda c: None, lambda c: ordinary(c, None))
    attempt("unauthorized-adjacent-action", initial, lambda c: None, lambda c: fresh(c, dict(basis, action="Director consolidate cycle")))
    need(accepted_before == snapshot(root), "NEGATIVES_MUTATED_ACCEPTED_INSTANCE")
    write(base, "negatives.json", json.dumps({"result": "PASS", "cases": records, "not_exercised": []}, indent=2))
    print(json.dumps(records, indent=2))


def verify(base, root, basis):
    print(ordinary(root))
    stops = []
    def expect_stop(name, action):
        try:
            action()
        except Stop as error:
            stops.append({"case": name, "outcome": "STOP_REQUIRED", "reason": str(error)})
        else:
            raise AssertionError("Expected STOP: " + name)
    before = snapshot(root)
    expect_stop("Repeated bootstrap", lambda: fresh(root, basis))
    expect_stop("Ordinary promotion without context", lambda: ordinary(root, None))
    clone = base / "reset-attack/ADAPT"
    shutil.copytree(root, clone)
    set_state(clone, SourceTruthVersion="NONE", CurrentPhase="INITIALIZED", CurrentAuthority="Director Lane", ExecutionReadiness="NEEDS_PLANNING", LastContextDelta="NONE")
    expect_stop("Reset to NONE", lambda: fresh(clone, dict(basis, state=state(clone))))
    stale = base / "stale-attack/ADAPT"
    shutil.copytree(root, stale)
    (stale / PRESERVED).write_bytes((stale / PRESERVED).read_bytes() + b"changed")
    expect_stop("Ordinary context stale source", lambda: ordinary(stale))
    need(before == snapshot(root), "VERIFY_MUTATED_INSTANCE")
    need(snapshot(base / "project") == json.loads(read(base, "project-before.json")), "PROJECT_MUTATED")
    result = {"result": "PASS", "synthetic_approvals_only": True, "stops": stops, "state": state(root), "final_hashes": snapshot(root), "source_sha256": basis["source_sha256"], "framework_version": basis["framework_version"]}
    write(base, "verify.json", json.dumps(result, indent=2))
    print(json.dumps({k: v for k, v in result.items() if k != "final_hashes"}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("scaffold", "promote", "negatives", "context", "verify"))
    parser.add_argument("--deployment", choices=("MODE_A_EXISTING_SOLUTION", "MODE_B_REQUIREMENTS_ONLY"), default="MODE_B_REQUIREMENTS_ONLY")
    parser.add_argument("--disposable", type=Path, required=True)
    options = parser.parse_args()
    base = options.disposable.resolve()
    need(base.is_dir() and base.name.startswith("adapt-bootstrap-v2-"), "EXTERNAL_DISPOSABLE_REQUIRED")
    need(not base.is_relative_to(FRAMEWORK.parent), "DISPOSABLE_INSIDE_WORKSPACE")
    if options.stage == "scaffold":
        scaffold(base, options.deployment)
    else:
        root = base / "acceptance/ADAPT"
        basis = json.loads(read(base, "basis.json"))
        {"promote": promote, "negatives": negative_cases, "context": context, "verify": verify}[options.stage](base, root, basis)
