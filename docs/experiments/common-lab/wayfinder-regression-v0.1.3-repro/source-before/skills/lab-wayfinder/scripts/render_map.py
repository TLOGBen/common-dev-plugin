#!/usr/bin/env python3
"""Render a wayfinder effort directory into a self-contained map.html.

Usage: python3 render_map.py <effort-dir> [output.html] [--language zh-TW|en] [--no-open]

<effort-dir> holds map.md and issues/NN-<slug>.md (see TRACKER.md).
The template lives next to this script at ../assets/map-template.html;
output defaults to <effort-dir>/map.html, which is then opened in the
user's browser unless --no-open is given.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path


LOCALES = {
    "zh-TW": {
        "htmlLang": "zh-Hant",
        "pageTitle": "Wayfinder 共識地圖",
        "eyebrow": "Wayfinder · 共識地圖",
        "routeChartAria": "決策路線圖",
        "routeChart": "決策路線圖",
        "graphAria": "票券阻擋關係圖",
        "legendFrontier": "前線 — 現在可處理",
        "legendClaimed": "已認領",
        "legendResolved": "已解決",
        "legendBlocked": "受阻",
        "legendHint": "滑過：標亮依賴鏈 · 點擊：開啟票券",
        "ticketsAria": "決策票券",
        "tickets": "決策票券",
        "filterAria": "依狀態篩選",
        "decisions": "目前已定案",
        "fog": "尚未釐清",
        "outOfScope": "範圍外",
        "status": {"frontier": "可處理", "claimed": "已認領", "blocked": "受阻", "resolved": "已解決"},
        "type": {"research": "研究", "prototype": "原型", "grilling": "決策釐清", "task": "任務"},
        "metaTemplate": "{total} 張票券 — {resolved} 張已解決 · {frontier} 張現在可處理 · {claimed} 張已認領 · {blocked} 張受阻",
        "generated": "產生時間",
        "source": "來源",
        "documentTitle": "Wayfinder 共識地圖",
        "destination": "目的地",
        "prerequisite": "前置",
        "prerequisiteResolved": "前置已解",
        "prerequisitePending": "未解前置阻擋",
        "prerequisiteMissing": "缺失前置阻擋",
        "question": "要回答的問題",
        "answer": "定案",
        "comments": "補充",
        "openTicket": "開啟 Markdown 票券",
        "all": "全部",
        "empty": "目前沒有內容",
        "currentFocus": "眼前要決定的事",
        "focusWarning": "指定焦點目前不可作為決定",
        "fullMap": "查看完整地圖與已定案事項",
        "evidence": "所依證據",
        "options": "選項與代價",
        "recommendation": "建議與理由",
        "context": "問題脈絡",
        "missingField": "原票沒有可呈現的問題或說明；未替來源補寫內容。",
        "focusProblems": {
            "invalid": "Current focus 必須只填一個現有票券 ID；未替你選取其他票券。",
            "resolved": "指定票券已解決，不應再次要求決定；請更新或移除呈現焦點。",
            "blocked": "指定票券尚有未解決或不存在的前置票券，現在還不能作為可決定事項。",
            "status": "指定票券狀態無法辨識，未將它推定為可決定事項。",
        },
    },
    "en": {
        "htmlLang": "en",
        "pageTitle": "Wayfinder Map",
        "eyebrow": "Wayfinder · shared map",
        "routeChartAria": "Route chart",
        "routeChart": "Route chart",
        "graphAria": "Ticket blocking graph",
        "legendFrontier": "frontier — takeable now",
        "legendClaimed": "claimed",
        "legendResolved": "resolved",
        "legendBlocked": "blocked",
        "legendHint": "hover: light the dependency chain · click: open the ticket",
        "ticketsAria": "Tickets",
        "tickets": "Tickets",
        "filterAria": "Filter by status",
        "decisions": "Decisions so far",
        "fog": "Not yet specified",
        "outOfScope": "Out of scope",
        "status": {"frontier": "frontier", "claimed": "claimed", "blocked": "blocked", "resolved": "resolved"},
        "type": {"research": "research", "prototype": "prototype", "grilling": "grilling", "task": "task"},
        "metaTemplate": "{total} tickets — {resolved} resolved · {frontier} on the frontier · {claimed} claimed · {blocked} in the blocked interior",
        "generated": "generated",
        "source": "source",
        "documentTitle": "Wayfinder",
        "destination": "destination",
        "prerequisite": "blocked by",
        "prerequisiteResolved": "prerequisites resolved",
        "prerequisitePending": "blocked by unresolved prerequisites",
        "prerequisiteMissing": "blocked by missing prerequisites",
        "question": "Question",
        "answer": "Answer",
        "comments": "Comments",
        "openTicket": "open the markdown ticket",
        "all": "all",
        "empty": "nothing here yet",
        "currentFocus": "The decision in front of you",
        "focusWarning": "The selected focus is not ready for a decision",
        "fullMap": "Explore the full map and settled decisions",
        "evidence": "Supporting evidence",
        "options": "Options and consequences",
        "recommendation": "Recommendation and reason",
        "context": "Question context",
        "missingField": "The source ticket contains no question or explanation to show; nothing was invented.",
        "focusProblems": {
            "invalid": "Current focus must contain only one existing ticket ID; no substitute was selected.",
            "resolved": "The selected ticket is already resolved; update or remove the view pointer instead of asking again.",
            "blocked": "The selected ticket has unresolved or missing prerequisites and is not ready for a decision.",
            "status": "The selected ticket has an unrecognized status; readiness is not assumed.",
        },
    },
}

STATIC_TOKENS = {
    "__WF_HTML_LANG__": "htmlLang",
    "__WF_PAGE_TITLE__": "pageTitle",
    "__WF_EYEBROW__": "eyebrow",
    "__WF_ROUTE_CHART_ARIA__": "routeChartAria",
    "__WF_ROUTE_CHART__": "routeChart",
    "__WF_GRAPH_ARIA__": "graphAria",
    "__WF_LEGEND_FRONTIER__": "legendFrontier",
    "__WF_LEGEND_CLAIMED__": "legendClaimed",
    "__WF_LEGEND_RESOLVED__": "legendResolved",
    "__WF_LEGEND_BLOCKED__": "legendBlocked",
    "__WF_LEGEND_HINT__": "legendHint",
    "__WF_TICKETS_ARIA__": "ticketsAria",
    "__WF_TICKETS__": "tickets",
    "__WF_FILTER_ARIA__": "filterAria",
    "__WF_DECISIONS__": "decisions",
    "__WF_FOG__": "fog",
    "__WF_OUT_OF_SCOPE__": "outOfScope",
}


def open_in_browser(path):
    for cmd in ("wslview", "xdg-open", "open"):
        if shutil.which(cmd):
            subprocess.Popen([cmd, str(path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
    # WSL without wslu: hand the file to Windows via its default association
    if shutil.which("wslpath") and shutil.which("explorer.exe"):
        win = subprocess.run(["wslpath", "-w", str(path)], capture_output=True, text=True).stdout.strip()
        if win:
            subprocess.Popen(["explorer.exe", win], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
    try:
        import webbrowser
        return webbrowser.open(path.as_uri())
    except Exception:
        return False


def sections(text):
    """Split markdown into {heading: body} by '## ' headings."""
    out = {}
    cur = None
    for line in text.splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m:
            cur = m.group(1)
            out[cur] = []
        elif cur is not None:
            out[cur].append(line)
    return {k: "\n".join(v).strip() for k, v in out.items()}


def bullets(body):
    """Extract top-level '- ' bullet items, ignoring comments/blank lines."""
    body = re.sub(r"<!--.*?-->", "", body or "", flags=re.S)
    return [m.group(1).strip() for m in re.finditer(r"^-\s+(.+)$", body, re.M)]


def parse_ticket(path):
    text = path.read_text(encoding="utf-8")
    title = next((m.group(1) for m in [re.search(r"^#\s+(.+)$", text, re.M)] if m), path.stem)
    field = lambda name: (re.search(rf"^{name}:\s*(.+)$", text, re.M) or [None, ""])[1].strip()
    sec = sections(text)
    intro = re.split(r"^##\s+", text, maxsplit=1, flags=re.M)[0]
    intro = "\n".join(line for line in intro.splitlines() if not re.match(r"^(#\s|(?:Type|Status|Blocked by):)", line)).strip()
    recognized = {"Question", "Evidence", "Options", "Recommendation", "Answer", "Comments"}
    extra = [f"{heading}\n\n{body}" for heading, body in sec.items() if heading not in recognized and body]
    context = "\n\n".join(part for part in [intro, *extra] if part)
    nn = path.stem.split("-", 1)[0]
    return {
        "id": nn,
        "title": title,
        "type": field("Type") or "task",
        "status": field("Status") or "open",
        "blockedBy": [b.strip().zfill(2) for b in field("Blocked by").split(",") if b.strip()],
        "question": sec.get("Question", ""),
        "context": context,
        "evidence": sec.get("Evidence", ""),
        "options": sec.get("Options", ""),
        "recommendation": sec.get("Recommendation", ""),
        "answer": sec.get("Answer", ""),
        "comments": sec.get("Comments", ""),
        "file": f"issues/{path.name}",
    }


def validate_tickets(tickets):
    """Reject ambiguous identities and blocking cycles before browser render."""
    by_id = {}
    for ticket in tickets:
        ticket_id = ticket["id"]
        if ticket_id in by_id:
            raise ValueError(f"WAYFINDER_DUPLICATE_TICKET_ID id={ticket_id}")
        by_id[ticket_id] = ticket

    visiting = []
    visited = set()

    def visit(ticket_id):
        if ticket_id in visited:
            return
        if ticket_id in visiting:
            start = visiting.index(ticket_id)
            cycle = [*visiting[start:], ticket_id]
            raise ValueError(f"WAYFINDER_BLOCKING_CYCLE path={'->'.join(cycle)}")
        visiting.append(ticket_id)
        for blocker_id in by_id[ticket_id]["blockedBy"]:
            if blocker_id in by_id:
                visit(blocker_id)
        visiting.pop()
        visited.add(ticket_id)

    for ticket_id in by_id:
        visit(ticket_id)


def resolve_focus(requested, tickets):
    """Resolve an explicit view pointer without changing or duplicating ticket state."""
    if requested is None:
        return None
    by_id = {ticket["id"]: ticket for ticket in tickets}
    ticket = by_id.get(requested) if re.fullmatch(r"[0-9]+", requested) else None
    problem = None
    if ticket is None:
        problem = "invalid"
    elif ticket["status"] == "resolved":
        problem = "resolved"
    elif ticket["status"] not in ("open", "claimed"):
        problem = "status"
    elif any(by_id.get(key, {}).get("status") != "resolved" for key in ticket["blockedBy"]):
        problem = "blocked"
    return {"requested": requested, "ticketId": ticket["id"] if problem is None else None, "problem": problem}


def atomic_write(path, content):
    """Replace the output path atomically without following a final symlink."""
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        for attempt in range(4):
            try:
                os.replace(temp_name, path)
                return
            except PermissionError:
                if attempt == 3:
                    raise
                time.sleep(0.05 * (2**attempt))
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def main():
    parser = argparse.ArgumentParser(description="Render a Wayfinder effort into a self-contained HTML map.")
    parser.add_argument("effort", type=Path)
    parser.add_argument("output", nargs="?", type=Path)
    parser.add_argument("--language", choices=tuple(LOCALES), default="zh-TW")
    parser.add_argument("--no-open", action="store_true")
    arguments = parser.parse_args()
    effort = arguments.effort.resolve()
    locale = LOCALES[arguments.language]
    map_md = (effort / "map.md").read_text(encoding="utf-8")
    sec = sections(map_md)
    title_m = re.search(r"^#\s+(?:Map:\s*)?(.+)$", map_md, re.M)

    tickets = [parse_ticket(p) for p in sorted((effort / "issues").glob("[0-9]*-*.md"))]
    try:
        validate_tickets(tickets)
    except ValueError as error:
        print(f"[FAIL] {error}", file=sys.stderr)
        return 1

    data = {
        "effort": title_m.group(1) if title_m else effort.name,
        "destination": sec.get("Destination", ""),
        "notes": bullets(sec.get("Notes", "")),
        "decisions": bullets(sec.get("Decisions so far", "")),
        "fog": bullets(sec.get("Not yet specified", "")),
        "outOfScope": bullets(sec.get("Out of scope", "")),
        "tickets": tickets,
        "focus": resolve_focus(sec.get("Current focus"), tickets),
        "generatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "source": str(effort),
        "language": arguments.language,
        "labels": locale,
    }

    template = (Path(__file__).resolve().parent.parent / "assets" / "map-template.html").read_text(encoding="utf-8")
    for token, key in STATIC_TOKENS.items():
        template = template.replace(token, locale[key])
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    html = template.replace("__WAYFINDER_DATA_JSON__", payload)

    out = arguments.output if arguments.output else effort / "map.html"
    atomic_write(out, html)
    print(f"wrote {out} ({len(data['tickets'])} tickets)")
    if not arguments.no_open and not open_in_browser(out.resolve()):
        print("could not open a browser; open the file manually")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
