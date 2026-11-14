# F19 layout and camera check (phase 1). Measures, it never changes a lesson.
# usage: python3 tools/f19_layout.py MODE PORT OUTDIR VP[,VP...] LESSON[,LESSON...]
#   MODE layout : lesson panel vs view toolbar on the start step and the first question (overlap, every panel button and
#                 every toolbar button really clickable at its centre, toolbar buttons >= 44 px, the 5 toolbar buttons work)
#   MODE views  : every camera view of the lesson: the parts the view frames (or, for a hand-written view, the region it asks
#                 for) must lie inside the safe area (free model area minus a 6 % margin on every side); head, hands and feet
#                 are either fully inside the safe area or fully out of the model area; no framed part under the toolbar.
#                 Screenshot per view.
#   MODE cam    : every camera view: the exact flyTo request and the camera projection (to prove a lesson's framing did not
#                 change between two builds). No waiting for animations.
# viewports: D1920 D1440 D1366 (desktop) · T1180L T820P (tablet, touch) · P393 (phone, touch)
# server: python3 -m http.server PORT --bind 127.0.0.1 in the build to measure (e.g. 8771 = frozen 8cc7f94, 8772 = branch)
import json, sys, os, time
from playwright.sync_api import sync_playwright
MODE, PORT, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
VPS, LESSONS = sys.argv[4].split(','), sys.argv[5].split(',')
VP = {'D1920': (1920, 1080, False), 'D1440': (1440, 900, False), 'D1366': (1366, 768, False),
      'T1180L': (1180, 820, True), 'T820P': (820, 1180, True), 'P393': (393, 851, True)}
os.makedirs(OUT, exist_ok=True)
# toolbar buttons are one shared component: their function is tested in these lessons only (all lessons by default)
TB_LESSONS = os.environ.get('F19_TOOLBAR_LESSONS', ','.join(LESSONS)).split(',')

