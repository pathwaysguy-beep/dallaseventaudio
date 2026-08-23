# -*- coding: utf-8 -*-
"""Bring every built page up to the current shared chrome.

Header, mobile drawer and the bottom-left palette dock are one design across 40
pages, but they were built over several weeks and had drifted into three header
vintages and two palette variants. Rather than rebuild every page from build
scripts of varying age, this replaces the chrome in place and appends the
canonical CSS as a final <style> so it wins the cascade against whatever nav CSS
the page already carried.

Idempotent: running it twice produces the same bytes. That is a hard
requirement, not a nicety, because it is the only thing that makes the script
safe to run before every commit.

Usage
-----
    python tools/sync_chrome.py            # sync every page under the repo root
    python tools/sync_chrome.py --check    # report drift, change nothing, exit 1

The fragments in tools/chrome/ ARE the source of truth for the shared chrome.
They were recovered from rent-uplighting/index.html on 23 Aug 2026 and verified
byte-identical to the versions in the build that produced the live site, so if
they are ever lost again they can be recovered the same way: every built page
carries the whole chrome verbatim between the chrome-sync markers.
"""
import io
import os
import re
import sys
import glob

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)          # tools/ lives inside the repo
SRC  = os.path.join(HERE, 'chrome')

HEADER  = io.open(SRC + '/header.html',       encoding='utf-8').read().rstrip()
DRAWER  = io.open(SRC + '/drawer.html',       encoding='utf-8').read().rstrip()
PALETTE = io.open(SRC + '/palette.html',      encoding='utf-8').read().rstrip()
CSS     = io.open(SRC + '/chrome.css',        encoding='utf-8').read().rstrip()
PALJS   = io.open(SRC + '/palette_js.html',   encoding='utf-8').read().rstrip()
NAVJS   = io.open(SRC + '/navdrawer_js.html', encoding='utf-8').read().rstrip()

MARK_CSS = '<!-- chrome-sync:css -->'
MARK_JS  = '<!-- chrome-sync:js -->'

STYLE_BLOCK = MARK_CSS + '\n<style>\n' + CSS + '\n</style>\n'
JS_BLOCK    = MARK_JS + '\n' + PALJS + '\n' + NAVJS + '\n'

# Selectors that are the page's own stale copy of the shared chrome.
CHROME_SEL = re.compile(
    r'(^|[\s,>])(header\b|nav\b|\.logo\b|\.navlinks\b|\.nl-[a-z]|\.navright\b|\.phone\b'
    r'|\.cta-btn\b|\.navburger\b|\.ndrawer\b|\.nd-[a-z]|body\.nav-locked\b|#paletteBar\b'
    r'|\.pal-[a-z]|\.sw-[a-z]|#palOpts\b)')

# A selector that opens with a body class other than .nav-locked is a deliberate
# per-page override of the chrome, not a stale duplicate of it.
PAGE_SCOPED = re.compile(r'^\s*body\.(?!nav-locked\b)[a-z-]+')


def is_chrome(sel):
    """True when a rule is a page's own copy of the shared chrome.

    /sensory-friendly-event-services is the first page to need the exemption:
    every rule on it is scoped under body.calm, including the one that hides
    #paletteBar, because that page collapses all three palettes into a single
    AA-verified set and a switcher that changes nothing is worse than none.
    Without this, the whole selector list would be dropped, taking the
    #chatBubble, .grain-overlay and .marquee rules down with it.
    """
    if PAGE_SCOPED.match(sel):
        return False
    return bool(CHROME_SEL.search(sel))


def match_element(s, start, tag):
    """Index just past the element opening at `start`, honouring nesting."""
    depth = 0
    for m in re.compile(r'<%s\b|</%s>' % (tag, tag)).finditer(s, start):
        if m.group(0).startswith('</'):
            depth -= 1
            if depth == 0:
                return m.end()
        else:
            depth += 1
    return -1


def drop_element(s, opener_re, tag):
    n = 0
    while True:
        m = re.search(opener_re, s)
        if not m:
            return s, n
        end = match_element(s, m.start(), tag)
        assert end > 0, 'unbalanced <%s> near offset %d' % (tag, m.start())
        s = s[:m.start()] + s[end:]
        n += 1


def drop_scripts(s, needles):
    out, i, dropped = [], 0, 0
    for m in re.finditer(r'<script\b[^>]*>.*?</script>', s, re.S):
        if any(x in m.group(0) for x in needles):
            out.append(s[i:m.start()])
            i = m.end()
            dropped += 1
    out.append(s[i:])
    return ''.join(out), dropped


def split_rules(css):
    """Split a stylesheet into (selector, full_text) pairs, honouring nesting."""
    out, i, n = [], 0, len(css)
    ws = re.compile(r'\s*(/\*.*?\*/\s*)*', re.S)
    while i < n:
        i = ws.match(css, i).end()
        if i >= n:
            break
        j = css.find('{', i)
        if j < 0:
            break
        sel = css[i:j].strip()
        d, k = 0, j
        while k < n:
            if css[k] == '{':
                d += 1
            elif css[k] == '}':
                d -= 1
                if d == 0:
                    break
            k += 1
        out.append((sel, css[i:k + 1]))
        i = k + 1
    return out


