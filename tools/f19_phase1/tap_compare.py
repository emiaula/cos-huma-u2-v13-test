# compare two tap_size.py outputs (same viewport): how many name-in-view cases have a smaller side under 44 px
import json, sys, statistics
B = {(r['lesson'], r['view']): r['parts'] for r in json.load(open(sys.argv[1]))}
N = {(r['lesson'], r['view']): r['parts'] for r in json.load(open(sys.argv[2]))}
rows = [(k, p, min(B[k][p].values()) if p in B[k] else None, min(N.get(k, {})[p].values()) if p in N.get(k, {}) else None) for k in B for p in set(B[k]) | set(N.get(k, {}))]
for tag, i in (('before', 2), ('after', 3)):
    v = [r[i] for r in rows if r[i] is not None]
    print(f'{tag}: {len(v)} fully visible name-in-view cases; smaller side < 44 px: {sum(x < 44 for x in v)}; median {statistics.median(v)} px')
for L in sorted({r[0][0] for r in rows}):
    b = [r[2] for r in rows if r[0][0] == L and r[2]]; n = [r[3] for r in rows if r[0][0] == L and r[3]]
    print(f'  {L}: median smaller side {statistics.median(b)} -> {statistics.median(n)} px')
both = [(r[2], r[3]) for r in rows if r[2] and r[3]]
print('cases in both builds:', len(both), '· median size ratio after/before: %.2f' % statistics.median(n / b for b, n in both))
print('no longer fully visible after:', sorted(f'{r[0][0]}.{r[0][1]}:{r[1]}' for r in rows if r[2] is not None and r[3] is None))
