# Read me first: where the rebuild stands, and how to pick it up cold

Written 7 September 2026 and brought up to date on 12 October 2026 (bundle 81)
so that any new session, on any machine, can resume without the chat that got
us here. Everything that matters lives in one of
three places: this repo, the `dea-*` skills saved in Steve's Claude account
(eleven of them as of 12 October), and the Cloudflare account. The private
side (leads, analytics figures, the open to-do list) lives in the "Dallas Event
Audio" project in Steve's Claude account, in its DEA status file, because this
repo is public. Nothing important lives only in a chat.

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
Steve unzips it in `~/Downloads` on the MacBook, runs `bash bundleNN/apply.sh`,
then `cd ~/dallaseventaudio && git push`. He also works from a Windows desktop
in PowerShell, where the bundle's `files/` folder is copied in with robocopy
and committed by hand (`npm.cmd` and `npx.cmd` there, never the bare names).
Ask which computer he is on before sending any commands. The script checks the repo is at
the commit the bundle was built against, copies the payload in, and commits
with a message that explains the change. The full protocol, including the
mistakes it exists to prevent, is the `dea-ship` skill.

Before building anything, fetch origin and diff against it: Steve may not
have applied the last bundle yet, and a bundle must never stack on an
unapplied one. If two are outstanding, the newer one is cumulative and the
older one is declared dead in the message.

## The gates every change passes

- `python3 tools/sync_chrome.py --check` must print `0 of N files drifted`
  (85 as of 24 October 2026).
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

