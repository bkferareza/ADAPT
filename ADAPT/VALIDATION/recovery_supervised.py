"""Read-only proposed FW-0006 human-supervised authorization scope checker.

The deployment operator authenticates humans through existing access controls
and supplies authorization explicitly through the maintenance entry. Packets
cannot supply that entry. This module validates declarations, not identity.
No file/network I/O, writer, provider selection or execution grant exists.
"""
from copy import deepcopy
from datetime import datetime, timezone
import json
import re


HUMAN_SUPERVISED = "HUMAN_SUPERVISED"
ROLES = {"Human Director", "Human Framework Maintainer"}
BINDING_KEYS = ("target", "workcell", "purpose", "task", "executor", "writes",
                "inputs", "evidence", "ids", "completion", "gates",
                "operation_reference", "audit_reference")


class Refusal(ValueError):
    pass


def _need(condition, reason):
    if not condition:
        raise Refusal(reason)


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _hash(value):
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def _time(value):
    _need(_text(value), "TIMESTAMP_REQUIRED")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    _need(parsed.tzinfo is not None, "TIMEZONE_REQUIRED")
    return parsed


def _path(value):
    _need(_text(value) and "\\" not in value and not value.startswith("/") and
          all(p not in {"", ".", ".."} and ":" not in p for p in value.split("/")),
          "UNSAFE_PATH")


def _exact(left, right):
    # JSON equality distinguishes True from 1, unlike Python mapping equality.
    def encode(value):
        return json.dumps(value, sort_keys=True, allow_nan=False, separators=(",", ":"))
    return encode(left) == encode(right)


