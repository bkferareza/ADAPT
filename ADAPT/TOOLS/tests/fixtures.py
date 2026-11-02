"""Synthetic canonical-derived fixtures, never approval records for real work."""
import hashlib
import json
import importlib.util
from pathlib import Path
import re
import shutil
import sys
import types


FRAMEWORK = Path(__file__).resolve().parents[2]
QUALIFICATION = FRAMEWORK.parent / ".adapt-local/maintenance/fw0006-human-governed-final"


def isolate_recovery(module, seen=None):
    """Test-only relocation of fixed disposable roots; never packet configuration.

    Keep WORKSPACE intact so real framework/ADAPT-DEV refusal tests retain their
    actual targets. Distributed code has no access to this test helper.
    """
    seen = set() if seen is None else seen
    if id(module) in seen:
        return
    seen.add(id(module))
    maintenance = FRAMEWORK.parent / ".adapt-local/maintenance"
    filename = Path(getattr(module, "__file__", "") or "").name
    if filename == "recovery_runtime.py":
        module.WORKSPACE = FRAMEWORK.parent
        module.MAINTENANCE = QUALIFICATION / "fw0006-runtime"
        module.SYNTHETIC_ROOT = module.MAINTENANCE / "synthetic"
        module.ACCEPTANCE_ROOT = QUALIFICATION / "fw0006-end-to-end/synthetic"
        module.LOCK_ROOT = module.MAINTENANCE / "locks"
    elif filename == "recovery_structural.py":
        module.EVIDENCE_ROOT = QUALIFICATION / "fw0006-structural-repair"
        module.SYNTHETIC_ROOT = module.EVIDENCE_ROOT / "synthetic"
    elif filename == "recovery_execution.py":
        module.EVIDENCE_ROOT = QUALIFICATION / "fw0006-safe-execution"
    if hasattr(module, "_load") and not getattr(module, "_qualification_loader", False):
        original_load = module._load
        def fixture_load(name):
            loaded = original_load(name)
            isolate_recovery(loaded)
            return loaded
        module._load = fixture_load
        module._qualification_loader = True
    for key, value in list(vars(module).items()):
        if isinstance(value, types.ModuleType) and getattr(value, "__file__", None):
            if any(Path(value.__file__).resolve().is_relative_to(root) for root in (FRAMEWORK, QUALIFICATION)):
                isolate_recovery(value, seen)
        elif isinstance(value, Path) and value.is_relative_to(maintenance) and not value.is_relative_to(QUALIFICATION):
            setattr(module, key, QUALIFICATION / value.relative_to(maintenance))


def runtime_child_setup(runtime):
    """Pass identical test boundaries to a real child process, outside its packet."""
    return "".join(f"r.{key}=pathlib.Path({str(getattr(runtime, key))!r});" for key in
                   ("MAINTENANCE", "SYNTHETIC_ROOT", "ACCEPTANCE_ROOT", "LOCK_ROOT"))
spec = importlib.util.spec_from_file_location("distribution", FRAMEWORK / "VALIDATION/distribute_tools.py")
distribution = importlib.util.module_from_spec(spec)
spec.loader.exec_module(distribution)