HELPERS = r"""
window.__f19 = (() => {
  const A = __app, T = A.THREE, cam = A.camera, MARGIN = .06;
  const rect = e => { if (!e || !e.offsetParent && getComputedStyle(e).position !== 'fixed') return null; const b = e.getBoundingClientRect(); return b.width && b.height ? { x0: b.left, y0: b.top, x1: b.right, y1: b.bottom } : null; };
  const shown = e => e && getComputedStyle(e).display !== 'none' && getComputedStyle(e).visibility !== 'hidden';
  // free model area: below the banner, beside/above the panel, clear of the toolbar when the toolbar is inside it
  function free() {
    const W = innerWidth, H = innerHeight; let x0 = 0, y0 = 0, x1 = W, y1 = H;
    const ban = document.querySelector('.banner'); if (shown(ban)) y0 = ban.getBoundingClientRect().bottom;
    const L = document.getElementById('L');
    if (shown(L)) { const r = L.getBoundingClientRect(); if (r.width < W * .9) x1 = Math.min(x1, r.left); else y1 = Math.min(y1, r.top); }
    const V = document.getElementById('Vbox');
    if (shown(V)) { const r = V.getBoundingClientRect(); if (r.left < x1 && r.top < y1 && r.width && r.height) { if (r.height >= r.width) x1 = Math.min(x1, r.left); else y1 = Math.min(y1, r.top); } }
    return { x0, y0, x1, y1 };
  }
  const inset = (f, m) => { const mx = (f.x1 - f.x0) * m, my = (f.y1 - f.y0) * m; return { x0: f.x0 + mx, y0: f.y0 + my, x1: f.x1 - mx, y1: f.y1 - my }; };
  const ov = (a, b) => { if (!a || !b) return 0; const w = Math.min(a.x1, b.x1) - Math.max(a.x0, b.x0), h = Math.min(a.y1, b.y1) - Math.max(a.y0, b.y0); return w > 0 && h > 0 ? Math.round(w * h) : 0; };
  // every visible button of the panel / toolbar: is the button itself what a tap at its centre reaches?
  function hits(sel) { return [...document.querySelectorAll(sel)].filter(b => shown(b) && b.offsetParent).map(b => { const r = b.getBoundingClientRect(); if (!r.width) return null;
      const cx = r.left + r.width / 2, cy = r.top + r.height / 2; const inView = cx >= 0 && cy >= 0 && cx < innerWidth && cy < innerHeight;
      const e = inView ? document.elementFromPoint(cx, cy) : null; return { id: b.id || b.className || b.textContent.trim().slice(0, 12), w: Math.round(r.width), h: Math.round(r.height), ok: !!e && (e === b || b.contains(e)), by: e && !(e === b || b.contains(e)) ? (e.id || e.className || e.tagName) : null }; }).filter(Boolean); }
  function layout() {
    const L = document.getElementById('L'), V = document.getElementById('Vbox');
    return { L: rect(L), V: shown(V) ? rect(V) : null, overlap: ov(shown(L) ? rect(L) : null, shown(V) ? rect(V) : null), free: free(),
      panel: hits('#L .Lhead button, #Lbody button, .Lnav button'), toolbar: hits('#Vbox button'),
      bodyFont: parseFloat(getComputedStyle(document.getElementById('Lbody')).fontSize) };
  }
  // world points of a set of meshes (sampled vertices)
  function pts(meshes, cap = 6000) {
    let n = 0; for (const m of meshes) n += m.geometry.attributes.position.count; const st = Math.max(1, Math.floor(n / cap)); const out = [], v = new T.Vector3();
    for (const m of meshes) { m.updateMatrixWorld(true); const p = m.geometry.attributes.position; for (let i = 0; i < p.count; i += st) { v.fromBufferAttribute(p, i).applyMatrix4(m.matrixWorld); out.push(v.clone()); } }
    return out;
  }
  function screen(points) { cam.updateMatrixWorld(true); const W = innerWidth, H = innerHeight;
    return points.map(p => { const q = p.clone().project(cam); return { x: (q.x + 1) / 2 * W, y: (1 - q.y) / 2 * H, front: q.z < 1 }; }); }
  const E = 1.5;   // px tolerance: a point exactly on the edge of the area counts as inside
  const frac = (sp, r) => sp.length ? sp.filter(p => p.front && p.x >= r.x0 - E && p.x <= r.x1 + E && p.y >= r.y0 - E && p.y <= r.y1 + E).length / sp.length : null;
  const bbox = sp => { const f = sp.filter(p => p.front); if (!f.length) return null; return { x0: Math.min(...f.map(p => p.x)), y0: Math.min(...f.map(p => p.y)), x1: Math.max(...f.map(p => p.x)), y1: Math.max(...f.map(p => p.y)) }; };
  const R = s => A.find(s, 'bone');
  const regions = {
    head: () => R(/^(frontal bone|occipital bone|mandible|left parietal bone|right parietal bone|left maxilla|right maxilla|left temporal bone|right temporal bone|left zygomatic bone|right zygomatic bone)$/),
    handL: () => R(/^left (.*metacarpal bone|scaphoid|lunate|capitate|hamate|trapezium|trapezoid|pisiform|triquetrum)$|phalanx of left (thumb|.*finger)$/),
    handR: () => R(/^right (.*metacarpal bone|scaphoid|lunate|capitate|hamate|trapezium|trapezoid|pisiform|triquetrum)$|phalanx of right (thumb|.*finger)$/),
    footL: () => R(/^left (calcaneus|talus|navicular bone|cuboid bone|.*cuneiform bone|.*metatarsal bone)$|phalanx of left .*toe$/),
    footR: () => R(/^right (calcaneus|talus|navicular bone|cuboid bone|.*cuneiform bone|.*metatarsal bone)$|phalanx of right .*toe$/) };
  const RP = {}; for (const k in regions) RP[k] = pts(regions[k](), 1500);
  // capture what a view asks for: meshes passed to boxOf (frame/helpers) or, for a hand-written view, centre + fitDist(h, w)
  let cap = null; const C = __curs.ctx, oBox = A.boxOf, oFly = A.flyTo, oFit = C.fitDist;
  A.boxOf = ms => { if (cap) cap.meshes = ms; return oBox(ms); };
  C.fitDist = (h, w) => { const d = oFit(h, w); if (cap) cap.fit = [h, w === undefined ? h * .55 : w]; return d; };
  A.flyTo = (t, o, ms) => { if (cap) { cap.t = t.toArray(); cap.o = o.toArray(); cap.ms = ms; } return oFly(t, o, cap && cap.fast ? 1 : ms); };
  function start(v, fast) { cap = { view: v, fast }; C.clearLabels && C.clearLabels(); C.view(v); const c = cap; return { t: c.t, o: c.o, mesh: !!c.meshes, fit: c.fit || null }; }
  function camState() { const v = cam.view; return { fov: cam.fov, aspect: cam.aspect, view: v && v.enabled ? [v.fullWidth, v.fullHeight, v.offsetX, v.offsetY, v.width, v.height] : null }; }
  function measure() {
    const c = cap, fr = free(), sf = inset(fr, MARGIN), V = document.getElementById('Vbox'), vr = shown(V) ? rect(V) : null;
    let tp;
    if (c.meshes) tp = pts(c.meshes);
    else if (c.fit && c.t) { cam.updateMatrixWorld(true); const t = new T.Vector3(...c.t), r = new T.Vector3().setFromMatrixColumn(cam.matrixWorld, 0), u = new T.Vector3().setFromMatrixColumn(cam.matrixWorld, 1);
      tp = []; for (const a of [-1, -.5, 0, .5, 1]) for (const b of [-1, -.5, 0, .5, 1]) tp.push(t.clone().addScaledVector(r, a * c.fit[1]).addScaledVector(u, b * c.fit[0])); }
    else tp = [];
    const sp = screen(tp), bb = bbox(sp);
    // head / hands / feet: 'in' = whole region inside the safe area, 'out' = none of it in the model area, else 'cut' (cut by an edge or in the margin)
    const reg = {}; for (const k in RP) { const s = screen(RP[k]), a = frac(s, sf), b = frac(s, fr); reg[k] = a >= .98 ? 'in' : b <= .02 ? 'out' : 'cut:' + b.toFixed(2); }
    return { view: c.view, kind: c.meshes ? 'parts' : (c.fit ? 'region' : 'none'), free: fr, safe: sf,
      inSafe: sp.length ? +frac(sp, sf).toFixed(3) : null, inFree: sp.length ? +frac(sp, fr).toFixed(3) : null,
      underToolbar: vr && sp.length ? +frac(sp, vr).toFixed(3) : 0, bbox: bb,
      fillH: bb ? +((bb.y1 - bb.y0) / (sf.y1 - sf.y0)).toFixed(3) : null, fillW: bb ? +((bb.x1 - bb.x0) / (sf.x1 - sf.x0)).toFixed(3) : null,
      regions: reg, cam: camState(), pos: cam.position.toArray().map(x => +x.toFixed(4)), target: A.controls.target.toArray().map(x => +x.toFixed(4)) };
  }
  return { layout, start, measure, camState };
})();
"""

