"""Contract tests for strategic_state.py state-construction tooling (init + CRUD)."""

import contextlib
import importlib.util
import io
import json
import pathlib
import re
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "plugins/common/skills/strategic-advance/scripts/strategic_state.py"
SEED = ROOT / "plugins/common/skills/strategic-advance/references/example-seed.json"

NOW = "2026-08-14T09:00:00+08:00"
PROBE_REF = (
    "scribe-probe:python3 /home/ops/drill/scripts/probe_state.py --front drill-recon"
    "@2026-08-14T08:58:00+08:00"
)
SEEDED_SOURCE_REF = "seeded: pending probe"
PROVENANCE_PATTERN = re.compile(
    r"^scribe-probe:.+@\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(Z|[+-]\d{2}:?\d{2})$"
)
GATING_REFUSAL = "gating claim 需 scribe-probe 出處（--source-ref 不符文法，拒絕寫入 PASS）"
NON_MAIN_OBSERVATION_REFUSAL = (
    "recovery.observation 僅限主攻前線：非主攻前線請於升級 ACTIVE 前以 set-claim 帶探針出處入冊"
)
RECOVERY_PROBE_REF = (
    "scribe-probe:git -C /home/ops/drill status --porcelain@2026-08-14T08:59:00+08:00"
)
YAML_UNAVAILABLE = "pyyaml 未安裝：YAML 種子不可用，請改用 JSON 種子"


def run_script(*arguments: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *arguments],
        capture_output=True,
        text=True,
    )


