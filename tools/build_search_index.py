#!/usr/bin/env python3
"""Rebuild /search-index.json for the header search bar (bundle 120).

Run from the repo root after adding, retiring or retitling a page:
    python3 tools/build_search_index.py

The index lists every page in sitemap.xml (so noindex pages, thank-you and
404 stay out) with its title, H1, meta description, a category and the label
the header menu gives it. The search bar fetches it the first time somebody
opens search, so it costs nothing on page load. Keep it small: no body text.
"""
import html as H
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOST = 'https://www.dallaseventaudio.com'

EVENTS = {'weddings', 'wedding-av-rental-dallas', 'corporate-events', 'private-events',
          'live-music-and-band-events', 'college-school-university-events',
          'rave-and-night-club-events', 'celebrity-and-luxury-events',
          'sensory-friendly-event-services', 'fort-worth'}
INFO = {'', 'our-story', 'our-work', 'venues', 'gallery', 'what-others-are-saying',
        'contact', 'privacy', 'blog', 'equipment-list'}


def clean(s):
    return re.sub(r'\s+', ' ', H.unescape(re.sub(r'<[^>]+>', ' ', s or ''))).strip()


def nav_labels():
    """Menu labels by path, from the header and drawer fragments."""
    out = {}
    for frag in ('tools/chrome/header.html', 'tools/chrome/drawer.html'):
        s = (ROOT / frag).read_text(encoding='utf-8')
        for href, label in re.findall(r'<a[^>]+href="(/[^"#?]*)"[^>]*>(.*?)</a>', s, re.S):
            label = clean(label)
            if label and href not in out:
                out[href] = label
    return out


def main():
    labels = nav_labels()
    locs = re.findall(r'<loc>([^<]+)</loc>', (ROOT / 'sitemap.xml').read_text(encoding='utf-8'))
    pages = []
    for loc in locs:
        path = loc.replace(HOST, '') or '/'
        slug = path.strip('/')
        f = ROOT / ((slug or 'index') + '.html')
        if not f.exists():
            raise SystemExit(f'sitemap lists {path} but {f.name} is missing')
        s = f.read_text(encoding='utf-8')
        title = clean((re.search(r'<title>(.*?)</title>', s, re.S) or [None, ''])[1])
        title = title.replace(' | Dallas Event Audio', '').strip()
        desc = (re.search(r'<meta name="description" content="([^"]*)"', s) or [None, ''])[1]
        h1 = clean((re.search(r'<h1[^>]*>(.*?)</h1>', s, re.S) or [None, ''])[1])
        if slug.startswith('post/'):
            cat = 'Guide'
        elif slug in EVENTS:
            cat = 'Event'
        elif slug in INFO:
            cat = 'Info'
        else:
            cat = 'Service'
        entry = {'u': path, 't': title, 'h': h1 if h1 != title else '',
                 'd': H.unescape(desc), 'c': cat}
        if labels.get(path):
            entry['k'] = labels[path]
        pages.append(entry)
    out = ROOT / 'search-index.json'
    out.write_text(json.dumps(pages, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    print(f'search-index.json written, {len(pages)} pages, {out.stat().st_size} bytes')


if __name__ == '__main__':
    main()