Done 13 September (bundle 51): a fourth video lane, `/tv-rental-dallas`
(32, 43 and 65 inch TVs on rolling stands, confidence monitors, TV versus
projector screen, corporate and trade show, weddings and covered outdoor
events). It was built on the projector page shell and lives in the Video
group of `tools/build_llms.py`, `sitemap.xml` and `_pages.json`. Keyword
Planner for the DFW DMA puts every TV rental term at 10 searches a month
(`/tmp` notes are gone; the numbers are in the bundle message), so the page
is a long-tail catch, not a head term. The header changed with it: Events,
Audio, DJ Services (a plain link to `/services-dj`), Lighting & FX (now
ending with Special Effects & Extras), Video (Projector & Screen, TV Rental,
Live Streaming, Photo & Video), Our Work (now carrying Equipment List) and
Contact. The phone number hides below 1080px so the header holds at 1024.
The DJ page now runs intro, event types (nine cards, with 5K Runs & Charity
Events added on Steve's brief: charity hosted, outdoor capable PA with the DJ
rig and the DJ, generator or battery bank when there is no power), what is
included, and only then the comparison sections. Every footer used to carry
a leftover draft label next to the copyright ("Blog post draft, wedding fog
effects" on 39 pages); it now reads "Serving Dallas-Fort Worth since 2001."
and every footer links the TV page. The two "Hurst" stat rows are gone.
Delta press event photos (TV on a stand, step and repeat) are on hold until
Steve clears the client branding; the page can take one in the corporate
split whenever he does.

Done 13 September (bundle 52): the response promise changed site-wide from
"a straightforward quote the same day" to "you'll hear back from us today,
with a straightforward quote within 24 hours" (Steve is behind a booth some
nights; the contact FAQ says a show-day reply may come late). The same
wording goes into the HoneyBook auto-reply and email templates, which are
Steve's to edit. The home page carries an owner note (Steve's three
sentences, no headshot by his choice) beside a "Rooms we know" venue list;
weddings, corporate events and private events carry longer venue lists for
their kind of room, and `/fort-worth` (under Events in the header) carries
the Tarrant County list. Every venue name came from HoneyBook: past projects
marked Busy with a location on record (935 of them), venues only, never a
client company, lists kept in `/tmp/dea/p44/venues.py` at build time and
now only in the pages. Add a venue only after a booked job there.
`/fort-worth` exists because Search Console shows 43 Fort Worth queries at
an average position of 12 with three clicks in a year; it is one page that
links down into the lanes, never a Fort Worth copy of a lane page. The
podium photo on it is the gallery's Fort Worth award ceremony shot, which
carries a client's step-and-repeat; Steve has seen it in the gallery.
Bundle 53 put the in-body links to `/fort-worth` in: the Fort Worth chip in
every service-area chip row, the footer brand line and Events column on
every page, and one sentence each on the home, DJ, weddings, projector, TV,
uplighting and our-story pages, so the page has contextual links and not
only the menu. The DJ page got its own venue list (wedding venues, hotels,
clubs and restaurants we have DJ'd in) from the same HoneyBook pull.
Bundle 54 added the last two lists, on the college page (schools, campuses
and athletic venues, from projects typed School Event and Sporting Event)
and the live music page (theaters, bars, breweries and ballrooms from
projects typed Concert/Music). That is the full set: home, weddings,
corporate, private events, DJ, Fort Worth, college, live music. Rental
pages, wedding AV rental, rave and the posts stay without one on purpose;
repeating the block further would read as boilerplate.
Bundle 55 linked `/tv-rental-dallas` from the body of the pages that already
mentioned TVs (corporate events, equipment list, wedding AV rental, photo
and video, our story, projector page), the same fix the Fort Worth page got
in bundle 53. Any new page needs its in-body links in the same bundle it
ships in; the menu alone is not enough.
Bundle 56 (14 September) added the Meta pixel (338389045071642) to the shared
analytics fragment under the same production hostname guard as GA4: stub
`window.fbq` everywhere, loader after the load event on production only,
PageView on every page, Lead on /thank-you beside form_submit_thankyou,
ordered after init. No noscript image, because an image cannot respect the
guard. The Wix site keeps its own pixel until cutover so the audience keeps
building; both sites carry the same pixel ID, so nothing changes in Meta at
cutover. Bundle 55 also repaired the our-story
FAQPage schema, which bundle 53 broke by putting the Fort Worth anchor tag
inside a JSON answer: sentence replacements must never touch text inside
`application/ld+json`, and every bundle now checks that every block parses.

Go-live (bundle 57, built 14 September, held for the cutover day, target
Sunday 20 September): the staging block is gone from `_headers` (the three
lines and nothing else), `robots.txt` is the go-live file, and the palette
dock is hidden by one rule at the end of the shared chrome CSS rather than
removed, so `tools/sync_chrome.py` keeps its invariants. The runbook is
`dea-go-live-runbook.md` in Steve's Downloads and in the chat: email is
Microsoft 365 (MX to outlook.com, SPF, two DKIM CNAMEs, DMARC, the MS= and
google-site-verification TXT records), and every one of those records has to
exist in the Cloudflare zone before the nameservers leave `wixdns.net`. Order
on the day: push this bundle, add both hostnames as Pages custom domains,
apex-to-www redirect rule with the query string preserved, SSL Full strict,
then the nameservers. Rollback is the two Wix nameservers back at the
registrar. Wix stays untouched for two weeks after.

Live (20 September 2026, evening, origin e6d6a20 then 58): the cutover
went as written. Zone `dallaseventaudio.com` on Cloudflare Free with
nameservers `betty` and `dakota.ns.cloudflare.com`, all 18 records DNS only
except the two Pages hostnames, SSL Full (strict), redirect rule "Apex to
www" (wildcard, 301, query string preserved), both hostnames Active on the
Pages project. Verified from Steve's Chrome on the real domain: 84 URLs 200,
55 redirects one hop, GA4, Ads and the Meta pixel firing, concierge
answering. Bundle 58, the same evening: Steve wants the palette dock on the
live site, so the one hiding rule from bundle 57 is removed again and the
chrome resynced. The dock is a visitor feature now, not a review tool.

Bundle 61 (21 September, first PageSpeed pass after go-live): mobile home
page scored 66 with the largest paint at 6.9 s, desktop 93. The same page
scored 97 in a local Lighthouse run where the production-only tags do not
load, so the gap was the Google tag downloading in the head on a slow
phone. The gtag loader now waits for the load event like the Meta pixel
(the stub and dataLayer stay immediate, nothing is lost). The hero lasers,
fog and grid animation are off under 700px. Accessibility items from the
same report, all site-wide: the palette toggle has an aria-label (its text
label is hidden at phone width), the footer "Fort Worth" inline link is
underlined, the footer column titles are h3 (they were h4 after an h2, a
skipped level), and every page's content sits in a main landmark between
the header and footer. Local Lighthouse mobile: accessibility 90 to 100,
performance unchanged, no layout shift introduced.

Bundle 62 (23 September): four things. Space Grotesk, the body face, is
font-display:optional (Unbounded stays on swap); PageSpeed timed the hero
subtitle's font repaint as the mobile largest paint, and the metric matched
fallback keeps the line box identical either way. The concierge now keeps
every conversation: the widget makes a random id on the first message,
keeps it in sessionStorage beside the history, and sends it with the page
path on every turn; the Worker upserts the transcript into the D1
`conversations` table (schema in `dea-concierge/sql/0001_conversations.sql`,
run once with `wrangler d1 execute DB --remote`). A cron in wrangler.jsonc
(12:00 UTC, so 7 am Dallas in summer) runs `scheduled()`, which has Claude
summarize the previous Dallas day's conversations and emails the digest to
LEAD_TO through Resend; the `digests` table stops a double send, and an
empty day sends nothing. POST /api/digest with an `x-digest-key` header
runs it by hand, only if the DIGEST_KEY secret exists. Old pages cached
without the widget change send no id and are not stored. Tests:
`npm test` in dea-concierge (plain node, stubbed D1 and fetch). New page
/privacy, built from the thank-you page's frame with the conversion script
removed, indexable, in the sitemap at 0.3, in llms.txt under The company,
linked as "Privacy" in the footer bottom row of all 81 pages. The footer
bottom row also gained 72px of bottom padding site-wide because the
concierge and palette pills covered the copyright line at the bottom of
every page on phones.

Bundle 63 (23 September): the third party tags wait for the first scroll,
tap or key press, or 3 s after the load event, whichever is first. After
bundle 62 the mobile home page still measured its largest paint at 5.9 s
(score 67 to 76 depending on the run) while the same page with no tags
measures 2.3 s locally. A lab test reproduced it: a 190 KiB script
injected on the load event moved local LCP from 2.3 s to 3.4 s, and a
requestAnimationFrame gate did nothing, because on a fast connection load
fires before a slow phone's first paint; a 3 s timer restored 2.3 s. The
gate lives in tools/chrome/analytics.html as window.__deaWhenReady and
both loaders use it. The thank-you page loads at once so its conversion
never waits, and the pixel's init and PageView now queue before any
Lead. The measurement cost is visitors who leave inside 3 s without
touching the screen; they stop appearing as sessions. The font change in
bundle 62 turned out to be neutral in Lighthouse and stays because it is
right for real phones.

Bundle 64 (26 September): bundle 63's tag gate is reverted. The Google tag
and Meta pixel load on the load event again, as in bundle 61; the pixel
still queues init and PageView up front. In the two days the gate was live,
GA4 engagement fell from about 75% to about 45% and pages per session from
2.3 to 1.6 with sessions flat, because GA4 times engagement from when the
tag loads and a fast click-through lost its page view; a paid visitor who
tapped through before the tag loaded also lost the gclid. Lab mobile
PageSpeed returns to the 70s. Field data (Cloudflare RUM, 92% good LCP) is
what ranks, and it was good with the tags on load. Do not gate the tags
behind interaction or a timer again. GA4 figures for 24 and 25 September
understate engagement and should not be compared with other days.

Bundle 65 (26 September, concierge only, no page changes): the morning
digest runs on claude-opus-5-5 at low effort (DIGEST_MODEL in
wrangler.jsonc, output_config effort "low", max_tokens 6000 because Opus
5.5 thinking counts toward it) and falls back once to MODEL if that call
fails. Transcripts go in <transcripts id="..."> tags with a matching random
id on the closing tag, and the digest system prompt says what is inside is
material to summarize, never instructions. The live chat stays on
claude-sonnet-4-5. prompt.js v5: the bot no longer promises a technician
at every booking; every booking is delivered, set up, tested and picked up,
and the technician stays for the services that call for it (Steve, 25
September). The WHAT EACH PAGE SAYS summaries in prompt.js still carry the
old "technician on every booking" wording from the pages; regenerate them
after the site-wide staffing pass. Tests: npm test (7).

Done 27 September (bundle 69): the site-wide staffing pass, on Steve's
page-by-page answers of 27 September (kept in the bundle message). Speaker,
subwoofer, DV12, DML500 and CDJ rentals are delivered, sound checked with the
client's source and picked up; fog and haze are placed and tested for the
DJ or planner to cue (Dancing on the Clouds is the one we run); uplighting,
DJ lighting, monogram, projector and TV are set up, tested and picked up,
with a technician or lighting engineer on request; sound equipment and audio
services carry a tech on request, recommended for complex setups; weddings
say DJ packages include the DJ, ceremony-only includes a one hour ceremony
audio engineer, and traveling DJs and bands get setup, sound check and
pickup after the send off. Corporate, line array, luxury, rave and club,
college, sensory-friendly, live music, streaming, photo and video, cold
sparks, clouds, lasers and follow spot keep the technician. The footer line
on 82 pages and the post-foot line on 37 posts changed to "delivered, set
up, tested and picked up by our own crew". Keyword pass from the 12-month
Search Console export: corporate AV services and corporate audio visual
services (corporate-events title, H1, H2s), Dallas event videographer
(services-photo-and-video title and H1), an audio equipment and sound system
rental section on rent-sound-equipment, "Rent sound equipment for your
wedding" on wedding-av-rental-dallas, "Rent DJ equipment for a wedding" on
the CDJ page, AV rental wording on the homepage. Stat rows now say "Service
radius from the Mid-Cities (76053)". Three old Wix post URLs 301 to their
new homes. llms.txt carries a key facts list and links a generated
llms-full.txt (tools/build_llms.py writes both). prompt.js v6 regenerates
WHAT EACH PAGE SAYS. wrangler.jsonc now mirrors the dashboard's logs
setting. Deploy the Worker after pushing.

Done 27 September (bundle 71; 70 was handed to the video chat): the base
location reads ZIP 76053 wherever the site said the company is in or works
out from Hurst (Steve, 27 September). Hurst stays where it is a city we
serve, in city lists and chips. The Organization schema address carries
postalCode 76053 in place of addressLocality. CO2 cannons keep the
technician. The single-item FAQs on equipment-list and gallery now say CDJs
and DJ mixers rent on their own, and everything else goes out as part of a
package.

Bundles 66 to 68 (26 September): the homepage production reel replaced the
photo and video placeholder (66); a gig post, a daytime country club wedding
in McKinney (67); a projector and screen explainer on the projector rental
page (68).

Bundle 72 (5 October): the business is named in the opening line of 18
service pages; The Knot, WeddingWire, YouTube and Instagram joined the
business profile links (`sameAs`); ChatGPT, Claude and Perplexity search
agents are allowed by name in robots.txt; chat leads now go from concierge@
to steve@ (wrangler.jsonc). Bundle 73 (5 October) added Facebook and
LinkedIn to the same profile links. The LinkedIn company page is id
112493261, administered from steve@dallaseventaudio.com.

Bundle 74 (7 October): concierge prompt v7. The bot asks for contact details
once, as the last step, and a phone number or an email alone counts as a lead
(`hasUsableContact` no longer needs a name). It never corrects a client's
model names. It names the DJ inventory when it fits (XDJ-RX3, XDJ-AZ,
CDJ-3000s, DJM-900NXS2, DJM-A9, DDJ-FLX6), says quotes come "within 24
hours" and never "today" or "same day", and handles insurance in one line:
DEA is insured and provides a certificate of insurance to any venue that
requires one; it never says rentals include insurance for the client or who
is responsible for the gear. Generators are in the power inventory. The
privacy page and the McKinney post now say "within 24 hours".

Bundle 75 (9 October): cold sparks are retired, on Steve's decision after a
fire marshal shut down a client's cold spark setup that ignored the floor
plan; permits take weeks and the risk is not worth it. `/rent-cold-sparks`
301s to `/services-extra` (all three URL forms) and the page is gone from the
header, drawer, footer, sitemap, `_pages.json`, `build_llms.py` and every
in-body mention, including the platinum wedding package. Where a page offered
sparks for an entrance or a first dance it now offers a CO2 burst and Dancing
on the Clouds. `/services-extra` reads "CO2 cannons, lasers, fog and
clouds." Concierge prompt v8 never opens with "No": it says DEA does not
offer cold sparks and leads with CO2 for an entrance and the clouds for a
first dance. The one client testimonial that mentions cold sparks on
`/what-others-are-saying` stays, because it is the client's own words.

## Where things stand on 20 October 2026

Origin is at bundle 91 (6e3e1a4). Bundle 93 is cumulative (it carries the
unpushed 92 plus the projector work; 92 is dead); the next bundle number is 99,
and 70 stays reserved for the video chat.
Bundle 77 was never pushed.

Bundle 78 (12 October), corporate events rebuild. Twelve months
of Search Console: about twenty corporate queries on the page, essentially
no clicks; the best positions are the Dallas-modified ones ("corporate av
dallas" 8.3, "corporate av services dallas" 8.4, "corporate event av dallas"
18, "conference av services dallas" 23), the broad ones sit at 34 to 47.
Search intent, checked in Steve's Chrome: the Dallas terms return vendor
event AV pages, a local pack and one list (PartySlate, which already lists
DEA); the broad "corporate audio visual" terms are shared with permanent
installers (Ford AV, Texadia, CTI, Avidex), which is not DEA's work, so the
page aims at the Dallas event terms. Changes: the scrolling keyword strip
and the keyword tags under the six room headings are gone (they read as
stuffing and Google saw "General session and keynotekeynote AV Dallas");
each tag's phrase now opens its card's prose. Four corporate reviews from
/what-others-are-saying (Kaleb G., Will S., Blake B. on Yelp, Brandon Klekar
on Google) sit in a new "In Their Words" section. The "cheaper
equipment-only quote" paragraph (implied pricing) became a line on event AV
versus permanent installs, with a matching FAQ. The SEO diff reports drops
on marquee-only terms on purpose. The what-others-are-saying Organization
schema no longer lists cold sparks (missed by bundle 75). Two of Steve's
jobs are written in: a training class at the Infomart (7 October 2026, two
EV ZLX speakers and an Epson 700U on a framed screen) in the breakout card,
and a medical symposium at the Renaissance Plano Legacy West (10 October
2026, Legacy ballroom: two ALR screens with an Epson each, two DV12s,
De-Feedback wireless mics, uplighting, logo projection) in the general
session card. Client names stay off the page. Infomart Dallas joined the
venue list (HoneyBook project marked Busy). The companion post
/post/why-av-production-matters-for-corporate-events was re-angled in the
same bundle to "What Is AV Production?" (slug unchanged), linking up to
/corporate-events#av-production from its body.

Cloudflare: the apex now 301s to www (redirect rule "Apex to www" with the
apex record proxied), and Crawler Hints is on, so Cloudflare pings IndexNow
when pages change. Search Console, GA4 and Bing all see the www host.

The chat digest emails "Concierge digest YYYY-MM-DD" to steve@ every morning.
Concierge v8 should be confirmed as deployed (`npx wrangler deployments
list`, or ask the chat about cold sparks) if it has not been already.

Still saying "same day" on purpose until Steve decides: the reply promise on
the contact FAQ, `/services-dj`, the clouds page and the sensory-friendly
page. Everything else says "within 24 hours".

Bundle 79 (12 October): YouTube embeds, click to load. The channel trailer
(UXXZR4QP1Y0, 0:47) sits in a new #video section on the homepage before the
reviews, and "Dancing on the Clouds: How the First Dance Cloud Works"
(DS_KD0NOuPA, 0:49) sits in the #dancing-on-the-clouds section of the clouds
page. Each is a .yt box with the YouTube preview image and a play button; a
page-local script swaps in a youtube-nocookie iframe on click, so nothing
from YouTube but the preview image loads before a visitor presses play. Each
page carries a VideoObject block, and the privacy page says so in one
paragraph. The corporate page gained a .job-figs row of three photos under
the room cards: the symposium panel, the same ballroom before doors (the
host's projected logo blurred on Steve's call, kept in frame to show logo
projection), and the Infomart training room (the screen's wireless HDMI
splash, which showed a Wi-Fi name and password, blurred). They are 16:9,
not the usual 4:3, because the subject runs edge to edge in all three.

Bundle 80 (12 October, late): corporate page follow-up after Steve ran the
page past Gemini. The intro now says the work is event AV, packed out after
the program, and names the two October jobs with a link down to the photo
row (#jobs, with a scroll margin for the sticky header). A "Check your date"
chip row follows the photos and another follows the reviews. The "What AV
production covers" lede is shorter. The homepage's in-body link to the
corporate page now reads "corporate event AV services in Dallas" (the
homepage held that query at position 32, which is the cannibalization the
rebuild flagged). Held on purpose: the title and H1, until a Search
Console re-pull around 26 October shows whether bundles 78 to 80 moved
clicks; if they did not, test "Corporate AV Company Dallas-Fort Worth |
Dallas Event Audio". Gemini's other points were already on the page (venue
list, certificate of insurance, 24 hour quotes, alt text, schema) or broke
house rules (negative framing in a description, a certificate promised
"within 24 hours").

Bundle 81 (14 October): quick wins from a site-wide review (the full review,
with 90-day numbers per page, is in the Claude project as
claude/site-review-2026-10-14.md because it carries analytics). The
microphone page title now leads with "Wireless Microphone Rental Dallas",
its best query (9.4, zero clicks); "party speaker rental" on
rent-sound-equipment and private-events now links to /dj-speaker-rental; and
/rent-laser-light-show gained the BreadcrumbList every other service page
has. Rebuild order from the review: projector and screen rental, services
lighting, the clouds page and wedding fog post split, rent-sound-equipment.

Bundle 82 (20 October): Microsoft Clarity heatmaps and session recordings,
project z0idn3mm8n, added to `tools/chrome/analytics.html` beside GA4 and the
Meta pixel, so it reaches every synced page. Same production hostname guard
and load-event timing as the other two tags; leave Clarity's form masking on.
The privacy page names Clarity and Microsoft. davidsbridalfrisco.html sits
outside the chrome sync and does not carry it.

Bundle 83 (20 October): the YouTube explainer "How Many Speakers Do You Need
for 100, 200 or 500 Guests?" (bZxNyXIbGZw, motion graphics built with
HyperFrames, narration by the ElevenLabs voice "Hope") is embedded on
/post/how-many-speakers-do-i-need-for-100-200-or-500-guests with the same
click-to-load box and VideoObject schema as the clouds page. The same post lost
its "What does speaker rental cost" section (dollar ranges) in favor of "What
comes with a speaker rental?", its description no longer promises rental costs
(blog card and llms updated to match), and the subwoofer answer no longer says
a sub "costs little". The separate AV-cost pricing post is untouched.

