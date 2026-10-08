#!/usr/bin/env python3
"""Fail-closed release validation for the common-dev LinkStart plugin."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "plugins" / "linkstart"
GENERATED = ROOT / "codex" / "plugins" / "linkstart"
SKILLS = {"link-start"}
SOURCE_PLUGIN_VERSION = "0.4.1"
GENERATED_PLUGIN_VERSION = "0.3.0+codex.20260828033021"
RUNTIME_VERSION = "0.1.5"
CHECKSUM_SCHEMA_VERSION = 1
PROTOCOL_MAJOR = "v1"
TARGET_FILES = {
    "linux-x64-musl": "linkstart",
    "windows-x64": "linkstart.exe",
    "macos-universal": "linkstart",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def is_executable(path: Path) -> bool:
    # Windows filesystems carry no exec bit; the mode that ships is the one git records.
    if os.name == "nt":
        listed = subprocess.run(
            ["git", "-C", str(ROOT), "ls-files", "-s", "--", str(path.relative_to(ROOT))],
            capture_output=True, text=True,
        ).stdout
        return listed.startswith("100755")
    return bool(path.stat().st_mode & stat.S_IXUSR)


def load(path: Path, errors: list[str]) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"json_invalid: {path.relative_to(ROOT)}: {exc}")
        return {}


def catalog_entry(catalog: dict, name: str) -> dict | None:
    matches = [entry for entry in catalog.get("plugins", []) if entry.get("name") == name]
    return matches[0] if len(matches) == 1 else None


def main() -> int:
    errors: list[str] = []
    blockers: list[str] = []

    for path in ROOT.rglob("*.json"):
        if any(part in {"prototype-hub", ".strategic-advance", ".scratch"} for part in path.parts):
            continue
        load(path, errors)

    source_manifest = load(SOURCE / ".claude-plugin" / "plugin.json", errors)
    generated_manifest = load(GENERATED / ".codex-plugin" / "plugin.json", errors)
    if source_manifest.get("name") != "linkstart" or source_manifest.get("version") != SOURCE_PLUGIN_VERSION:
        errors.append(f"manifest_mismatch: Claude linkstart must be version {SOURCE_PLUGIN_VERSION}")
    if generated_manifest.get("name") != "linkstart" or generated_manifest.get("version") != GENERATED_PLUGIN_VERSION:
        errors.append(f"manifest_mismatch: generated Codex linkstart must be version {GENERATED_PLUGIN_VERSION}")

    source_skills = {p.parent.name for p in (SOURCE / "skills").glob("*/SKILL.md")}
    generated_skills = {p.parent.name for p in (GENERATED / "skills").glob("*/SKILL.md")}
    if source_skills != SKILLS:
        errors.append(f"skill_set_mismatch: Claude has {sorted(source_skills)}, expected {sorted(SKILLS)}")
    if generated_skills != SKILLS:
        errors.append(f"skill_set_mismatch: Codex has {sorted(generated_skills)}, expected {sorted(SKILLS)}")

    claude_catalog = load(ROOT / ".claude-plugin" / "marketplace.json", errors)
    layout_a = load(ROOT / ".agents" / "plugins" / "marketplace.json", errors)
    layout_b = load(ROOT / "codex" / ".agents" / "plugins" / "marketplace.json", errors)
    ce = catalog_entry(claude_catalog, "linkstart")
    ae = catalog_entry(layout_a, "linkstart")
    be = catalog_entry(layout_b, "linkstart")
    if not ce or ce.get("source") != "./plugins/linkstart" or ce.get("version") != SOURCE_PLUGIN_VERSION:
        errors.append("catalog_mismatch: Claude linkstart entry")
    if not ae or ae.get("source", {}).get("path") != "./codex/plugins/linkstart":
        errors.append("catalog_mismatch: Codex Layout A linkstart entry")
    if not be or be.get("source", {}).get("path") != "./plugins/linkstart":
        errors.append("catalog_mismatch: Codex Layout B linkstart entry")
    for label, entry in (("Layout A", ae), ("Layout B", be)):
        if not entry or entry.get("policy") != {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}:
            errors.append(f"catalog_policy_mismatch: {label}")

    for source_file in (SOURCE / "skills").rglob("*"):
        if (
            not source_file.is_file()
            or source_file.name == "SKILL.md"
            or source_file.suffix == ".pyc"
            or "__pycache__" in source_file.parts
            or "assets" in source_file.parts
        ):
            continue
        rel = source_file.relative_to(SOURCE)
        generated_file = GENERATED / rel
        if not generated_file.is_file():
            errors.append(f"generated_asset_missing: {rel}")
        elif source_file.read_bytes() != generated_file.read_bytes():
            errors.append(f"generated_asset_changed: {rel}")

    source_assets = SOURCE / "skills" / "link-start" / "assets"
    generated_assets = GENERATED / "skills" / "link-start" / "assets"
    checksums_path = source_assets / "checksums.json"
    if not checksums_path.is_file():
        blockers.append("runtime_binary_missing: skills/link-start/assets/checksums.json")
        checksums = {}
    else:
        checksums = load(checksums_path, errors)
    if checksums and (
        set(checksums) != {"schemaVersion", "runtimeVersion", "protocolMajor", "releaseTag", "artifacts"}
        or checksums.get("schemaVersion") != CHECKSUM_SCHEMA_VERSION
        or checksums.get("runtimeVersion") != RUNTIME_VERSION
        or checksums.get("protocolMajor") != PROTOCOL_MAJOR
        or checksums.get("releaseTag") != f"v{checksums.get('runtimeVersion')}"
    ):
        errors.append("checksums_schema_invalid")

    records = {
        item.get("target"): item
        for item in checksums.get("artifacts", [])
        if isinstance(item, dict) and item.get("target")
    }
    for target, filename in TARGET_FILES.items():
        rel = Path("bin") / target / filename
        src = source_assets / rel
        dst = generated_assets / rel
        record = records.get(target)
        if not src.is_file():
            blockers.append(f"runtime_binary_missing: skills/link-start/assets/{rel}")
            continue
        if not record:
            blockers.append(f"runtime_binary_missing: checksum record for {target}")
            continue
        expected_record_fields = {
            "target",
            "path",
            "size",
            "sha256",
            "sourceRepository",
            "sourceTag",
            "sourceCommit",
            "workflowRun",
        }
        if set(record) != expected_record_fields:
            errors.append(f"runtime_binary_invalid: {target} checksum record fields")
        if record.get("sourceRepository") != "https://github.com/TLOGBen/LinkStart":
            errors.append(f"runtime_binary_invalid: {target} source repository")
        if record.get("sourceTag") != checksums.get("releaseTag"):
            errors.append(f"runtime_binary_invalid: {target} source tag")
        if not isinstance(record.get("sourceCommit"), str) or not record.get("sourceCommit"):
            errors.append(f"runtime_binary_invalid: {target} source commit")
        if not isinstance(record.get("workflowRun"), str) or not record.get("workflowRun"):
            errors.append(f"runtime_binary_invalid: {target} workflow provenance")
        if record.get("path") != rel.as_posix() or record.get("size") != src.stat().st_size or record.get("sha256") != digest(src):
            errors.append(f"runtime_binary_invalid: {target} metadata/hash/size")
        if target != "windows-x64" and not is_executable(src):
            errors.append(f"runtime_binary_invalid: {target} source mode is not executable")
        if not dst.is_file():
            errors.append(f"generated_binary_missing: {target}")
        elif (src.stat().st_size, digest(src)) != (dst.stat().st_size, digest(dst)):
            errors.append(f"generated_binary_changed: {target} hash/size")
        elif target != "windows-x64" and stat.S_IMODE(src.stat().st_mode) != stat.S_IMODE(dst.stat().st_mode):
            errors.append(f"generated_binary_changed: {target} mode")

    if checksums_path.is_file():
        generated_checksums = generated_assets / "checksums.json"
        if not generated_checksums.is_file() or checksums_path.read_bytes() != generated_checksums.read_bytes():
            errors.append("generated_asset_changed: checksums.json")

    if errors:
        print("LINKSTART_RELEASE_INVALID")
        for item in errors:
            print(f"ERROR {item}")
    if blockers:
        print("LINKSTART_RELEASE_BLOCKED")
        for item in blockers:
            print(f"BLOCKER {item}")
    if errors or blockers:
        return 2
    print("LINKSTART_RELEASE_VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
