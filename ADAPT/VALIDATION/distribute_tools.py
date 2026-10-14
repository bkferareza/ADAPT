"""Narrow new-instance tooling copy/verification step; not a scaffold engine."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys


def distribute(framework, instance, verify=False):
    framework, instance = Path(framework).resolve(), Path(instance).resolve()
    source, target = framework / "TOOLS", instance / "TOOLS"
    if not instance.is_dir() or instance == framework or instance.is_relative_to(framework):
        raise ValueError("Instance must be an existing scaffold target outside framework source")
    if not (instance / "02_DIRECTOR_LANE/PROJECT_CONTROL_PLANE.md").is_file():
        raise ValueError("Instance must already contain copied canonical starters")
    manifest = json.loads((source / "MANIFEST.json").read_text(encoding="utf-8"))
    expected = manifest["files"]
    for name, digest in expected.items():
        path = (source / name).resolve()
        if not path.is_relative_to(source.resolve()) or path.is_symlink() or not path.is_file():
            raise ValueError("Unsafe or missing distribution source")
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError("Source distribution hash mismatch: " + name)
    if not verify:
        if target.exists():
            raise ValueError("TOOLS already exists; existing instances are never overwritten")
        target.mkdir()
        try:
            for name in sorted(expected):
                destination = target / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source / name, destination)
            shutil.copyfile(source / "MANIFEST.json", target / "MANIFEST.json")
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
    return {"files": expected, "verified": True, "prospective_only": True}


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
