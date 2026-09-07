#!/usr/bin/env python3
"""Prospective direct-Astra policy contrast; retain all prior worker-fit evidence."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
sys.dont_write_bytecode = True
REPO = Path(__file__).resolve().parents[1]

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def inventory(root):
    found = {}
    for p in sorted(root.rglob('*')):
        assert not p.is_symlink(), 'No symbolic links in owned fixtures'
        if p.is_file():
            found[str(p.relative_to(root))] = sha(p)
    return found

def jput(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2)
        stream.write('\n')

def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def freeze(output):
    assert not output.exists(), 'Fresh evidence directory required'
    output.mkdir(parents=True)
    scratch = Path(tempfile.mkdtemp(prefix='astra-direct-policy-v1-'))
    jobs = []
    sources = {str(Path(__file__).resolve()): sha(Path(__file__).resolve())}
    for number, case in enumerate(('count-label', 'event-projection'), 1):
        label = 'D' + str(number)
        src = REPO/'scripts/worker_fit_fixtures'/case/'public'
        root = scratch/label
        root.mkdir()
        for source in sorted(src.rglob('*')):
            assert not source.is_symlink()
            if not source.is_file():
                continue
            sources[str(source)] = sha(source)
            target = root/source.relative_to(src)
            target.parent.mkdir(parents=True, exist_ok=True)
            content = source.read_bytes()
            if source.name == 'TASK.md':
                text = content.decode('utf-8')
                assert text.count('\n主手負責') == 1
                business, old_policy = text.split('\n主手負責', 1)
                task = business.rstrip() + '\n\n## 本次執行政策\n\n由你（Astra/high）直接完成實作、必要測試與結果交接；本次不委派其他模型或 agent，也不載入額外 skill。可改範圍仍限上述產品檔及相關 tests；執行快取只能在 src/tests 內。不得修改 TASK.md 或新增根目錄檔案。不要新增依賴、網路、設定、commit/push 或操作其他目錄。使用者不在場，已授權細節自行判斷，繼續到可驗證完成或有真實阻礙。最後交代完成結果、實際證據與限制；自驗不是獨立驗收，沒有可觀測費用時不估報帳單。\n'
                content = task.encode('utf-8')
                business_hash = hashlib.sha256(business.rstrip().encode()).hexdigest()
            with target.open('xb') as stream:
                stream.write(content)
        spec = {'model': 'gpt-6-astra', 'sandbox': 'workspace-write', 'cwd': str(root),
                'timeout_seconds': 600, 'input_sha256': {str(root/'TASK.md'): sha(root/'TASK.md')},
                'prompt': '請完整讀取並完成此工作目錄 TASK.md。此為直接實作政策的單次有界實驗，無額外 skill 或委派。僅讀本工作目錄 TASK.md、src/、tests/；不要讀父目錄、其他案例、全域設定或任何不可見 oracle。遵守檔案與權限範圍，使用既有工具，不修改平台限制。'}
        plan_path = output/(label+'-spec.json')
        jput(plan_path, spec)
        jobs.append({'label': label, 'case': case, 'workspace': str(root), 'initial_sha256': inventory(root),
                     'business_contract_sha256': business_hash, 'spec': str(plan_path),
                     'output': str(output/(label+'-run')),
                     'allowed_writes': ['src/count-label.mjs', 'tests/'] if case == 'count-label' else ['src/', 'tests/']})
    for p in (REPO/'scripts/lab_evolve_dispatch.py', REPO/'scripts/common_lab_ab.py',
              REPO/'scripts/astra_lead_fixtures/_evaluation/verify_moe.py',
              REPO/'scripts/worker_fit_fixtures/event-projection/_evaluation/verify_moe.py'):
        sources[str(p)] = sha(p)
    receipt = {'kind': 'direct-policy-not-skill-only-ab', 'scratch': str(scratch), 'jobs': jobs,
               'source_sha256': sources, 'actual_cost_usd': None, 'no_automatic_retry': True,
               'author_acceptance_is_not_independent': True}
    jput(output/'frozen-plan.json', receipt)
    return receipt

def verify(job, output):
    root = Path(job['workspace'])
    result = json.loads((Path(job['output'])/'result.json').read_text())
    simple = load(REPO/'scripts/astra_lead_fixtures/_evaluation/verify_moe.py', 'simple_direct')
    before = inventory(root)
    if job['case'] == 'count-label':
        checks, evidence = simple.count_label(root/'src')
        checks['verifier_left_fixture_unchanged'] = before == inventory(root)
        product = {'passed': all(checks.values()), 'checks': checks, 'evidence': evidence}
    else:
        oracle = load(REPO/'scripts/worker_fit_fixtures/event-projection/_evaluation/verify_moe.py', 'event_direct')
        product = oracle.verify(root)
    initial = job['initial_sha256']
    changed = sorted(p for p in set(initial)|set(before) if initial.get(p) != before.get(p))
    allowed = lambda p: any(p.startswith(a) if a.endswith('/') else p == a for a in job['allowed_writes'])
    report = {'label': job['label'], 'case': job['case'], 'episode_status': result['status'],
              'product': product, 'changed_paths': changed,
              'scope_violations': [p for p in changed if not allowed(p)],
              'initial_sha256': initial, 'final_sha256': before,
              'oracle_left_fixture_unchanged': before == inventory(root),
              'worker_dispatched': False, 'implementation_acceptance_separation': False,
              'human_comprehension': None, 'actual_cost_usd': None, 'model_calls': 0,
              'lead_trace_review': 'PENDING_MAIN_REVIEW'}
    jput(output/(job['label']+'-oracle.json'), report)
    print(json.dumps({'label': job['label'], 'product_passed': product['passed'],
                      'checks': len(product['checks']), 'scope_violations': report['scope_violations']}))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--run-label', choices=('D1', 'D2'))
    parser.add_argument('--verify-label', choices=('D1', 'D2'))
    args = parser.parse_args()
    output = args.output.resolve()
    assert not (args.run_label and args.verify_label)
    if not (output/'frozen-plan.json').exists():
        assert not args.run_label and not args.verify_label
        receipt = freeze(output)
        print(json.dumps({'status': 'frozen', 'jobs': len(receipt['jobs']), 'scratch': receipt['scratch']}))
        return
    receipt = json.loads((output/'frozen-plan.json').read_text())
    assert all(sha(Path(p)) == h for p,h in receipt['source_sha256'].items()), 'Source drift'
    label = args.run_label or args.verify_label
    assert label, 'Frozen evidence is not overwritten'
    job = next(row for row in receipt['jobs'] if row['label'] == label)
    if args.run_label:
        assert inventory(Path(job['workspace'])) == job['initial_sha256'], 'Starting fixture drift'
        completed = subprocess.run([sys.executable, '-B', str(REPO/'scripts/lab_evolve_dispatch.py'),
                                    '--plan', job['spec'], '--output', job['output']],
                                   capture_output=True, text=True, timeout=650)
        print(completed.stdout, end='')
        print(completed.stderr, file=sys.stderr, end='')
        raise SystemExit(completed.returncode)
    verify(job, output)

if __name__ == '__main__':
    main()
