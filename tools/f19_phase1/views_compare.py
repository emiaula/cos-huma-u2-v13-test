import json, sys, collections
B = {(r['lesson'], r['view'], r['vp']): r for r in json.load(open(sys.argv[1]))}
N = {(r['lesson'], r['view'], r['vp']): r for r in json.load(open(sys.argv[2]))}
LES = sys.argv[3].split(',')
def cats(r):
    c = {}
    if r['inSafe'] is not None and r['inSafe'] < .98: c['T'] = r['inSafe']            # framed parts not fully inside the safe area
    cut = lambda v: v.startswith('cut') and float(v[4:]) < .98          # really cut by an edge (part of it not on screen)
    tight = lambda v: v.startswith('cut') and float(v[4:]) >= .98       # whole on screen but inside the 6 % margin
    if cut(r['regions']['head']): c['H'] = r['regions']['head']
    x = [k for k in ('handL', 'handR', 'footL', 'footR') if cut(r['regions'][k])]
    if x: c['X'] = x
    m = [k for k in r['regions'] if tight(r['regions'][k])]
    if m: c['M'] = m
    if r['underToolbar']: c['B'] = r['underToolbar']                                   # framed parts under the toolbar
    return c
tot = collections.Counter(); per = collections.defaultdict(lambda: collections.Counter())
viewsum = collections.defaultdict(lambda: {'b': set(), 'n': set()})
for k in sorted(B):
    if k[0] not in LES or k not in N: continue
    cb, cn = cats(B[k]), cats(N[k])
    for c in 'THXBM':
        s = ('both' if c in cb and c in cn else 'fixed' if c in cb else 'new' if c in cn else None)
        if s: tot[(c, s)] += 1; per[k[0]][(c, s)] += 1
    viewsum[(k[0], k[1])]['b'] |= set(cb); viewsum[(k[0], k[1])]['n'] |= set(cn)
    if '-v' in sys.argv and (cb or cn): print(k, 'BASE', cb, 'NEW', cn, 'fillH %.2f->%.2f' % (B[k]['fillH'] or 0, N[k]['fillH'] or 0))
n = sum(1 for k in B if k[0] in LES and k in N)
print('cases (view x viewport):', n)
for c, name in zip('THXBM', ['target not fully in safe area', 'head cut by an edge', 'hand/foot cut by an edge', 'target under toolbar', 'head/hand/foot only in margin']):
    b = tot[(c, 'both')] + tot[(c, 'fixed')]; a = tot[(c, 'both')] + tot[(c, 'new')]
    print(f'{c} {name:32s} before {b:3d}  after {a:3d}  fixed {tot[(c,"fixed")]:3d}  new {tot[(c,"new")]:3d}')
clean_b = sum(1 for k in B if k[0] in LES and k in N and not {x for x in cats(B[k]) if x!='M'}); clean_n = sum(1 for k in N if k[0] in LES and k in B and not {x for x in cats(N[k]) if x!='M'})
print('cases with no issue: before', clean_b, 'after', clean_n)
print('per view (union over viewports), after:')
for (L, v), s in sorted(viewsum.items()):
    print(f'  {L} {v:14s} before {"".join(sorted(s["b"])) or "-":5s} after {"".join(sorted(s["n"])) or "-"}')