def fresh_instance(target, mode="MODE_B_REQUIREMENTS_ONLY"):
    """Replay the documented mechanical new-instance steps; not a product scaffold engine."""
    target = Path(target)
    shutil.copytree(FRAMEWORK / "CANONICAL_STARTERS", target)
    for folder in ("CONTEXT_PACKS", "CONTEXT_DELTAS", "CONTEXT_SUMMARIES"):
        (target / "10_CONTEXT_ECONOMY" / folder).mkdir()
    version = re.search(r"Current Framework Version: (\S+)", (FRAMEWORK / "FRAMEWORK_LEARNING_REGISTER.md").read_text(encoding="utf-8"))[1]
    for file in target.rglob("*.md"):
        if file.relative_to(target).as_posix() in {"00_FRAMEWORK/ARTIFACT_STANDARDS.md", "15_COMMANDS_AND_DRIVERS/COMMAND_SYNTAX.md"}:
            continue
        lines = file.read_text(encoding="utf-8").splitlines(keepends=True)
        for i in range(min(8, len(lines))):
            for key, token, value in [("PROJECT", "PROJECT_NAME", "Fixture"), ("VERSION", "ADAPT_VERSION", version),
                                      ("INITIALIZED", "INITIALIZATION_DATE", "2026-10-15"), ("LAST_UPDATED", "DATE", "2026-10-15")]:
                if lines[i].startswith(key + ":"):
                    lines[i] = lines[i].replace("{{" + token + "}}", value)
        file.write_text("".join(lines), encoding="utf-8")
    values = {
        "ProjectName": "Fixture", "ProjectType": "Web App", "DeploymentMode": mode,
        "RoutingMode": "PROTECTED_DEFAULT", "InitializationMode": "FULL_EXTERNAL_ADAPT_INSTANCE_SCAFFOLD",
        "SourceTruthVersion": "NONE", "ActiveMilestone": "NONE", "ActiveCycle": "NONE", "ActiveHandoff": "NONE",
        "CurrentAuthority": "Director Lane", "ExecutionReadiness": "NEEDS_PLANNING", "CurrentPhase": "INITIALIZED",
        "ActiveWorkcell": "NONE", "Blocked": "NO", "ActiveBlockers": "NONE", "ActiveGaps": "NONE",
        "LastAction": "Synthetic mechanical scaffold replay 2026-10-15", "LastContextDelta": "NONE",
        "NextExpectedAction": "Run Director intake", "LastConsolidatedAt": "NEVER", "Notes": "Synthetic fixture, no execution authority",
    }
    plane = target / "02_DIRECTOR_LANE/PROJECT_CONTROL_PLANE.md"
    content = plane.read_text(encoding="utf-8")
    for field, value in values.items():
        content = re.sub(r"^\| " + field + r" \| .*? \|$", lambda _: f"| {field} | {value} |", content, flags=re.M)
    plane.write_text(content, encoding="utf-8")
    guard = target / "07_GUARDRAILS/SCOPE_GUARDRAIL.md"
    guard.write_text(guard.read_text(encoding="utf-8").replace("{{ROUTING_MODE}}", "PROTECTED_DEFAULT"), encoding="utf-8")
    # The actual mandatory distribution mechanism, not an ad hoc tool copy.
    distribution.distribute(FRAMEWORK, target)
    distribution.distribute(FRAMEWORK, target, verify=True)
    return values


