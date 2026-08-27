# -*- coding: utf-8 -*-
"""Serve the WebP and AVIF that were already encoded, at the width the page
actually paints.

The repository has carried 284 WebP and 284 AVIF files at four widths since the
image pipeline ran, and nothing referenced any of them: every page served the
full size JPEG. This wires them up.

Two mechanisms, because the site uses images two ways.

An <img> becomes a <picture> with an AVIF source, a WebP source and the original
as the fallback <img>, which keeps the existing src, alt, width, height and
loading attributes exactly as they were. A browser that understands neither new
format still gets the file it got before.

A CSS background becomes image-set(), which is the same idea for the cases where
there is no element to wrap.

The sizes attribute is measured rather than guessed. tools/imgsizes.json records
how wide each image is actually painted on each page at 1440 and at 390, taken
from a real render, so the browser is told the truth and picks the smallest
candidate that covers it.

Idempotent, like sync_chrome.py: an <img> already inside a <picture> is left
alone, and a background already using image-set() is left alone.

Usage
-----
    python tools/optimize_images.py            # rewrite every page
    python tools/optimize_images.py --check    # report, change nothing, exit 1
"""
import io
import json
import os
import re
import sys
import glob

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
WIDTHS = (480, 768, 1200, 1920)
SIZES = json.load(io.open(os.path.join(HERE, 'imgsizes.json'), encoding='utf-8'))

IMG = re.compile(r'<img\b[^>]*?src="(/images/[^"]+)"[^>]*>')
CSSURL = re.compile(r"url\('(/images/[^']+)'\)")


def derivatives(src):
    """Widths that exist on disk for this image, per format."""
    stem, _ = os.path.splitext(src.lstrip('/'))
    out = {}
    for fmt in ('avif', 'webp'):
        have = [w for w in WIDTHS
                if os.path.exists(os.path.join(SITE, '%s-%dw.%s' % (stem, w, fmt)))]
        if have:
            out[fmt] = have
    return out


def srcset(src, widths, fmt):
    stem, _ = os.path.splitext(src)
    return ', '.join('%s-%dw.%s %dw' % (stem, w, fmt, w) for w in widths)


def sizes_attr(page, src):
    """From the measured render. Falls back to a full width hint, which is the
    safe direction to be wrong in: it over-fetches rather than under-fetching."""
    m = (SIZES.get(page) or {}).get(src) or {}
    d, mob = m.get('d'), m.get('m')
    if d and mob:
        return '(max-width: 640px) %dpx, %dpx' % (mob, d)
    if d:
        return '%dpx' % d
    return '100vw'


def rewrite_imgs(s, page, report):
    out, i = [], 0
    for m in IMG.finditer(s):
        # already wrapped by a previous run
        if s.rfind('<picture>', 0, m.start()) > s.rfind('</picture>', 0, m.start()):
            continue
        src = m.group(1)
        d = derivatives(src)
        if not d:
            continue
        sz = sizes_attr(page, src)
        src_tags = ''.join(
            '<source type="image/%s" srcset="%s" sizes="%s">' % (fmt, srcset(src, d[fmt], fmt), sz)
            for fmt in ('avif', 'webp') if fmt in d)
        tag = m.group(0)
        if ' loading=' not in tag and ' data-hero' not in tag:
            tag = tag[:-1].rstrip() + ' loading="lazy" decoding="async">'
        out.append(s[i:m.start()])
        out.append('<picture>' + src_tags + tag + '</picture>')
        i = m.end()
        report['img'] += 1
    out.append(s[i:])
    return ''.join(out)


def rewrite_css(s, report):
    def one(m):
        src = m.group(1)
        d = derivatives(src)
        if not d:
            return m.group(0)
        # the widest derivative, because a background has no sizes negotiation
        parts = []
        for fmt in ('avif', 'webp'):
            if fmt in d:
                stem, _ = os.path.splitext(src)
                parts.append("url('%s-%dw.%s') type('image/%s')"
                             % (stem, max(d[fmt]), fmt, fmt))
        parts.append("url('%s')" % src)
        report['css'] += 1
        return 'image-set(' + ', '.join(parts) + ')'

    # Anything already inside an image-set() from a previous run is left alone.
    # The first version of this guarded with a fixed lookbehind window, which the
    # original url sitting at the tail of a long image-set slipped straight past,
    # and a second run nested the whole thing inside itself. Spans, not windows.
    spans = []
    for m in re.finditer(r'image-set\(', s):
        d, j = 0, m.end() - 1
        while j < len(s):
            if s[j] == '(':
                d += 1
            elif s[j] == ')':
                d -= 1
                if d == 0:
                    break
            j += 1
        spans.append((m.start(), j))

    def guarded(m):
        if any(a <= m.start() < b for a, b in spans):
            return m.group(0)
        return one(m)

    return re.sub(r"url\('(/images/[^']+)'\)", guarded, s)


def process(path, write=True):
    rel = os.path.relpath(path, SITE).replace('\\', '/')
    s0 = io.open(path, encoding='utf-8').read()
    report = {'img': 0, 'css': 0}
    s = rewrite_imgs(s0, rel, report)
    s = rewrite_css(s, report)
    changed = s != s0
    if changed and write:
        io.open(path, 'w', encoding='utf-8').write(s)
    return changed, report


def main():
    check = '--check' in sys.argv
    files = sorted(f for f in glob.glob(SITE + '/**/*.html', recursive=True)
                   if '/tools/' not in f.replace('\\', '/'))
    n = ti = tc = 0
    for f in files:
        ch, rep = process(f, write=not check)
        n += ch
        ti += rep['img']
        tc += rep['css']
        if rep['img'] or rep['css']:
            print('%-6s %-54s picture-%d image-set-%d' % (
                'DRIFT' if (ch and check) else ('EDIT' if ch else 'same'),
                os.path.relpath(f, SITE), rep['img'], rep['css']))
    print('\n%d of %d files %s, %d picture elements, %d backgrounds'
          % (n, len(files), 'drifted' if check else 'changed', ti, tc))
    if check and n:
        sys.exit(1)


if __name__ == '__main__':
    main()
