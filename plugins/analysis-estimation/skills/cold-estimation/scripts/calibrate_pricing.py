"""Optional, traceable price calibration over unchanged operation inputs."""
from copy import deepcopy
from pathlib import Path
import argparse
import hashlib
import json
import estimate_math as base

DEFAULT_PROFILES = Path(__file__).with_name('pricing-calibration.json')


def totals(result):
    result['known_totals'] = {
        key: sum((row.get(key) or 0) for row in result['items'])
        for key in ('E_pd', 'V_pd', 'unsplit_pd')
    }
    assert sum(result['known_totals'].values()) == result['known_subtotal_pd']
    return result


def calculate(data, profiles):
    original = totals(base.calculate(data))
    settings = data.get('calibration')
    if settings is None:
        return original, deepcopy(data), None
    if not isinstance(settings, dict):
        raise ValueError('calibration must be an object')
    profile = settings.get('profile')
    if not isinstance(profile, str) or profile not in profiles.get('profiles', {}):
        raise ValueError('unknown calibration profile; do not infer a route from project names')
    factor = base.number(profiles['profiles'][profile]['coefficient'])
    if factor == 0:
        raise ValueError('calibration coefficient must be positive')
    exempt = settings.get('fixed_operation_ids', [])
    if not isinstance(exempt, list) or any(not isinstance(x, str) for x in exempt) or len(exempt) != len(set(exempt)):
        raise ValueError('fixed_operation_ids must be a list of unique operation IDs')
    operations = {op['id']: op for row in data['items'] for op in row.get('operations', [])}
    if set(exempt) - set(operations):
        raise ValueError('a fixed operation ID does not exist in the unchanged input')
    if exempt and not str(settings.get('fixed_basis', '')).strip():
        raise ValueError('fixed operations need their existing fee or responsibility basis')

    effective = deepcopy(data)
    trace = []
    for row in effective['items']:
        original_hours = {'E': base.D(0), 'V': base.D(0)}
        fixed_hours = {'E': base.D(0), 'V': base.D(0)}
        for op in row.get('operations', []):
            hours, _ = base.operation_hours(op)
            original_hours[op['kind']] += hours
            if op['id'] in exempt:
                fixed_hours[op['kind']] += hours
            else:
                op['hours'] = str(base.number(op['hours']) * factor)
        trace.append({
            'id': row['id'], 'original_hours': original_hours,
            'fixed_hours': fixed_hours,
            'variable_hours': {k: original_hours[k] - fixed_hours[k] for k in ('E', 'V')}
        })
    adjusted = totals(base.calculate(effective))
    if [(r['id'], r['status']) for r in adjusted['items']] != [(r['id'], r['status']) for r in original['items']]:
        raise ValueError('calibration would change a scope classification; retain the original result and review the formula')
    metadata = {
        'version': profiles['version'], 'profile': profile, 'coefficient': factor,
        'basis': profiles['basis'], 'fixed_operation_ids': exempt,
        'fixed_basis': settings.get('fixed_basis'),
        'original_known_subtotal_pd': original['known_subtotal_pd'],
        'original_known_totals': original['known_totals'],
        'trace': trace,
        'limits': [
            'Only operation-hour rates are calibrated; count and batch ratios remain unchanged.',
            'Fixed allocations, explicitly identified fixed operations and additions retain their original values.',
            'Original pending and scope-review states are preserved; calibration cannot complete missing work.',
            'Coefficients are empirical calibration parameters, not observed productivity measurements.'
        ]
    }
    adjusted['calibration'] = metadata
    return adjusted, effective, original