def enrich_dispatch(instance):
    """Add synthetic declared binding/evidence to the original integration fixture."""
    root = Path(instance)
    def read(ref):
        return (root / ref).read_text(encoding="utf-8")
    def write(ref, value):
        path = root / ref
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value, encoding="utf-8")
    scope_ref = "02_DIRECTOR_LANE/SCOPE_CONTRACT_BACKEND_TEST.md"
    scope = read(scope_ref).replace("{{VERSION}}", "1").replace("{{BI-ID}}", "BI-001").replace("{{BI_TITLE}}", "Synthetic inspection").replace("NOT_STARTED / IN_PROGRESS / COMPLETE / BLOCKED", "NOT_STARTED")
    write(scope_ref, scope)
    member_ref = "03_WORKCELLS/BACKEND_TEST/ACTION_PROMPT.md"
    member = read("08_TEMPLATES/ACTION_PROMPT_ROLE_IDENTITY_TEMPLATE.md").replace("{{ROLE}}_{{IDENTITY}}", "BACKEND_TEST").replace("{{IDENTITY}}", "Test").replace("{{ROLE}}", "Backend Developer")
    member = member.replace("{{AUTHORITY_SCOPE}}", "Inspect BI-001 under Director-assigned scope").replace("{{MUTATION_SCOPE}}", "src/example.py").replace("{{QA_INDEPENDENCE_STATUS}}", "FULL")
    write(member_ref, member)
    guard = "07_GUARDRAILS/SCOPE_GUARDRAIL.md"
    write(guard, read(guard).replace("{{ROUTING_MODE}}", "PROTECTED_DEFAULT"))
    decision_ref = "02_DIRECTOR_LANE/DECISION_LOG.md"
    decisions = read(decision_ref).replace("## Status Values", "| DEC-001 | Synthetic scoped mutation approval | Fixture only | Synthetic human record | 2026-10-15 | BACKEND_TEST, src/example.py | NONE | ACTIVE | Not real approval |\n| DEC-002 | Synthetic milestone approval | Fixture only | Synthetic human record | 2026-10-15 | M01 | NONE | ACTIVE | Not real approval |\n\n## Status Values")
    write(decision_ref, decisions)
    approval = "02_DIRECTOR_LANE/SYNTHETIC_APPROVAL.md"
    write(approval, "# Synthetic fixture approval reference\nNot approval for real work.\n")
    source = "01_SOURCE_TRUTH/FIXTURE_REQUIREMENTS.md"
    write(source, "# Fixture\nA synthetic web application inspection example.\n")
    versions = read("01_SOURCE_TRUTH/SOURCE_TRUTH_VERSION_LOG.md").replace("## Document Types", f"| SOURCE_TRUTH_V0.1 | {source} | Requirements Document | Synthetic Director | 2026-10-15 | Fixture only | NONE | ACTIVE |\n\n## Document Types")
    write("01_SOURCE_TRUTH/SOURCE_TRUTH_VERSION_LOG.md", versions)
    emitter = "02_DIRECTOR_LANE/FIXTURE_DIRECTOR_BLUEPRINT.md"
    suites = json.loads((FRAMEWORK / "TOOLS/supporting_modules/instance_inventory.json").read_text())["role_agents"]
    def blueprint(role):
        content = "# Synthetic " + role + " Blueprint\n"
        for agent in suites[role]:
            content += "\n## " + agent + "\n"
            entries = {"Purpose": f"{agent}: bounded synthetic {role} task, no real execution.",
                       "Inputs": "Assigned BI-001 handoff, versioned fixture requirements and Director scope.",
                       "Actions": f"{agent} reviews its synthetic fixture responsibility only.",
                       "Outputs": f"{agent} contributes its Stage Record row to the fixture evidence.",
                       "Boundaries": "No self-assignment, no source changes outside src/example.py; no QA certification.",
                       "Stop Conditions": "Missing authority, scope, source or context requires a Director blocker route.",
                       "Evidence Produced": "Synthetic GROUNDED fixture record; not independent review or real approval.",
                       "Next Handoff": "Director Lane receives unresolved fixture items; stop after bounded handoff."}
            for name, value in entries.items():
                content += f"\n### {name}\n\n{value}\n"
        return content
    write(emitter, blueprint("Director"))
    write("03_WORKCELLS/BACKEND_TEST/DEFAULT_AGENT_BLUEPRINT.md", blueprint("Backend Developer"))
    report = "02_DIRECTOR_LANE/FIXTURE_EVIDENCE.md"
    rows = "".join(f"| {i+1} | {agent} | Synthetic | {'Fixture intake only' if i == 0 else 'Not engaged by synthetic intake task'} | GROUNDED | 1 | {'COMPLETE' if i == 0 else 'NOT_APPLICABLE'} |\n" for i, agent in enumerate(suites["Director"]))
    write(report, "# Synthetic evidence report\n\n## Stage Record\n\n| # | Stage (agent) | Inputs | Outputs / evidence | Evidence class | Attempts | Result |\n|---|---|---|---|---|---|---|\n" + rows)
    handoff_ref = "06_HANDOFFS/ACTIVE/HO-0001.md"
    handoff = read(handoff_ref).replace("{{ER-ID}}", "ER-001").replace("{{EVIDENCE_DESCRIPTION}}", "Synthetic fixture report")
    handoff = re.sub(r"`03_WORKCELLS/.*?/EVIDENCE/ER-001\.md`", "`" + report + "`", handoff)
    fields = {"Command": "Run atomic handoff dispatch", "WorkItem": "BI-001", "ScopeContract": scope_ref,
              "ScopeDecision": "DEC-001", "MilestoneDecision": "DEC-002", "ApprovalReference": approval,
              "ActionPrompt": member_ref, "MutationPaths": "src/example.py", "SourceTruthDocument": source,
              "ContextPack": "10_CONTEXT_ECONOMY/CONTEXT_PACKS/CP-0001.md", "EmittingBlueprint": emitter}
    handoff += "\n## Operator Dispatch Binding\n\n| Field | Value |\n|-------|-------|\n" + "".join(f"| {k} | {v} |\n" for k, v in fields.items())
    write(handoff_ref, handoff)
    references = [handoff_ref, scope_ref, member_ref, "03_WORKCELLS/BACKEND_TEST/WORKCELL_IDENTITY.md",
                  "03_WORKCELLS/BACKEND_TEST/DEFAULT_AGENT_BLUEPRINT.md", decision_ref, source, approval,
                  "01_SOURCE_TRUTH/SOURCE_TRUTH_VERSION_LOG.md", emitter, report, guard]
    context_ref = fields["ContextPack"]
    context = read(context_ref) + "\n## File Integrity\n\n| Path | SHA256 |\n|------|--------|\n"
    context += "".join(f"| {ref} | {hashlib.sha256((root/ref).read_bytes()).hexdigest()} |\n" for ref in references)
    write(context_ref, context)
    if not (root / "TOOLS").exists():
        distribution.distribute(FRAMEWORK, root)
