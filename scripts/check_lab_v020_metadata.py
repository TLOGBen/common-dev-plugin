#!/usr/bin/env python3
"""Resolve one verified validator/spec mismatch without editing a frozen package.

The installed quick validator excludes compatibility. Agent Skills specification
allows a nonempty string up to 500 characters. Validate that field separately,
then run the unmodified quick validator on an exact temporary projection of all
remaining metadata and the unchanged body. Original failures remain in the log.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import yaml

ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quick-validator", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    assert not args.receipt.exists() and not args.receipt.is_symlink()
    root = Path(tempfile.mkdtemp(prefix="lab020-metadata-projections-"))
    items = []
    for name in ("common-lab", "baransu-lab", "estimate-lab"):
        package = ROOT / "experiments" / (name + "-v0.2.0") / "plugins" / name
        for entry in sorted(package.glob("skills/*/SKILL.md")):
            original_bytes = entry.read_bytes()
            text = original_bytes.decode("utf-8")
            _, frontmatter, body = text.split("---", 2)
            data = yaml.safe_load(frontmatter)
            compatibility = data.pop("compatibility")
            assert isinstance(compatibility, str) and 1 <= len(compatibility) <= 500
            assert data["name"] == entry.parent.name
            projection = root / name / entry.parent.name / "SKILL.md"
            projection.parent.mkdir(parents=True)
            with projection.open("x", encoding="utf-8") as stream:
                stream.write("---\n" + yaml.safe_dump(data, allow_unicode=True, sort_keys=False) + "---" + body)
            projected = projection.read_text(encoding="utf-8").split("---", 2)
            assert projected[2] == body and yaml.safe_load(projected[1]) == data
            process = subprocess.run([sys.executable, "-B", str(args.quick_validator), str(projection.parent)],
                                     capture_output=True, text=True, timeout=10)
            assert entry.read_bytes() == original_bytes
            items.append({"source": str(entry.relative_to(ROOT)), "source_sha256": hashlib.sha256(original_bytes).hexdigest(),
                          "compatibility": compatibility, "compatibility_spec_check": "PASS",
                          "projection": str(projection), "body_unchanged": True,
                          "quick_validator_exit": process.returncode, "stdout": process.stdout, "stderr": process.stderr})
    assert len(items) == 15
    status = "PASS_WITH_VALIDATOR_COMPATIBILITY_NOTE" if all(i["quick_validator_exit"] == 0 for i in items) else "FAIL"
    with args.receipt.open("x", encoding="utf-8") as stream:
        json.dump({"status": status, "observed_utc": datetime.now(timezone.utc).isoformat(),
                   "basis": "https://agentskills.io/specification#compatibility-field",
                   "original_validation": "validation.json", "retained_projections": str(root), "skills": items,
                   "limits": "Not an unmodified quick-validator PASS on the frozen files; compatibility separately checked. No runtime behavior claim."},
                  stream, ensure_ascii=False, indent=2)
    print(json.dumps({"status": status, "skill_count": len(items), "receipt": str(args.receipt)}))
    raise SystemExit(0 if status != "FAIL" else 1)


if __name__ == "__main__":
    main()
