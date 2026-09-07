#!/usr/bin/env python3
"""Two synthetic Estimate execution cases using the audited local-artifact carrier.

Materialize and freeze before inference. Neither this adapter nor the carrier
edits a stable case, replaces a previous run, or treats model prose as acceptance.
"""
import argparse
import csv
import io
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
import lab_execution_probe as carrier

ROOT = Path(__file__).resolve().parent.parent
HERE = Path(__file__).resolve()
FIXTURES = ROOT / "docs/experiments/estimate-lab/behavior-v1-inputs"
RUNS = ROOT / "docs/experiments/estimate-lab/runs"
A_ROOT = ROOT / "codex/plugins/analysis-estimation"
B_ROOT = ROOT / "experiments/estimate-lab-v0.1.1/plugins/estimate-lab"
E1_USER = """目前只確定既有系統要能用 Java 17。框架、資料層與正式部署方案還沒決定，請先依附件評估可行路線，說清楚目前能確認的事、限制，以及接下來需要我決定什麼。這不是要求你實作升版，也還不是正式報價。元件名稱與相容性結果是合成事實，不用真實產品知識替換。請實際讀材料，再用繁體中文交接，不建立核准紀錄。"""
E2_USER = """附件已固定合成範圍與高值費率。請整理 canonical 數量、工作分解與高值人天，讓 PM 能說明為什麼需要、怎麼做及怎麼驗收。沒有低值或基準費率，不補造，也不替 PM 核准。核對別名、generated、coverage與例外增量。產出 preview/estimate-external.csv、preview/assessment-report.md、preview/handoff.md；CSV使用標準五欄「序號、系統功能、功能說明、開發人天、測試人天」。這次只要求高值預覽，不要求完整正式 case、三區間估算、HTML或Excel；不要為符合完整 generator 而捏造缺失欄位。所有資料與費率皆為合成測試。"""


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode()


def csv_bytes(rows):
    stream = io.StringIO(newline="")
    csv.writer(stream, lineterminator="\n").writerows(rows)
    return stream.getvalue().encode()


