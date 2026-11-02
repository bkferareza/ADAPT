"""One reviewed synthetic action, using the existing bounded writers, then STOP.

execute_reviewed accepts the unchanged recovery_plan_review envelope and its
separate authorization. execution_context must be exactly {mode:
"SYNTHETIC_TEST_ONLY", binding: <prepared authorization_binding>}. This explicit
test entry is not human authentication or production permission. No CLI, target
override, retry, resume, rollback, distribution or release grant is provided.

An exclusive, durable external claim consumes operation_reference before writer
dispatch. Claims and outcomes are never removed, including on refusal/crash.
This is local synthetic single-use evidence, not production replay protection.
Existing writers retain responsibility for ownership and write-time checks.
"""
from copy import deepcopy
from pathlib import Path

import importlib.util

_spec = importlib.util.spec_from_file_location(
    "execution_review", Path(__file__).with_name("recovery_plan_review.py"))
review = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(review)
structural = review._load("recovery_structural")
runtime = structural.runtime
assembly, pre = runtime.assembly, runtime.pre
EVIDENCE_ROOT = runtime.WORKSPACE / ".adapt-local/maintenance/fw0006-safe-execution"


def _need(condition, code):
    if not condition:
        raise ValueError(code)


def _evidence_path(path):
    return runtime._checked(path, runtime.WORKSPACE / ".adapt-local/maintenance")


def _eligibility(root, external, plan):
    """Read existing ownership/history without removing or interpreting it away."""
    if plan["kind"] == "STRUCTURAL":
        owner = structural._checked(root.parent / (root.name + ".structural.lock"))
        outputs = [structural._checked(external / name)
                   for name in ("journal.jsonl", "plan.json")]
    else:
        owner = runtime.lock_path(root)
        outputs = [runtime._file(external, ref) for ref in (
            plan["proposed"]["journal"]["path"],
            plan["proposed"]["return"]["manifest"],
            plan["proposed"]["return"]["destination"])]
    _need(not owner.exists(), "EXISTING_WRITER_OWNERSHIP_STOP")
    _need(not any(path.exists() for path in outputs), "PRIOR_EXECUTION_EVIDENCE_STOP")


