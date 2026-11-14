# lessons outside the pilot: every camera request (target, offset) and projection must be identical in both builds
# usage: python3 cam_compare.py cam_before.json cam_after.json
import json, sys, collections
B = {(r['lesson'], r['view'], r['vp']): r for r in json.load(open(sys.argv[1]))}
N = {(r['lesson'], r['view'], r['vp']): r for r in json.load(open(sys.argv[2]))}
flat = lambda r: [*r['req']['t'], *r['req']['o'], r['cam']['fov'], r['cam']['aspect'], *(r['cam']['view'] or [])]
print('cases', len(B), 'same set', set(B) == set(N), 'per lesson', dict(collections.Counter(k[0] for k in B)))
d = [(k, max(abs(x - y) for x, y in zip(flat(B[k]), flat(N[k])))) for k in B if len(flat(B[k])) == len(flat(N[k]))]
print('max abs difference', max(x for _, x in d), '· cases differing by more than 1e-6:', sum(x > 1e-6 for _, x in d), '· shape mismatch:', len(B) - len(d))
