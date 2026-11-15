# F19 open defect F19-14 (registration only, not fixed): on the phone (393×851) one l10 answer option has its centre
# under the «Continua» bar. Reproduces the case and reports the geometry, before and after scrolling the panel.
# usage: python3 tools/f19_phase1/l10_phone_option.py PORT OUT.json
import json, sys, time
from playwright.sync_api import sync_playwright
PORT, OUT = sys.argv[1], sys.argv[2]
JS = r"""()=>{const r=e=>{const b=e.getBoundingClientRect();return [Math.round(b.left),Math.round(b.top),Math.round(b.width),Math.round(b.height)]};
 const body=document.getElementById('Lbody'),nav=document.querySelector('.Lnav');
 const opts=[...document.querySelectorAll('#Lbody button.opt')].filter(b=>b.offsetParent).map(b=>{const q=b.getBoundingClientRect(),cx=q.left+q.width/2,cy=q.top+q.height/2,e=document.elementFromPoint(cx,cy);
   return {text:b.textContent.trim().slice(0,40),rect:r(b),hit:!!e&&(e===b||b.contains(e)),by:e&&!(e===b||b.contains(e))?(e.id||e.className):null}});
 return {step:__curs.S[__curs.idx].id,body:{rect:r(body),scrollTop:body.scrollTop,scrollHeight:body.scrollHeight,clientHeight:body.clientHeight,scrollable:body.scrollHeight>body.clientHeight+2},nav:r(nav),opts}}"""
with sync_playwright() as pw:
    br = pw.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
    ctx = br.new_context(viewport={'width': 393, 'height': 851}, is_mobile=True, has_touch=True); pg = ctx.new_page()
    pg.goto(f'http://127.0.0.1:{PORT}/curs.html?l=l10'); pg.wait_for_function('window.__curs', timeout=300000)
    pg.click('#Lbegin', timeout=180000); time.sleep(3)
    for _ in range(14):
        if pg.evaluate("!!document.querySelector('#Lbody .opts, #Lbody .q')"): break
        if pg.evaluate("getComputedStyle(document.getElementById('Lskip')).display!=='none'"): pg.click('#Lskip')
        else: pg.evaluate("document.getElementById('Lnext').disabled||document.getElementById('Lnext').click()")
        time.sleep(.8)
    time.sleep(2); before = pg.evaluate(JS); pg.screenshot(path=OUT.replace('.json', '_before.png'))
    # the child scrolls the panel (or the browser scrolls the option into view)
    pg.evaluate("[...document.querySelectorAll('#Lbody button.opt')].filter(b=>b.offsetParent).pop().scrollIntoView({block:'nearest'})"); time.sleep(.6)
    after = pg.evaluate(JS); pg.screenshot(path=OUT.replace('.json', '_scrolled.png'))
    # can the hidden option be tapped where it is shown before scrolling? (a real tap at its centre)
    res = {'before_scroll': before, 'after_scroll': after}
    json.dump(res, open(OUT, 'w'), ensure_ascii=False, indent=1); print(json.dumps(res, ensure_ascii=False)[:1500]); br.close()
