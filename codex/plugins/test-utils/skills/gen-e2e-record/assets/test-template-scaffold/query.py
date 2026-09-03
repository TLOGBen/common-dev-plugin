#!/usr/bin/env python3
"""test-template 速查工具。

掃描本檔所在目錄底下所有 **/*.md 的 frontmatter，依條件過濾後印出命中項目的
id / kind / site / when / 路徑，方便接著 Read 載入。

用法：
    python query.py                  # 列全部
    python query.py [關鍵字]          # 關鍵字（掃 id/tags/when/summary）
    python query.py --site myapp
    python query.py --tag login
    python query.py --kind flow
    （可組合：python query.py popup --site myapp --kind selector）

純標準庫，自帶極簡 frontmatter 解析（支援 key: value 與 [a, b] 清單），不依賴 pyyaml。
"""

import argparse
import os
import sys

# ROOT = 本檔所在目錄（部署後即 .claude/test-template/）
ROOT = os.path.dirname(os.path.abspath(__file__))


def parse_frontmatter(text):
    """從檔案內容取出開頭 --- ... --- 區塊，解析成 dict。

    僅支援 `key: value` 與 `key: [a, b, c]` 兩種形式，足夠本 schema 使用。
    解析失敗或無 frontmatter 時回傳空 dict。
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}

    meta = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" not in line:
            continue
        key, _, raw = line.partition(":")
        key = key.strip()
        raw = raw.strip()
        if raw.startswith("[") and raw.endswith("]"):
            inner = raw[1:-1].strip()
            value = [item.strip() for item in inner.split(",") if item.strip()] if inner else []
        else:
            value = raw
        meta[key] = value
    return meta


def iter_templates(root):
    """走訪 root 下所有 .md，yield (相對路徑, meta)。"""
    for dirpath, _, filenames in os.walk(root):
        for name in filenames:
            if not name.endswith(".md"):
                continue
            full = os.path.join(dirpath, name)
            try:
                with open(full, "r", encoding="utf-8") as f:
                    text = f.read()
            except OSError:
                continue
            meta = parse_frontmatter(text)
            if not meta.get("id"):
                # 沒有 frontmatter 的檔（例如 README.md）跳過
                continue
            rel = os.path.relpath(full, root)
            yield rel, meta


def project_relative_path(rel):
    """輸出時用相對專案根的路徑，方便直接 Read。"""
    return os.path.join(".claude/test-template", rel).replace(os.sep, "/")


def matches(meta, keyword, site, tag, kind):
    if site and str(meta.get("site", "")).lower() != site.lower():
        return False
    if kind and str(meta.get("kind", "")).lower() != kind.lower():
        return False
    if tag:
        tags = meta.get("tags", [])
        if isinstance(tags, str):
            tags = [tags]
        if tag.lower() not in [t.lower() for t in tags]:
            return False
    if keyword:
        tags = meta.get("tags", [])
        if isinstance(tags, str):
            tags = [tags]
        haystack = " ".join([
            str(meta.get("id", "")),
            " ".join(tags),
            str(meta.get("when", "")),
            str(meta.get("summary", "")),
        ]).lower()
        if keyword.lower() not in haystack:
            return False
    return True


def main():
    parser = argparse.ArgumentParser(
        description="test-template 速查工具：依條件過濾 frontmatter 並印出命中項目。"
    )
    parser.add_argument("keyword", nargs="?", default=None,
                        help="關鍵字（掃 id/tags/when/summary）")
    parser.add_argument("--site", default=None, help="站台代號過濾")
    parser.add_argument("--tag", default=None, help="標籤過濾")
    parser.add_argument("--kind", default=None,
                        help="類別過濾：login | env | flow | selector | gotcha")
    args = parser.parse_args()

    results = []
    for rel, meta in iter_templates(ROOT):
        if matches(meta, args.keyword, args.site, args.tag, args.kind):
            results.append((rel, meta))

    results.sort(key=lambda r: (str(r[1].get("site", "")), str(r[1].get("kind", "")), str(r[1].get("id", ""))))

    if not results:
        print("（無命中）查無符合條件的 template。")
        cond = []
        if args.keyword:
            cond.append(f"關鍵字={args.keyword}")
        if args.site:
            cond.append(f"--site {args.site}")
        if args.tag:
            cond.append(f"--tag {args.tag}")
        if args.kind:
            cond.append(f"--kind {args.kind}")
        if cond:
            print("目前條件：" + "、".join(cond))
        print("提示：")
        print("  - 放寬條件試試（例如只用關鍵字、或不加 --site）")
        print("  - 直接 `python query.py` 列出全部，確認有哪些 template")
        print("  - 還沒有對應 template → 照通用原則做，做完把可重用部分沉澱成新 template")
        return 0

    print(f"命中 {len(results)} 筆：\n")
    for rel, meta in results:
        print(f"- id={meta.get('id')}  kind={meta.get('kind', '?')}  site={meta.get('site', '?')}")
        when = meta.get("when")
        if when:
            print(f"  when : {when}")
        print(f"  path : {project_relative_path(rel)}")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
