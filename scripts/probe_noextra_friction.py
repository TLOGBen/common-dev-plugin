#!/usr/bin/env python3
"""Zero-model counterexamples; never edits the observed actor workspace."""
import argparse
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
sys.dont_write_bytecode = True


def inventory(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob('*')) if p.is_file()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    workspace = args.workspace.resolve(strict=True)
    target = args.output.absolute()
    if target.exists() or target.is_symlink() or target.resolve().is_relative_to(workspace):
        raise ValueError('New disjoint output required')
    before = inventory(workspace)
    sys.path.insert(0, str(workspace))
    import catalog
    source = json.loads((workspace/'data/services.json').read_text())
    original = catalog.build_catalog
    original_value = original(source)
    def legal_key_reordering(document):
        result = original(document)
        return {**result, 'items': [dict(reversed(list(row.items()))) for row in result['items']]}
    reordered_value = legal_key_reordering(source)
    canonical = lambda v: json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    assert canonical(original_value) == canonical(reordered_value)
    assert all(type(old[k]) is type(new[k]) for old, new in zip(original_value['items'], reordered_value['items']) for k in old)
    catalog.build_catalog = legal_key_reordering
    spec = importlib.util.spec_from_file_location('observed_tests', workspace/'tests/test_build.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    output = io.StringIO()
    result = unittest.TextTestRunner(stream=output, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(module))
    catalog.build_catalog = original
    assert before == inventory(workspace), 'Probe modified the actor workspace'
    scratch = Path(tempfile.mkdtemp(prefix='astra-pycompile-friction-'))
    sample = scratch/'sample.py'
    with sample.open('x', encoding='utf-8') as stream:
        stream.write('value = 1\n')
    command = [sys.executable, '-B', '-m', 'py_compile', str(sample)]
    compiled = subprocess.run(command, cwd=scratch, capture_output=True, text=True, timeout=15)
    cache = sorted(str(p.relative_to(scratch)) for p in scratch.rglob('*.pyc'))
    assert compiled.returncode == 0 and len(cache) == 1
    receipt = {
        'model_calls': 0, 'actor_workspace': str(workspace), 'actor_workspace_unchanged': before == inventory(workspace),
        'key_order_control': {'canonical_content_equal': True, 'field_types_equal': True,
            'tests_run': result.testsRun, 'failures': [str(test) for test, _ in result.failures],
            'errors': [str(test) for test, _ in result.errors], 'stdout': output.getvalue()},
        'explicit_compile_control': {'scratch_retained': str(scratch), 'command': command,
            'exit_code': compiled.returncode, 'stdout': compiled.stdout, 'stderr': compiled.stderr,
            'generated_pyc': cache, 'python': sys.version, 'scope': 'Task-owned generated fixture only, no original source edited or files deleted'},
        'limits': 'Key-order failure is a test overconstraint, not wrong current product output. Explicit py_compile writes cache despite -B; this does not reclassify the frozen role-scope failure or grant further writes.',
    }
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('x', encoding='utf-8') as stream:
        json.dump(receipt, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps({'workspace_unchanged': receipt['actor_workspace_unchanged'], 'test_failures':len(result.failures),
                      'test_errors':len(result.errors), 'explicit_compile_cache_files':len(cache)}, ensure_ascii=False))

if __name__ == '__main__':
    main()
