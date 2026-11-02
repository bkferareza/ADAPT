"""Read-only prospective human review of existing synthetic recovery plans.

prepare_review(plan) accepts an envelope with kind (STRUCTURAL or CONTEXT),
proposed (the exact existing planner output), request (SupervisedVerifier's
BINDING_KEYS), evidence_root, and, for CONTEXT, the original assembly packet.
The target root comes from request.target. STRUCTURAL uses proposed.scope.
It rechecks the original plan against current bytes; it never replaces that plan.

validate_review(plan, authorization) takes separately supplied operator input:
{maintenance_scope: existing supervised scope, human_authorization: existing
supervised attestation}. The attestation's binding must be the returned
authorization_binding, including ids.review containing both fingerprints.
The operator authenticates humans, supplies current withdrawal evidence, and
issues fresh task/operation/approval references for each new recovery attempt.
This stateless checker cannot detect replay of identical evidence for the same
attempt or authenticate humans. No writer is connected; all outcomes STOP.
"""
from copy import deepcopy
import difflib
import importlib.util
from pathlib import Path


def _load(name):
    spec = importlib.util.spec_from_file_location(
        "review_" + name, Path(__file__).with_name(name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


assembly = _load("recovery_assembly")
supervised = _load("recovery_supervised")
pre = assembly.pre

PRESERVED = ["all blocker identities and statuses", "retry and failure history",
             "lifecycle state", "pending handoffs", "framework learning dispositions",
             "effective framework version", "ordinary execution gates",
             "separate blocker resolution and operational handback"]
STOPS = ["Missing, expired, withdrawn or conflicting human approval",
         "Changed plan, target, task, scope, completion, source or before-image",
         "Any interrupted attempt requires fresh explicit authorization",
         "No writer connected; no production execution authority",
         "Future writer must recheck actual bytes, authority and exclusive ownership"]


def _need(condition, code):
    if not condition:
        raise ValueError(code)


def _same(left, right):
    return supervised._exact(left, right)


def _diff(before, after, path):
    # JSON-escaped text preserves CR/LF, BOM, trailing spaces and missing newline.
    # Each diff line is one exact source line encoded as a JSON string.
    def lines(data):
        if data is None:
            return []
        return [assembly.canonical(line) + "\n"
                for line in data.decode("utf-8").splitlines(keepends=True)]
    return "".join(difflib.unified_diff(lines(before), lines(after),
                   fromfile=path + " (before)", tofile=path + " (after)"))


def prepare_review(plan):
    """Return exact images, escaped unified diffs and a separate approval binding.

    Malformed/stale plans raise ValueError or an existing planner refusal. No
    approval is inferred from any envelope/packet field. No filesystem writes.
    Structural placement is represented in the existing supervised schema as
    set_fields:[placement]; the original relocation operation remains bound too.
    """
    plan = deepcopy(plan)
    _need(set(plan) == ({"kind", "proposed", "request", "evidence_root"} |
                       ({"packet"} if plan["kind"] == "CONTEXT" else set())),
          "EXACT_PLAN_ENVELOPE_REQUIRED")
    proposed, request = plan["proposed"], plan["request"]
    _need(set(request) == set(supervised.BINDING_KEYS), "EXACT_REQUEST_REQUIRED")
    _need(proposed["operational_authority"] is False, "OPERATIONAL_AUTHORITY_FORBIDDEN")
    unsigned = {k: v for k, v in proposed.items() if k != "plan_sha256"}
    _need(assembly.fingerprint(unsigned) == proposed["plan_sha256"], "PLAN_FINGERPRINT_MISMATCH")
    root = Path(request["target"]["root"])
    external = Path(plan["evidence_root"])
    _need(root.is_absolute() and str(root) == str(root.resolve()) and
          external.is_absolute() and str(external) == str(external.resolve()) and
          not external.is_relative_to(root) and not root.is_relative_to(external),
          "EXACT_DISJOINT_ROOTS_REQUIRED")
    # Read the actual separately located evidence, never its approval claims.
    for reference in request["evidence"].values():
        _need(pre.digest(pre.raw(external, reference["path"])) == reference["sha256"],
              "CHANGED_EVIDENCE_BYTES")

    if plan["kind"] == "STRUCTURAL":
        structural = _load("recovery_structural")
        scope = proposed["scope"]
        expected = structural.plan(root, scope)
        _need(_same(expected, proposed), "CHANGED_STRUCTURAL_PLAN_OR_SOURCE")
        _need(request["writes"] == [{"path": scope["path"], "operation": "set_fields",
              "fields": ["placement"], "before_sha256": proposed["before_sha256"]}],
              "STRUCTURAL_MUTATION_SCOPE_MISMATCH")
        _need(_same(request["ids"], {"blocker": scope["blocker"]}), "STRUCTURAL_ID_MISMATCH")
        _need(len(request["inputs"]) == len(proposed["baseline"]) and
              {i["path"]: i["sha256"] for i in request["inputs"]} == proposed["baseline"],
              "STRUCTURAL_SOURCE_BINDING_MISMATCH")
        writes = [{"path": scope["path"], "operation": scope["operation"],
                   "permitted_fields": ["placement"],
                   "before_image_hex": proposed["before_image_hex"],
                   "after_image_hex": proposed["after_image_hex"],
                   "expected_original_sha256": proposed["before_sha256"],
                   "proposed_final_sha256": proposed["after_sha256"]}]
        problem = "Blocker row misplaced outside canonical Blockers table: " + scope["blocker"]
        outcome = "Canonical register placement; all eleven blocker values preserved"
        operations = writes
    elif plan["kind"] == "CONTEXT":
        packet = plan["packet"]
        for key in ("target", "purpose", "task", "executor", "writes", "inputs",
                    "evidence", "ids", "completion"):
            _need(_same(request[key], packet[key]), "CONTEXT_REQUEST_MISMATCH:" + key)
        gates = assembly._record(external, packet, "authorization")["gates"]
        # Existing synthetic preflight uses SYNTHETIC_APPROVED; supervised
        # evidence uses APPROVED. Both original declarations stay fingerprinted.
        gates = {key: "APPROVED" if value == "SYNTHETIC_APPROVED" and
                 proposed["synthetic_only"] is True else value for key, value in gates.items()}
        _need(_same(request["gates"], gates), "CONTEXT_GATE_MISMATCH")
        _need(assembly.validate_plan(root, external, packet, proposed)["valid"],
              "CHANGED_CONTEXT_PLAN_OR_SOURCE")
        writes, operations = proposed["write_set"], proposed["operations"]
        problem = packet["failure_reason"]
        outcome = "Proposed recovery-only DRAFT artifacts, ARCHIVED index and OPEN stale finding; NOT_APPLIED"
    else:
        raise ValueError("UNSUPPORTED_PLAN_KIND")

    # Supervised schema checks run even before approvals exist.
    structure = supervised.SupervisedVerifier().verify(request)
    _need(structure["structural_status"] == "PASS", "INVALID_SUPERVISED_REQUEST")
    files = []
    for write in writes:
        before = None if write["before_image_hex"] is None else bytes.fromhex(write["before_image_hex"])
        after = bytes.fromhex(write["after_image_hex"])
        _need(("ABSENT" if before is None else pre.digest(before)) == write["expected_original_sha256"]
              and pre.digest(after) == write["proposed_final_sha256"], "IMAGE_HASH_MISMATCH")
        files.append({"path": write["path"], "operation": write["operation"],
                      "fields": write["permitted_fields"],
                      "before_sha256": write["expected_original_sha256"],
                      "after_sha256": write["proposed_final_sha256"],
                      "before_image_hex": write["before_image_hex"],
                      "after_image_hex": write["after_image_hex"],
                      "diff": _diff(before, after, write["path"])})
    review_hash = assembly.fingerprint(plan)
    binding = deepcopy(request)
    _need("review" not in binding["ids"], "RESERVED_REVIEW_BINDING")
    binding["ids"]["review"] = {"plan_sha256": proposed["plan_sha256"],
                                "review_sha256": review_hash}
    review = {"status": "REVIEW_PREPARED", "operational_authority": False,
              "kind": plan["kind"], "target": request["target"],
              "purpose": request["purpose"], "task": request["task"],
              "problem": problem, "files": files, "operations": deepcopy(operations),
              "expected_state": outcome, "completion": request["completion"],
              "unchanged_governance": list(PRESERVED), "risks_and_stop_conditions": list(STOPS),
              "plan_sha256": proposed["plan_sha256"], "review_sha256": review_hash,
              "authorization_binding": binding, "canonical_writes": 0}
    paragraphs = ["# Recovery plan review", "Target: " + assembly.canonical(request["target"]),
                  "Purpose: " + request["purpose"], "Task: " + request["task"],
                  "Current problem: " + problem, "Expected state: " + outcome,
                  "Plan SHA256: " + proposed["plan_sha256"], "Review SHA256: " + review_hash,
                  "Diff notation: JSON-escaped UTF-8 source lines; CR/LF and BOM are explicit."]
    for item in files:
        paragraphs += ["File: " + item["path"], "Permitted change: " + assembly.canonical(
            {k: item[k] for k in ("operation", "fields")}),
            "Before SHA256: " + item["before_sha256"], "After SHA256: " + item["after_sha256"], item["diff"]]
    current = {item["path"]: item["before_image_hex"] for item in files}
    for number, operation in enumerate(operations, 1):
        path = operation["path"]
        before_hex = current[path]
        after_hex = operation["after_image_hex"]
        before = None if before_hex is None else bytes.fromhex(before_hex)
        after = bytes.fromhex(after_hex)
        paragraphs += ["Operation " + str(number) + ": " + path,
                       "Before SHA256: " + ("ABSENT" if before is None else pre.digest(before)),
                       "After SHA256: " + pre.digest(after), _diff(before, after, path)]
        current[path] = after_hex
    paragraphs += ["Approval binding (includes actor, gates, sources and completion): " + assembly.canonical(binding),
                   "Unchanged governance: " + "; ".join(PRESERVED),
                   "Risks and STOP conditions: " + "; ".join(STOPS),
                   "Human authentication and current approval withdrawal checks belong to the operator. STOP."]
    review["text"] = "\n\n".join(paragraphs) + "\n"
    return review


def validate_review(plan, authorization):
    """Validate separately supplied explicit evidence; always return STOP, no writes."""
    result = {"status": "REVIEW_REFUSED", "action": "STOP", "valid": False,
              "operational_authority": False, "human_authenticity": "UNVERIFIED",
              "canonical_writes": 0, "findings": []}
    try:
        _need(isinstance(authorization, dict) and
              set(authorization) == {"maintenance_scope", "human_authorization"},
              "SEPARATE_HUMAN_AUTHORIZATION_REQUIRED")
        review = prepare_review(plan)
        authorization = deepcopy(authorization)
        verified = supervised.SupervisedVerifier(authorization["maintenance_scope"]).verify(
            review["authorization_binding"], human_authorization=authorization["human_authorization"])
        result["supervised"] = verified
        _need(verified["status"] == "SUPERVISED_EVIDENCE_VALID", "HUMAN_AUTHORIZATION_MISMATCH_OR_INVALID")
        result.update(status="REVIEW_EVIDENCE_VALID", valid=True,
                      plan_sha256=review["plan_sha256"], review_sha256=review["review_sha256"])
    except Exception as error:
        # Do not expose arbitrary paths/input contents through malformed exceptions.
        result["findings"].append(str(error) if type(error) is ValueError else "PLAN_REVALIDATION_FAILED")
    return result