Bundle 84 (20 October): two new posts, both feeding /corporate-events.
/post/corporate-holiday-party-av-dallas (holiday party sound, lighting and
video at 50, 150 or 300 guests, and when to book December; venues named on
Steve's say-so, clients never) and
/post/how-to-choose-an-av-company-for-a-conference-or-gala (ten questions,
written for the long AI-search questions that were landing on the corporate
page). Both built from the speakers post template, with BlogPosting and
BreadcrumbList schema, blog cards, ItemList entries, sitemap, _pages.json and
llms. The corporate page links to each from its holiday card and its
"why companies choose" intro. Both use existing corporate photos; Steve owes
holiday party photos to swap in.

Bundle 85 (21 October): contact page conversion pass, from the first day of
Clarity data (half of desktop contact visitors never scrolled past 20%, and
the HoneyBook form starts about two screens down on desktop and four on a
phone). A Request a Quote button in the hero and the header Get a Quote button
(rewritten on this page only by a small page-local script, header copy only,
drawer untouched) both jump to the form card, id quote-form. The duplicate
lead paragraph above the form folded into the section intro. "Same-Day Reply"
became "Reply Within 24 Hours" in the badge and marquee, and the FAQ answer
dropped "same day" (FAQPage schema matches). The email address keeps to one
line on desktop (val-email class, break point after the @ on narrow screens).
The Knot proof line grammar fixed. Note that the HoneyBook form itself still
lists cold spark machines; that lives in HoneyBook, not the repo.

Bundle 86 (21 October): above-the-fold pass. A Playwright scan of every page
at 1440x900 and on an iPhone 13 found that only contact, laser and weddings had
a quote button in the first screen; on the other service pages the first
in-page quote button was the final CTA, 8,000 to 37,000 pixels down, and
Clarity showed the header Get a Quote taking half of all clicks on the
projector page. 34 hero-page pages now carry two copies of a two-button row
(Request a Quote to /contact, Call 817-210-7957 to tel): hero-ctas-d after the
intro paragraph for desktop, hero-ctas-m straight after the H1 for phones
(700px and under), so exactly one shows. Weddings got the phone copy of its
own buttons. On the home page the duplicate hero logo shrank (440px to 300px,
40vw on phones), the phone hero padding and eyebrow tightened, and the phone
button row sits under the H1. Blog posts were left alone on purpose. The CSS
for the rows sits right after each page's base hero-ctas rule, because the
base rule's display:flex would otherwise win.

Bundle 87 (21 October): the AV Concierge pill on phones (700px and under) is
now a short "Ask" pill tucked 14px from the corner, about 71 by 41 pixels
instead of the full label, because it sat over the new hero call button. The
label lives in two spans in tools/chrome/widget.html (cb-label and cb-short)
and the bubble carries aria-label "AV Concierge chat". Desktop is unchanged.
The id chatBubble is untouched, so the sensory-friendly page still suppresses
it.

Bundle 88 (21 October): phone and text taps count as leads. The shared
listener in tools/chrome/analytics.html still sends contact_click for every
tel, sms and mailto tap, and now also sends call_tap for a phone tap and
text_tap for a text tap, the same names the David's Bridal page already used.
Both were created in GA4 on 21 October as key events (Create with code, no
default value, counted once per session). Email taps are deliberately not a
key event. Google Ads imports them as Secondary conversions first, so they
show up in reports without steering bidding; promoting them to Primary is a
later decision. Tested by routing the production hostname to the local tree:
a tel tap pushed contact_click plus call_tap, an sms tap contact_click plus
text_tap, a mailto tap contact_click only.

Bundle 89 (22 October): unique openings and gear lines on 11 pages
(subwoofers, line array, DJ and party speakers, sound equipment, projectors,
clouds, uplighting, DJ services, DJ lighting, audio services, corporate
events). Every opening had started "Dallas Event Audio rents ... across
Dallas-Fort Worth" and spent half its length on delivery and setup; each now
leads with the page's top Search Console cluster from the last 90 days and is
shorter. A p.gear-line under each H1 names the gear DEA owns, model names only
from the inventory (lighting by function, per the standing rule, except the
ADJ WMX1 MK3 WOLFMIX controller Steve added as an uplighting option on 22
October). The rent-sound-equipment and services-audio openings keep "Dallas
Event Audio" because those pages rank for the brand. The WMX1 MK3 was also
added to the equipment list uplighting card and the concierge inventory in
dea-concierge/src/prompt.js, which needs a wrangler deploy to go live.
Steve's BassBoss inventory: SSP118-MK3, VS21-MK3 and ZV28-MK3 subs and DV12-MK3
tops, one per stand or a 2x2 array; quantities are not published.

Bundle 90 (22 October): the palette dock stays. Steve's call, 22 October
2026: it is a fun way for visitors to play with the site, not a review tool to
remove. tools/chrome/palette_js.html now sends GA4 palette_open (page_path)
when the dock opens and palette_change (palette, page_path) when a theme is
picked, and pushes the same two names to Clarity as custom events. Both calls
are guarded. To see which palette people pick in GA4 reports, register
"palette" as an event-scoped custom dimension in GA4 admin. (Done 22 October:
custom dimension "Palette".)

Bundle 91 (22 October): /rent-bassboss-subwoofers rebuilt around Steve's own
photos and published specs. The four model cards are reordered subs first
(SSP118, VS21, ZV28, then the DV12 top), each with a 4:3 photo and a
"Published" spec line taken from the bassboss.com product pages (Steve, 22
October: the website is more current than the cut sheets, so use its figures).
A two-photo strip follows: Rave & Buster's at Dave & Buster's (event cleared,
naming approved by Steve) and the VS21s beside the ZV28s in the shop. A new
#compare section has three tables (single 18, single 21, double 18) comparing
BassBoss with QSC, JBL, RCF, Mackie, Electro-Voice and Yamaha, every figure
from the maker's own page or sheet, checked October 2026: low end with the
tolerance each maker publishes, output as the published peak figure at 1 m,
amplifier wattage deliberately left off, sources linked. Two FAQs added
(BassBoss vs QSC/JBL/RCF; which BassBoss sub to rent), FAQPage schema matches,
meta description names the models. Photos live in /images/subwoofers/; the
DV12 photo is cropped to keep a QSC speaker out of frame (DEA does not stock
QSC). Full research:
project doc claude/bassboss-rebuild-research.md.

Bundle 92 (22 October): Steve cut the "bigger BASSBOSS boxes" claim (double
and quad 21s, MFLA modules), which is outside the inventory. The block is gone
from /rent-bassboss-subwoofers; on /dj-speaker-rental the same addon now reads
"When the room outgrows a pair of speakers" and names only owned gear (SSP118,
VS21, ZV28 and the DV12 array), keeping its links to the subwoofer and line
array pages. llms-full.txt rebuilt.

Bundle 93 (22 October), projector cannibalization fix. Search Console showed
/post/projector-rental-dallas-tx ranking for the service page's head terms
("projector rental" 129 impressions at 22.8, "projector rental near me" 75 at
18, "rent a projector" 73 at 16.4) while /projector-screen-rental sat at about
15 to 17 on the same terms. The post keeps its slug and is re-angled to its
own queries (projector for an office or business presentation, meeting
projector): new title, H1, description, sub, body, FAQ, dateModified, and the
blog.html and our-work.html cards and schema names. The head-term words drop
on purpose, so the SEO diff on the post FAILS by design (word count -18%,
"projector rental" headings gone); the service page diff passes. The post
still links to /projector-screen-rental three times. On the service page: a
"Where to rent a projector and screen near you" block with Fort Worth wording
in the service area section, a near-me FAQ (visible and schema), the guide
link re-labelled, and "community screenings" removed (no outdoor movie
setups). Open question for Steve: the long throw card says a 124 inch tripod
or 144 inch screen while the gear line says 120 inch; left as is until he
confirms the sizes.

Bundle 94 (23 October): two quote buttons that scrolled instead of leaving
the page now go straight to /contact. On the clouds page the final "Get a
fog machine quote" button pointed at #quote, a section higher on the same
page with no form, so it scrolled visitors back up (Steve found it). On the
home page both hero "Get Your Quote" buttons pointed at #contact, the closing
section, which added a step before the form. Only those three hrefs change.
Rule: a quote button links to /contact, never to an anchor, except on
/contact itself where the anchor is the form.

Bundle 95 (23 October): /contact. Steve's call: the hero line "Call, text,
email, or send the form below..." is cut to bring the form up the page (the
24-hour promise still shows in the badge, the side card and elsewhere). A
one-line note now sits above the HoneyBook form: "Only your email, event date
and event type are required. The rest helps us quote faster." Why: GA4 showed
/contact visits up since the move but thank-you views falling (about 9% of
visits by mid October), and Clarity showed about 30% of desktop visitors
scrolling past the whole form without sending it. Steve's test submission on
23 October reached /thank-you and HoneyBook, so the form itself works. The
form's fields stay as they are (DJ, photo and video are real services).