def open_lesson(br, vp, L):
    W, H, touch = VP[vp]
    ctx = br.new_context(viewport={'width': W, 'height': H}, is_mobile=(vp == 'P393'), has_touch=touch, device_scale_factor=1)
    pg = ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    # a new browser context starts with empty storage: the lesson opens on its start page with a fresh record
    pg.goto(f'http://127.0.0.1:{PORT}/curs.html?l={L}'); pg.wait_for_function('window.__curs', timeout=300000); time.sleep(.5)
    pg.click('#Lbegin', timeout=180000); time.sleep(2.5); pg.evaluate(HELPERS)
    return ctx, pg, errs, touch

def press(pg, sel, touch):
    (pg.tap if touch else pg.click)(sel)

def toolbar_works(pg, touch):
    """the 5 toolbar buttons: zoom in / out change the distance, turn goes behind, reset goes back, A+ toggles big text."""
    d = lambda: pg.evaluate("__app.camera.position.distanceTo(__app.controls.target)")
    side = lambda: pg.evaluate("(()=>{const c=__app.camera.position.clone().sub(__app.controls.target);return Math.sign(c.z)})()")
    res = {}; d0, s0 = d(), side()
    press(pg, '#Vin', touch); time.sleep(2.2); res['Vin'] = d() < d0 * .9
    press(pg, '#Vout', touch); time.sleep(2.2); res['Vout'] = abs(d() - d0) < d0 * .05
    press(pg, '#Vturn', touch); time.sleep(2.8); res['Vturn'] = side() == -s0 or s0 == 0
    press(pg, '#Vrst', touch); time.sleep(2.8); res['Vrst'] = side() == s0
    b0 = pg.evaluate("document.body.classList.contains('bigtext')"); press(pg, '#Vtxt', touch); time.sleep(.4)
    res['Vtxt'] = pg.evaluate("document.body.classList.contains('bigtext')") != b0; press(pg, '#Vtxt', touch); time.sleep(.3)
    return res

