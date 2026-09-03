#!/usr/bin/env python3
"""init-test-template — 在任何專案鋪好 test-template 記憶庫。

行為：
  1. 找目標專案根（預設：往上找 git 根，找不到用 cwd；可用 --target 指定）。
  2. 建立 .claude/test-template/{login,env,flow,selector}/ 目錄。
  3. 從 scaffold（本檔旁的 assets/test-template-scaffold/）複製 README.md、query.py
     到 .claude/test-template/，並把 login/example.md 複製進去當範例。
  4. idempotent：已存在的檔案跳過並印提示；--force 可覆寫。
  5. 最後跑一次 query.py 當冒煙測試，並印「下一步」指引。

用法：
    python init-test-template.py [--target <專案根>] [--force]
"""

import argparse
import os
import shutil
import subprocess
import sys

# scaffold 來源：相對本檔 → assets/test-template-scaffold/
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCAFFOLD_DIR = os.path.join(SCRIPT_DIR, "test-template-scaffold")

SUBDIRS = ["login", "env", "flow", "selector"]
# (來源相對 scaffold 路徑, 目標相對 test-template 路徑)
COPY_FILES = [
    ("README.md", "README.md"),
    ("query.py", "query.py"),
    (os.path.join("login", "example.md"), os.path.join("login", "example.md")),
]


def find_project_root(target):
    if target:
        return os.path.abspath(target)
    # 往上找 git 根
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True,
        )
        root = out.stdout.strip()
        if root:
            return root
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    return os.getcwd()


def ensure_dir(path):
    if os.path.isdir(path):
        print(f"  [skip] 目錄已存在：{path}")
    else:
        os.makedirs(path, exist_ok=True)
        print(f"  [new]  建立目錄：{path}")


def copy_file(src, dst, force):
    if not os.path.isfile(src):
        print(f"  [warn] scaffold 缺檔，略過：{src}")
        return
    if os.path.isfile(dst) and not force:
        print(f"  [skip] 已存在（--force 可覆寫）：{dst}")
        return
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    action = "overwrite" if os.path.isfile(dst) and force else "new"
    print(f"  [{action}] 複製：{dst}")


def main():
    parser = argparse.ArgumentParser(description="在專案鋪好 .claude/test-template/ 記憶庫")
    parser.add_argument("--target", default=None, help="目標專案根（預設找 git 根或 cwd）")
    parser.add_argument("--force", action="store_true", help="覆寫已存在的檔案")
    args = parser.parse_args()

    if not os.path.isdir(SCAFFOLD_DIR):
        print(f"[error] 找不到 scaffold 來源：{SCAFFOLD_DIR}")
        return 2

    root = find_project_root(args.target)
    base = os.path.join(root, ".claude", "test-template")
    print(f"目標專案根：{root}")
    print(f"記憶庫位置：{base}\n")

    print("建立目錄：")
    ensure_dir(base)
    for sub in SUBDIRS:
        ensure_dir(os.path.join(base, sub))

    print("\n複製檔案：")
    for src_rel, dst_rel in COPY_FILES:
        copy_file(
            os.path.join(SCAFFOLD_DIR, src_rel),
            os.path.join(base, dst_rel),
            args.force,
        )

    # 冒煙測試：跑剛鋪好的 query.py
    query_py = os.path.join(base, "query.py")
    print("\n冒煙測試（query.py）：")
    if os.path.isfile(query_py):
        try:
            out = subprocess.run(
                [sys.executable, query_py],
                capture_output=True, text=True, check=False,
            )
            print(out.stdout.rstrip())
            if out.stderr.strip():
                print(out.stderr.rstrip())
        except OSError as e:
            print(f"  [warn] query.py 執行失敗：{e}")
    else:
        print("  [warn] query.py 未就位，略過冒煙測試。")

    print("\n下一步：")
    print(f"  1. 速查：python .claude/test-template/query.py [關鍵字] [--site X] [--kind Y]")
    print(f"  2. 改寫或刪除範例：.claude/test-template/login/example.md")
    print(f"  3. 跑過、驗證過一個流程後，把可重用片段沉澱成新 template（檔名=id.md）")
    print(f"  4. schema 與寫法見：.claude/test-template/README.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
