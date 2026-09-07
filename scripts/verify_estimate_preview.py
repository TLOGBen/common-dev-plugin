#!/usr/bin/env python3
"""Read-only verification of frozen E2 previews, including actual Markdown parsing."""
import argparse
import csv
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re

from markdown_it import MarkdownIt


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect(result):
    root = Path(result['fixture_dir'])
    artifacts = result['artifact_observations']
    for relative, digest in artifacts['fixture_after_sha256'].items():
        assert sha(root / relative) == digest, ('Frozen artifact drift', relative)
    expected = ['preview/assessment-report.md', 'preview/estimate-external.csv', 'preview/handoff.md']
    assert artifacts['changed_paths'] == expected
    assert not artifacts['outside_allowlist_changes']
    with (root / expected[1]).open(encoding='utf-8-sig', newline='') as stream:
        rows = list(csv.reader(stream))
    assert rows[0] == ['序號', '系統功能', '功能說明', '開發人天', '測試人天']
    assert len(rows) == 5 and all(len(row) == 5 for row in rows)
    assert [row[0] for row in rows[1:]] == ['1', '2', '3', '4']
    values = [(Decimal(row[3]), Decimal(row[4])) for row in rows[1:]]
    assert values == [(Decimal('4'), Decimal('1')), (Decimal('2'), Decimal('1')),
                      (Decimal('1.5'), Decimal('1.5')), (Decimal('0'), Decimal('2'))]
    assert tuple(sum(pair[i] for pair in values) for i in (0, 1)) == (Decimal('7.5'), Decimal('5.5'))
    renderer = MarkdownIt('commonmark').enable('table')
    report = (root / expected[0]).read_text()
    parsed = renderer.parse(report)
    tables = [token.map for token in parsed if token.type == 'table_open']
    lines = report.splitlines()
    groups = []
    for index, line in enumerate(lines):
        if line.startswith('|') and (index == 0 or not lines[index - 1].startswith('|')):
            end = index + 1
            while end < len(lines) and lines[end].startswith('|'):
                end += 1
            groups.append({'line': index + 1, 'rows_including_header': end - index,
                           'header': line, 'rendered_as_table': any(a <= index < b for a, b in tables)})
    links = []
    for match in re.finditer(r'\[[^\]]+\]\(([^)]+)\)', (root / expected[2]).read_text()):
        value = match.group(1)
        target = (root / 'preview' / value).resolve()
        assert target.is_relative_to(root.resolve()), ('Out-of-fixture handoff link', value)
        links.append({'target': value, 'exists': target.is_file()})
    assert links and all(item['exists'] for item in links)
    return {'arm': result['arm'], 'fixture': str(root), 'frozen_hashes_verified': True,
            'csv_structure_and_numbers': 'PASS', 'handoff_links': links,
            'markdown_pipe_groups': groups, 'rendered_table_count': len(tables),
            'unrendered_pipe_group_count': sum(not item['rendered_as_table'] for item in groups),
            'render_basis': 'markdown-it-py CommonMark with table extension; no browser/pixel or human check',
            'semantic_quality': 'LEAD_REVIEW_REQUIRED; parser does not grade the estimates'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--summary', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists(), 'Fresh receipt required'
    data = json.loads(args.summary.read_text())
    results = [inspect(row) for row in data['results'] if row['case_id'] == 'canonical-high-preview']
    assert len(results) == 2
    payload = {'summary_sha256': sha(args.summary), 'results': results, 'input_mutations': False}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8') as stream:
        json.dump(payload, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps(payload, ensure_ascii=False))


if __name__ == '__main__':
    main()
