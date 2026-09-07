from .normalization import normalize_events


def project_accounts(snapshots, events, requested_ids):
    by_id = {row['account_id']: dict(row) for row in snapshots}
    for event in normalize_events(events):
        row = by_id.get(event['account_id'])
        if row and event['revision'] > row['revision']:
            row['balance'] += event['delta']
            row['revision'] = event['revision']
    accounts = []
    for account_id in sorted(set(requested_ids)):
        row = by_id.get(account_id)
        accounts.append({'account_id': account_id, 'status': 'complete' if row else 'missing',
                         'revision': row['revision'] if row else None,
                         'balance': row['balance'] if row else None,
                         'first_missing_revision': None})
    return {'accounts': accounts, 'duplicates_ignored': 0}
