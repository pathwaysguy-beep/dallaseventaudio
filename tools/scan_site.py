# -*- coding: utf-8 -*-
"""Read every page the way the concierge would need to know it: what the page
is, who it is for, what is on it, and the questions it already answers."""
import glob, html, io, json, os, re

R = '/tmp/dea/gh3/'
TAG = re.compile(r'<[^>]+>')

def text(s):
    s = re.sub(r'(?is)<(script|style)\b.*?</\1>', ' ', s)
    # keep internal link targets: the concierge needs the URL, not just the label
    s = re.sub(r'(?is)<a [^>]*href="(/[^"#]*)"[^>]*>(.*?)</a>', r'\2 (\1)', s)
    s = TAG.sub(' ', s)
    s = html.unescape(s).replace('\u00a0', ' ').replace('\u00b7', '.')
    s = s.replace('\u2019', "'").replace('\u2018', "'")
    s = s.replace('\u201c', '"').replace('\u201d', '"')
    s = s.replace('\u2014', ' - ').replace('\u2013', '-')
    s = re.sub(r'\s+', ' ', s).strip()
    return re.sub(r'\s+([.,;:)])', r'\1', s).replace('( /', '(/')

def one(s, pat, g=1):
    m = re.search(pat, s, re.S | re.I)
    return text(m.group(g)) if m else ''

pages = []
for fn in sorted(glob.glob(R + '*.html')) + sorted(glob.glob(R + 'post/*.html')):
    base = os.path.basename(fn)
    if base == '404.html':
        continue
    s = io.open(fn, encoding='utf-8').read()
    slug = '/' + ('post/' if '/post/' in fn else '') + base[:-5]
    if base == 'index.html':
        slug = '/'

    # The visible FAQ carries the same words as the FAQPage schema, plus the
    # internal links, so read the page rather than the schema.
    faqs = [(text(m.group(1)), text(m.group(2))) for m in re.finditer(
        r'<summary[^>]*>(.*?)</summary>\s*<(?:div class="ans"|p)>(.*?)</(?:div|p)>',
        s, re.S)]
    if not faqs:
        for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
            try:
                d = json.loads(m.group(1))
            except Exception:
                continue
            nodes = d if isinstance(d, list) else [d]
        nodes = [x for n in nodes for x in
                 (n.get('@graph', [n]) if isinstance(n, dict) else [n])]
        for node in nodes:
                if isinstance(node, dict) and node.get('@type') == 'FAQPage':
                    for q in node.get('mainEntity', []):
                        faqs.append((text(q.get('name', '')),
                                     text(q.get('acceptedAnswer', {}).get('text', ''))))

    h2 = [text(m.group(1)) for m in re.finditer(r'<h2[^>]*>(.*?)</h2>', s, re.S | re.I)]
    body = text(re.sub(r'(?is)<(header|footer|nav)\b.*?</\1>', ' ', s))
    paras = [text(m.group(1)) for m in re.finditer(r'<p[^>]*>(.*?)</p>', s, re.S | re.I)]
    paras = [p for p in paras if len(p) > 90]

    pages.append({
        'slug': slug,
        'title': one(s, r'<title>(.*?)</title>'),
        'desc': one(s, r'<meta name="description" content="([^"]*)"'),
        'h1': one(s, r'<h1[^>]*>(.*?)</h1>'),
        'h2': [h for h in h2 if h and len(h) < 130],
        'lead': paras[:3],
        'faqs': faqs,
        'words': len(body.split()),
    })

json.dump(pages, io.open('/tmp/dea/site_scan.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('%d pages' % len(pages))
print('%d FAQ pairs' % sum(len(p['faqs']) for p in pages))
print('%d words of body copy' % sum(p['words'] for p in pages))
print('%d H2 headings' % sum(len(p['h2']) for p in pages))
