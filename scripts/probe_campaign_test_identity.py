#!/usr/bin/env python3
"""Read-only counterexample: same values/types need not preserve object identity."""
import argparse
import copy
from datetime import datetime, timezone
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import time
import unittest

sys.dont_write_bytecode = True


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixture', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root = args.fixture.resolve(strict=True)
    assert not args.output.exists(), 'Refusing to overwrite earlier evidence'
    paths = [root / 'catalog.py', root / 'search_index.py', root / 'tests/test_build.py',
             root / 'data/services.json']
    before = {str(p): digest(p) for p in paths}
    started = datetime.now(timezone.utc).isoformat()
    timer = time.monotonic()
    sys.path.insert(0, str(root))
    from catalog import build_catalog
    from search_index import build_index
    spec = importlib.util.spec_from_file_location('observed_worker_tests', root / 'tests/test_build.py')
    tests = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tests)

    def cloned_tags(document):
        catalog = build_catalog(document)
        for item in catalog['items']:
            tags = item['tags']
            assert type(tags) in (list, tuple), 'Counterexample covers JSON lists and the worker tuple control only'
            item['tags'] = type(tags)(list(tags))
        return catalog

    def run_suite(builder):
        tests.build_catalog = builder
        output = io.StringIO()
        result = unittest.TextTestRunner(stream=output, verbosity=2).run(
            unittest.defaultTestLoader.loadTestsFromModule(tests))
        return {'tests_run': result.testsRun, 'successful': result.wasSuccessful(),
                'failures': [{'test': test.id(), 'traceback': trace} for test, trace in result.failures],
                'errors': [{'test': test.id(), 'traceback': trace} for test, trace in result.errors],
                'output': output.getvalue()}

    original_tests = run_suite(build_catalog)
    alternate_tests = run_suite(cloned_tags)
    source = json.loads((root / 'data/services.json').read_text(encoding='utf-8'))
    controls = [('actual_source', source), ('empty', {'release_id': 'empty', 'records': []})]
    for tag_type in (list, tuple):
        controls.append((tag_type.__name__, {'release_id': 'control', 'records': [
            {'id': 'z', 'name': '配管, 大型', 'region': 'north', 'slots': 0,
             'tags': tag_type(['第二標籤', 'maintenance']), 'status': 'active', 'channel': 'standard'},
            {'id': 'a', 'name': 'A', 'region': 'north', 'slots': 2,
             'tags': tag_type(['maintenance', 'first']), 'status': 'active', 'channel': 'standard'},
            {'id': 'hidden', 'name': 'Premium', 'region': 'west', 'slots': 4,
             'tags': tag_type(['private']), 'status': 'active', 'channel': 'premium'}]}))
    behavior = []
    for name, document in controls:
        saved = copy.deepcopy(document)
        original, alternate = build_catalog(document), cloned_tags(document)
        checks = {
            'catalog_values_equal': original == alternate,
            'catalog_field_types_equal': all(type(a[key]) is type(b[key])
                for a, b in zip(original['items'], alternate['items']) for key in a),
            'index_equal': build_index(original) == build_index(alternate),
            'input_unchanged': document == saved,
            'nonempty_tags_are_distinct_objects': all(a['tags'] is not b['tags']
                for a, b in zip(original['items'], alternate['items']) if a['tags']),
        }
        assert all(checks.values()), (name, checks)
        behavior.append({'control': name, 'checks': checks})
    assert original_tests['successful'] and original_tests['tests_run'] == 5
    assert not alternate_tests['successful'] and not alternate_tests['errors']
    assert len(alternate_tests['failures']) == 1
    failure = alternate_tests['failures'][0]
    assert failure['test'].endswith('test_filters_and_preserves_exact_fields_in_id_order')
    assert 'self.assertIs(catalog["items"][1]["tags"], tags)' in failure['traceback']
    assert before == {str(p): digest(p) for p in paths}, 'Original fixture changed'
    report = {
        'started_utc': started, 'ended_utc': datetime.now(timezone.utc).isoformat(),
        'wall_seconds': time.monotonic() - timer, 'model_calls': 0,
        'fixture': str(root), 'source_sha256': before, 'fixture_unchanged': True,
        'original_tests': original_tests, 'same_values_and_types_alternate_tests': alternate_tests,
        'behavior_controls': behavior, 'finding': 'TEST_OVERCONSTRAINS_OBJECT_IDENTITY',
        'scope': 'This supplied test suite rejects a same-value, same-type alternate. The delivered product itself is correct. No claim about all inputs, model internals, or skill causality.',
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8') as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps({'finding': report['finding'], 'original_pass': original_tests['successful'],
                      'alternate_rejected_tests': len(alternate_tests['failures']),
                      'behavior_controls_passed': len(behavior), 'fixture_unchanged': True,
                      'output': str(args.output)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
