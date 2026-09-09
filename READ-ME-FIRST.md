# Read me first: where the rebuild stands, and how to pick it up cold

Written 7 September 2026 so that any new session, on any machine, can resume
without the chat that got us here. Everything that matters lives in one of
three places: this repo, the nine `dea-*` skills saved in Steve's Claude
account, and the Cloudflare account. Nothing important lives only in a chat.

## The shape of the project

dallaseventaudio.com is moving off Wix onto Cloudflare Pages, page by page,
as static HTML in this repo. 40 top-level pages plus 38 posts under `post/`.
Every live URL survives byte for byte because Google Ads campaigns point at
them; no slug with impressions, clicks or an Ads final URL ever changes.

The preview is https://dallaseventaudio.pages.dev, deployed from `main` on
every push. It is kept out of Google by the staging block in `_headers` and
the `Disallow: /` in `robots.txt`, both of which come out in the same commit
as the DNS switch. The live site is still Wix until that day.

## How work gets delivered

Claude works in a cloud sandbox and cannot push. Every change ships as a
numbered zip (`dea-bundleNN.zip`) holding an `apply.sh` and a `payload/`.
Steve unzips it in `~/Downloads` on the Mac, runs `bash bundleNN/apply.sh`,
then `cd ~/dallaseventaudio && git push`. The script checks the repo is at
the commit the bundle was built against, copies the payload in, and commits
with a message that explains the change. The full protocol, including the
mistakes it exists to prevent, is the `dea-ship` skill.

Before building anything, fetch origin and diff against it: Steve may not
have applied the last bundle yet, and a bundle must never stack on an
unapplied one. If two are outstanding, the newer one is cumulative and the
older one is declared dead in the message.

## The gates every change passes

- `python3 tools/sync_chrome.py --check` must print `0 of 79 files drifted`.
  The header, nav drawer, palette dock, fonts, analytics, widget and shared
  CSS are fragments in `tools/chrome/` and this script stamps them into every
  page. Page-local scripts go above the `<!-- chrome-sync:js -->` marker.
- Copy: `dea_copy_check.py` (the eight defects, bold in prose, British
  spellings, pricing tokens) and `dea_seo_diff.py before.html after.html`
  (keyword counts within 15%, headings, links, JSON-LD, title 25 to 62,
  description 110 to 165). Both are assets of the `dea-copy-standards`
  skill. The baseline is always `git show HEAD:<file>`, never Wix.
- Headless QA at 1440, 1024 and 390: no horizontal overflow, no script
  errors, every JSON-LD block parsing. Template in `dea-page-rebuild`.
- "Site-wide" means `*.html` and `post/*.html` both. Two false claims came
  from scoping to the top level only.

## Standing rules that are easy to break

Never state or imply pricing (the cost post and the speakers post are the
two exceptions). No photo booths, and never link `/rent-photobooth`. Floor
monograms are never marketed. Three lanes: `/rent-laser-light-show` is
lasers only, `/monogram-projector` is gobos and monograms only,
`/projector-screen-rental` is video projectors and screens only. The line
array is BassBoss DV12, two by two on a heavy duty tripod stand to 13 feet,
never flown; DAS Aero 12 and LX218CA are gone. DEA always transports both
ways and always sets up; the only variable is whether the technician stays.
Zero em or en dashes in copy. Texas English. Keep it positive. Photo rights
are confirmed per event, not per photo. Steve does not want multiple-choice
questions: state the call and proceed.

## Images

An empty image slot is an element with no inline style and a hidden
`<span class="slot">/images/path.jpg</span>` naming what it is waiting for.
A filled slot carries `style="--img:image-set(...)"` with the AVIF, WebP and
JPEG at 1920 wide and the span removed. `slots.py` in `dea-image-pipeline`
lists what is still empty (33 across 17 pages as of bundle 15). Photos are
cropped 4:3 and encoded by `derive.py` in the same skill. Video is an mp4
and webm pair with a poster, lazy-attached from `data-mp4` and `data-webm`.
The full-resolution photo library is on Steve's Windows Dell, offline until
repaired; everything else arrives through chat.

## The concierge