def load_script_module():
    spec = importlib.util.spec_from_file_location("strategic_state_under_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def gating_claim_ids(state: dict) -> set:
    gating = set()
    for front in state["battlefields"]:
        gating.add(front["entryClaimId"])
        gating.add(front["exitClaimId"])
    gating.add(state["decision"]["pivotClaimId"])
    for criterion in state["strategicObjective"]["victoryCriteria"]:
        gating.update(criterion.get("evidenceClaimIds", []))
    return gating


class StateInitContractTest(unittest.TestCase):
    def setUp(self):
        self._directory = tempfile.TemporaryDirectory()
        self.tmp = pathlib.Path(self._directory.name)
        self.addCleanup(self._directory.cleanup)
        self.out = self.tmp / "state.json"

    def init_state(self, *extra: str) -> subprocess.CompletedProcess:
        return run_script("init", str(SEED), str(self.out), "--now", NOW, *extra)

    # A8 (1) + A2 + V1 byte-wise
    def test_example_seed_expands_to_valid_state_and_prints_v1(self):
        result = self.init_state()
        self.assertEqual(result.returncode, 0, result.stderr)

        state = json.loads(self.out.read_text(encoding="utf-8"))
        expected = (
            f"STATE_INITIALIZED mission={state['missionId']} "
            f"claims={len(state['currentTruth']['evidenceClaims'])} "
            f"fronts={len(state['battlefields'])}\n"
        )
        self.assertEqual(result.stdout, expected)

        validated = run_script("validate", str(self.out))
        self.assertEqual(validated.returncode, 0, validated.stderr)
        self.assertTrue(
            validated.stdout.startswith("STRATEGIC_STATE_VALID"),
            validated.stdout,
        )

    # A4 as the validator permits it: exactly one birth PASS — the ACTIVE MAIN
    # entry claim, carrying probe provenance — and every other claim UNKNOWN
    # with a non-scribe-probe sourceRef.
    def test_init_claim_posture_is_one_probe_backed_entry_pass(self):
        self.assertEqual(self.init_state().returncode, 0)
        state = json.loads(self.out.read_text(encoding="utf-8"))
        claims = state["currentTruth"]["evidenceClaims"]

        active_main = [
            front
            for front in state["battlefields"]
            if front["effort"] == "MAIN" and front["status"] == "ACTIVE"
        ]
        self.assertEqual(len(active_main), 1)

        passing = [claim for claim in claims if claim["status"] == "PASS"]
        self.assertEqual([claim["id"] for claim in passing], [active_main[0]["entryClaimId"]])
        self.assertRegex(passing[0]["sourceRef"], PROVENANCE_PATTERN)

        for claim in claims:
            if claim["id"] == passing[0]["id"]:
                continue
            self.assertEqual(claim["status"], "UNKNOWN", claim["id"])
            self.assertEqual(claim["sourceRef"], SEEDED_SOURCE_REF, claim["id"])
            self.assertNotRegex(claim["sourceRef"], PROVENANCE_PATTERN)

        # Cold-start posture discovered against the validator.
        self.assertEqual(state["strategicClarity"]["status"], "UNCLEAR")
        self.assertEqual(state["strategicClarity"]["route"], "OPERATOR_RESOLVE")
        self.assertEqual(state["strategicClarity"]["unclearCauses"], ["PIVOT_UNPROBED"])
        self.assertTrue(state["strategicClarity"]["wayfinderMapPath"].strip())
        self.assertEqual(state["terminalAssessment"]["status"], "IN_PROGRESS")
        self.assertEqual(state["takeoverReadiness"]["result"], "NOT_READY")
        self.assertEqual(state["intervention"]["status"], "NOT_REQUIRED")
        self.assertIsNone(state["latestVerifiedAdvance"])

    # A5 / A8 (3)
    def test_set_claim_with_probe_ref_on_gating_claim_keeps_state_valid(self):
        self.assertEqual(self.init_state().returncode, 0)
        state = json.loads(self.out.read_text(encoding="utf-8"))
        deferred = [front for front in state["battlefields"] if front["status"] == "DEFERRED"]
        self.assertTrue(deferred, "example seed must ship a DEFERRED front")
        claim_id = deferred[0]["entryClaimId"]
        self.assertIn(claim_id, gating_claim_ids(state))

        result = run_script(
            "set-claim",
            str(self.out),
            claim_id,
            "--status",
            "PASS",
            "--source-ref",
            PROBE_REF,
            "--observed-at",
            NOW,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout.strip(),
            f"CLAIM_UPDATED id={claim_id} status=PASS state={self.out}",
        )

        updated = json.loads(self.out.read_text(encoding="utf-8"))
        claim = next(item for item in updated["currentTruth"]["evidenceClaims"] if item["id"] == claim_id)
        self.assertEqual(claim["status"], "PASS")
        self.assertEqual(claim["sourceRef"], PROBE_REF)

        validated = run_script("validate", str(self.out))
        self.assertEqual(validated.returncode, 0, validated.stderr)
        self.assertTrue(validated.stdout.startswith("STRATEGIC_STATE_VALID"))

    # A5 / A8 (4) — V3 byte-wise, file untouched
    def test_gating_pass_without_probe_ref_is_refused(self):
        self.assertEqual(self.init_state().returncode, 0)
        state = json.loads(self.out.read_text(encoding="utf-8"))
        claim_id = [front for front in state["battlefields"] if front["status"] == "DEFERRED"][0][
            "entryClaimId"
        ]
        before = self.out.read_bytes()

        result = run_script(
            "set-claim",
            str(self.out),
            claim_id,
            "--status",
            "PASS",
            "--source-ref",
            "operator 貼上的終端輸出",
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn(GATING_REFUSAL, result.stderr)
        self.assertEqual(self.out.read_bytes(), before)

    # A5 — non-gating claims keep honest free-text provenance
    def test_non_gating_pass_accepts_free_text_source_ref(self):
        self.assertEqual(self.init_state().returncode, 0)
        state = json.loads(self.out.read_text(encoding="utf-8"))
        gating = gating_claim_ids(state)
        target = next(
            claim["id"]
            for claim in state["currentTruth"]["evidenceClaims"]
            if claim["id"] not in gating and claim["id"].startswith("claim-risk-")
        )
        result = run_script(
            "set-claim",
            str(self.out),
            target,
            "--status",
            "FAIL",
            "--source-ref",
            "唯讀設定檢查",
            "--observed-at",
            NOW,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    # A6 — invalid result never reaches disk
    def test_set_front_invalid_transition_is_not_persisted(self):
        self.assertEqual(self.init_state().returncode, 0)
        state = json.loads(self.out.read_text(encoding="utf-8"))
        pending = [front for front in state["battlefields"] if front["status"] == "PENDING"]
        self.assertTrue(pending, "example seed must ship a PENDING front")
        before = self.out.read_bytes()

        result = run_script("set-front", str(self.out), pending[0]["id"], "--status", "ACTIVE")
        self.assertEqual(result.returncode, 1)
        stderr_lines = [line for line in result.stderr.splitlines() if line.strip()]
        self.assertTrue(stderr_lines)
        for line in stderr_lines:
            self.assertTrue(line.startswith("[FAIL] "), line)
        self.assertEqual(self.out.read_bytes(), before)

    # A6 — add-claim keeps the file valid by construction
    def test_add_claim_appends_and_revalidates(self):
        self.assertEqual(self.init_state().returncode, 0)
        result = run_script(
            "add-claim",
            str(self.out),
            "--id",
            "claim-extra-context",
            "--source-type",
            "LOG",
            "--source-ref",
            "戰役 ledger 追記",
            "--predicate",
            "DRILL_LEDGER_APPEND_COUNT >= 1",
            "--observed-at",
            NOW,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        state = json.loads(self.out.read_text(encoding="utf-8"))
        added_status = next(
            claim["status"]
            for claim in state["currentTruth"]["evidenceClaims"]
            if claim["id"] == "claim-extra-context"
        )
        self.assertEqual(
            result.stdout.strip(),
            f"CLAIM_ADDED id=claim-extra-context status={added_status} state={self.out}",
        )
        added = [
            claim
            for claim in state["currentTruth"]["evidenceClaims"]
            if claim["id"] == "claim-extra-context"
        ]
        self.assertEqual(len(added), 1)
        self.assertEqual(added[0]["status"], "UNKNOWN")

        from_json = run_script(
            "add-claim",
            str(self.out),
            "--json",
            json.dumps(
                {
                    "id": "claim-json-probe",
                    "sourceType": "LOG",
                    "sourceRef": "手動追記",
                    "predicate": "JSON_PATH_EXERCISED == true",
                    "observedAt": "2026-08-14T09:05:00+08:00",
                    "validUntil": "2026-08-14T11:00:00+08:00",
                    "authorityRank": 2,
                },
                ensure_ascii=False,
            ),
        )
        self.assertEqual(from_json.returncode, 0, from_json.stderr)
        state = json.loads(self.out.read_text(encoding="utf-8"))
        from_json_claim = next(
            claim
            for claim in state["currentTruth"]["evidenceClaims"]
            if claim["id"] == "claim-json-probe"
        )
        self.assertEqual(from_json_claim["authorityRank"], 2)
        self.assertEqual(from_json_claim["validUntil"], "2026-08-14T11:00:00+08:00")

        duplicate = run_script(
            "add-claim",
            str(self.out),
            "--id",
            "claim-extra-context",
            "--source-type",
            "LOG",
            "--source-ref",
            "重複 id",
            "--predicate",
            "DRILL_LEDGER_APPEND_COUNT >= 2",
        )
        self.assertEqual(duplicate.returncode, 1)

    # Discovered constraint: a later observation must carry state.updatedAt with it.
    def test_observation_later_than_now_advances_updated_at(self):
        self.assertEqual(self.init_state().returncode, 0)
        state = json.loads(self.out.read_text(encoding="utf-8"))
        claim_id = [front for front in state["battlefields"] if front["status"] == "DEFERRED"][0][
            "entryClaimId"
        ]
        later = "2026-08-14T09:20:00+08:00"

        result = run_script(
            "set-claim",
            str(self.out),
            claim_id,
            "--status",
            "PASS",
            "--source-ref",
            PROBE_REF,
            "--observed-at",
            later,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        updated = json.loads(self.out.read_text(encoding="utf-8"))
        self.assertEqual(updated["updatedAt"], later)
        self.assertEqual(run_script("validate", str(self.out)).returncode, 0)

    # A7
    def test_init_refuses_existing_output_without_force(self):
        self.assertEqual(self.init_state().returncode, 0)
        first = self.out.read_bytes()

        blocked = self.init_state()
        self.assertEqual(blocked.returncode, 1)
        self.assertEqual(
            blocked.stderr.strip(),
            f"[FAIL] 輸出路徑已存在：{self.out}；加上 --force 才覆寫",
        )
        self.assertEqual(self.out.read_bytes(), first)

        forced = self.init_state("--force")
        self.assertEqual(forced.returncode, 0, forced.stderr)

    # A6 / V7c — a standalone-legal set-front success, byte-exact stdout
    def test_set_front_success_prints_front_updated(self):
        self.assertEqual(self.init_state().returncode, 0)
        state = json.loads(self.out.read_text(encoding="utf-8"))
        pending = [front for front in state["battlefields"] if front["status"] == "PENDING"]
        self.assertTrue(pending, "example seed must ship a PENDING front")
        front = pending[0]

        result = run_script(
            "set-front",
            str(self.out),
            front["id"],
            "--status",
            "DEFERRED",
            "--defer-reason",
            "演習期間資源保留，暫緩清除前線",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout.strip(),
            f"FRONT_UPDATED id={front['id']} status=DEFERRED "
            f"effort={front['effort']} state={self.out}",
        )
        validated = run_script("validate", str(self.out))
        self.assertEqual(validated.returncode, 0, validated.stderr)

    # A4 as amended — mutating main effort births exactly two probe-backed PASS claims
    def test_mutating_main_seed_births_probe_backed_recovery_pass(self):
        seed = json.loads(SEED.read_text(encoding="utf-8"))
        main = next(front for front in seed["battlefields"] if front.get("mainEffort"))
        main["mutationScope"] = ["rm -r plugins/legacy-pipeline"]
        main["recovery"] = {
            "action": "git restore 還原整個 plugins/ 樹",
            "steps": ["停止委派", "git status 列出被動路徑", "git restore 後 ls 對帳"],
            "readinessPredicate": "DRILL_WORKTREE_CLEAN_BASELINE == true",
            "successPredicate": "git status --porcelain 回到空輸出",
            "stopCondition": "還原後仍有計畫外路徑殘留",
            "observation": {
                "sourceRef": RECOVERY_PROBE_REF,
                "observedAt": "2026-08-14T08:59:00+08:00",
            },
        }
        seed_path = self.tmp / "mutating-seed.json"
        seed_path.write_text(json.dumps(seed, ensure_ascii=False), encoding="utf-8")

        result = run_script("init", str(seed_path), str(self.out), "--now", NOW)
        self.assertEqual(result.returncode, 0, result.stderr)
        state = json.loads(self.out.read_text(encoding="utf-8"))
        passes = [
            claim
            for claim in state["currentTruth"]["evidenceClaims"]
            if claim["status"] == "PASS"
        ]
        self.assertEqual(
            sorted(claim["id"] for claim in passes),
            sorted([f"claim-front-{main['id']}-entry", f"claim-front-{main['id']}-recovery"]),
        )
        for claim in passes:
            self.assertRegex(claim["sourceRef"], PROVENANCE_PATTERN)
        validated = run_script("validate", str(self.out))
        self.assertEqual(validated.returncode, 0, validated.stderr)

    # A4 as amended / V6 — non-main recovery.observation is refused at init
    def test_non_main_recovery_observation_is_refused(self):
        seed = json.loads(SEED.read_text(encoding="utf-8"))
        support = next(
            front
            for front in seed["battlefields"]
            if not front.get("mainEffort") and front.get("mutationScope")
        )
        support.setdefault("recovery", {})["observation"] = {
            "sourceRef": RECOVERY_PROBE_REF,
            "observedAt": "2026-08-14T08:59:00+08:00",
        }
        seed_path = self.tmp / "non-main-observation-seed.json"
        seed_path.write_text(json.dumps(seed, ensure_ascii=False), encoding="utf-8")

        result = run_script("init", str(seed_path), str(self.out), "--now", NOW)
        self.assertEqual(result.returncode, 1)
        self.assertIn(NON_MAIN_OBSERVATION_REFUSAL, result.stderr)
        self.assertFalse(self.out.exists())

        # the refusal is unconditional: an EMPTY-mutationScope non-main front is refused too
        bare_seed = json.loads(SEED.read_text(encoding="utf-8"))
        bare = next(
            front
            for front in bare_seed["battlefields"]
            if not front.get("mainEffort") and not front.get("mutationScope")
        )
        bare.setdefault("recovery", {})["observation"] = {
            "sourceRef": RECOVERY_PROBE_REF,
            "observedAt": "2026-08-14T08:59:00+08:00",
        }
        bare_path = self.tmp / "bare-non-main-observation-seed.json"
        bare_path.write_text(json.dumps(bare_seed, ensure_ascii=False), encoding="utf-8")

        bare_result = run_script("init", str(bare_path), str(self.out), "--now", NOW)
        self.assertEqual(bare_result.returncode, 1)
        self.assertIn(NON_MAIN_OBSERVATION_REFUSAL, bare_result.stderr)
        self.assertFalse(self.out.exists())

    # A9 — the Codex carrier ships byte-identical script and seed
    def test_codex_carrier_mirrors_script_and_seed(self):
        codex_root = ROOT / "codex/plugins/common/skills/strategic-advance"
        self.assertEqual(
            (codex_root / "scripts/strategic_state.py").read_bytes(), SCRIPT.read_bytes()
        )
        self.assertEqual((codex_root / "references/example-seed.json").read_bytes(), SEED.read_bytes())

    # A1 / A8 (5)
    def test_yaml_seed_without_pyyaml_prints_v4_and_exits_2(self):
        module = load_script_module()
        seed_path = self.tmp / "seed.yaml"
        seed_path.write_text("missionId: drill\n", encoding="utf-8")
        argv = ["strategic_state.py", "init", str(seed_path), str(self.out)]
        stderr = io.StringIO()

        with mock.patch.dict(sys.modules, {"yaml": None}), mock.patch.object(sys, "argv", argv):
            with contextlib.redirect_stderr(stderr):
                code = module.main()

        self.assertEqual(code, 2)
        self.assertIn(YAML_UNAVAILABLE, stderr.getvalue())
        self.assertFalse(self.out.exists())


if __name__ == "__main__":
    unittest.main()


class TakeoverBlockOptionalTest(unittest.TestCase):
    """Schema 6: the takeoverReadiness block is optional — absent means autonomous posture."""

    def test_init_without_takeover_block_produces_valid_state_without_key(self):
        seed = json.loads(SEED.read_text(encoding="utf-8"))
        seed.pop("takeoverReadiness")
        with tempfile.TemporaryDirectory() as tmp:
            seed_path = pathlib.Path(tmp) / "seed.json"
            out_path = pathlib.Path(tmp) / "state.json"
            seed_path.write_text(json.dumps(seed, ensure_ascii=False), encoding="utf-8")
            result = run_script("init", str(seed_path), str(out_path), "--now", NOW)
            self.assertEqual(result.returncode, 0, result.stderr)
            state = json.loads(out_path.read_text(encoding="utf-8"))
            self.assertNotIn("takeoverReadiness", state)
            self.assertEqual(state["schemaVersion"], 6)
            self.assertNotIn(
                "claim-readiness-actor",
                {claim["id"] for claim in state["currentTruth"]["evidenceClaims"]},
            )
            validate = run_script("validate", str(out_path))
            self.assertEqual(validate.returncode, 0, validate.stdout + validate.stderr)


class HandoffCommandTest(unittest.TestCase):
    """`handoff` completes one front and activates the next in a single validated write."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.out = pathlib.Path(self.tmp.name) / "state.json"
        run_script("init", str(SEED), str(self.out), "--now", NOW)
        self.addCleanup(self.tmp.cleanup)

    def test_handoff_refuses_without_probe_provenance(self):
        before = self.out.read_text(encoding="utf-8")
        result = run_script(
            "handoff", str(self.out), "drill-recon", "drill-retire",
            "--exit-source-ref", "operator says done",
        )
        self.assertEqual(result.returncode, 1)
        self.assertEqual(self.out.read_text(encoding="utf-8"), before)

    def test_handoff_atomic_success_updates_front_decision_and_clarity(self):
        probe = "scribe-probe:git -C /home/ops/drill status --short@2026-08-14T09:30:00+08:00"
        result = run_script(
            "handoff", str(self.out), "drill-recon", "drill-retire",
            "--exit-source-ref", probe,
            "--entry-source-ref", probe,
            "--recovery-source-ref", probe,
            "--now", "2026-08-14T09:31:00+08:00",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        state = json.loads(self.out.read_text(encoding="utf-8"))
        fronts = {front["id"]: front for front in state["battlefields"]}
        self.assertEqual(fronts["drill-recon"]["status"], "COMPLETE")
        self.assertEqual(fronts["drill-retire"]["status"], "ACTIVE")
        self.assertEqual(fronts["drill-retire"]["effort"], "MAIN")
        self.assertEqual(state["decision"]["activeFrontId"], "drill-retire")
        self.assertEqual(state["decision"]["pivotClaimId"], "claim-front-drill-retire-pivot")
        self.assertEqual(state["strategicClarity"]["route"], "OPERATOR_RESOLVE")
        self.assertIn("PIVOT_UNPROBED", state["strategicClarity"]["unclearCauses"])
        self.assertEqual(state["progress"]["activeFrontStartedAt"], "2026-08-14T09:31:00+08:00")
        validate = run_script("validate", str(self.out))
        self.assertEqual(validate.returncode, 0, validate.stdout + validate.stderr)


class PostRendererFeatureSliceTest(unittest.TestCase):
    """Renderer changes must not disconnect later priority/slice/toll feature slices."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name)
        self.out = self.root / "state.json"
        initialized = run_script("init", str(SEED), str(self.out), "--now", NOW)
        self.assertEqual(initialized.returncode, 0, initialized.stderr)
        self.addCleanup(self.tmp.cleanup)

    def test_slice_inherits_carrier_roots_and_revalidates(self):
        carrier = self.root / "carrier"
        updated = run_script(
            "set-front",
            str(self.out),
            "drill-retire",
            "--status",
            "PENDING",
            "--carrier-root",
            str(carrier),
            "--now",
            "2026-08-14T09:01:00+08:00",
        )
        self.assertEqual(updated.returncode, 0, updated.stderr)

        created = run_script(
            "set-front",
            str(self.out),
            "drill-retire-db",
            "--slice-of",
            "drill-retire",
            "--entry-state",
            "DB_PENDING",
            "--terminal-state",
            "DB_READY",
            "--objective",
            "Prepare the database transition",
            "--now",
            "2026-08-14T09:02:00+08:00",
        )
        self.assertEqual(created.returncode, 0, created.stderr)
        self.assertIn("SLICE_FRONT_CREATED", created.stdout)

        state = json.loads(self.out.read_text(encoding="utf-8"))
        child = next(front for front in state["battlefields"] if front["id"] == "drill-retire-db")
        self.assertEqual("DEFERRED", child["status"])
        self.assertEqual([str(carrier)], child["carrierRoots"])
        self.assertEqual("claim-front-drill-retire-db-entry", child["entryClaimId"])
        self.assertEqual("claim-front-drill-retire-db-exit", child["exitClaimId"])
        validated = run_script("validate", str(self.out))
        self.assertEqual(validated.returncode, 0, validated.stderr)

    def test_priority_order_beats_score_without_reviving_ineligible_front(self):
        seed = json.loads(SEED.read_text(encoding="utf-8"))
        seed["objective"]["priorityOrder"] = ["drill-recon"]
        seed["battlefields"][2].pop("deferReason", None)
        seed_path = self.root / "priority-seed.json"
        priority_state = self.root / "priority-state.json"
        seed_path.write_text(json.dumps(seed, ensure_ascii=False), encoding="utf-8")

        initialized = run_script("init", str(seed_path), str(priority_state), "--now", NOW)
        self.assertEqual(initialized.returncode, 0, initialized.stderr)
        state = json.loads(priority_state.read_text(encoding="utf-8"))
        candidates = {item["frontId"]: item for item in state["decision"]["candidates"]}

        self.assertEqual(["drill-recon"], state["strategicClarity"]["candidateMainEffortIds"])
        self.assertTrue(candidates["drill-release-audit"]["eligible"])
        self.assertLess(
            candidates["drill-release-audit"]["totalScore"],
            candidates["drill-recon"]["totalScore"],
        )
        self.assertFalse(candidates["drill-retire"]["eligible"])
        self.assertNotIn("drill-retire", state["strategicClarity"]["candidateMainEffortIds"])

    def test_toll_accepts_only_strict_distance_reduction(self):
        ledger = self.root / "run-ledger.jsonl"
        accepted = run_script(
            "toll",
            str(self.out),
            "--organ",
            "seal",
            "--before",
            "5",
            "--after",
            "4",
            "--ledger",
            str(ledger),
            "--now",
            "2026-08-14T09:03:00+08:00",
        )
        self.assertEqual(accepted.returncode, 0, accepted.stderr)
        lines = ledger.read_text(encoding="utf-8").splitlines()
        self.assertEqual(1, len(lines))
        self.assertEqual("ORGAN_LOOP_TOLL", json.loads(lines[0])["event"])

        refused = run_script(
            "toll",
            str(self.out),
            "--organ",
            "seal",
            "--before",
            "4",
            "--after",
            "4",
            "--ledger",
            str(ledger),
            "--now",
            "2026-08-14T09:04:00+08:00",
        )
        self.assertEqual(refused.returncode, 1)
        self.assertIn("過路費未付", refused.stderr)
        self.assertEqual(lines, ledger.read_text(encoding="utf-8").splitlines())
