"""Narrow new-instance tooling copy/verification step; not a scaffold engine."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys


RECOVERY_CONTRACTS = (
    "00_FRAMEWORK/GOVERNANCE_RULES.md",
    "15_COMMANDS_AND_DRIVERS/CONTROL_PLANE_SCHEMA.md",
    "15_COMMANDS_AND_DRIVERS/MUTATION_PERMISSION_MATRIX.md",
    "15_COMMANDS_AND_DRIVERS/STOP_RULES.md",
    "10_CONTEXT_ECONOMY/CONTEXT_RULES.md",
    "07_GUARDRAILS/CONTEXT_GUARDRAIL.md",
)


def _contract_body(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    # Scaffold population changes only these instance header values. Preserve
    # every other byte of contract content (apart from supported line endings).
    for index in range(min(8, len(lines))):
        if lines[index].partition(":")[0] in {"PROJECT", "VERSION", "INITIALIZED", "LAST_UPDATED"}:
            lines[index] = lines[index].partition(":")[0] + ": <instance header>"
    return lines


def distribute(framework, instance, verify=False):
    framework, instance = Path(framework).resolve(), Path(instance).resolve()
    source, target = framework / "TOOLS", instance / "TOOLS"
    if not instance.is_dir() or instance == framework or instance.is_relative_to(framework):
        raise ValueError("Instance must be an existing scaffold target outside framework source")
    if not (instance / "02_DIRECTOR_LANE/PROJECT_CONTROL_PLANE.md").is_file():
        raise ValueError("Instance must already contain copied canonical starters")
    manifest = json.loads((source / "MANIFEST.json").read_text(encoding="utf-8"))
    expected = manifest["files"]
    # Same manifest, with instance-relative paths for siblings of TOOLS. Keep
    # recovery files in VALIDATION so their existing relative imports stay intact.
    extra = manifest.get("instance_files", {})
    if extra:
        for name in RECOVERY_CONTRACTS:
            path = instance / name
            if path.resolve() != path or not path.is_file() or _contract_body(path) != _contract_body(
                    framework / "CANONICAL_STARTERS" / name):
                raise ValueError("Missing or mismatched recovery governance contract: " + name)
    for name, digest in extra.items():
        relative = Path(name)
        if relative.is_absolute() or ".." in relative.parts or relative.parts[0] != "VALIDATION":
            raise ValueError("Unsafe instance distribution path: " + name)
        path = framework / relative
        if path.is_symlink() or path.resolve() != path or not path.is_file():
            raise ValueError("Unsafe or missing instance distribution source: " + name)
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError("Source distribution hash mismatch: " + name)
        destination = instance / relative
        if destination.resolve() != destination:
            raise ValueError("Unsafe instance distribution target: " + name)
    for name, digest in expected.items():
        relative = Path(name)
        if relative.is_absolute() or ".." in relative.parts or not relative.parts:
            raise ValueError("Unsafe tooling distribution path: " + name)
        path = (source / name).resolve()
        if not path.is_relative_to(source.resolve()) or path.is_symlink() or not path.is_file():
            raise ValueError("Unsafe or missing distribution source")
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError("Source distribution hash mismatch: " + name)
        if (target / relative).resolve() != target / relative:
            raise ValueError("Unsafe tooling distribution target: " + name)
    if not verify:
        if target.exists():
            raise ValueError("TOOLS already exists; existing instances are never overwritten")
        if any((instance / name).exists() for name in extra):
            raise ValueError("Instance tooling already exists; never overwrite")
        target.mkdir()
        try:
            for name in sorted(expected):
                destination = target / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source / name, destination)
            shutil.copyfile(source / "MANIFEST.json", target / "MANIFEST.json")
            for name in sorted(extra):
                destination = instance / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(framework / name, destination)
        except OSError:
            raise ValueError("Tool copy failed; partial new target preserved for inspection") from None
    target_resolved = target.resolve()
    if target_resolved != target or not target_resolved.is_relative_to(instance):
        raise ValueError("Target tools resolve outside the explicit instance")
    actual = {p.relative_to(target).as_posix() for p in target.rglob("*") if p.is_file()}
    if actual != set(expected) | {"MANIFEST.json"}:
        raise ValueError("Unexpected/missing distributed files")
    for name, digest in expected.items():
        path = (target / name).resolve()
        if not path.is_relative_to(target) or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError("Distributed hash mismatch: " + name)
    if (target / "MANIFEST.json").read_bytes() != (source / "MANIFEST.json").read_bytes():
        raise ValueError("Distributed manifest differs from framework source")
    for name, digest in extra.items():
        path = instance / name
        if not path.is_file() or path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError("Distributed hash mismatch: " + name)
    return {"files": expected, "instance_files": extra,
            "verified": True, "prospective_only": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--framework", required=True)
    parser.add_argument("--instance", required=True)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    try:
        print(json.dumps(distribute(args.framework, args.instance, args.verify), indent=2))
        return 0
    except (ValueError, OSError) as error:
        print("Tool distribution failed: " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
