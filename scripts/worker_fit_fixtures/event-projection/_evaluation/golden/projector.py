def project_accounts(snapshots, events, requested_ids):
    def text(value):
        return isinstance(value, str) and bool(value)
    def integer(value):
        return type(value) is int
    if not all(isinstance(value, list) for value in (snapshots, events, requested_ids)):
        raise ValueError('lists required')
    if not all(text(value) for value in requested_ids):
        raise ValueError('invalid request')
    by_account = {}
    for value in snapshots:
        if (not isinstance(value, dict) or not text(value.get('account_id')) or
                not integer(value.get('revision')) or value['revision'] < 0 or
                not integer(value.get('balance'))):
            raise ValueError('invalid snapshot')
        if value['account_id'] in by_account:
            raise ValueError('snapshot conflict')
        by_account[value['account_id']] = (value['revision'], value['balance'])
    identities, revisions, duplicates = {}, {}, 0
    for value in events:
        if (not isinstance(value, dict) or not text(value.get('event_id')) or
                not text(value.get('account_id')) or not integer(value.get('revision')) or
                value['revision'] <= 0 or not integer(value.get('delta'))):
            raise ValueError('invalid event')
        identity = value['event_id']
        body = (value['account_id'], value['revision'], value['delta'])
        if identity in identities:
            if identities[identity] != body:
                raise ValueError('event identity conflict')
            duplicates += 1
            continue
        pair = body[:2]
        if pair in revisions:
            raise ValueError('event revision conflict')
        identities[identity] = body
        revisions[pair] = identity
    accounts = []
    for account in sorted(set(requested_ids)):
        if account not in by_account:
            accounts.append({'account_id': account, 'status': 'missing', 'revision': None,
                             'balance': None, 'first_missing_revision': None})
            continue
        revision, balance = by_account[account]
        pending = sorted((rev, delta) for acc, rev, delta in identities.values()
                         if acc == account and rev > revision)
        missing = None
        for rev, delta in pending:
            if rev != revision + 1:
                missing = revision + 1
                break
            revision, balance = rev, balance + delta
        accounts.append({'account_id': account, 'status': 'incomplete' if missing else 'complete',
                         'revision': revision, 'balance': None if missing else balance,
                         'first_missing_revision': missing})
    return {'accounts': accounts, 'duplicates_ignored': duplicates}
