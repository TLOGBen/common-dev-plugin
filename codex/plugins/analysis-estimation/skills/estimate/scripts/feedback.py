#!/usr/bin/env python3
"""Prepare de-identified feedback cards and optionally publish a confirmed issue."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class FeedbackError(RuntimeError):
    """Feedback preparation or optional publication error."""


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def atomic_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="\n", delete=False, dir=path.parent, prefix=f".{path.name}.", suffix=".tmp") as stream:
        stream.write(value)
        temporary = Path(stream.name)
    temporary.replace(path)


def load_case_terms(case_root: Path) -> list[str]:
    generic = {"case", "cases", "project", "assessment", "feedback", "output", "outputs"}
    root_name = case_root.resolve().name.strip()
    terms = [root_name] if len(root_name) >= 6 and root_name.lower() not in generic else []
    path = case_root.resolve() / "assessment-state.json"
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return terms
    for key in ("caseId", "name"):
        value = state.get(key)
        if isinstance(value, str) and len(value.strip()) >= 3 and value.strip().lower() not in generic:
            terms.append(value.strip())
    return terms


def redact(value: str, sensitive_terms: list[str]) -> tuple[str, list[str]]:
    text = value
    findings: list[str] = []
    patterns = (
        ("credential", r"(?i)\b(password|passwd|pwd|secret|token|api[_-]?key|authorization)\s*[:=]\s*[^\s,;]+", r"\1=[REDACTED]"),
        ("url", r"(?i)https?://[^\s)\]]+", "[URL REMOVED]"),
        ("private-ip", r"(?<!\d)(?:10|127|169\.254|172\.(?:1[6-9]|2\d|3[01])|192\.168)(?:\.\d{1,3}){3}(?!\d)", "[NETWORK REMOVED]"),
        ("local-path", r"(?i)(?:[A-Z]:\\|/home/|/Users/|/mnt/[a-z]/)[^\s,;]+", "[PATH REMOVED]"),
        ("email", r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", "[EMAIL REMOVED]"),
        ("hash", r"\b[0-9a-f]{32,64}\b", "[IDENTIFIER REMOVED]"),
    )
    for label, pattern, replacement in patterns:
        updated, count = re.subn(pattern, replacement, text, flags=re.IGNORECASE)
        if count:
            findings.append(f"{label}:{count}")
        text = updated
    for term in sorted({term for term in sensitive_terms if len(term) >= 3}, key=len, reverse=True):
        pattern = re.escape(term)
        text, count = re.subn(pattern, "[PROJECT REMOVED]", text, flags=re.IGNORECASE)
        if count:
            findings.append(f"project-term:{count}")
    return text.strip(), findings


def markdown_card(packet: dict[str, Any]) -> str:
    local = packet["localCard"]
    return "\n".join([
        f"# 使用回饋 {packet['feedbackId']}", "",
        f"- 建立時間：{packet['createdAt']}",
        f"- 證據等級：{local['evidenceStrength']}",
        "",
        "## 原本要完成的任務", "", local["task"], "",
        "## 遇到的摩擦", "", local["friction"], "",
        "## 實際影響", "", local["impact"], "",
        "## 期望結果", "", local["expected"], "",
        "## 根因假說", "", local["rootCause"], "",
        "## 可分享的最小重現", "", local["reproduction"], "",
        "## 中央 Issue 狀態", "", packet["issueStatus"], "",
    ])


def issue_body(issue: dict[str, str]) -> str:
    return "\n".join([
        "## 抽象使用任務", "", issue["task"], "",
        "## 可遷移根因", "", issue["rootCause"], "",
        "## 對 Skill 的影響", "", issue["impact"], "",
        "## 期望行為", "", issue["expected"], "",
        "## 去識別最小重現", "", issue["reproduction"], "",
        "## 證據等級", "", issue["evidenceStrength"], "",
        "_本 Issue 僅保留通用根因；案件與專案證據留在原環境。_", "",
    ])


def prepare(args: argparse.Namespace) -> dict[str, Any]:
    root = args.case_root.resolve()
    queue = root / "feedback-queue"
    terms = load_case_terms(root) + list(args.sensitive_term or [])
    local_card = {
        "task": args.task.strip(), "friction": args.friction.strip(), "impact": args.impact.strip(),
        "expected": args.expected.strip(), "rootCause": args.root_cause.strip(),
        "reproduction": (args.reproduction or "尚未形成可分享的最小重現").strip(),
        "evidenceStrength": args.evidence_strength,
    }
    if not local_card["rootCause"]:
        raise FeedbackError("請先在案件本地形成根因假說；中央回饋不以專案紀錄取代根因")
    central: dict[str, str] = {}
    findings: list[str] = []
    for key in ("task", "impact", "expected", "rootCause", "reproduction"):
        central[key], current = redact(local_card[key], terms)
        findings.extend(current)
    central["evidenceStrength"] = args.evidence_strength
    joined = "\n".join(central.values())
    unsafe_tokens = [term for term in terms if len(term) >= 3 and re.search(re.escape(term), joined, re.IGNORECASE)]
    if unsafe_tokens:
        raise FeedbackError("去識別後仍含案件識別資訊，請留在本地繼續分析")
    fingerprint = hashlib.sha256((central["rootCause"] + "\n" + central["expected"]).encode("utf-8")).hexdigest()[:12]
    feedback_id = f"feedback-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{fingerprint}"
    title = f"[pm-estimation] {central['rootCause'][:72]}"
    issue = {"title": title, "body": issue_body(central), **central}
    packet = {
        "schemaVersion": 1,
        "feedbackId": feedback_id,
        "createdAt": now_iso(),
        "localCard": local_card,
        "issueDraft": issue,
        "redactionFindings": sorted(set(findings)),
        "issueStatus": "草稿已建立；有 tracker 與權限時可在人工確認後發布，否則本地回饋已完成。",
    }
    json_path = queue / f"{feedback_id}.json"
    md_path = queue / f"{feedback_id}.md"
    draft_path = queue / f"{feedback_id}.issue.md"
    atomic_text(json_path, json.dumps(packet, ensure_ascii=False, indent=2) + "\n")
    atomic_text(md_path, markdown_card(packet))
    atomic_text(draft_path, f"# {title}\n\n{issue['body']}")
    return {"ok": True, "feedbackId": feedback_id, "json": str(json_path), "markdown": str(md_path), "issueDraft": str(draft_path), "redactionFindings": packet["redactionFindings"]}


def capabilities(_: argparse.Namespace) -> dict[str, Any]:
    return {
        "ok": True,
        "git": shutil.which("git"),
        "githubCli": shutil.which("gh"),
        "gitlabCli": shutil.which("glab"),
        "issueRequired": False,
        "message": "缺少 Git、tracker、登入或權限時，本地回饋卡仍是完整結果。",
    }


def publish(args: argparse.Namespace) -> dict[str, Any]:
    if not args.confirmed:
        raise FeedbackError("外部 Issue 建立需要先預覽草稿並傳入 --confirmed")
    try:
        packet = json.loads(args.packet.resolve().read_text(encoding="utf-8"))
        draft = packet["issueDraft"]
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as exc:
        raise FeedbackError(f"無法讀取回饋 packet：{exc}") from exc
    executable = shutil.which(args.tracker)
    if not executable:
        raise FeedbackError(f"找不到 {args.tracker}；本地回饋卡已完成，不需要為此修復環境")
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".md", delete=False) as stream:
        stream.write(draft["body"])
        body_file = Path(stream.name)
    try:
        if args.tracker == "gh":
            command = [executable, "issue", "create", "--repo", args.repo, "--title", draft["title"], "--body-file", str(body_file)]
        else:
            command = [executable, "issue", "create", "--repo", args.repo, "--title", draft["title"], "--description", draft["body"]]
        result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", check=False)
        if result.returncode != 0:
            raise FeedbackError(f"Issue 未建立；本地回饋仍保留。{result.stderr.strip() or result.stdout.strip()}")
        return {"ok": True, "tracker": args.tracker, "repo": args.repo, "result": result.stdout.strip()}
    finally:
        body_file.unlink(missing_ok=True)


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)
    command = commands.add_parser("prepare")
    command.add_argument("case_root", type=Path)
    command.add_argument("--task", required=True)
    command.add_argument("--friction", required=True)
    command.add_argument("--impact", required=True)
    command.add_argument("--expected", required=True)
    command.add_argument("--root-cause", required=True)
    command.add_argument("--reproduction")
    command.add_argument("--evidence-strength", choices=("single-case", "cross-case", "core-risk", "maintainer-judgment"), default="single-case")
    command.add_argument("--sensitive-term", action="append", default=[])
    command.set_defaults(handler=prepare)
    command = commands.add_parser("capabilities")
    command.set_defaults(handler=capabilities)
    command = commands.add_parser("publish")
    command.add_argument("--packet", type=Path, required=True)
    command.add_argument("--tracker", choices=("gh", "glab"), required=True)
    command.add_argument("--repo", required=True)
    command.add_argument("--confirmed", action="store_true")
    command.set_defaults(handler=publish)
    return root


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8", errors="replace")
    args = parser().parse_args(argv)
    try:
        result = args.handler(args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except FeedbackError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