def goto_question(pg):
    for _ in range(14):
        if pg.evaluate("!!document.querySelector('#Lbody .opts, #Lbody .q')"): break
        if pg.evaluate("getComputedStyle(document.getElementById('Lskip')).display!=='none'"): pg.click('#Lskip')
        else: pg.evaluate("document.getElementById('Lnext').disabled||document.getElementById('Lnext').click()")
        time.sleep(.8)
    time.sleep(1.5); return pg.evaluate("__curs.S[__curs.idx].id")

rows = []
with sync_playwright() as pw:
    br = pw.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
    for vp in VPS:
        os.makedirs(f'{OUT}/{vp}', exist_ok=True)
        for L in LESSONS:
            ctx, pg, errs, touch = open_lesson(br, vp, L)
            if MODE == 'layout':
                g = pg.evaluate("__f19.layout()"); pg.screenshot(path=f'{OUT}/{vp}/{L}__intro.png')
                rows.append({'vp': vp, 'lesson': L, 'step': 'intro', **g})
                sid = goto_question(pg); g = pg.evaluate("__f19.layout()"); pg.screenshot(path=f'{OUT}/{vp}/{L}__q.png')
                rows.append({'vp': vp, 'lesson': L, 'step': 'question:' + sid, **g, 'toolbarWorks': toolbar_works(pg, touch) if L in TB_LESSONS else 'not run'})
            else:
                for v in pg.evaluate("Object.keys(__curs.CFG.views||{})"):
                    req = pg.evaluate("([v,f])=>__f19.start(v,f)", [v, MODE == 'views'])
                    if MODE == 'cam':
                        rows.append({'vp': vp, 'lesson': L, 'view': v, 'req': req, 'cam': pg.evaluate("__f19.camState()")}); continue
                    # wait until the camera has really arrived (slow software rendering), then one more frame
                    pg.wait_for_function("([t,o])=>{const p=__app.camera.position,q=__app.controls.target;return Math.hypot(p.x-t[0]-o[0],p.y-t[1]-o[1],p.z-t[2]-o[2])<1e-3&&Math.hypot(q.x-t[0],q.y-t[1],q.z-t[2])<1e-3}", arg=[req['t'], req['o']], timeout=30000)
                    time.sleep(.8); m = pg.evaluate("__f19.measure()")
                    pg.screenshot(path=f'{OUT}/{vp}/{L}__{v}.png'); rows.append({'vp': vp, 'lesson': L, 'req': req, **m})
            rows[-1]['errs'] = errs[:]
            print(MODE, PORT, vp, L, 'errs', len(errs), flush=True); ctx.close()
            json.dump(rows, open(f'{OUT}/{MODE}.json', 'w'), ensure_ascii=False, indent=0)   # saved after every lesson
    br.close()
json.dump(rows, open(f'{OUT}/{MODE}.json', 'w'), ensure_ascii=False, indent=0)
