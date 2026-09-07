#!/usr/bin/env python3
"""Export opt-in skill laboratories through the installed transfer, without replacement.

Review --preflight in a separate invocation before export. Staging remains for audit.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tomllib
import yaml
sys.dont_write_bytecode = True

REPO = Path(__file__).resolve().parent.parent
ROOT_TOKEN = "${CLAUDE_PLUGIN_ROOT}"
RESOURCE_TOKEN = "${LAB_SKILL_DIR}"
PLUGIN_SPECS = {
    "common-lab": {"skills": 11, "explicit": ["lab-wait-what"],
                   "roles": {"lab-executor": ["lab-delegate", "lab-strategic-advance"],
                             "lab-calibrator": ["lab-strategic-advance"]}},
    "baransu-lab": {"skills": 4, "explicit": [],
                    "roles": {"lab-verifier": ["lab-review", "lab-seal"]}},
    "estimate-lab": {"skills": 1, "explicit": [],
                     "roles": {"lab-estimate-auditor": ["lab-estimate"]}},
}
ESTIMATE_TESTS_DROP = "skill-root 子目錄 `tests/` 未複製（非 scripts/references/assets/evals/agents 標準目錄）"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def inventory(root):
    return {str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(root.rglob("*")) if path.is_file() and "__pycache__" not in path.parts}


def digest(items):
    return hashlib.sha256(json.dumps(items, sort_keys=True).encode()).hexdigest()


def preflight(args):
    for value in (args.output, args.staging, args.report_dir):
        require(not Path(value).is_symlink(), "TARGET_MISMATCH: symbolic-link target")
    source, target, staging, reports, transfer = (Path(value).resolve() for value in
        (args.source, args.output, args.staging, args.report_dir, args.transfer))
    require((source / ".claude-plugin/plugin.json").is_file(), "Missing source manifest")
    require(transfer.is_file(), "Missing installed transfer.py")
    require(not target.exists() and not staging.exists(), "TARGET_MISMATCH: output/staging exists")
    for candidate in (target, staging):
        require(candidate != source and not candidate.is_relative_to(source)
                and not source.is_relative_to(candidate), "TARGET_MISMATCH: source overlap")
        require(candidate.parent != candidate, "TARGET_MISMATCH: protected root")
    require(not target.is_relative_to(staging) and not staging.is_relative_to(target),
            "TARGET_MISMATCH: staging/output overlap")
    for name in ("transfer-report.txt", "export-receipt.json"):
        require(not (reports / name).exists(), "TARGET_MISMATCH: report already exists: " + name)
    manifest = json.loads((source / ".claude-plugin/plugin.json").read_text())
    require(manifest["name"] in PLUGIN_SPECS and manifest.get("defaultEnabled") is False,
            "Expected a supported opt-in laboratory source")
    for protected in (source, target, staging):
        require(reports != protected and not reports.is_relative_to(protected),
                "TARGET_MISMATCH: reports overlap source/output/staging")
    overlay = Path(args.interface).resolve() if args.interface else (
        REPO / "codex-metadata" / manifest["name"] / "plugin-interface.json")
    require(overlay.is_file(), "Missing source UI metadata overlay")
    interface = json.loads(overlay.read_text(encoding="utf-8"))
    require(isinstance(interface, dict), "UI metadata must be an interface object")
    validator = Path(args.validator).resolve() if args.validator else None
    require(validator is None or validator.is_file(), "Missing plugin validator")
    files = inventory(source)
    require(not any(path.is_symlink() for path in source.rglob("*")),
            "TARGET_MISMATCH: source contains symbolic links")
    skill_ui = {}
    for path in sorted((REPO / "codex-metadata" / manifest["name"]).glob("*/openai.yaml")):
        require(not path.is_symlink() and (source / "skills" / path.parent.name / "SKILL.md").is_file(),
                "UI metadata must belong to an authored skill")
        skill_ui[str(path.resolve())] = hashlib.sha256(path.read_bytes()).hexdigest()
    return {"verdict": "TARGET_MATCH", "source": str(source), "output": str(target),
            "staging": str(staging), "report_dir": str(reports), "transfer": str(transfer),
            "plugin": manifest["name"], "version": manifest["version"],
            "interface": str(overlay), "interface_sha256": hashlib.sha256(overlay.read_bytes()).hexdigest(),
            "validator": str(validator) if validator else None,
            "output_exists": False, "staging_exists": False, "source_files": files,
            "source_sha256": digest(files),
            "skill_ui_sources": skill_ui,
            "recovery": "Existing state untouched; new staging retained for reproducibility."}


def load_transfer(path):
    spec = importlib.util.spec_from_file_location("common_lab_installed_transfer", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def preserve_estimate_tests(module, source):
    """Restore the one audited auxiliary directory before the unchanged closure guard.

    The installed module and its original dropped-content report remain untouched.
    No other skill or non-standard directory is implicitly accepted.
    """
    original = module.copy_aux
    expected = (source / "skills/lab-estimate").resolve()

    def copy_aux_with_tests(skill_source, target, report, known_skills=frozenset()):
        original(skill_source, target, report, known_skills)
        if skill_source.resolve() == expected:
            tests = skill_source / "tests"
            require(tests.is_dir() and not (target / "tests").exists(),
                    "Expected fresh Estimate tests destination")
            require(not any(path.is_symlink() for path in tests.rglob("*")),
                    "Estimate tests must not contain symbolic links")
            shutil.copytree(tests, target / "tests", ignore=shutil.ignore_patterns("__pycache__"))
            require(inventory(tests) == inventory(target / "tests"), "Estimate tests byte mismatch")

    module.copy_aux = copy_aux_with_tests


def restore_skill_ui(package, audit):
    restored = []
    for value, expected_hash in audit["skill_ui_sources"].items():
        source = Path(value)
        require(hashlib.sha256(source.read_bytes()).hexdigest() == expected_hash,
                "Skill UI metadata changed during export")
        overlay = yaml.safe_load(source.read_text(encoding="utf-8"))
        require(isinstance(overlay, dict) and set(overlay) <= {"interface", "policy", "dependencies"},
                "Unrecognized skill UI metadata")
        target = package / "skills" / source.parent.name / "agents/openai.yaml"
        current = yaml.safe_load(target.read_text(encoding="utf-8")) if target.is_file() else {}
        current = current or {}
        for section, values in overlay.items():
            require(isinstance(values, dict), "Skill UI section must be an object")
            current.setdefault(section, {}).update(values)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(yaml.safe_dump(current, allow_unicode=True, sort_keys=False), encoding="utf-8")
        restored.append(str(target.relative_to(package)))
    return restored


def adapt_resources(package):
    adapted = []
    for skill in sorted((package / "skills").iterdir()):
        if not (skill / "SKILL.md").is_file():
            continue
        changed = []
        for path in sorted(skill.rglob("*.md")):
            text = path.read_text(encoding="utf-8")
            if ROOT_TOKEN not in text:
                continue
            updated = text
            for referenced_skill, relative in re.findall(
                    re.escape(ROOT_TOKEN) + r"/skills/([A-Za-z0-9_-]+)/([A-Za-z0-9_./-]+)", text):
                relative = relative.rstrip(".")
                resolved = (package / "skills" / referenced_skill / relative).resolve()
                require(resolved.is_relative_to(package.resolve()) and resolved.is_file(),
                        "Resource does not resolve inside package: " + relative)
                anchor = ROOT_TOKEN + "/skills/" + referenced_skill + "/"
                replacement = RESOURCE_TOKEN + ("/" if referenced_skill == skill.name
                                                else "/../" + referenced_skill + "/")
                updated = updated.replace(anchor, replacement)
            for agent in re.findall(re.escape(ROOT_TOKEN) + r"/agents/([A-Za-z0-9_-]+)\.md", text):
                definition = package / ".codex-agents" / (agent + ".toml")
                require(definition.is_file(), "Missing generated bundled agent: " + agent)
                updated = updated.replace(ROOT_TOKEN + "/agents/" + agent + ".md",
                                          RESOURCE_TOKEN + "/../../.codex-agents/" + agent + ".toml")
            path.write_text(updated, encoding="utf-8")
            changed.append(str(path.relative_to(package)))
        if changed:
            entry = skill / "SKILL.md"
            content = entry.read_text(encoding="utf-8")
            boundary = content.find("\n---", 4)
            require(content.startswith("---\n") and boundary != -1, "Malformed frontmatter")
            end = content.find("\n", boundary + 1) + 1
            adapter = (
                "\n## Lab Resource Resolution\n\n"
                "Before reading a bundled reference or running a bundled script, resolve "
                "the absolute directory containing this loaded SKILL.md as LAB_SKILL_DIR. "
                "Verify that its frontmatter name is " + skill.name + ". Use the resulting "
                "absolute path in file tools; for shell examples, bind LAB_SKILL_DIR to "
                "that verified path in the same shell invocation. This variable is not "
                "preconfigured by Codex. Never guess an install-cache path or use the "
                "working directory as the skill root. If this entrypoint or a referenced "
                "resource cannot be read, stop that operation with "
                "SKILL_RESOURCE_MISSING and report the missing path.\n\n")
            entry.write_text(content[:end] + adapter + content[end:], encoding="utf-8")
            adapted.extend(changed)
    for path in package.rglob("*.md"):
        require(ROOT_TOKEN not in path.read_text(encoding="utf-8"), "Unresolved root: " + str(path))
    return adapted


def verify(source, staging, plugin):
    spec = PLUGIN_SPECS[plugin]
    package = staging / "plugins" / plugin
    manifest = json.loads((package / ".codex-plugin/plugin.json").read_text())
    require(manifest["name"] == plugin and manifest["skills"] == "./skills/", "Manifest mismatch")
    interface = manifest["interface"]
    for field in ("displayName", "shortDescription", "longDescription", "developerName", "category"):
        require(isinstance(interface.get(field), str) and interface[field].strip(),
                "Missing interface field: " + field)
    require(isinstance(interface.get("capabilities"), list)
            and all(isinstance(item, str) and item.strip() for item in interface["capabilities"]),
            "Invalid interface capabilities")
    require(isinstance(interface.get("defaultPrompt"), list)
            and 0 < len(interface["defaultPrompt"]) <= 3
            and all(isinstance(item, str) and 0 < len(item) <= 128 for item in interface["defaultPrompt"]),
            "Invalid interface default prompts")
    catalog = json.loads((staging / ".agents/plugins/marketplace.json").read_text())
    require(catalog["name"] == plugin and len(catalog["plugins"]) == 1, "Catalog not isolated")
    require(catalog["plugins"][0]["source"]["path"] == "./plugins/" + plugin, "Catalog source mismatch")
    skills = sorted((package / "skills").glob("*/SKILL.md"))
    require(len(skills) == spec["skills"], "Unexpected generated skill count")
    for entry in skills:
        data = yaml.safe_load(entry.read_text().split("---", 2)[1])
        require(data["name"] == entry.parent.name, "Skill identity mismatch")
    for skill in spec["explicit"]:
        policy = yaml.safe_load((package / "skills" / skill / "agents/openai.yaml").read_text())
        require(policy["policy"]["allow_implicit_invocation"] is False, "Explicit-only policy lost")
    for name, consumers in spec["roles"].items():
        role = tomllib.loads((package / ".codex-agents" / (name + ".toml")).read_text())
        require(role["name"] == name and role["developer_instructions"].strip(), "Missing role")
        require(not any(key in role for key in ("model", "model_reasoning_effort", "sandbox_mode")),
                "Role must inherit runtime policy")
        for consumer in consumers:
            text = (package / "skills" / consumer / "SKILL.md").read_text()
            require("AGENT_DEFINITION_MISSING" in text and ".codex-agents/" + name + ".toml" in text,
                    "Bundled-agent resolver lost")
    copied = []
    for path in source.rglob("*"):
        relative = path.relative_to(source)
        if path.is_file() and ("scripts" in relative.parts or "assets" in relative.parts
                               or "tests" in relative.parts or path.name == "requirements.lock"):
            if "__pycache__" in relative.parts:
                continue
            require((package / relative).read_bytes() == path.read_bytes(), "Copied bytes changed: " + str(relative))
            copied.append(str(relative))
    return {"skill_count": len(skills), "explicit_only_skills": spec["explicit"], "bundled_agent_resolver": True,
            "unchanged_scripts_assets": copied}


def export(args):
    audit = preflight(args)
    print(json.dumps(audit, indent=2))
    if args.preflight:
        return
    source, target, staging, report_dir = (Path(audit[name]) for name in
        ("source", "output", "staging", "report_dir"))
    module = load_transfer(audit["transfer"])
    if audit["plugin"] == "estimate-lab":
        preserve_estimate_tests(module, source)
    reports, summary = module.transfer_plugin(source, staging)
    require(not summary.get("unhandled_components") and summary.get("content_closure_verified"),
            "Incomplete component closure")
    require(not summary.get("manifest_manual") and not summary.get("aux_manual"),
            "Unclassified plugin-level manual review")
    package = staging / "plugins" / audit["plugin"]
    adapted = adapt_resources(package)
    restored_ui = restore_skill_ui(package, audit)
    overlay = Path(audit["interface"])
    require(hashlib.sha256(overlay.read_bytes()).hexdigest() == audit["interface_sha256"],
            "UI metadata changed during export")
    manifest_path = package / ".codex-plugin/plugin.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest.setdefault("interface", {}).update(json.loads(overlay.read_text(encoding="utf-8")))
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    catalog_path = staging / ".agents/plugins/marketplace.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    catalog.setdefault("interface", {})["displayName"] = manifest["interface"]["displayName"]
    catalog_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    followups = []
    for report in reports:
        require(not report.skipped, "Skipped skill content requires review")
        for item in report.dropped:
            require(audit["plugin"] == "estimate-lab" and report.skill_name == "lab-estimate"
                    and item == ESTIMATE_TESTS_DROP, "Unclassified dropped skill content: " + item)
            followups.append({"skill": report.skill_name, "item": item, "action": "refresh-mapping",
                              "resolved_by": "tests copied before unchanged content-closure guard; bytes verified"})
        for item in report.manual_review:
            require("CLAUDE_PLUGIN_ROOT" in item, "Unclassified manual review: " + item)
            followups.append({"skill": report.skill_name, "item": item, "action": "refresh-mapping",
                              "resolved_by": "verified LAB_SKILL_DIR adapter"})
    for item in summary.get("manifest_dropped", []):
        followups.append({"skill": "manifest", "item": item, "action": "accept-as-lossy",
                          "resolved_by": "No Codex manifest field; AVAILABLE catalog remains opt-in"})
    checks = verify(source, staging, audit["plugin"])
    if audit["validator"]:
        validation = subprocess.run([sys.executable, audit["validator"], str(package)],
                                    capture_output=True, text=True)
        require(validation.returncode == 0, "Plugin validator failed: " + validation.stdout + validation.stderr)
        checks["plugin_validator"] = validation.stdout.strip()
    require(inventory(source) == audit["source_files"], "Source changed during export")
    require(not target.exists(), "Output appeared during export")
    shutil.copytree(staging, target)
    report_dir.mkdir(parents=True, exist_ok=True)
    report_text = "# " + audit["plugin"] + " transfer receipt\n\n" + json.dumps(summary, ensure_ascii=False, indent=2)
    report_text += "\n\n" + "\n".join(report.render() for report in reports)
    report_text += "\n### Verified laboratory adapter\n\n"
    report_text += "- Source unchanged; script/asset bytes and complete agent resolver verified.\n"
    report_text += "- Package resources use verified LAB_SKILL_DIR, not a presumed Codex environment variable.\n"
    report_text += "- Codex interface fields are overlaid from the versioned codex-metadata source.\n"
    report_text += "\n### Next-port follow-ups\n\n"
    report_text += "\n".join("- " + item["skill"] + ": " + item["item"] + " - " + chr(96) +
                             item["action"] + chr(96) + "; " + item["resolved_by"]
                             for item in followups) if followups else "- none"
    with (report_dir / "transfer-report.txt").open("x", encoding="utf-8") as stream:
        stream.write(report_text + "\n")
    receipt = {"exported_at": datetime.now(timezone.utc).isoformat(), "preflight": audit,
               "transfer_sha256": hashlib.sha256(Path(audit["transfer"]).read_bytes()).hexdigest(),
               "source_sha256": audit["source_sha256"], "output_sha256": digest(inventory(target)),
               "interface_source": audit["interface"], "interface_sha256": audit["interface_sha256"],
               "skill_ui_sources": audit["skill_ui_sources"], "restored_skill_ui": restored_ui,
               "output_files": inventory(target), "adapted_files": adapted, "checks": checks,
               "followups": followups, "staging_retained": str(staging)}
    with (report_dir / "export-receipt.json").open("x", encoding="utf-8") as stream:
        json.dump(receipt, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps({"status": "EXPORTED", "output": str(target), "checks": checks,
                      "source_sha256": receipt["source_sha256"], "output_sha256": receipt["output_sha256"]},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default=str(REPO / "plugins/common-lab"))
    parser.add_argument("--output", default=str(REPO / "experiments/common-lab"))
    parser.add_argument("--report-dir", default=str(REPO / "docs/experiments/common-lab"))
    parser.add_argument("--staging", required=True, help="A separate, nonexistent staging directory")
    parser.add_argument("--transfer", required=True, help="Installed codex-skill-transfer/scripts/transfer.py")
    parser.add_argument("--interface", help="UI metadata source; defaults to codex-metadata/<plugin>/plugin-interface.json")
    parser.add_argument("--validator", help="Optional installed plugin-creator/scripts/validate_plugin.py")
    parser.add_argument("--preflight", action="store_true", help="Read-only source/target inspection")
    try:
        export(parser.parse_args())
    except (ValueError, OSError, KeyError) as error:
        print("EXPORT_ERROR: " + str(error), file=sys.stderr)
        sys.exit(2)
