#!/usr/bin/env python3
"""Bounded unittest/probe output visibility control, separate from skill evaluation."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import secrets
import subprocess
import sys
import tempfile
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/experiments/trace-visibility-v2'

def put(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as stream:
        stream.write(text)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    assert not OUT.exists(), 'Fresh bounded control only'
    root = Path(tempfile.mkdtemp(prefix='trace-visibility-v2-'))
    jobs, truth = [], {}
    for label, model in [('U1', 'gpt-6-astra'), ('U2', 'gpt-5.6-sol')]:
        cwd = root / label
        cases = []
        for n in range(1, 5):
            place = cwd / ('case-' + str(n))
            source = place / ('test_markers.py' if n <= 2 else 'probe.py')
            stdout_marker = 'STDOUT_' + secrets.token_hex(16)
            stderr_marker = 'STDERR_' + secrets.token_hex(16)
            marker_file = place / 'markers.json'
            put(marker_file, json.dumps({'stdout': stdout_marker, 'stderr': stderr_marker}) + '\n')
            shared = "import json, sys\nfrom pathlib import Path\nvalues = json.loads(Path(__file__).with_name('markers.json').read_text())\n"
            if n <= 2:
                content = shared + "import unittest\nclass Markers(unittest.TestCase):\n    @classmethod\n    def setUpClass(cls):\n        print(values['stdout'], flush=True)\n        print(values['stderr'], file=sys.stderr, flush=True)\n"
                content += ''.join('    def test_' + str(i) + '(self):\n        self.assertEqual(' + str(i) + ', ' + str(i) + ')\n' for i in range(7))
                command = 'python3 -B -m unittest discover -s ' + str(place) + ' -v'
                argv = ['python3', '-B', '-m', 'unittest', 'discover', '-s', str(place), '-v']
            else:
                content = shared + "print(values['stdout'], flush=True)\nprint(values['stderr'], file=sys.stderr, flush=True)\nprint('probe_value=True', flush=True)\n"
                expression = 'import runpy; runpy.run_path(' + repr(str(source)) + ')'
                command = 'python3 -B -c "' + expression + '"'
                argv = ['python3', '-B', '-c', expression]
            put(source, content)
            check = subprocess.run(argv, cwd=cwd, text=True, capture_output=True, timeout=10)
            assert check.returncode == 0
            assert stdout_marker in check.stdout and stderr_marker in check.stderr
            if n <= 2:
                assert 'Ran 7 tests' in check.stderr and 'OK' in check.stderr
            cases.append({'label': 'C' + str(n), 'source': str(source), 'markers_file': str(marker_file), 'command': command, 'expected_stdout': stdout_marker, 'expected_stderr': stderr_marker, 'expected_tests': 7 if n <= 2 else None, 'selfcheck': {'exit_code': check.returncode, 'stdout_verified': True, 'stderr_verified': True}})
        files = [str(p) for p in cwd.rglob('*') if p.is_file()]
        hashes = {p: sha(Path(p)) for p in files}
        prompt = ('Run the four exact commands below once each using command execution, with their listed absolute paths. They execute synthetic disposable Python fixtures only: no network, secrets, environment change, or writes. Independent commands may run in parallel. Do not retry or modify a command that fails. Do not combine commands.\n'
                  'You may inspect the four listed .py sources with cat before execution if useful. Do not directly inspect markers.json, any plan, logs, truth, other files or global context. Reading markers.json inside the approved supplied program is part of execution. Do not use other agents or skills.\n'
                  'Return one JSON object per command label with stdout_marker, stderr_marker, observed_test_count (null for a non-test or if not observed), observed_probe_value (null if not observed), and observed_exit_code. Copy markers only from output available to you; use null when unavailable. Briefly identify missing evidence. Do not infer an observed count from source.\n\n'
                  + '\n\n'.join(case['label'] + '\nSource allowed: ' + case['source'] + '\nCommand: ' + case['command'] for case in cases))
        plan = {'model': model, 'sandbox': 'read-only', 'timeout_seconds': 180, 'cwd': str(cwd), 'input_sha256': hashes, 'prompt': prompt}
        plan_path = OUT / (label + '.plan.json')
        put(plan_path, json.dumps(plan, indent=2) + '\n')
        jobs.append((label, plan_path, OUT / (label + '-run')))
        truth[label] = {'model': model, 'cases': cases, 'input_sha256': hashes}
    put(OUT / 'private-truth.json', json.dumps({'created_utc': datetime.now(timezone.utc).isoformat(), 'root': str(root), 'cases': truth, 'script_sha256': sha(Path(__file__))}, indent=2) + '\n')
    put(OUT / 'design.md', '# CLI 輸出控制：unittest 與 probe\n\n兩個新上下文 Astra／Sol，各四個只執行一次的合成命令：兩個 unittest、兩個 python -c probe。stdout／stderr 各含不同的 128-bit 隨機標記，標記只存在命令會讀取的 fixture，沒有出現在 prompt 或命令參數。每次命令使用不同 fixture，避免從前次讀取得知標記。local self-check 驗證兩條 stream 與 7 tests。\n\n這是外部紀錄是否足以重建模型可見內容的有限量測控制，不計入 skill train／held-out、不改 rubric。若 final 有正確 nonce 但任何 captured tool output 都無對應內容，可支持採集缺口；全可見只代表本批未重現，不能修補歷史空白。兩次 normal read-only CLI、不變更政策、不重試。結束後不再無限追查 telemetry。\n')
    runner = ROOT / 'scripts/lab_evolve_dispatch.py'
    def call(job):
        label, plan, output = job
        result = subprocess.run([sys.executable, '-B', str(runner), '--plan', str(plan), '--output', str(output)], capture_output=True, text=True, timeout=210)
        return {'label': label, 'exit_code': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(call, jobs))
    put(OUT / 'dispatch-results.json', json.dumps(results, indent=2) + '\n')
    print(json.dumps({'root': str(root), 'calls': len(results), 'dispatch_exit_codes': [r['exit_code'] for r in results]}), flush=True)

if __name__ == '__main__':
    main()
