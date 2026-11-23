"""Convert KanjiVG hiragana SVGs into sampled stroke polylines (data/strokes.json).
Usage: python3 -I tools/kanjivg_to_json.py vendor-raw/kanjivg data/strokes.json
KanjiVG (c) Ulrich Apel, CC BY-SA 3.0 — https://kanjivg.tagaini.net
"""
import json, math, os, re, sys, xml.etree.ElementTree as ET

def tokens(d):
    for m in re.finditer(r'[MmCcSsLlHhVvZz]|-?\d*\.?\d+(?:e-?\d+)?', d):
        yield m.group(0)

def parse(d):
    toks = list(tokens(d)); i = 0; cmd = None
    x = y = 0.0; segs = []; lastc2 = None
    def num():
        nonlocal i
        v = float(toks[i]); i += 1; return v
    while i < len(toks):
        if re.match(r'[A-Za-z]', toks[i]): cmd = toks[i]; i += 1
        if cmd in 'Mm':
            nx, ny = num(), num()
            if cmd == 'm': nx += x; ny += y
            x, y = nx, ny; lastc2 = None; cmd = 'l' if cmd == 'm' else 'L'
            start = (x, y)
        elif cmd in 'Cc':
            p = [num() for _ in range(6)]
            if cmd == 'c': p = [p[0]+x, p[1]+y, p[2]+x, p[3]+y, p[4]+x, p[5]+y]
            segs.append(((x, y), (p[0], p[1]), (p[2], p[3]), (p[4], p[5])))
            lastc2 = (p[2], p[3]); x, y = p[4], p[5]
        elif cmd in 'Ss':
            p = [num() for _ in range(4)]
            if cmd == 's': p = [p[0]+x, p[1]+y, p[2]+x, p[3]+y]
            c1 = (2*x - lastc2[0], 2*y - lastc2[1]) if lastc2 else (x, y)
            segs.append(((x, y), c1, (p[0], p[1]), (p[2], p[3])))
            lastc2 = (p[0], p[1]); x, y = p[2], p[3]
        elif cmd in 'Ll':
            nx, ny = num(), num()
            if cmd == 'l': nx += x; ny += y
            segs.append(((x, y), (x, y), (nx, ny), (nx, ny))); x, y = nx, ny; lastc2 = None
        elif cmd in 'Zz':
            pass
        else:
            raise ValueError('unsupported ' + cmd)
    return segs

def bez(s, t):
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = s; u = 1 - t
    return (u**3*x0 + 3*u*u*t*x1 + 3*u*t*t*x2 + t**3*x3, u**3*y0 + 3*u*u*t*y1 + 3*u*t*t*y2 + t**3*y3)

def sample(segs, step=1.5):
    pts = [segs[0][0]]
    for s in segs:
        for k in range(1, 41):
            p = bez(s, k / 40)
            if math.dist(p, pts[-1]) >= step: pts.append(p)
    end = bez(segs[-1], 1)
    if math.dist(end, pts[-1]) > 0.2: pts.append(end)
    return [[round(a, 1), round(b, 1)] for a, b in pts]

src, out = sys.argv[1], sys.argv[2]
res = {}
for fn in sorted(os.listdir(src)):
    if not fn.endswith('.svg'): continue
    ch = chr(int(fn[:-4], 16))
    root = ET.parse(os.path.join(src, fn)).getroot()
    paths = [e for e in root.iter() if e.tag.endswith('path') and re.search(r'-s\d+$', e.get('id', ''))]
    paths.sort(key=lambda e: int(e.get('id').rsplit('-s', 1)[1]))
    res[ch] = [sample(parse(p.get('d'))) for p in paths]
with open(out, 'w') as f:
    json.dump(res, f, ensure_ascii=False, separators=(',', ':'))
print(len(res), 'chars', os.path.getsize(out), 'bytes')
print(' '.join(f'{c}{len(v)}' for c, v in res.items()))