def execute_reviewed(plan, authorization, execution_context):
    """Execute exactly one unchanged reviewed plan within fixed synthetic roots.

    Results always say STOP and operational_authority=false. Successful results
    preserve the actual writer result, independent audit, complete final hashes,
    journal hash, review evidence and durable claim/outcome paths. A missing
    outcome next to a claim is interrupted/uncertain evidence, never retryable.
    """
    result = {"status": "REFUSED", "action": "STOP", "operational_authority": False,
              "real_execution": "UNAUTHORIZED", "human_authenticity": "UNVERIFIED",
              "authorization_class": "SYNTHETIC_TEST_ONLY", "findings": []}
    consumed, outcome = False, None
    try:
        plan, authorization, execution_context = deepcopy((plan, authorization, execution_context))
        _need(isinstance(plan, dict) and plan.get("kind") in {"STRUCTURAL", "CONTEXT"},
              "EXACT_PLAN_KIND_REQUIRED")
        # Reuse each writer's unmodified hardcoded boundary before any output.
        checker = structural._checked if plan["kind"] == "STRUCTURAL" else (
            lambda path: runtime._checked(path, runtime.SYNTHETIC_ROOT))
        root = checker(plan["request"]["target"]["root"])
        external = checker(plan["evidence_root"])
        _need(root.is_dir() and external.is_dir() and not root.is_relative_to(external)
              and not external.is_relative_to(root), "DISJOINT_FIXTURES_REQUIRED")
        validated = review.validate_review(plan, authorization)
        result["review"] = validated
        _need(validated["valid"] is True, "REVIEW_AUTHORIZATION_REFUSED")
        _need(authorization["human_authorization"]["synthetic"] is True and
              validated["supervised"]["human_authorization_evidence"] == "SYNTHETIC_VALID",
              "SEPARATE_SYNTHETIC_AUTHORIZATION_REQUIRED")
        binding = authorization["human_authorization"]["binding"]
        _need(isinstance(execution_context, dict) and
              set(execution_context) == {"mode", "binding"} and
              execution_context["mode"] == "SYNTHETIC_TEST_ONLY" and
              review._same(execution_context["binding"], binding),
              "EXACT_SYNTHETIC_EXECUTION_BINDING_REQUIRED")
        if plan["kind"] == "STRUCTURAL":
            _need(plan["proposed"]["status"] == "REPAIR_PLANNED", "REPAIR_ACTION_REQUIRED")
            _need(plan["proposed"]["scope"]["human"] ==
                  authorization["maintenance_scope"]["authorities"]["Human Framework Maintainer"],
                  "STRUCTURAL_MAINTAINER_MISMATCH")
        _eligibility(root, external, plan)
        # One fixed external operation namespace: callers cannot select a fresh
        # ledger directory to reuse a reference or change its execution identity.
        claims = _evidence_path(EVIDENCE_ROOT / "references")
        _need(not claims.is_relative_to(root) and not claims.is_relative_to(external)
              and not root.is_relative_to(claims) and not external.is_relative_to(claims),
              "CLAIMS_MUST_BE_EXTERNAL")
        claims.mkdir(parents=True, exist_ok=True)
        _evidence_path(claims)
        key = pre.digest(plan["request"]["operation_reference"].encode("utf-8"))
        claim = _evidence_path(claims / (key + ".claim.json"))
        outcome = _evidence_path(claims / (key + ".outcome.json"))
        _need(not claim.exists() and not outcome.exists(), "CONSUMED_OR_CONFLICTING_REFERENCE")
        identity = {"kind": plan["kind"], "binding": binding,
                    "plan": plan, "authorization": authorization,
                    "authorization_sha256": assembly.fingerprint(authorization),
                    "execution_context": execution_context,
                    "plan_sha256": validated["plan_sha256"],
                    "review_sha256": validated["review_sha256"],
                    "retry": "FORBIDDEN", "operational_authority": False}
        encoded_claim = runtime._encoded(identity)
        runtime._persist_new(claim, encoded_claim)
        consumed = True
        result.update(claim=str(claim), outcome=str(outcome),
                      claim_sha256=pre.digest(encoded_claim),
                      plan_sha256=validated["plan_sha256"], review_sha256=validated["review_sha256"])
        # Recheck authorization expiry and actual source/before-image bytes after
        # consuming the reference and immediately before invoking the writer.
        final_review = review.validate_review(plan, authorization)
        _need(final_review["valid"] is True, "DISPATCH_REVALIDATION_REFUSED")
        _need(_evidence_path(claim).read_bytes() == encoded_claim, "CLAIM_CHANGED")
        _eligibility(root, external, plan)
        if plan["kind"] == "STRUCTURAL":
            written = structural.execute(root, external, plan["proposed"]["scope"], plan["proposed"])
            result["writer"] = written
            checked = structural.audit(root, external)
            expected_status = "SYNTHETIC_REPAIR_VALIDATED"
            snapshot = structural._snapshot
        else:
            written = runtime.execute(root, external, plan["packet"], plan["proposed"])
            result["writer"] = written
            checked = runtime.audit(root, runtime._file(external, plan["proposed"]["journal"]["path"]),
                                    plan["proposed"])
            expected_status = "SYNTHETIC_EXECUTION_VALIDATED"
            snapshot = runtime._snapshot
        result["audit"] = checked
        _need(written["status"] == expected_status and checked["status"] == expected_status,
              "WRITER_OR_FINAL_AUDIT_REFUSED")
        _need(_evidence_path(claim).read_bytes() == encoded_claim, "CLAIM_CHANGED")
        journal = checker(written["journal"])
        result.update(status="SYNTHETIC_REVIEWED_EXECUTION_VALIDATED",
                      final_hashes=snapshot(root), journal=str(journal),
                      journal_sha256=pre.digest(journal.read_bytes()))
    except Exception as error:
        result.update(status="INTERRUPTED" if consumed else "REFUSED")
        result["findings"].append(str(error) if type(error) is ValueError else
                                  "EXECUTION_PRECONDITION_OR_IO_FAILURE")
    if consumed:
        # A publication failure remains an interruption. Never delete the claim
        # or alter existing outcomes to make an invocation look successful.
        try:
            runtime._persist_new(_evidence_path(outcome), runtime._encoded(result))
        except Exception:
            result.update(status="INTERRUPTED")
            result["findings"].append("OUTCOME_PERSISTENCE_FAILED")
    return result