def strip_chrome_css(s, dropped):
    """Remove the page's own header/nav/palette rules so the canonical set is the
    only definition, rather than a later rule that has to out-specify a stale
    one. A stale top-strip #paletteBar rule sets top/left/right, which the
    bottom-dock rule never resets, and the two together once produced a full
    viewport overlay that swallowed every tap on the site.
    """
    def fix_block(m):
        css = m.group(2)
        rules = split_rules(css)
        # Reassembling from split_rules() loses comments and indentation, so only
        # touch blocks that actually contain stale chrome. Blocks with nothing to
        # drop come back byte-identical, which is what keeps hand-written CSS
        # comments on the page.
        hit = any(
            is_chrome(sel) or (
                sel.startswith('@media')
                and any(is_chrome(s2) for s2, _ in
                        split_rules(txt[txt.find('{') + 1: txt.rfind('}')])))
            for sel, txt in rules)
        if not hit:
            return m.group(0)
        keep = []
        for sel, txt in rules:
            if sel.startswith('@media'):
                inner = txt[txt.find('{') + 1: txt.rfind('}')]
                sub = [t for s2, t in split_rules(inner) if not is_chrome(s2)]
                dropped.extend(s2 for s2, _ in split_rules(inner) if is_chrome(s2))
                if sub:
                    keep.append(sel + '{\n' + '\n'.join(sub) + '\n}')
            elif is_chrome(sel):
                dropped.append(sel)
            else:
                keep.append(txt)
        return m.group(1) + '\n' + '\n'.join(keep) + '\n' + m.group(3)

    return re.sub(r'(<style[^>]*>)(.*?)(</style>)', fix_block, s, flags=re.S)


def body_open(s, path):
    """Locate the real <body ...>, which is always after </head>.

    Searching the whole document finds the first literal '<body>' instead, and
    on /sensory-friendly-event-services that is a line of CSS commentary
    explaining which class the overrides hang off. Injecting the header into a
    comment inside a <style> block leaves a page that greps clean and renders no
    navigation at all.
    """
    h = s.find('</head>')
    assert h > 0, 'no </head> in ' + path
    m = re.search(r'<body[^>]*>', s[h:])
    assert m, 'no <body ...> after </head> in ' + path
    return h + m.start(), h + m.end()


def sync(path, write=True):
    s0 = io.open(path, encoding='utf-8').read()
    s = s0
    rep = {'css_rules_dropped': []}

    # --- 1. strip whatever chrome is already there ------------------------
    s, rep['old_palette'] = drop_element(s, r'<div id="paletteBar"', 'div')
    s, rep['old_drawer']  = drop_element(s, r'<div class="ndrawer"', 'div')
    s, rep['old_header']  = drop_element(s, r'<header\b', 'header')
    s, rep['old_js']      = drop_scripts(
        s, ['navBurger', 'paletteBar', "getElementById('palToggle')"])
    # previously injected blocks, so a re-run replaces rather than stacks
    s = re.sub(re.escape(MARK_CSS) + r'\s*<style>.*?</style>\s*', '', s, flags=re.S)
    s = s.replace(MARK_JS, '')
    s = strip_chrome_css(s, rep['css_rules_dropped'])
    # removals leave orphaned blank lines; collapse so re-running converges
    s = re.sub(r'\n[ \t]*\n([ \t]*\n)+', '\n\n', s)
    _, at = body_open(s, path)
    s = s[:at] + re.sub(r'^[ \t\n]*', '', s[at:], count=1)
    s = re.sub(r'[ \t\n]*</body>', '\n</body>', s, count=1)

    # --- 2. insert the canonical chrome -----------------------------------
    assert '</head>' in s and '</body>' in s, path
    s = s.replace('</head>', STYLE_BLOCK + '</head>', 1)
    _, at = body_open(s, path)
    s = s[:at] + '\n\n  ' + PALETTE + '\n\n  ' + HEADER + '\n\n  ' + DRAWER + '\n' + s[at:]
    s = s.replace('</body>', JS_BLOCK + '</body>', 1)

    # --- 3. sanity --------------------------------------------------------
    for tok, want in [('id="navBurger"', 1), ('id="navDrawer"', 1),
                      ('id="paletteBar"', 1), ('<header>', 1), ('</header>', 1),
                      ('class="pal-toggle"', 1), (MARK_CSS, 1), (MARK_JS, 1)]:
        got = s.count(tok)
        assert got == want, '%s: %s appears %d times, expected %d' % (
            path, tok, got, want)
    for tag in ('div', 'header', 'nav', 'button', 'section', 'a'):
        o = len(re.findall(r'<%s\b' % tag, s))
        c = len(re.findall(r'</%s>' % tag, s))
        assert o == c, '%s: <%s> %d open vs %d close' % (path, tag, o, c)

    changed = s != s0
    if changed and write:
        io.open(path, 'w', encoding='utf-8').write(s)
    return changed, rep


def main():
    check = '--check' in sys.argv
    files = sorted(f for f in glob.glob(SITE + '/**/*.html', recursive=True)
                   if '/tools/' not in f.replace('\\', '/'))
    n = 0
    for f in files:
        ch, rep = sync(f, write=not check)
        n += ch
        print('%-6s %-58s palette-%d drawer-%d header-%d js-%d css-%d' % (
            'DRIFT' if (ch and check) else ('EDIT' if ch else 'same'),
            os.path.relpath(f, SITE), rep['old_palette'], rep['old_drawer'],
            rep['old_header'], rep['old_js'], len(rep['css_rules_dropped'])))
    print('\n%d of %d files %s' % (n, len(files), 'drifted' if check else 'changed'))
    if check and n:
        sys.exit(1)


if __name__ == '__main__':
    main()
