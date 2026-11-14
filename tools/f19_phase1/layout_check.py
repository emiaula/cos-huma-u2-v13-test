import json, sys, collections
rows = []
for f in sys.argv[1:]:
    try: rows += json.load(open(f))
    except Exception as e: print('skip', f, e)
c = collections.Counter(); bad = []
for r in rows:
    c['steps'] += 1
    if r['overlap']: bad.append((r['vp'], r['lesson'], r['step'], 'overlap', r['overlap']))
    for b in r['panel']:
        if not b['ok']: bad.append((r['vp'], r['lesson'], r['step'], 'panel button blocked', b['id'], b['by']))
    for b in r['toolbar']:
        c['toolbar buttons'] += 1
        if not b['ok']: bad.append((r['vp'], r['lesson'], r['step'], 'toolbar button blocked', b['id'], b['by']))
        if min(b['w'], b['h']) < 44: bad.append((r['vp'], r['lesson'], r['step'], 'toolbar button small', b['id'], b['w'], b['h']))
    c['panel buttons'] += len(r['panel'])
    tw = r.get('toolbarWorks')
    if isinstance(tw, dict):
        c['toolbar function tests'] += 1
        for k, v in tw.items():
            if not v: bad.append((r['vp'], r['lesson'], r['step'], 'toolbar button does not work', k))
    if r.get('errs'): bad.append((r['vp'], r['lesson'], r['step'], 'JS errors', r['errs']))
print(dict(c)); print('vps', sorted({r['vp'] for r in rows}), 'lessons', len({r['lesson'] for r in rows}))
print('problems:', len(bad))
for b in bad: print(' ', b)
