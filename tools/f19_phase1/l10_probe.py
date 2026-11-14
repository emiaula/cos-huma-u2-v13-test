# l10 evidence (read-only): are the biceps / triceps / elbow label covered by the view toolbar or by the panel?
import json, sys, time
from playwright.sync_api import sync_playwright
PORT, OUT = sys.argv[1], sys.argv[2]
VP = {'D1920': (1920, 1080, False), 'D1440': (1440, 900, False), 'D1366': (1366, 768, False),
      'T1180L': (1180, 820, True), 'T820P': (820, 1180, True), 'P393': (393, 851, True)}
JS = r"""()=>{const A=__app,T=A.THREE,cam=A.camera;cam.updateMatrixWorld(true);
 const rr=e=>{const b=e.getBoundingClientRect();return{x0:b.left,y0:b.top,x1:b.right,y1:b.bottom}};
 const V=rr(document.getElementById('Vbox')),L=rr(document.getElementById('L')),W=innerWidth,H=innerHeight;
 const ban=document.querySelector('.banner').getBoundingClientRect().bottom;
 const inR=(p,r)=>p.x>=r.x0&&p.x<=r.x1&&p.y>=r.y0&&p.y<=r.y1;
 const out={};
 for(const [k,re] of [['biceps',/left biceps brachii/],['triceps',/left triceps brachii/]]){const ms=A.find(re,'muscle');const pts=[];const v=new T.Vector3();
  for(const m of ms){m.updateMatrixWorld(true);const p=m.geometry.attributes.position;const st=Math.max(1,Math.floor(p.count/1500));for(let i=0;i<p.count;i+=st){v.fromBufferAttribute(p,i).applyMatrix4(m.matrixWorld);const q=v.clone().project(cam);pts.push({x:(q.x+1)/2*W,y:(1-q.y)/2*H})}}
  const vis=pts.filter(p=>p.x>=0&&p.x<=W&&p.y>=ban&&p.y<=H&&!inR(p,L));
  out[k]={onScreen:+(vis.length/pts.length).toFixed(3),underToolbar:+(vis.filter(p=>inR(p,V)).length/pts.length).toFixed(3)};}
 const e=A.elbows.Left.center.clone().project(cam);const ep={x:(e.x+1)/2*W,y:(1-e.y)/2*H};out.elbow={x:Math.round(ep.x),y:Math.round(ep.y),underToolbar:inR(ep,V),underPanel:inR(ep,L)};
 const lb=[...document.querySelectorAll('#labels .lbl')].filter(x=>x.offsetParent).map(x=>({t:x.textContent,r:rr(x)}));
 const ov=(a,b)=>Math.max(0,Math.min(a.x1,b.x1)-Math.max(a.x0,b.x0))*Math.max(0,Math.min(a.y1,b.y1)-Math.max(a.y0,b.y0));
 out.labelsUnderToolbar=lb.filter(l=>ov(l.r,V)>0).map(l=>l.t);out.labels=lb.map(l=>l.t);return out}"""
res = []
with sync_playwright() as pw:
    br = pw.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
    for vp, (W, H, touch) in VP.items():
        ctx = br.new_context(viewport={'width': W, 'height': H}, is_mobile=(vp == 'P393'), has_touch=touch); pg = ctx.new_page()
        pg.goto(f'http://127.0.0.1:{PORT}/curs.html?l=l10'); pg.wait_for_function('window.__curs', timeout=300000)
        pg.evaluate("localStorage.clear()"); pg.reload(); pg.wait_for_function('window.__curs', timeout=300000)
        pg.click('#Lbegin'); time.sleep(4)
        # the step where the names are labelled on the model (biceps, triceps, colze)
        for _ in range(12):
            if pg.evaluate("document.querySelectorAll('#labels .lbl').length>=2"): break
            if pg.evaluate("getComputedStyle(document.getElementById('Lskip')).display!=='none'"): pg.click('#Lskip')
            else: pg.evaluate("document.getElementById('Lnext').disabled||document.getElementById('Lnext').click()")
            time.sleep(1.2)
        time.sleep(2.5); r = pg.evaluate(JS); r['vp'] = vp; r['step'] = pg.evaluate("__curs.S[__curs.idx].id"); res.append(r)
        pg.screenshot(path=f'{OUT}_{vp}.png'); print(vp, json.dumps(r), flush=True); ctx.close()
    br.close()
json.dump(res, open(OUT + '.json', 'w'), indent=0)
