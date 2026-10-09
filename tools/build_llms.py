#!/usr/bin/env python3
"""Rebuild /llms.txt from the pages' own titles and meta descriptions.
Run from the repo root after any title or description change:  python3 tools/build_llms.py
Every URL is the production host. The David's Bridal flyer page, thank-you and 404 are left out on purpose."""
import re, html as H, os
def meta(f):
    s = open(f, encoding='utf-8').read()
    m = re.search(r'<meta name="description" content="([^"]*)"', s); t = re.search(r'<title>([^<]*)</title>', s)
    return H.unescape(t.group(1)).replace(' | Dallas Event Audio', '').strip(), H.unescape(m.group(1)).strip()
GROUPS = [
 ('Event types', ['fort-worth','weddings','wedding-av-rental-dallas','corporate-events','private-events','live-music-and-band-events','college-school-university-events','rave-and-night-club-events','celebrity-and-luxury-events','sensory-friendly-event-services']),
 ('Sound', ['services-audio','rent-sound-equipment','rent-line-array-speaker-system','rent-bassboss-subwoofers','dj-speaker-rental','flat-panel-audio-dml500','feedback-free-microphone-rentals','equipment-list']),
 ('Lighting and effects', ['services-lighting','rent-uplighting','rent-dj-lighting','monogram-projector','rent-laser-light-show','rent-follow-spot-light','rent-fog-machine','rent-dancing-on-the-clouds-low-lyin','services-extra']),
 ('Video', ['projector-screen-rental','tv-rental-dallas','live-streaming-services','services-photo-and-video']),
 ('DJ', ['services-dj','rent-sound-equipment/cdj-rental-dallas']),
 ('The company', ['our-story','our-work','gallery','what-others-are-saying','contact','privacy']),
]
HOST = 'https://www.dallaseventaudio.com'
out = ['# Dallas Event Audio', '',
'> Full service event AV company in Dallas-Fort Worth, Texas, in business since 2001. Sound, wireless microphones, lighting, DJ services, projection, live streaming and effects, delivered, set up, tested and picked up by our own crew, with an on-site technician for the services that call for one. Based in the Mid-Cities (ZIP 76053), serving venues within about 40 miles across Dallas, Fort Worth, Arlington, Plano, Frisco, Southlake, Irving and McKinney.', '',
'Key facts:', '',
'- Business: Dallas Event Audio, event AV rental, DJ services and production, since 2001',
'- Home base: Mid-Cities, Dallas-Fort Worth, ZIP 76053',
'- Service area: about 40 miles, including Dallas, Fort Worth, Arlington, Plano, Frisco, Southlake, Irving and McKinney',
'- Phone and text: 817-210-7957',
'- Quotes: ' + HOST + '/contact, written for the room and returned within 24 hours',
'- How bookings work: white glove and turnkey. Our crew delivers, sets up, tests and picks up every booking. A technician stays on site for DJ, live sound, corporate, live streaming and operated effects, and on request for other rentals',
'- Microphones: every wireless microphone runs our AI-powered De-Feedback system',
'- Insurance: fully insured, with certificates sent to the venue', '']
for name, slugs in GROUPS:
    out += [f'## {name}', '']
    for slug in slugs:
        t, d = meta(slug + '.html'); out.append(f'- [{t}]({HOST}/{slug}): {d}')
    out.append('')
out += ['## Blog', '']
for p in sorted(p for p in os.listdir('post') if p.endswith('.html')):
    t, d = meta('post/' + p); out.append(f'- [{t}]({HOST}/post/{p[:-5]}): {d}')
out += ['', '## Optional', '', f'- [Full text of every page]({HOST}/llms-full.txt): the complete wording of each page and post above, in one file', f'- [Sitemap]({HOST}/sitemap.xml)', '']
open('llms.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('llms.txt written,', sum(1 for l in out if l.startswith('- [')), 'links')

# llms-full.txt: the same pages, full text, generated from the pages themselves so it
# can never say something a page does not.
import html as _h
def _text(f):
    s = open(f, encoding='utf-8').read()
    m = re.search(r'<main[^>]*>(.*?)</main>', s, re.S)
    b = m.group(1) if m else s
    b = re.sub(r'<(script|style|svg|noscript)[^>]*>.*?</\\1>', ' ', b, flags=re.S)
    b = re.sub(r'<h1[^>]*>(.*?)</h1>', lambda x: '\n\n# ' + re.sub('<[^>]+>', '', x.group(1)) + '\n\n', b, flags=re.S)
    b = re.sub(r'<h2[^>]*>(.*?)</h2>', lambda x: '\n\n## ' + re.sub('<[^>]+>', '', x.group(1)) + '\n\n', b, flags=re.S)
    b = re.sub(r'<h3[^>]*>(.*?)</h3>', lambda x: '\n\n### ' + re.sub('<[^>]+>', '', x.group(1)) + '\n\n', b, flags=re.S)
    b = re.sub(r'</(p|li|div|summary|figcaption|tr)>', '\n', b)
    b = _h.unescape(re.sub(r'<[^>]+>', ' ', b))
    lines = [re.sub(r'[ \t]+', ' ', l).strip() for l in b.split('\n')]
    outl, prev = [], ''
    for l in lines:
        if not l or l == prev: continue
        outl.append(l); prev = l
    return '\n'.join(outl)
full = ['# Dallas Event Audio: full text', '', out[2], '', 'Every page and post on ' + HOST + ', in full. The short index is ' + HOST + '/llms.txt.', '']
pages = [('', 'index.html')] + [(slug, slug + '.html') for _, slugs in GROUPS for slug in slugs]
pages += [('post/' + p[:-5], 'post/' + p) for p in sorted(os.listdir('post')) if p.endswith('.html')]
for slug, f in pages:
    t, d = meta(f)
    full += ['---', '', f'Page: {t}', f'URL: {HOST}/{slug}'.rstrip('/'), f'Summary: {d}', '', _text(f), '']
open('llms-full.txt', 'w', encoding='utf-8').write('\n'.join(full))
print('llms-full.txt written,', len(pages), 'pages,', sum(len(x) for x in full) // 1024, 'KiB')
