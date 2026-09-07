#!/usr/bin/env python3
"""Read-only human projection of the existing campaign; never grants approval."""
import argparse
from datetime import datetime, timezone
import hashlib
import html
import json
from pathlib import Path
import re
import sys
from urllib.parse import quote
sys.dont_write_bytecode = True
from campaign import inspect_state, check_evidence


def text(value):
    value = html.escape(' '.join(str(value).split()), quote=False)
    return re.sub(r'([\\\x60*_{}\[\]#|])', r'\\\1', value)


def link(path, label):
    return '[' + text(label) + '](<' + quote(str(path), safe='/:-._') + '>)'


def observation(item):
    try:
        check_evidence(item, fresh=True)
        return {'valid': True, 'reason': '檔案與紀錄的雜湊一致'}
    except (ValueError, OSError, TypeError) as error:
        return {'valid': False, 'reason': str(error)}


def project(state):
    inspect_state(state)
    criteria = []
    for key, criterion in state['criteria'].items():
        proof = observation(criterion.get('evidence')) if criterion.get('evidence') is not None else None
        criteria.append({'id': key, **criterion, 'proof_check': proof})
    operations = []
    for key, operation in state['operations'].items():
        proof = observation(operation.get('evidence')) if operation['outcome'] in ('succeeded', 'failed') else None
        operations.append({'id': key, **operation, 'proof_check': proof})
    focus = state.get('focus')
    if focus is not None:
        if not isinstance(focus, dict) or focus.get('criterion') not in state['criteria']:
            raise ValueError('Invalid focus; do not guess the next criterion')
        if not all(isinstance(focus.get(k), str) and focus[k].strip() for k in ('move', 'expect')):
            raise ValueError('Focus needs an explicit move and expected change')
    block = next((event.get('reason') for event in reversed(state['events'])
                  if isinstance(event, dict) and event.get('action') == 'block'), None)
    return {'objective': state['objective'], 'scope': state['scope'], 'revision': state['revision'],
            'status': state['status'], 'focus': focus,
            'focus_already_met': bool(focus and state['criteria'][focus['criterion']]['result'] == 'met'),
            'block_reason': block if state['status'] == 'blocked' else None,
            'criteria': criteria, 'operations': operations,
            'evidence_failures': [row['id'] for row in criteria + operations
                                  if row['proof_check'] is not None and not row['proof_check']['valid']]}


def render(state, state_path, observed_at):
    view = project(state)
    status = {'active': '進行中', 'blocked': '等待必要條件', 'complete': '帳本已記錄結案'}[view['status']]
    lines = ['# 接手便箋', '', text(view['objective']), '',
             f'帳本狀態：{status}；版本 {view["revision"]}。證據完整性觀測時間：{text(observed_at)}。', '']
    if view['evidence_failures']:
        lines += ['**證據需刷新：不能把這份便箋當成完成證明。**', '']
    lines += ['目標與條件沿用帳本原文。這是只讀整理，不是新增驗收、授權或人的同意；雜湊一致也不證明內容足以支持結論。', '',
              '## 目前接續點', '']
    if view['status'] == 'complete':
        lines += ['目前帳本已結案；便箋不會重啟工作或替下一件事取得授權。']
    else:
        if view['status'] == 'blocked' and not view['block_reason']:
            lines += ['等待原因未記錄；本工具不替主手猜測。']
        if view['block_reason']:
            lines += ['等待原因（帳本紀錄）：' + text(view['block_reason'])]
        if view['focus']:
            focus = view['focus']
            lines += [text(focus['criterion']) + '：' + text(focus['move']),
                      '預期可觀察變化：' + text(focus['expect'])]
            if view['focus_already_met']:
                lines += ['此主攻對應條件已記錄達成，接續點可能落後；需主手重新判斷，不自動挑下一個條件。']
        else:
            lines += ['尚未記錄主攻；本工具不代選下一步。']
    pending = [row for row in view['operations'] if row['outcome'] in ('pending', 'unknown')]
    if pending:
        lines += ['', '## 未結操作：釐清結果前不要重送', '']
        for row in pending:
            lines += ['- ' + text(row['id']) + '｜' + text(row['outcome']) + '｜目標：' + text(row['target'])]
            if row.get('note'):
                lines += ['  ' + text(row['note'])]
    unmet = [row for row in view['criteria'] if row['result'] != 'met' or not row['proof_check']['valid']]
    met = [row for row in view['criteria'] if row['result'] == 'met' and row['proof_check']['valid']]
    for title, rows in [('尚未達成或需要補證', unmet), ('已記錄達成（不是另一次驗收）', met)]:
        lines += ['', '## ' + title, '']
        if not rows:
            lines += ['無此類紀錄。']
        for row in rows:
            lines += ['- ' + text(row['id']) + '：' + text(row['text'])]
            if row.get('note'):
                lines += ['  紀錄判斷：' + text(row['note'])]
            if row['proof_check'] is not None:
                if row['proof_check']['valid']:
                    lines += ['  ' + link(row['evidence']['path'], '查看所據證據') + '（本次雜湊一致）']
                else:
                    lines += ['  證據未通過完整性檢查：' + text(row['proof_check']['reason'])]
    failed_proofs = [row for row in view['operations'] if row['proof_check'] is not None and not row['proof_check']['valid']]
    if failed_proofs:
        lines += ['', '## 歷次操作證據需刷新', '']
        for row in failed_proofs:
            lines += ['- ' + text(row['id']) + '｜紀錄結果 ' + text(row['outcome']) + '：' + text(row['proof_check']['reason'])]
    lines += ['', '## 範圍與原始紀錄', '', text(view['scope']), '',
              link(state_path, '查看完整帳本（含事件與操作紀錄）'), '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('state', type=Path)
    parser.add_argument('--output', type=Path, help='Optional new Markdown file; existing files are never replaced')
    args = parser.parse_args()
    path = args.state.resolve(strict=True)
    if args.state.is_symlink():
        raise ValueError('State symlinks are not supported')
    before = path.read_bytes()
    output = render(json.loads(before), path, datetime.now(timezone.utc).isoformat())
    if path.read_bytes() != before:
        raise ValueError('State changed during projection; reload rather than publish stale view')
    if args.output:
        target = args.output.absolute()
        if target.suffix != '.md' or target.is_symlink() or target.exists():
            raise ValueError('A new .md destination is required; no overwrite')
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('x', encoding='utf-8') as stream:
            stream.write(output)
        print('HANDOFF_BRIEF_WRITTEN ' + str(target))
    else:
        print(output, end='')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, TypeError, json.JSONDecodeError) as error:
        print('BRIEF_ERROR: ' + str(error), file=sys.stderr)
        sys.exit(2)
