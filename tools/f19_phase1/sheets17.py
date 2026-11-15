# 17 views × 6 viewports: before 8cc7f94 | pilot 856a79b | now (composed views) — one JPEG per view
import json, os
from PIL import Image, ImageDraw, ImageFont
F=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',14); FB=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',16)
OUT='sheets17'; os.makedirs(OUT,exist_ok=True)
COMP=[('l03','braç'),('l03','braçDarrere'),('l03','tot'),('l07','braç'),('l07','tronc'),('l07','esquena'),('l08','cap'),('l08','capCostat'),('l08','coll'),('l08','collDarrere'),('l08','davant'),('l08','davantCostat')]
DCL=[('l04','cama'),('l04','camaDarrere'),('l04','tot'),('l04','peu'),('l07','peu')]
VPS=['D1920','D1440','D1366','T1180L','T820P','P393']
B={(r['lesson'],r['view'],r['vp']):r for r in json.load(open('run/base_all.json'))}
P={(r['lesson'],r['view'],r['vp']):r for r in json.load(open('run/br_all.json'))}
N={(r['lesson'],r['view'],r['vp']):r for r in json.load(open('run/new_all.json'))}
def base(vp,L,v):
    for d in (['run/views_base_fix','run/views_base'] if L=='l08' else ['run/views_base_fix2','run/views_base'] if L=='l07' else ['run/views_base']):
        p=f'{d}/{vp}/{L}__{v}.png'
        if os.path.exists(p): return p
def tag(r):
    t=[]
    if r['inSafe'] is not None and r['inSafe']<.98: t.append('target cut')
    for k,v in r['regions'].items():
        if v.startswith('cut') and float(v[4:])<.98: t.append(f'{k} {float(v[4:]):.0%}')
    if r['underToolbar']: t.append('under toolbar')
    return ', '.join(t) or 'ok'
for L,v in COMP+DCL:
    comp=(L,v) in COMP; cols=[('8cc7f94',lambda vp: base(vp,L,v),B),('856a79b',lambda vp: f'run/views_br/{vp}/{L}__{v}.png',P)]
    if comp: cols.append(('now',lambda vp: f'v2/{vp}/{L}__{v}.png',N))
    rows=[]
    for vp in VPS:
        ims=[Image.open(f(vp)).convert('RGB') for _,f,_ in cols]; th=200 if ims[0].size[0]>ims[0].size[1] else 420; s=th/ims[0].size[1]; ims=[i.resize((int(i.size[0]*s),th)) for i in ims]
        w=max(ims[0].size[0],250); r=Image.new('RGB',(len(ims)*(w+6)+70,th+36),'white'); d=ImageDraw.Draw(r); d.text((2,100),vp,fill='black',font=FB)
        for j,(im,(name,_,data)) in enumerate(zip(ims,cols)):
            x=70+j*(w+6); t=tag(data[(L,v,vp)]); d.text((x,2),f'{name}: {t}'[:40],fill=(0,110,0) if t=='ok' else (170,0,0),font=F); r.paste(im,(x,20))
        rows.append(r)
    W=max(r.size[0] for r in rows); sh=Image.new('RGB',(W,sum(r.size[1] for r in rows)+34),(235,235,235))
    ImageDraw.Draw(sh).text((6,8),f'{L} · {v} · '+('8cc7f94 | 856a79b | now (declarative composition)' if comp else '8cc7f94 | 856a79b = now (not changed; hand/foot case review)'),fill='black',font=FB)
    y=34
    for r in rows: sh.paste(r,(0,y)); y+=r.size[1]
    sh.save(f'{OUT}/{L}_{v}.jpg',quality=72)
print('ok', len(os.listdir(OUT)))