The chat widget on every page posts to the `dea-concierge` Cloudflare
Worker, whose source is in `dea-concierge/` here. The system prompt is
`dea-concierge/src/prompt.js` and nowhere else. Edit it, commit, then
`cd dea-concierge && npx wrangler deploy` (Steve is logged in to Wrangler on
the Mac). Leads are emailed through Resend to pathwaysguy@gmail.com and
stored in the D1 database `dea-leads`. The widget's local greeting in
`tools/chrome/widget_js.html` must stay identical to the prompt's greeting.
`tools/scan_site.py` rebuilds the page digest the prompt is generated from.

## Where things stand on 9 September 2026

Done: all 78 pages rebuilt and gated; blog copy pass; concierge v3 prompt
deployed and answering from page prose; SEO review against Google's 2026
updates (`SEO-REVIEW-2026-09-07.md` at the repo root; its fixes are in
the repo).

Posts, settled 9 September: Steve's rule is that a post with zero clicks in
the last three months of Search Console is worth no work on the new site, so
the 25 silent posts stay exactly as they are (slugs and all) and the 13 that
earn clicks got the story pass, their photos and their links (bundles 44,
47, 48). Re-pull the three-month click list before touching any post again.
Open, needing Steve: confirming the review count on the homepage. Settled 9 September: DEA is a
service-area business with no street address, so the city-level schema stands
(and now names Tarrant, Dallas, Denton and Collin counties plus Dallas and
Fort Worth in `areaServed`); AI crawlers are allowed at go-live, and the
ready robots file is `tools/robots.go-live.txt`, to be copied over
`/robots.txt` in the cutover commit. Done
since: the byline (Steve), the story pass on every top-level page, the
negative scan (dea-negative-scan, headings clean site-wide), the concierge
prompt v4, and `/llms.txt` (rebuilt by `tools/build_llms.py` after any title
or description change; every URL in it is the www host). Done 9 September as well: the CDJ page opens with a six-card lineup
(CDJ-3000 pair, DJM-900NXS2, DJM-A9, XDJ-AZ, XDJ-RX3, DDJ-FLX6), every card
on Steve's own photo; the gallery carries the recent photos and clips (47
tiles). The SQ-5 slot is filled (warehouse bench shot, swap for a show photo when
one exists). The mic and speaker slot on the microphone page is filled from a still of
Steve's wedding speech clip (DV12, Shure Beta 58, De-Feedback), so every
image slot on the site is filled; the `.slot{display:none}` rule in the
shared chrome CSS can go whenever the chrome is next touched. Open, at
cutover: the staging blocks, `#paletteBar`, sitemap submission, two weeks
watching Search Console. Cutover mechanics, in order: move the nameservers
to Cloudflare before touching any record at Wix; add both
`www.dallaseventaudio.com` and the apex as Pages custom domains, with a
Cloudflare redirect rule sending apex to www that keeps path and query;
SSL mode Full (strict); leave HSTS off or at a short max-age for the first
week, and no preload until every subdomain is confirmed on HTTPS; then test
a handful of old Wix URLs over http and non-www with `curl -I` and confirm
each lands on its final page in one hop. Redirect rules keep query strings
(gclid tested on the preview) and now have trailing-slash twins. The Worker
already allows the www and apex origins and rate-limits by IP.

## The story pass (standing queue, started 8 September 2026)

The copy gates are clean site-wide. What keeps a reader on a page is
different: a scene from a real night instead of a definition, at least one
job Steve actually ran, and every paragraph saying what happens on the day
rather than what the service "provides." The pass goes page by page, in
traffic order, and each page ships as its own small bundle so Steve can
judge the voice before the next one. Corporate-events was the first. Steve
supplies the examples (a line or two per page is enough: the venue type, what
went wrong or right, what the client noticed); Claude writes them in and the
SEO gate holds the keywords. Never invent a job, a venue or a client. Keep
client names out unless Steve says otherwise. Every top-level page, our-story and the 13
click-earning posts are done. Posts carry their photos in a `.post-fig`
figure (responsive picture, lazy) and the De-Feedback post carries the
ceremony clip with sound in a `.post-demo` block; reuse both when a post
gets a photo. Floor monograms are never marketed and photo booths are never
offered, so read for those when an older post is touched.

## If you are a new session

Clone this repo, load the `dea-*` skills, read this file and `dea-ship`,
fetch origin, and ask Steve for nothing until you have read the last three
commit messages. They are written to be read.
