# F19 phone check (393×851, 360×740): every view of the given lessons — framing (measure() of f19_layout.py), size of
# every fully visible name, name labels against the toolbar / panel / screen edge (with how much of each label the
# toolbar hides: the toolbar is drawn above the labels; labels take no taps), and for l04 the real tappable area of
# every name under the player's own rule (ray hit, plus the 8-px box of a small piece when no other named part is in
# front). Measures only.
# usage: python3 tools/f19_phase1/phone_check.py PORT OUTDIR VP LESSON[,LESSON...]
import json, sys, os, time
from playwright.sync_api import sync_playwright
PORT, OUT, VPN, LESSONS = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4].split(',')
VP = {'P393': (393, 851), 'P360': (360, 740)}
W, H = VP[VPN]; os.makedirs(f'{OUT}/{VPN}', exist_ok=True)
SRC = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'f19_layout.py')).read()
HELPERS = SRC.split('HELPERS = r"""')[1].split('"""')[0]
# per view: (1) size of every name fully visible, (2) labels vs toolbar/panel/edges, (3) l04: real tappable area
EXTRA = r"""
window.__ev = (() => {
  const A = __app, T = A.THREE, cam = A.camera, C = __curs.ctx, CFG = __curs.CFG;
  const R = e => { const b = e.getBoundingClientRect(); return { x0: b.left, y0: b.top, x1: b.right, y1: b.bottom }; };
  const ov = (a, b) => Math.max(0, Math.min(a.x1, b.x1) - Math.max(a.x0, b.x0)) * Math.max(0, Math.min(a.y1, b.y1) - Math.max(a.y0, b.y0));
  function free() { const W = innerWidth, H = innerHeight, ban = document.querySelector('.banner').getBoundingClientRect().bottom, L = R(document.getElementById('L')), V = R(document.getElementById('Vbox'));
    const f = { x0: 0, y0: ban, x1: W, y1: L.y0 }; if (V.x0 < f.x1 && V.y0 < f.y1) { if (V.y1 - V.y0 >= V.x1 - V.x0) f.x1 = Math.min(f.x1, V.x0); else f.y1 = Math.min(f.y1, V.y0); } return f; }
  function proj(ms, cap = 600) { const v = new T.Vector3(), out = []; cam.updateMatrixWorld(true);
    for (const m of ms) { m.updateMatrixWorld(true); const p = m.geometry.attributes.position, st = Math.max(1, Math.floor(p.count / cap)); for (let i = 0; i < p.count; i += st) { const q = v.fromBufferAttribute(p, i).applyMatrix4(m.matrixWorld).project(cam); out.push([(q.x + 1) / 2 * innerWidth, (1 - q.y) / 2 * innerHeight]); } } return out; }
  function sizes() { const f = free(), out = {};
    for (const [k, ms] of Object.entries(C.parts)) { if (!ms || !ms.length) continue; const sp = proj(ms);
      const inn = sp.filter(([x, y]) => x >= f.x0 && x <= f.x1 && y >= f.y0 && y <= f.y1).length / sp.length; if (inn < .98) continue;
      const xs = sp.map(p => p[0]), ys = sp.map(p => p[1]); out[k] = { w: Math.round(Math.max(...xs) - Math.min(...xs)), h: Math.round(Math.max(...ys) - Math.min(...ys)), box: [Math.min(...xs), Math.min(...ys), Math.max(...xs), Math.max(...ys)] }; }
    return out; }
  // the player's own rule (hitAt + nearSmall), copied: a tap counts when the ray hits the target, or (no other named
  // structure in front) the tap is within 8 px of the on-screen box of a target piece smaller than 40 px
  function nearSmall(x, y, targets) { for (const m of targets) { const b = A.boxOf([m]), xs = [], ys = [];
      for (const cx of [b.min.x, b.max.x]) for (const cy of [b.min.y, b.max.y]) for (const cz of [b.min.z, b.max.z]) { const v = new T.Vector3(cx, cy, cz).project(cam); xs.push((v.x + 1) / 2 * innerWidth); ys.push((1 - v.y) / 2 * innerHeight); }
      const w = Math.max(...xs) - Math.min(...xs), h = Math.max(...ys) - Math.min(...ys);
      if (w < 40 && h < 40 && x > Math.min(...xs) - 8 && x < Math.max(...xs) + 8 && y > Math.min(...ys) - 8 && y < Math.max(...ys) + 8) return true; } return false; }
  function tapArea(k, box) { const targets = new Set(C.parts[k]), f = free(), [x0, y0, x1, y1] = box, e = 12;
    const area = (x1 - x0 + 2 * e) * (y1 - y0 + 2 * e), st = Math.max(2, Math.sqrt(area / 3000)); let n = 0, ray = 0;
    for (let x = x0 - e; x <= x1 + e; x += st) for (let y = y0 - e; y <= y1 + e; y += st) {
      if (x < f.x0 || x > f.x1 || y < f.y0 || y > f.y1) continue;   // only where the child can actually tap the model
      const h = __curs.hitAt(x, y, targets); if (h.ok) { n++; ray++; } else if (!h.hard && nearSmall(x, y, targets)) n++; }
    return { area: Math.round(n * st * st), rayArea: Math.round(ray * st * st), side: Math.round(Math.sqrt(n * st * st)) }; }
  function labels(keys) { C.clearLabels(); C.nameLabels(keys); }
  function labelCheck() { const V = R(document.getElementById('Vbox')), L = R(document.getElementById('L')), f = free();
    return [...document.querySelectorAll('#labels .lbl')].filter(e => e.offsetParent).map(e => { const r = R(e); const hid = [...document.querySelectorAll('#Vbox button')].reduce((a, bt) => a + ov(r, R(bt)), 0), area = (r.x1 - r.x0) * (r.y1 - r.y0);
      return { t: e.textContent, rect: [Math.round(r.x0), Math.round(r.y0), Math.round(r.x1), Math.round(r.y1)], onToolbar: ov(r, V) > 0, hiddenByButtons: +(hid / area).toFixed(2), onPanel: ov(r, L) > 0, outside: r.x0 < 0 || r.x1 > innerWidth || r.y0 < f.y0 - 1 }; }); }
  return { sizes, tapArea, labels, labelCheck };
})();
"""
rows = []
with sync_playwright() as pw:
    br = pw.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
    for L in LESSONS:
        ctx = br.new_context(viewport={'width': W, 'height': H}, is_mobile=True, has_touch=True); pg = ctx.new_page()
        pg.goto(f'http://127.0.0.1:{PORT}/curs.html?l={L}'); pg.wait_for_function('window.__curs', timeout=300000)
        pg.click('#Lbegin', timeout=180000); time.sleep(2.5); pg.evaluate(HELPERS); pg.evaluate(EXTRA)
        for v in pg.evaluate("Object.keys(__curs.CFG.views||{})"):
            req = pg.evaluate("([v,f])=>__f19.start(v,f)", [v, True])
            pg.wait_for_function("([t,o])=>{const p=__app.camera.position;return Math.hypot(p.x-t[0]-o[0],p.y-t[1]-o[1],p.z-t[2]-o[2])<1e-3}", arg=[req['t'], req['o']], timeout=30000)
            time.sleep(.8); m = pg.evaluate("__f19.measure()"); pg.screenshot(path=f'{OUT}/{VPN}/{L}__{v}.png')
            sz = pg.evaluate("__ev.sizes()")
            tap = {k: pg.evaluate("([k,b])=>__ev.tapArea(k,b)", [k, s['box']]) for k, s in sz.items()} if L == 'l04' else {}
            pg.evaluate("k=>__ev.labels(k)", list(sz.keys())); time.sleep(1.2); lab = pg.evaluate("__ev.labelCheck()")
            pg.screenshot(path=f'{OUT}/{VPN}/{L}__{v}__labels.png'); pg.evaluate("__curs.ctx.clearLabels()")
            rows.append({'vp': VPN, 'lesson': L, 'view': v, **m, 'sizes': {k: {'w': s['w'], 'h': s['h']} for k, s in sz.items()}, 'tap': tap, 'labels': lab})
        print(VPN, L, flush=True); ctx.close()
        json.dump(rows, open(f'{OUT}/{VPN}.json', 'w'), ensure_ascii=False, indent=0)
    br.close()