Bundle 96 (24 October): Chauvet DJ Geyser P7 LED fog jets added. Steve
switched to the Geyser P7 (he owns them; never publish quantities). New
section #geyser-fog-jet on /rent-fog-machine between haze and high density
fog, with an Offer in the Service schema (FAQ unchanged), and a new card 05
in the fog section of /equipment-list (Power, cable and stands is now 06; the
ItemList description names the P7). Positioning, Steve's call: CO2 stays on
offer and in the ads, and the P7 is the substitute for longer lasting effects
or venues that will not take cylinders. Specs from chauvetdj.com: 17,000 cfm,
seven 9 W RGBA+UV LEDs in two zones, QDF fluid, 0.7 gal tank, 4 minute heat
up, 1,290 W, 18.16 lb, 15 DMX channels plus wireless remote. The concierge
prompt does not list the P7 yet.

Queued work, in Steve's order: a local SEO audit with `dea-local-seo-audit`;
then DJ and lighting content passes, the live streaming page, and pruning
or redirecting the old posts that earn nothing.

## Venues we've worked (bundle 97, 24 October 2026)

New page `/venues` (`venues.html`): 316 public event venues from Steve's
booked HoneyBook projects (late 2020 to 24 October 2026, past events only),
grouped by city, with a client-side search box and a Clouds tag on the 72
venues where Dancing on the Clouds ran. Names only: no client names, job
counts or prices. Left off on purpose: private homes, plain street addresses,
and buildings owned by the client (company offices, schools, churches,
hospitals). The list is generated from the booking analysis, not hand-typed;
regenerate it rather than editing names one by one. The clouds page gained a
"Venues where we've run Dancing on the Clouds" section (#clouds-venues) above
#included. Linked from the header and drawer (Our Work menu), every footer's
Company column, our-work, weddings and fort-worth. Venue guide pages wait
until event photos are matched to venues. `sync_chrome.py --check` now covers
85 files.

Bundle 98 (26 October 2026), venues by event type: Steve wanted the page to
read as every kind of event, not mainly Clouds. Each venue `<li>` now carries
`data-t` (wedding, corporate, private, music, gala, school, worship, sports,
clouds) taken from the HoneyBook project type of the booked jobs there
(Busy projects first; a venue with no Busy match falls back to its other
projects). A filter row of buttons above the search box (All venues, Weddings,
Corporate events, Private parties, Live music and club nights, Galas and
fundraisers, School and university, Church events, Sporting events, Dancing on
the Clouds) works together with the search; on phones the row swipes
sideways. No counts are shown, per the venue rules. 8 venues have no event
type on record and appear under All venues only. The filter fires a GA4
event `venue_filter` with the filter name. Sub, section intro, H2 and meta
description now name the event types and link the event pages.

Bundle 99 (26 October 2026), cumulative: carries bundle 98 (venues by event
type; 98 was never pushed and is dead) plus two AV Concierge fixes in
`tools/chrome/widget_js.html` and `chrome.css`, synced to all 85 pages.
Steve saw the iPhone keyboard cover the chat input now and then, and Clarity
showed a phone visitor tapping the greeting about 15 times as if its four
choices were buttons. (1) On phones the chat no longer focuses the input when
it opens, so the keyboard stays down until the visitor taps the box, and a
visualViewport listener lifts and caps the bottom sheet to the area the
keyboard leaves visible (iOS Safari does not shrink the layout viewport, and
82vh ignored the keyboard; 82dvh is now the CSS fallback). Desktop is
unchanged. (2) Under the greeting, four tap-to-answer buttons (Planning an
event, Planner or coordinator, DJ, band or performer, Just have a question)
send their text as the first message and disappear; GA4 event
chat_quick_reply carries the choice. The Worker and its prompt are untouched.

Bundle 100 (26 October 2026), cumulative: carries 98 and 99 (both never
pushed, both dead) plus chat links that keep the visitor on the site. A link
the concierge writes to a page of this site (a path, or a full
dallaseventaudio.com URL) now opens in the same window instead of a new tab;
clicking it sets the sessionStorage flag `dea-chat-follow`, and the next page
opens the chat with the conversation intact (the history was already kept in
sessionStorage). A plain reload does not reopen it. Off-site links still open
in a new tab. GA4 event chat_link_click carries the path. The prompt
(dea-concierge/src/prompt.js, rule 11 and the page digest intro) now asks the
bot to link each service or equipment page it names, written as markdown
links on the words with the path only, up to three per answer. The prompt
change needs `npx wrangler deploy` from dea-concierge/ to go live.

Bundle 103 (26 October 2026), venues by service: each venue `<li>` also
carries `data-s`, the services booked there (past jobs only), from the same
booking analysis as the list: sound, dj, mics (wireless mics and De-Feedback),
uplighting, stage (moving heads and stage lighting), projection, lasers, fog
(fog and haze), clouds, co2, stream (live streaming), tvs. Tokens are sorted
most booked first. Cold sparks, photo booths, monograms, labor, delivery and
fees are never tags. Up to three pills sit beside each name (`.vtags` holding
`.vtag` spans, the old Clouds pill style), most booked first; Clouds always
shows where it applies, replacing the third pill if needed. 41 venues come from
older proposals with no line items and show no pills; they still appear under
All services. A second filter row, `#serviceFilter` (buttons with `data-s`),
sits under the event-type row with small "Event type" and "Service" labels;
the Dancing on the Clouds button moved from the event row to the service row
(the `clouds` token stays in `data-t` too). Event type, service and search
combine. GA4 `venue_filter` sends `service_<token>` for service buttons. The
section intro links the service pages and names the AI-powered De-Feedback
system with wireless mics. No counts are shown, per the venue rules.

Bundle 104 (26 October 2026): the service pills read as clutter in three
columns, so `.vtags` became a quiet second line under each venue name: plain
text in `--dim`, sentence case, separated by middle dots, with Clouds in the
accent color (`.vt-clouds`). Same tokens and order as bundle 103.

## Phone links, clouds, TV 55 and CDJ quick quote (bundle 108, 28 October 2026)

- Shared chrome (tools/chrome/navdrawer_js.html, chrome.css, analytics.html): with a mouse (hover:hover and pointer:fine), clicking any tel: link copies 817-210-7957 and shows a short note instead of dialing. Touch screens keep tap-to-call. GA4 logs the desktop click as contact_click with contact_method phone_copy and does NOT send call_tap, so the Google Ads call conversion stays phone taps only. GA4 had 0 desktop call_tap in 90 days; Clarity logged desktop phone clicks as dead clicks. davidsbridalfrisco is outside the chrome sync and unchanged.
- Homepage title and description test, approved 28 Oct; compare Search Console CTR about 25 Nov against the 4 weeks before. Title "AV Equipment Rental Dallas-Fort Worth | Sound, Lights, Video", description names speakers, wireless mics, projectors, TVs and lighting, delivered, set up and tested, quotes within 24 hours. Old title "AV Equipment Rental in Dallas-Fort Worth | Dallas Event Audio".
- /tv-rental-dallas: 55 inch TV added (meta and og description, Service description, OfferCatalog, the lineup sentence, hero spec line, a 55 inch sizing card, and the sizing FAQ in both the visible answer and FAQPage). Steve owns 32, 43, 55 and 65; no larger sizes.
- /rent-dancing-on-the-clouds-low-lyin, from Clarity (28 Oct: 41% of mobile views left without scrolling; taps on the size card text; desktop phone dead clicks): on phones at 700px and under the dimmed hero film is removed before it loads and a clear photo of the effect (the hero poster) sits under the H1, with Request a Quote and Text us (sms with a prefilled body) and a call line. Each of the four size cards gets "See a floor this size" (scrolls the reel to the clip with the closest floor and plays it: Junior to Barn venue #floor-small, Nimbus to Grand ballroom #floor-standard, Entour Ice to Uplit room #floor-wide, Cumulus to Live band #floor-stage), "Request this size" (/contact) and, on touch screens, "Text us about it" naming the machine. The wording says a floor this size, not that machine; which machine ran in each clip is not known. The reel and fog film videos already lazy-load (preload none plus IntersectionObserver).
- /rent-sound-equipment/cdj-rental-dallas: "Text us your date to check availability" (sms with a prefilled date and venue line, phones only; bundle 108 shipped it as "Text us your gear list for a quick quote", reworded in bundle 109 on Steve's call) under the mobile CTAs, and a scrolling strip of six of our own gear photos (480w webp) in the hero.

## Review count (bundle 107, 28 October 2026)

Steve, 28 October: the headline review figure is 4.9 across 187 reviews,
Google, The Knot, Yelp and WeddingWire together. The thank-you page stat now
says so (it read "Google rating across 43 reviews"). The per-platform counts
on the reviews page, /contact and the thank-you profile cards stay as they
are, since each one is that platform's own number.

## Speed pass (bundle 106, 27 October 2026)

PageSpeed mobile on 27 October: home 92, projector 74, clouds 66, contact 32.
Changes: (1) /contact loads the HoneyBook form script (about 1.8 MB with
Google reCAPTCHA) on the first scroll, tap or key press, when the form nears
the screen, or when the URL hash starts with #quote; the noscript fallback
is unchanged. (2) tools/chrome/analytics.html loads the Meta pixel script
after the load event on the first interaction or after 4 seconds; init and
PageView are still queued first, so the thank-you Lead keeps its order.
(3) The header logo carries fetchpriority="high" (it is the largest paint on
pages without a hero photo). (4) The clouds page reel and closing clip take
their posters from data-poster when they come within 800px of the screen.
(5) The projector explainer posters were resized from 1920 to 1280 wide
(about 120 KB to 58 KB each). Local Lighthouse: clouds 84 to 93, projector
87 to 90. Do not move the HoneyBook loader back into the page head.

## Dead clicks, quote promises and pricing (bundle 105, 27 October 2026)

Clarity dead clicks showed visitors tapping things that looked tappable. The
twelve service-area chips on /contact are now links: Fort Worth goes to
/fort-worth, every other city to `/venues?q=<city>`, and /venues reads `q`
from the URL into its search box (capped at 60 characters). The four use
cards on /rent-fog-machine link from their headings, with a stretched link
covering the card (Grand entrance and Halloween and haunts to /contact, Club
and concert to /rave-and-night-club-events, Photo and video to
/services-photo-and-video). The remaining "same day" reply promises on
services-dj, the clouds page and sensory-friendly (visible FAQ and schema)
now say a quote within 24 hours; the certificate of insurance lines keep
"same day" on purpose. The cost post
(post/av-equipment-rental-dallas-fort-worth-cost, slug unchanged) no longer
carries any dollar figures: the intro and the package list describe what
goes into a quote instead, dateModified 2026-10-27. Projector screen sizes
per Steve: 120 inch tripod, 144 inch matte white, 150 inch Elite Screens
ultra short throw ambient light rejecting. /corporate-events links the
Frontiers of Flight keynote post from its product launch block. The
concierge prompt lists /venues under THE COMPANY (needs `npx wrangler
deploy`).

## Frontiers of Flight keynote post (bundle 101, 26 October 2026)

Gig post /post/product-launch-keynote-frontiers-of-flight-museum: a software company's product launch keynote in the
main hall of the Frontiers of Flight Museum (Dallas Love Field), with the Epson
700U ultra short throw projector on the stage, the ambient light rejecting
screen, two speakers on tripods, three lapel mics and a handheld on De-Feedback.
Five photos in images/blog (4:3 ladder, no EXIF on the originals, so no date in
the copy). The client is unnamed in text, alt and filenames; its slides stay on
screen in the photos, the same as the other projector photos. The presenter photo
replaced the Class A hangar shot in the projector page's ultra short throw slot;
the old ultra-short-throw-projector-rental-dallas image files are now unused.
The projector page links the post from that section. Built by patch.py on top of
bundle 100, so the post inherits whatever chrome 100 carried.

## Tools skip node_modules (bundle 102, 26 October 2026)

tools/sync_chrome.py, tools/image_gaps.py and tools/optimize_images.py glob every
.html under the repo. Running `npx wrangler deploy` installs dea-concierge/node_modules,
which contains HTML files, and sync_chrome.py then crashed with "no </head>". All three
now skip tools/, node_modules/, dea-concierge/, .wrangler/ and .git/. node_modules stays
gitignored; leave it in place.

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
commit messages. They are written to be read. Then read the DEA status file
in the Claude project for the private to-do list, and keep both up to date:
this file in the next bundle, the status file by handing Steve a new copy.