def render(data, result, original, digest):
    if original is None:
        return base.render(data, result, digest)
    meta = result['calibration']
    lines = [
        '# 經驗校準的定價結果', '',
        f"公式版本：{meta['version']}；路線：{meta['profile']}；係數：{meta['coefficient']}。",
        f"依據：{meta['basis']}", '',
        '每欄校準工時 = 固定工時 + 原可調工時 × 路線係數。批次數量已按原 N/N0 換算；不再乘第二次数量。',
        '依原自然工項取整：含批次採 ROUND_HALF_UP，其他列採 ceil。固定額度和一般加值沿用原數值。', '',
        '| ID | 工作 | 原始 E/V 小時 | 固定 E/V 小時 | 校準後 E/V 小時 | 執行人天 | 驗證人天 | 合計 |',
        '|---|---|---:|---:|---:|---:|---:|---:|'
    ]
    for source, row, trace in zip(data['items'], result['items'], meta['trace']):
        def pair(values):
            return str(values['E']) + ' / ' + str(values['V'])
        def display(key):
            if row.get(key) is not None:
                return row[key]
            if row['status'] == 'pending':
                return '待估'
            if row['status'] == 'fixed' and key in ('E_pd', 'V_pd'):
                return '未拆'
            return '待處理' if key == 'total_pd' else '—'
        values = [row['id'], source.get('name', ''), pair(trace['original_hours']),
                  pair(trace['fixed_hours']), str(display('E_hours')) + ' / ' + str(display('V_hours')),
                  display('E_pd'), display('V_pd'), display('total_pd')]
        lines.append('| ' + ' | '.join(base.md(v) for v in values) + ' |')
    lines += ['', f"校準後已估小計：{result['known_subtotal_pd']} 人天；E {result['known_totals']['E_pd']}、V {result['known_totals']['V_pd']}、未拆 {result['known_totals']['unsplit_pd']}。",
              f"校準前已估小計：{original['known_subtotal_pd']} 人天（工程判斷基準，供覆核）。", '',
              '## 原工項與操作保持不變', '',
              '下段保留原始操作、工時、數量與計價依據；最終交付人天引用上表的校準結果，不混用兩套總額。', '',
              base.render(data, original, digest)]
    return '\n'.join(lines) + '\n'


def publish(input_path, output_directory, profile_path=DEFAULT_PROFILES):
    source = Path(input_path)
    out = Path(output_directory)
    if out.exists():
        raise ValueError('output directory already exists; choose a new version')
    raw = source.read_bytes()
    profiles_raw = Path(profile_path).read_bytes()
    data = json.loads(raw)
    profiles = json.loads(profiles_raw)
    for row in data['items']:
        for op in row.get('operations', []):
            if not str(op.get('description', '')).strip():
                raise ValueError('each priced operation needs a readable action/result description')
    result, effective, original = calculate(data, profiles)
    result['input_sha256'] = hashlib.sha256(raw).hexdigest()
    result['script_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    result['base_script_sha256'] = hashlib.sha256(Path(base.__file__).read_bytes()).hexdigest()
    result['profiles_sha256'] = hashlib.sha256(profiles_raw).hexdigest()
    report = render(data, result, original, result['input_sha256'])
    out.mkdir(parents=True, exist_ok=False)
    with (out/'input.json').open('xb') as handle:
        handle.write(raw)
    with (out/'profiles.json').open('xb') as handle:
        handle.write(profiles_raw)
    for name, payload in [('result.json', result), ('effective-input.json', effective)]:
        with (out/name).open('x', encoding='utf-8') as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2, default=base.serial)
            handle.write('\n')
    with (out/'pricing.md').open('x', encoding='utf-8') as handle:
        handle.write(report)
    return {'output': str(out), 'known_subtotal_pd': result['known_subtotal_pd'], 'complete': result['complete'],
            'input_sha256': result['input_sha256'], 'profiles_sha256': result['profiles_sha256']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input')
    parser.add_argument('output_directory')
    parser.add_argument('--profiles', default=str(DEFAULT_PROFILES))
    args = parser.parse_args()
    print(json.dumps(publish(args.input, args.output_directory, args.profiles), ensure_ascii=False, default=base.serial))
