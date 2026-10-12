#!/usr/bin/env python3
"""Validate Claude and both hand-maintained Codex marketplace layouts."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def entries(path):
    catalog = load(path)
    assert catalog["name"] == "common-dev", f"Unexpected marketplace id: {path}"
    plugins = catalog["plugins"]
    result = {entry["name"]: entry for entry in plugins}
    assert len(result) == len(plugins), f"Duplicate plugin names: {path}"
    return result


def main():
    claude = entries(ROOT / ".claude-plugin/marketplace.json")
    layout_a = entries(ROOT / ".agents/plugins/marketplace.json")
    layout_b = entries(ROOT / "codex/.agents/plugins/marketplace.json")
    sources = {p.name for p in (ROOT / "plugins").iterdir() if p.is_dir()}
    ports = {p.name for p in (ROOT / "codex/plugins").iterdir() if p.is_dir()}
    assert set(claude) == sources, "Claude catalog and package directories differ"
    assert set(layout_a) == set(layout_b) == ports, "Codex layouts and packages differ"
    assert sources - ports == {"common-mod"}, "Unexpected Claude-only plugins"
    assert ports <= sources, "Codex plugin has no Claude source"
    for name, entry in claude.items():
        assert entry["source"] == f"./plugins/{name}", name
        source = load(ROOT / "plugins" / name / ".claude-plugin/plugin.json")
        assert source["name"] == name, name
        assert entry["version"] == source["version"], f"Claude version drift: {name}"
        if name not in ports:
            continue
        port = load(ROOT / "codex/plugins" / name / ".codex-plugin/plugin.json")
        assert port["name"] == name, name
        assert port["version"] == source["version"], f"Port version drift: {name}"
        a, b = layout_a[name], layout_b[name]
        assert a["source"] == {"source": "local", "path": f"./codex/plugins/{name}"}, name
        assert b["source"] == {"source": "local", "path": f"./plugins/{name}"}, name
        assert {k: v for k, v in a.items() if k != "source"} == {
            k: v for k, v in b.items() if k != "source"
        }, f"Catalog metadata drift: {name}"
        assert a["policy"] == {
            "installation": "AVAILABLE", "authentication": "ON_INSTALL"
        }, f"Unexpected policy: {name}"
        assert a["category"], f"Missing category: {name}"
    print(f"MARKETPLACE_VALID: {len(sources)} Claude plugins, {len(ports)} Codex plugins")


if __name__ == "__main__":
    main()
