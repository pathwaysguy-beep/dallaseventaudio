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
 ('Event types', ['weddings','wedding-av-rental-dallas','corporate-events','private-events','live-music-and-band-events','college-school-university-events','rave-and-night-club-events','celebrity-and-luxury-events','sensory-friendly-event-services']),
 ('Sound', ['services-audio','rent-sound-equipment','rent-line-array-speaker-system','rent-bassboss-subwoofers','dj-speaker-rental','flat-panel-audio-dml500','feedback-free-microphone-rentals','equipment-list']),
 ('Lighting and effects', ['services-lighting','rent-uplighting','rent-dj-lighting','monogram-projector','rent-laser-light-show','rent-follow-spot-light','rent-fog-machine','rent-dancing-on-the-clouds-low-lyin','rent-cold-sparks','services-extra']),
 ('Video', ['projector-screen-rental','live-streaming-services','services-photo-and-video']),
 ('DJ', ['services-dj','rent-sound-equipment/cdj-rental-dallas']),
 ('The company', ['our-story','our-work','gallery','what-others-are-saying','contact']),
]
HOST = 'https://www.dallaseventaudio.com'
out = ['# Dallas Event Audio', '',
'> Full service event AV company in Dallas-Fort Worth, Texas, in business since 2001. Sound, wireless microphones, lighting, DJ services, projection, live streaming and effects, all delivered, set up, tuned and run by our own technicians. Based in ZIP 76053, serving venues within about 40 miles across Dallas, Fort Worth, Arlington, Plano, Frisco, Southlake, Irving and McKinney.', '',
'Every booking is full service: we own the equipment, deliver it, set it up, run it for the event and take it away. Every wireless microphone runs our AI-powered De-Feedback system. Every quote is written for the room and returned the same day. Phone and text: 817-210-7957. Quotes: ' + HOST + '/contact', '']
for name, slugs in GROUPS:
    out += [f'## {name}', '']
    for slug in slugs:
        t, d = meta(slug + '.html'); out.append(f'- [{t}]({HOST}/{slug}): {d}')
    out.append('')
out += ['## Blog', '']
for p in sorted(p for p in os.listdir('post') if p.endswith('.html')):
    t, d = meta('post/' + p); out.append(f'- [{t}]({HOST}/post/{p[:-5]}): {d}')
out += ['', '## Optional', '', f'- [Sitemap]({HOST}/sitemap.xml)', '']
open('llms.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('llms.txt written,', sum(1 for l in out if l.startswith('- [')), 'links')
