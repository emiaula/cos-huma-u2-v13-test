# before/after contact sheets for the F19 phase-1 pilot (JPEG, small) + layout sheets
import json, os, sys, glob
from PIL import Image, ImageDraw, ImageFont
R = '/home/claude/f19p1/run'; OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
try: F = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
except Exception: F = ImageFont.load_default()
B = {(r['lesson'], r['view'], r['vp']): r for r in json.load(open(f'{R}/base_all.json'))}
N = {(r['lesson'], r['view'], r['vp']): r for r in json.load(open(f'{R}/br_all.json'))}
def find(dirs, vp, name):
    for d in dirs:
        p = f'{R}/{d}/{vp}/{name}'
        if os.path.exists(p): return p
def tag(r):
    t = []
    if r['inSafe'] is not None and r['inSafe'] < .98: t.append('T%.2f' % r['inSafe'])
    for k, v in r['regions'].items():
        if v.startswith('cut') and float(v[4:]) < .98: t.append(f'{k} cut')
    if r['underToolbar']: t.append('toolbar')
    return ' '.join(t) or 'ok'
VPS = ['D1920', 'D1440', 'D1366', 'T1180L', 'T820P', 'P393']
for L in ['l03', 'l04', 'l07', 'l08']:
    for vp in VPS:
        views = [k[1] for k in N if k[0] == L and k[2] == vp]
        cw = 300; cells = []
        for v in views:
            a = find(['views_base_fix', 'views_base_fix2', 'views_base'], vp, f'{L}__{v}.png') if (L, vp) in [('l08', 'D1440'), ('l08', 'D1366'), ('l07', 'T1180L')] else find(['views_base'], vp, f'{L}__{v}.png')
            b = find(['views_br'], vp, f'{L}__{v}.png')
            ia, ib = Image.open(a).convert('RGB'), Image.open(b).convert('RGB'); s = cw / ia.size[0]; h = int(ia.size[1] * s)
            c = Image.new('RGB', (2 * cw + 8, h + 40), 'white'); d = ImageDraw.Draw(c)
            d.text((4, 2), f'{v} · before: {tag(B[(L, v, vp)])}', fill='black', font=F); d.text((4, 20), f'after: {tag(N[(L, v, vp)])}', fill=(0, 90, 0) if tag(N[(L, v, vp)]) == 'ok' else (160, 0, 0), font=F)
            c.paste(ia.resize((cw, h)), (0, 40)); c.paste(ib.resize((cw, h)), (cw + 8, 40)); cells.append(c)
        cols = 3 if cells[0].size[0] < 700 else 2
        rows = [cells[i:i + cols] for i in range(0, len(cells), cols)]
        W = cols * (cells[0].size[0] + 12); H = sum(max(c.size[1] for c in r) + 12 for r in rows) + 30
        sh = Image.new('RGB', (W, H), (235, 235, 235)); ImageDraw.Draw(sh).text((6, 6), f'F19 phase 1 · {L} · {vp} · each pair: before (8cc7f94) | after (f19-phase1)', fill='black', font=F)
        y = 30
        for r in rows:
            x = 0
            for c in r: sh.paste(c, (x, y)); x += c.size[0] + 12
            y += max(c.size[1] for c in r) + 12
        sh.save(f'{OUT}/views_{L}_{vp}.jpg', quality=72)
print('ok')
