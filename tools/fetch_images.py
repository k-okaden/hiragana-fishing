"""Fetch one freely licensed photo per creature from Wikipedia/Wikimedia Commons.
Usage: python3 -I tools/fetch_images.py data/creatures.json vendor-raw/images data/credits.json [id ...]
Writes raw downloads to vendor-raw/images and license info to data/credits.json.
Optional ids re-fetch only those; data/overrides.json may map id -> "File:Name.jpg".
"""
import json, os, re, sys, time, urllib.error, urllib.parse, urllib.request, html

UA = 'hiragana-fishing-prototype/0.1 (educational, non-commercial)'
FREE = re.compile(r'^(CC0|CC BY|CC-BY|Public domain|PD|Attribution|GFDL|No restrictions|KOGL)', re.I)

def get(url):
    for attempt in range(6):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code != 429 or attempt == 5: raise
            time.sleep(10 * (attempt + 1))

def api(host, **params):
    params.update(format='json', formatversion='2')
    return json.loads(get(f'https://{host}/w/api.php?' + urllib.parse.urlencode(params)))

def strip(s):
    return html.unescape(re.sub(r'<[^>]+>', '', s or '')).strip()

creatures, outdir, credits_path = sys.argv[1], sys.argv[2], sys.argv[3]
only = set(sys.argv[4:])
os.makedirs(outdir, exist_ok=True)
creatures = json.load(open(creatures))
credits = json.load(open(credits_path)) if os.path.exists(credits_path) else {}
overrides = json.load(open('data/overrides.json')) if os.path.exists('data/overrides.json') else {}

for c in creatures:
    cid = c['id']
    if only and cid not in only: continue
    if not only and cid in credits: continue
    try:
        if cid in overrides:
            fname = overrides[cid]
            page = c['wiki']
        else:
            r = api('en.wikipedia.org', action='query', titles=c['wiki'], prop='pageimages', piprop='name', redirects=1)
            p = r['query']['pages'][0]
            page = p.get('title', c['wiki'])
            if 'pageimage' not in p:
                print('NOIMAGE', cid, page); continue
            fname = 'File:' + p['pageimage']
        r = api('commons.wikimedia.org', action='query', titles=fname, prop='imageinfo', iiprop='url|extmetadata|mime|user', iiurlwidth=960)
        pg = r['query']['pages'][0]
        if 'imageinfo' not in pg:
            print('NOTCOMMONS', cid, fname); continue
        ii = pg['imageinfo'][0]; md = ii.get('extmetadata', {})
        lic = strip(md.get('LicenseShortName', {}).get('value'))
        if not FREE.match(lic):
            print('NONFREE', cid, fname, lic); continue
        data = get(ii['thumburl'])
        ext = '.png' if ii['thumburl'].lower().endswith('.png') else '.jpg'
        raw = os.path.join(outdir, cid + ext)
        open(raw, 'wb').write(data)
        credits[cid] = {
            'file': fname, 'raw': raw, 'mime': ii.get('mime'),
            'artist': strip(md.get('Artist', {}).get('value'))[:120] or 'Unknown',
            'license': lic, 'licenseUrl': strip(md.get('LicenseUrl', {}).get('value')),
            'source': ii['descriptionurl'], 'page': page,
        }
        credits[cid]['uploader'] = ii.get('user')
        if credits[cid]['artist'].lower() in ('self', 'unknown', ''):
            print('WARN artist unclear, check the file page and fix data/credits.json:', cid, ii['descriptionurl'])
        print('OK', cid, lic, len(data) // 1024, 'KB', fname)
    except Exception as e:
        print('ERR', cid, e)
    time.sleep(3)

json.dump(credits, open(credits_path, 'w'), ensure_ascii=False, indent=1)
print('total', len(credits))
