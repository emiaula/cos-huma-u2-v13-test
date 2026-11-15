import json, collections, os
from PIL import Image, ImageDraw, ImageFont
F=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)
N=json.load(open('run/new_all.json')); comp={(r['lesson'],r['view']) for r in json.load(open('v2/views.json'))}
cut=lambda v: v.startswith('cut') and float(v[4:])<.98
pv=collections.defaultdict(list)
for r in N:
    for k,v in r['regions'].items():
        if cut(v): pv[(r['lesson'],r['view'])].append((k,r['vp'],float(v[4:])))
cells=[]
for (L,v),cases in sorted(pv.items()):
    vps=[c[1] for c in cases]; vp='D1440' if 'D1440' in vps else ('T820P' if 'T820P' in vps else vps[0])
    d='v2' if (L,v) in comp else 'run/views_br'
    im=Image.open(f'{d}/{vp}/{L}__{v}.png').convert('RGB'); s=300/im.size[1] if im.size[0]>im.size[1] else 300/im.size[1]
    im=im.resize((int(im.size[0]*s),300))
    txt=', '.join(f'{k} {f:.0%}' for k,p,f in cases if p==vp)
    c=Image.new('RGB',(max(im.size[0],380),340),'white'); dr=ImageDraw.Draw(c); dr.text((3,2),f'{L} {v} · {vp}',fill='black',font=F); dr.text((3,20),f'visible: {txt}',fill=(160,0,0),font=F); c.paste(im,(0,40)); cells.append(c)
cols=4; W=max(c.size[0] for c in cells); rows=(len(cells)+cols-1)//cols
sh=Image.new('RGB',(cols*(W+8),rows*348),(230,230,230))
for i,c in enumerate(cells): sh.paste(c,((i%cols)*(W+8),(i//cols)*348))
sh.save('dclass_sheet.jpg',quality=80); print(len(cells), sh.size)
