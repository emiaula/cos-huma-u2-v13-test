# summary of phone_check.py output: target against the 3 % phone safe area (from the stored screen box of the target),
# head / hand / foot cuts, target under the toolbar, label collisions, name sizes
# usage: python3 tools/f19_phase1/phone_summary.py phone_check_P393.json [phone_check_P360.json …]
import json, sys, statistics
E = 1.5   # px tolerance, as in f19_layout.py
cut = lambda s: s.startswith('cut') and float(s[4:]) < .98
for f in sys.argv[1:]:
    R = json.load(open(f)); vp = R[0]['vp']
    def in3(r):
        fr, b = r['free'], r['bbox']; mx, my = (fr['x1'] - fr['x0']) * .03, (fr['y1'] - fr['y0']) * .03
        return b['x0'] >= fr['x0'] + mx - E and b['x1'] <= fr['x1'] - mx + E and b['y0'] >= fr['y0'] + my - E and b['y1'] <= fr['y1'] - my + E
    sizes = [min(s['w'], s['h']) for r in R for s in r['sizes'].values()]
    print(f'{vp}: views {len(R)} · target inside 3 % safe area {sum(in3(r) for r in R if r["bbox"])}/{sum(1 for r in R if r["bbox"])} · '
          f'target inside model area {sum(1 for r in R if r["inFree"] is not None and r["inFree"] >= .98)}/{len(R)} · head cut {sum(cut(r["regions"]["head"]) for r in R)} · '
          f'hand/foot cut {sum(cut(r["regions"][k]) for r in R for k in ("handL", "handR", "footL", "footR"))} · target under toolbar {sum(1 for r in R if r["underToolbar"])} · '
          f'labels on toolbar {sum(l["onToolbar"] for r in R for l in r["labels"])}, on panel {sum(l["onPanel"] for r in R for l in r["labels"])}, off edge {sum(l["outside"] for r in R for l in r["labels"])} · '
          f'name sizes median {statistics.median(sizes)} px, < 44 px {sum(x < 44 for x in sizes)}/{len(sizes)}')
    for r in R:
        if r['bbox'] and not in3(r): print('   outside 3 % safe area:', r['lesson'], r['view'])
        for l in r['labels']:
            if l['onToolbar']: print('   label on toolbar:', r['lesson'], r['view'], l['t'], l.get('hidden', ''))