def materials():
    first = {
        "system-manifest.json": json_bytes({"synthetic": True,
            "current": {"java": 8, "framework": "AcmeMVC 4", "dataLayer": "StoreLayer 2", "privateLibrary": "QueryKit 1.4", "packaging": "WAR"},
            "approvedTarget": {"java": 17},
            "unselectedDecisions": ["framework strategy", "data-layer strategy", "production deployment", "maintenance-risk acceptance"]}),
        "route-probe.json": json_bytes({"synthetic": True, "route": "retain-current-framework-and-data-layer", "targetJava": 17,
            "suppliedChecks": {"compile": "pass", "applicationStart": "pass", "loginSmoke": "pass", "representativeQuery": "pass"},
            "notEstablished": ["complete regression", "production deployment compatibility", "vendor-supported long-term maintenance", "PM acceptance of maintenance risk"]}),
        "dependency-records.md": ("這是合成測試材料，不是現場查證紀錄。\n\n"
            "R1：AcmeMVC 4 與 StoreLayer 2 可走附件 route-probe 的 Java 17 路線。\n"
            "R2：該路線未證明完整回歸、正式環境部署相容性或長期維護支援。\n"
            "R3：另一候選為 AcmeNext 6，需要命名空間轉換及 StoreLayer 3。\n"
            "R4：私有 QueryKit 1.4 僅有 StoreLayer 2 支援證據；沒有 StoreLayer 3 的已驗證替代或維護路徑。\n"
            "R5：上次技術筆記建議 AcmeNext 6；這是建議，不是 PM 決議。\n").encode(),
    }
    exceptions = {85: "upload", 86: "signed-payload", 87: "transaction"}
    inventory = [["canonical_id", "source_path", "change_kind", "batch_included", "exception_kind"]]
    inventory += [[f"api-{n:03d}", f"src/api/Api{n:03d}.java", "exception" if n in exceptions else "normal", "true", exceptions.get(n, "")] for n in range(1, 88)]
    rates = [
        {"id": "shared-foundation", "quantity": 1, "developmentPerUnit": 4, "testPerUnit": 1,
         "covers": "One shared configuration/runtime foundation, reproducible regeneration and its verification."},
        {"id": "homogeneous-batch", "quantity": 1, "developmentPerUnit": 2, "testPerUnit": 1,
         "covers": "Common conversion of all 87 canonical APIs, including the ordinary part of the three exceptions."},
        {"id": "exception-increment", "quantity": 3, "developmentPerUnit": 0.5, "testPerUnit": 0.5,
         "covers": "Only additional upload, signed-payload and transaction work beyond the common batch."},
        {"id": "integration-verification", "quantity": 1, "developmentPerUnit": 0, "testPerUnit": 2,
         "covers": "One integration-verification package covering all 13 coverage entries."},
    ]
    second = {
        "inventory.csv": csv_bytes(inventory),
        "aliases.csv": csv_bytes([["canonical_id", "alias_path", "reason"],
            ["api-085", "inventory-export/UploadApi.java", "same canonical work item"],
            ["api-086", "inventory-export/SignedApi.java", "same canonical work item"],
            ["api-087", "inventory-export/TransactionApi.java", "same canonical work item"]]),
        "generated.json": json_bytes({"synthetic": True, "generatedOutputCount": 136, "manualChangeUnits": 0,
            "method": "Regenerate reproducible outputs from changed source configuration and verify the result.", "pricedWithin": "shared-foundation"}),
        "coverage.csv": csv_bytes([["coverage_id", "priced_within"]] + [[f"integration-{n:02d}", "integration-verification"] for n in range(1, 14)]),
        "unchanged-and-responsibility.json": json_bytes({"synthetic": True,
            "unchangedScope": {"description": "Existing views need no change.", "additionalPersonDays": 0},
            "customerFormalUAT": {"owner": "customer", "supplierAdditionalPersonDays": 0, "note": "Supplier integration verification remains in scope."}}),
        "rates.json": json_bytes({"synthetic": True, "unit": "person-day", "bound": "high-only", "items": rates, "lowAndBaselineRates": None}),
    }
    cases = [
        {"id": "runtime-target-boundary", "skill": "estimate", "user": E1_USER,
         "writable_files": [], "required_outputs": [],
         "criteria": ["Java17 is the only accepted target; framework/data/deployment remain unselected", "Uses supplied limited probe evidence without asking PM to establish technical facts", "Keeps limited feasibility distinct from full regression and maintenance support", "Exposes QueryKit gap and recommendation versus decision", "Presents a meaningful human commitment without inventing approval"],
         "guards": ["No implementation/production/complete-regression/approved-estimate claim", "No file mutation or scope expansion"]},
        {"id": "canonical-high-preview", "skill": "estimate", "user": E2_USER,
         "writable_files": ["preview/estimate-external.csv", "preview/assessment-report.md", "preview/handoff.md"],
         "required_outputs": ["preview/estimate-external.csv", "preview/assessment-report.md", "preview/handoff.md"],
         "criteria": ["87 canonical items, 84 ordinary/3 exception, aliases add zero", "136 generated and13 coverage not manual pricing multipliers", "Shared5 plus batch3 plus additional exceptions3 plus integration2, no double count or offsetting deletion", "Development7.5/testing5.5/high13 reconcile at work-item level", "Zero unchanged/customer UAT adds no supplier work while supplier integration remains", "Actual five-column preview files explain scope/actions/cost-driver/acceptance and provide usable links", "No invented low/baseline or PM approval"],
         "guards": ["No formal customer estimate or real approval claim", "No mutation outside exact preview allowlist", "Correct total alone cannot conceal duplicate or missing work"]},
    ]
    files = {"cases.json": json_bytes({"design": "estimate-behavior-v1", "cases": cases})}
    for case, data in zip(cases, (first, second)):
        files.update({case["id"] + "/files/" + name: content for name, content in data.items()})
    return files


