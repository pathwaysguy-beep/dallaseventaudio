# -*- coding: utf-8 -*-
"""Which declared image slots have no photo behind them.

No page on this site ships an empty <img>. Every slot names the exact file it
wants, in an <img src>, a --img:url() custom property, a <source srcset> or a
poster attribute, and the alt text describing the intended photo was written
when the page was built. So the shopping list writes itself: every referenced
filename with no file in /images, paired with the description already on the
page.

Responsive derivatives (-480w/-768w/-1200w/-1920w, .avif/.webp) collapse to
their base, so one line out is one photograph to go find.

Usage
-----
    python tools/image_gaps.py           # grouped report
    python tools/image_gaps.py --csv     # page,file,brief  for a spreadsheet
"""
import io
import os
import re
import sys
import glob
import collections

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)

REF   = re.compile(r'/images/([A-Za-z0-9._\-/]+)\.(?:jpg|jpeg|png|webp|avif|gif)', re.I)
DERIV = re.compile(r'-(?:480|768|1200|1920)w$')


def on_disk():
    """Every photo in /images, as a set of extension-free, derivative-free stems."""
    have = set()
    root = os.path.join(SITE, 'images')
    for dirpath, _dirs, files in os.walk(root):
        for fn in files:
            rel = os.path.relpath(os.path.join(dirpath, fn), root)
            rel = rel.replace('\\', '/')
            stem = DERIV.sub('', os.path.splitext(rel)[0])
            have.add(stem)
    return have


def brief(s, at, span=1200):
    """The alt text or caption nearest a reference: that is the photo brief."""
    win = s[max(0, at - span): at + span]
    for pat in (r'alt="([^"]{6,})"',
                r'<figcaption[^>]*>(.*?)</figcaption>',
                r'<span class="cap">(.*?)</span>'):
        m = re.search(pat, win, re.S)
        if m:
            t = re.sub(r'<[^>]+>', ' ', m.group(1))
            t = re.sub(r'/images/\S+', '', t)
            return re.sub(r'\s+', ' ', t).strip()[:110]
    return ''


def scan():
    have = on_disk()
    pages = collections.OrderedDict()
    files = sorted(f for f in glob.glob(SITE + '/**/*.html', recursive=True)
                   if '/tools/' not in f.replace('\\', '/'))
    for f in files:
        rel = os.path.relpath(f, SITE).replace('\\', '/')
        s = io.open(f, encoding='utf-8', errors='replace').read()
        cut = s.find('</header>')          # skip the shared chrome
        s = s[cut:] if cut > 0 else s
        seen = set()
        for m in REF.finditer(s):
            stem = DERIV.sub('', m.group(1))
            if stem in have or stem in seen:
                continue
            seen.add(stem)
            pages.setdefault(rel, []).append((stem, brief(s, m.start())))
    return have, pages


def main():
    have, pages = scan()
    total = sum(len(v) for v in pages.values())
    if '--csv' in sys.argv:
        print('page,file,brief')
        for page, items in pages.items():
            for fn, b in items:
                print('%s,%s,"%s"' % (page, fn, b.replace('"', "'")))
        return
    print('photos on disk: %d    pages with gaps: %d    photos still needed: %d'
          % (len(have), len(pages), total))
    print()
    for page, items in pages.items():
        print('--- %s  (%d)' % (page.replace('/index.html', '') or '/', len(items)))
        for fn, b in items:
            print('    %-62s %s' % (fn, b))
        print()


if __name__ == '__main__':
    main()
