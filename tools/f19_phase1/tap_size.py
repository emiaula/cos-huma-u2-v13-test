# F19 phase 1: on-screen size of every name's model parts in every view (are the tap targets big enough?)
# usage: python3 tools/f19_phase1/tap_size.py PORT OUT.json VP LESSON[,LESSON...]
# For each view and each name of the lesson whose parts are fully visible in the model area: the screen box of those
# parts (sampled vertices), its smaller side in px. Run it on two builds and compare.
import json, sys, time, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from playwright.sync_api import sync_playwright
PORT, OUT, VPN, LESSONS = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4].split(',')
VP = {'D1440': (1440, 900, False), 'T1180L': (1180, 820, True), 'T820P': (820, 1180, True), 'P393': (393, 851, True)}
W, H, touch = VP[VPN]
SRC = open(os.path.join(os.path.dirname(__file__), '..', 'f19_layout.py')).read()
HELPERS = SRC.split('HELPERS = r"""')[1].split('"""')[0]
JS = r"""()=>{const A=__app,T=A.THREE,cam=A.camera,C=__curs.ctx;cam.updateMatrixWorld(true);
 const W=innerWidth,H=innerHeight,ban=document.querySelector('.banner').getBoundingClientRect().bottom,L=document.getElementById('L').getBoundingClientRect(),V=document.getElementById('Vbox').getBoundingClientRect();
 let fr={x0:0,y0:ban,x1:W,y1:H}; if(L.width<W*.9) fr.x1=L.left; else fr.y1=L.top;
 if(V.left<fr.x1&&V.top<fr.y1){ if(V.height>=V.width) fr.x1=Math.min(fr.x1,V.left); else fr.y1=Math.min(fr.y1,V.top); }
 const out={};
 for(const [k,ms] of Object.entries(C.parts)){ if(!ms||!ms.length) continue; const v=new T.Vector3(),sp=[];
  for(const m of ms){m.updateMatrixWorld(true);const p=m.geometry.attributes.position,st=Math.max(1,Math.floor(p.count/400));for(let i=0;i<p.count;i+=st){const q=v.fromBufferAttribute(p,i).applyMatrix4(m.matrixWorld).project(cam);sp.push([(q.x+1)/2*W,(1-q.y)/2*H])}}
  const inn=sp.filter(([x,y])=>x>=fr.x0&&x<=fr.x1&&y>=fr.y0&&y<=fr.y1).length/sp.length; if(inn<.98) continue;
  const xs=sp.map(p=>p[0]),ys=sp.map(p=>p[1]); out[k]={w:Math.round(Math.max(...xs)-Math.min(...xs)),h:Math.round(Math.max(...ys)-Math.min(...ys))};}
 return out}"""
res = []
with sync_playwright() as pw:
    br = pw.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
    for L in LESSONS:
        ctx = br.new_context(viewport={'width': W, 'height': H}, is_mobile=(VPN == 'P393'), has_touch=touch); pg = ctx.new_page()
        pg.goto(f'http://127.0.0.1:{PORT}/curs.html?l={L}'); pg.wait_for_function('window.__curs', timeout=300000)
        pg.click('#Lbegin', timeout=180000); time.sleep(2.5); pg.evaluate(HELPERS)
        for v in pg.evaluate("Object.keys(__curs.CFG.views||{})"):
            req = pg.evaluate("([v,f])=>__f19.start(v,f)", [v, True])
            pg.wait_for_function("([t,o])=>{const p=__app.camera.position;return Math.hypot(p.x-t[0]-o[0],p.y-t[1]-o[1],p.z-t[2]-o[2])<1e-3}", arg=[req['t'], req['o']], timeout=30000)
            time.sleep(.5); res.append({'vp': VPN, 'lesson': L, 'view': v, 'parts': pg.evaluate(JS)})
        print(L, flush=True); ctx.close()
    br.close()
json.dump(res, open(OUT, 'w'), ensure_ascii=False, indent=0)