class SupervisedVerifier:
    def __init__(self, maintenance_scope=None):
        """Scope supplied by the human-controlled maintenance entry, never packet data.

        It binds target, workcell, executor, required_gates and authorities.
        The organization is responsible for identity and access to normal ADAPT interaction.
        """
        self._scope = deepcopy(maintenance_scope)

    def verify(self, packet, *, human_authorization=None):
        """Check separately supplied current human authorization; never grant writes.

        The embedding entry must supply human_authorization from explicit human
        input, never extract it from the packet or infer it from approved=true.
        """
        now = datetime.now(timezone.utc)
        result = {
            "status": "AUTHORITY_UNVERIFIED", "operational_authority": False,
            "structural_status": "UNVERIFIED", "human_authorization_evidence": "UNVERIFIED",
            "scope_status": "UNVERIFIED",
            "release_or_adoption": "UNVERIFIED", "synthetic": None,
            "checked_at": now.isoformat(), "findings": [],
            "outstanding_requirements": ["FLC_005_PROMOTION", "FW_0006_PUBLICATION",
                "TARGET_INSTALLATION_OR_ADOPTION", "HUMAN_REVIEWED_PLAN_AUTHORIZATION",
                "SOURCE_AND_BEFORE_IMAGE_BYTE_VERIFICATION", "PRODUCTION_WRITER_AUTHORIZATION",
                "SEPARATE_BLOCKER_RESOLUTION", "SEPARATE_OPERATIONAL_HANDBACK"],
        }

        def check(section, action, success="PASS"):
            try:
                action()
                result[section] = success
                return True
            except Exception as error:
                # Expose only static refusal codes for malformed input.
                code = str(error) if type(error) is Refusal else "PREREQUISITE_UNAVAILABLE"
                result[section] = "UNVERIFIED"
                result["findings"].append({"section": section, "code": code})
                return False

        binding, attestation = {}, {}
        config = self._scope

        def structure():
            _need(isinstance(packet, dict), "REQUEST_REQUIRED")
            binding.update(deepcopy({key: packet[key] for key in BINDING_KEYS}))
            _need(all(_text(binding[k]) for k in ("workcell", "task", "executor",
                  "operation_reference", "audit_reference")), "REQUEST_IDENTITY_REQUIRED")
            _need(binding["purpose"] == "RECOVERY_BOOTSTRAP_AUTHORIZATION", "PURPOSE_MISMATCH")
            _need(isinstance(binding["target"], dict) and
                  set(binding["target"]) == {"root", "identity"} and
                  all(_text(v) for v in binding["target"].values()), "TARGET_REQUIRED")
            _need(isinstance(binding["ids"], dict) and bool(binding["ids"]) and
                  isinstance(binding["completion"], dict) and bool(binding["completion"]),
                  "COMPLETION_BINDING_REQUIRED")
            _need(isinstance(binding["writes"], list) and bool(binding["writes"]), "SCOPE_REQUIRED")
            aliases = set()
            for write in binding["writes"]:
                _path(write["path"])
                alias = write["path"].casefold()
                _need(alias not in aliases, "ALIASED_WRITE")
                aliases.add(alias)
                _need(write["operation"] in {"create", "append_row", "append_open_row", "set_fields"}
                      and isinstance(write["fields"], list) and bool(write["fields"])
                      and all(_text(f) for f in write["fields"])
                      and len(set(write["fields"])) == len(write["fields"]), "INVALID_WRITE_SCOPE")
                _need((write["operation"] == "create" and write["before_sha256"] == "ABSENT") or
                      (write["operation"] != "create" and _hash(write["before_sha256"])),
                      "BEFORE_IMAGE_REQUIRED")
            _need(isinstance(binding["inputs"], list) and bool(binding["inputs"]), "INPUTS_REQUIRED")
            aliases = set()
            for source in binding["inputs"]:
                _path(source["path"])
                _need(source["path"].casefold() not in aliases and _hash(source["sha256"]),
                      "SOURCE_HASH_OR_ALIAS")
                aliases.add(source["path"].casefold())
                _need(_time(source["verified_at"]) <= now, "FUTURE_SOURCE_VERIFICATION")
            _need(isinstance(binding["evidence"], dict) and bool(binding["evidence"]),
                  "EVIDENCE_REQUIRED")
            aliases = set()
            for reference in binding["evidence"].values():
                _path(reference["path"])
                _need(reference["path"].casefold() not in aliases and _hash(reference["sha256"]),
                      "EVIDENCE_HASH_OR_ALIAS")
                aliases.add(reference["path"].casefold())
            _need(isinstance(binding["gates"], dict) and bool(binding["gates"]) and
                  all(v == "APPROVED" for v in binding["gates"].values()), "GATES_NOT_APPROVED")

        if not check("structural_status", structure):
            return result

        def maintenance_authorization():
            _need(isinstance(config, dict), "MAINTENANCE_SCOPE_REQUIRED")
            _need(isinstance(human_authorization, dict), "EXPLICIT_HUMAN_AUTHORIZATION_REQUIRED")
            attestation.update(deepcopy(human_authorization))
            _need(type(attestation["synthetic"]) is bool, "EVIDENCE_CLASS_REQUIRED")
            result["synthetic"] = attestation["synthetic"]
            _need(_time(attestation["checked_at"]) <= now < _time(attestation["expires_at"]) and
                  _time(attestation["not_before"]) <= _time(attestation["approved_at"]) <=
                  _time(attestation["checked_at"]) and attestation["withdrawn"] is False,
                  "EXPIRED_WITHDRAWN_OR_INVALID_APPROVAL")

        if not check("human_authorization_evidence", maintenance_authorization):
            return result

        def scope():
            _need(_exact(attestation["binding"], binding), "APPROVED_REQUEST_MISMATCH")
            _need(_exact(binding["target"], config["target"]) and
                  binding["workcell"] == config["workcell"] and
                  binding["executor"] == config["executor"], "TARGET_WORKCELL_OR_EXECUTOR_MISMATCH")
            _need(isinstance(config["required_gates"], list) and bool(config["required_gates"]) and
                  set(config["required_gates"]) <= set(binding["gates"]), "REQUIRED_GATES_MISSING")
            _need(attestation["audit_reference"] == binding["audit_reference"] and
                  _text(attestation["audit_preservation_reference"]), "PRESERVED_AUDIT_REQUIRED")

        if not check("scope_status", scope):
            return result

        def approvals():
            authorities = config["authorities"]
            _need(set(authorities) == ROLES and all(_text(v) for v in authorities.values()),
                  "HUMAN_AUTHORITIES_REQUIRED")
            approvals = attestation["approvals"]
            _need(isinstance(approvals, list) and len(approvals) == 2 and
                  {a["role"] for a in approvals} == ROLES, "SEPARATE_CAPACITY_APPROVALS_REQUIRED")
            references = {}
            for approval in approvals:
                _need(approval["human"] == authorities[approval["role"]] and
                      approval["approved"] is True and _text(approval["role_basis_reference"]), "GOVERNANCE_CAPACITY_UNVERIFIED")
                reference = approval["approval_reference"]
                _need(_text(reference) and (reference not in references or
                      references[reference] == approval['human']), "SEPARATE_APPROVAL_EVENTS_REQUIRED")
                # One interaction can explicitly exercise multiple capacities
                # of one human. Distinct authorities retain distinct sources.
                references[reference] = approval['human']
                _need(_time(attestation["not_before"]) <= _time(approval["approved_at"]) <=
                      _time(attestation["checked_at"]), "CAPACITY_APPROVAL_TIME_INVALID")
                if approval["role"] == "Human Director":
                    _need(_text(approval["designation_reference"]), "DIRECTOR_DESIGNATION_REQUIRED")

        if check("human_authorization_evidence", approvals,
                 "SYNTHETIC_VALID" if result["synthetic"] else "DECLARED_HUMAN_APPROVAL"):
            result["status"] = "SUPERVISED_EVIDENCE_VALID"
        # No declaration or result can grant production execution in this slice.
        return result
