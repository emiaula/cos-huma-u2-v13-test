# F19 todo «phone small-bone tapping» — read-only evaluation for l04 (kneecap, fibula, foot bones).
# For every view in which l04 asks the child to tap a bone (practice, scored and review), and for candidate close-up
# shots composed on the fly with the existing shared compose() (nothing in the lesson is changed), it measures the real
# tappable area of each bone under the player's own rule (phone_check.py). The scoring rule is not touched.
# usage: python3 tools/f19_phase1/small_bones.py PORT OUT.json VP
import json, sys, os, time
from playwright.sync_api import sync_playwright
PORT, OUT, VPN = sys.argv[1], sys.argv[2], sys.argv[3]
W, H = {'P393': (393, 851), 'P360': (360, 740)}[VPN]
SRC = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'phone_check.py')).read()
EXTRA = SRC.split('EXTRA = r"""')[1].split('"""')[0]
# where l04 asks for a tap today (curs/l04.js: groups g1 g2 g3 + review): view → names
CURRENT = {'cama': ['femur', 'rotula', 'tibia', 'perone'], 'camaCostat': ['femur', 'rotula'], 'camaDarrere': ['tibia', 'perone'],
           'peu': ['tars', 'metatars', 'falangesPeu'], 'peuCostat': ['tars', 'metatars', 'falangesPeu'], 'tot': ['femur', 'rotula', 'tibia', 'perone', 'tars', 'metatars', 'falangesPeu']}
# candidate close-ups (target, direction, options) — same compose() the lessons already use
CAND = {'genoll_davant_p3': (['rotula'], [.3, .05, 1], {'pad': 3}, ['rotula']),
        'genoll_davant_p5': (['rotula'], [.3, .05, 1], {'pad': 5}, ['rotula']),
        'genoll_costat_p4': (['rotula'], [1, .05, .3], {'pad': 4}, ['rotula']),
        'camaBaixa_costat': (['tibia', 'perone'], [1, .05, .2], {}, ['tibia', 'perone']),
        'camaBaixa_davant': (['tibia', 'perone'], [.3, .05, 1], {}, ['tibia', 'perone']),
        'peu_dalt': (['tars', 'metatars', 'falangesPeu'], [.35, .8, 1], {}, ['tars', 'metatars', 'falangesPeu'])}
res = []
with sync_playwright() as pw:
    br = pw.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
    ctx = br.new_context(viewport={'width': W, 'height': H}, is_mobile=True, has_touch=True); pg = ctx.new_page()
    pg.goto(f'http://127.0.0.1:{PORT}/curs.html?l=l04'); pg.wait_for_function('window.__curs', timeout=300000)
    pg.click('#Lbegin', timeout=180000); time.sleep(2.5); pg.evaluate(EXTRA)
    shots = [(v, 'view', None, n) for v, n in CURRENT.items()] + [(k, 'candidate', c, c[3]) for k, c in CAND.items()]
    for name, kind, c, names in shots:
        if kind == 'view': pg.evaluate("v=>__curs.ctx.view(v)", name)
        else: pg.evaluate("([t,d,o])=>__curs.ctx.compose(t,d,o)", [c[0], c[1], c[2]])
        time.sleep(4); sz = pg.evaluate("__ev.sizes()"); png = OUT.replace('.json', f'_{name}.png'); pg.screenshot(path=png)
        row = {'vp': VPN, 'shot': name, 'kind': kind, 'bones': {}}
        for n in names:
            if n not in sz: row['bones'][n] = {'visible': False}; continue
            t = pg.evaluate("([k,b])=>__ev.tapArea(k,b)", [n, sz[n]['box']]); row['bones'][n] = {'w': sz[n]['w'], 'h': sz[n]['h'], **t}
        res.append(row); print(VPN, name, json.dumps(row['bones']), flush=True)
    br.close()
json.dump(res, open(OUT, 'w'), ensure_ascii=False, indent=1)
