# -*- coding: utf-8 -*-
"""Flatten every slug/index.html to slug.html, so Cloudflare Pages serves the
URL the site actually declares.

Why this exists. Pages resolves a request in a fixed order: an exact file, then
the path with .html appended, then path/index.html. Only the last of those
carries a redirect: ask for /rent-uplighting when the file is
rent-uplighting/index.html and Pages answers 308 to /rent-uplighting/. Measured
on the preview: 78 of 80 URLs redirected. The two that did not were / and /404,
and /404 is served clean for exactly one reason, that 404.html sits flat at the
repo root. That is the control that says this fix works.

Nothing about the pages themselves changes. Canonicals, og:url, sitemap.xml,
internal links and the _redirects destinations are all already written without
the trailing slash, which is to say they were right all along and the file
layout was wrong. Moving the files is the whole change.

Byte-for-byte: every file is moved, never rewritten. The only edited files are
_pages.json, which records where each page lives, and sync_chrome.py, whose
standalone-page exemption names a path.
"""
import io
import json
import os
import shutil
import subprocess
import sys

SITE = sys.argv[1] if len(sys.argv) > 1 else '.'
GIT = '--git' in sys.argv


def run(*a):
    subprocess.check_call(a, cwd=SITE)


def main():
    moves = []
    for root, dirs, files in os.walk(SITE):
        if 'tools' in root.replace('\\', '/').split('/') or '.git' in root:
            continue
        if 'index.html' not in files:
            continue
        rel = os.path.relpath(root, SITE).replace('\\', '/')
        if rel == '.':
            continue                      # the homepage stays index.html
        moves.append((rel + '/index.html', rel + '.html'))

    moves.sort()
    for src, dst in moves:
        assert not os.path.exists(os.path.join(SITE, dst)), 'would clobber ' + dst
    for src, dst in moves:
        if GIT:
            run('git', 'mv', src, dst)
        else:
            shutil.move(os.path.join(SITE, src), os.path.join(SITE, dst))
        print('  %-62s -> %s' % (src, dst))

    # Directories are empty now unless they held a nested page. post/ keeps its
    # 38 files, rent-sound-equipment/ keeps cdj-rental-dallas.html.
    removed = 0
    for root, dirs, files in os.walk(SITE, topdown=False):
        if '.git' in root:
            continue
        try:
            if root != SITE and not os.listdir(root):
                os.rmdir(root)
                removed += 1
        except OSError:
            pass

    # _pages.json records file locations, so it has to follow.
    pj = os.path.join(SITE, '_pages.json')
    if os.path.exists(pj):
        pages = json.load(io.open(pj, encoding='utf-8'))
        n = 0
        for p in pages:
            f = p.get('file', '')
            if f.endswith('/index.html'):
                p['file'] = f[:-len('/index.html')] + '.html'
                n += 1
        io.open(pj, 'w', encoding='utf-8').write(
            json.dumps(pages, indent=1, ensure_ascii=False) + '\n')
        print('\n_pages.json: %d paths rewritten' % n)

    # sync_chrome.py names the standalone page by path.
    sc = os.path.join(SITE, 'tools', 'sync_chrome.py')
    s = io.open(sc, encoding='utf-8').read()
    old = "'davidsbridalfrisco/index.html',   # printed on David's Bridal Frisco flyers"
    new = "'davidsbridalfrisco.html',         # printed on David's Bridal Frisco flyers"
    assert s.count(old) == 1, 'standalone exemption not found in sync_chrome.py'
    io.open(sc, 'w', encoding='utf-8').write(s.replace(old, new, 1))

    print('\n%d pages flattened, %d empty directories removed' % (len(moves), removed))


if __name__ == '__main__':
    main()