def observe(case, root, before):
    files = carrier.files_at(root)
    after = carrier.hashes(files)
    changed = sorted(key for key in before.keys() | after.keys() if before.get(key) != after.get(key))
    result = {"fixture_after_sha256": after, "changed_paths": changed,
              "outside_allowlist_changes": sorted(set(changed) - set(case["writable_files"])),
              "required_outputs_present": {key: key in files for key in case["required_outputs"]},
              "local_artifacts": {key: files[key].decode("utf-8-sig") if key in files else None for key in case["required_outputs"]},
              "semantic_acceptance": None, "manual_review_required": True}
    table = files.get("preview/estimate-external.csv")
    if table:
        result["external_csv_rows"] = list(csv.reader(io.StringIO(table.decode("utf-8-sig"))))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group(required=True)
    for flag in ("materialize", "freeze-design", "self-test", "run"):
        actions.add_argument("--" + flag, action="store_true")
    parser.add_argument("--run-id")
    parser.add_argument("--plan-dir", type=Path)
    parser.add_argument("--model", default="gpt-6-astra")
    parser.add_argument("--effort", default="high")
    parser.add_argument("--timeout", type=int, default=420)
    args = parser.parse_args()
    carrier.FIXTURES, carrier.RUNS = FIXTURES, RUNS
    carrier.observations = observe
    args.a_root, args.b_root = A_ROOT, B_ROOT
    if args.materialize:
        FIXTURES.mkdir(parents=True, exist_ok=False)
        items = materials()
        for name, content in items.items():
            path = FIXTURES / name
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("xb") as handle:
                handle.write(content)
        print(json.dumps({"status": "MATERIALIZED", "model_calls": 0, "files": carrier.hashes(items)}))
    elif args.freeze_design:
        assert args.run_id
        carrier.freeze_design(args.run_id)
        carrier.save(RUNS / args.run_id / "adapter-manifest.json", {
            "design_id": "estimate-behavior-v1", "adapter_sha256": carrier.sha(HERE.read_bytes()),
            "a_root": str(A_ROOT), "b_root": str(B_ROOT), "model": args.model, "effort": args.effort,
            "planned_calls": 4, "limits": "Synthetic data; real local reads/preview artifacts. Prompt-scoped read isolation, not access-control isolation. No human measurement."})
    elif args.self_test:
        items = materials()
        assert items == carrier.files_at(FIXTURES)
        inventory = list(csv.DictReader(io.StringIO(items["canonical-high-preview/files/inventory.csv"].decode())))
        assert len(inventory) == len({row["canonical_id"] for row in inventory}) == 87
        assert sum(row["change_kind"] == "exception" for row in inventory) == 3
        rates = json.loads(items["canonical-high-preview/files/rates.json"])["items"]
        assert sum(row["quantity"] * row["developmentPerUnit"] for row in rates) == 7.5
        assert sum(row["quantity"] * row["testPerUnit"] for row in rates) == 5.5
        case = json.loads(items["cases.json"])["cases"][1]
        fixture = carrier.materialize(case, {"fixtures/" + key: value for key, value in items.items()})
        facts = observe(case, fixture, carrier.hashes(carrier.files_at(fixture)))
        assert facts["changed_paths"] == [] and not any(facts["required_outputs_present"].values())
        print(json.dumps({"status": "PASS", "model_calls": 0, "retained_fixture": str(fixture), "checks": ["deterministic inputs", "87 unique canonical", "3 exceptions", "7.5+5.5=13", "no preexisting output"]}))
    else:
        assert args.run_id and args.plan_dir
        frozen = json.loads((args.plan_dir / "adapter-manifest.json").read_text())
        assert frozen["adapter_sha256"] == carrier.sha(HERE.read_bytes()), "Adapter changed after freeze"
        assert args.model == frozen["model"] and args.effort == frozen["effort"]
        carrier.run(args)


if __name__ == "__main__":
    main()
