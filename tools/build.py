"""Build dist/index.html (data inlined) and dist/img/*.jpg (resized photos).
Usage: python3 -I tools/build.py
"""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *a: os.path.join(ROOT, *a)

creatures = json.load(open(P('data/creatures.json')))
strokes = json.load(open(P('data/strokes.json')))
credits = json.load(open(P('data/credits.json'))) if os.path.exists(P('data/credits.json')) else {}
skip = set(json.load(open(P('data/skip_images.json')))) if os.path.exists(P('data/skip_images.json')) else set()

os.makedirs(P('dist/img'), exist_ok=True)
out_credits = {}
for c in creatures:
    cr = credits.get(c['id'])
    if not cr or c['id'] in skip or not os.path.exists(P(cr['raw'])):
        c.pop('img', None); continue
    dst = P('dist/img', c['id'] + '.jpg')
    if not os.path.exists(dst) or os.path.getmtime(dst) < os.path.getmtime(P(cr['raw'])):
        subprocess.run(['sips', '-Z', '640', '-s', 'format', 'jpeg', '-s', 'formatOptions', '72', P(cr['raw']), '--out', dst],
                       check=True, stdout=subprocess.DEVNULL)
    c['img'] = 'img/' + c['id'] + '.jpg'
    out_credits[c['id']] = {k: cr[k] for k in ('artist', 'license', 'licenseUrl', 'source', 'file')}

data = {'creatures': creatures, 'strokes': strokes, 'credits': out_credits}
src = open(P('src/index.html')).read()
html = src.replace('/*__DATA__*/null', json.dumps(data, ensure_ascii=False, separators=(',', ':')))
open(P('dist/index.html'), 'w').write(html)
# CREDITS.md (generated; keep in sync with data/credits.json)
lines = ['# クレジット / Credits', '',
         'このファイルは `tools/build.py` が `data/credits.json` から生成します。手で編集しないでください。', '',
         '## 書き順データ / Stroke order data', '',
         '`data/strokes.json` は KanjiVG のひらがなSVGを点列に変換したものです。',
         'KanjiVG — Copyright (C) Ulrich Apel — https://kanjivg.tagaini.net — '
         '[CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/)。',
         '変換したデータも CC BY-SA 3.0 で提供します。', '',
         '## 写真 / Photos (Wikimedia Commons)', '',
         '各写真は元のライセンスのまま利用しています。`dist/img/` の画像は長辺640pxに縮小し、JPEGに変換しています。',
         'Each photo keeps its original license. Images in `dist/img/` were resized to 640px and converted to JPEG.', '']
for c in creatures:
    cr = out_credits.get(c['id'])
    if not cr: continue
    lic = f"[{cr['license']}]({cr['licenseUrl']})" if cr.get('licenseUrl') else cr['license']
    lines.append(f"- **{c['name']}** (`img/{c['id']}.jpg`) — {cr['artist']} — {lic} — [{cr['file']}]({cr['source']})")
open(P('CREDITS.md'), 'w').write('\n'.join(lines) + '\n')

missing = [c['id'] for c in creatures if 'img' not in c]
print('html', len(html.encode()) // 1024, 'KB; images', len(out_credits), '; missing', missing)
