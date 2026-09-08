# dallaseventaudio.com, pre-launch SEO review against Google's 2026 updates

Reviewed 7 September 2026 against the repo at fdcf245 plus bundles 16 and 17. Every one of the 79 pages was checked by script; four were run through Lighthouse on a mobile profile and the homepage through PageSpeed Insights on the Pages preview.

## What Google changed this year, and what it means here

Google shipped two core updates (27 March, 21 May), a Discover core update (5 February) and three spam updates (24 March, 24 June, 18 August). The analyses of the core updates agree on the pattern: narrow specialist sites with first-hand experience and real examples gained, aggregators and generic rewrites lost, and the E-E-A-T bar that used to apply to health and money now applies to most competitive queries. The August spam update was the loudest of the year and hit scaled, programmatic and thin AI-written content across whole domains, not just the offending sections.

On 7 May Google stopped showing FAQ rich results. FAQPage markup is still valid schema and Google says unused structured data does not hurt, so the 37 FAQ blocks stay: they are real, visible, and they match the answers on the page. They just no longer earn a SERP dropdown.

PageSpeed Insights now carries an Agentic Browsing category that checks whether a page is navigable by AI agents through its accessibility tree. The one failure on the homepage is the palette toggle button, which is review-only and comes out at cutover.

## Where the site stands

Already clean before this review: unique titles and descriptions inside the limits on all 78 indexable pages, a self-referencing canonical on the www host everywhere, one H1 per page, alt text on every image, no broken internal links, no links into redirects, all 194 JSON-LD blocks parsing, no aggregateRating anywhere, no near-duplicate service pages (the doorway-page pattern the spam updates punish), 77-entry sitemap, 79-rule redirect map from Wix's own export.

PageSpeed Insights on the homepage, mobile: Performance 96, Accessibility 91, Best Practices 100, LCP 2.0 s, CLS 0, TBT 0 ms. SEO shows 69 only because staging is blocked from indexing, which is correct until cutover. The weddings page and the speakers post scored 97 and 99 locally.

## Fixed in bundle 17

The uplighting page was the one real problem. Its color mixer started a full-frame-rate canvas fade 900 ms after load and ran it forever, off-screen or not, on a 1560 by 960 buffer with stacked blur filters. Lighthouse mobile: performance 29, blocking time 81 seconds. It now paints only when the stage is in view, at about 20 frames a second, pauses off-screen and in background tabs, respects a manual stop, and uses a half-size buffer on phones. After: performance 89, blocking time 0.

Open Graph and Twitter card images were missing on every page; 31 pages now use their own lead photo and the other 47 use a brand card built from the site's logo and fonts. The 38 BlogPosting blocks were missing `image`, the one recommended Article property they lacked, and now carry it.

The homepage Organization block is now Organization plus LocalBusiness with an @id, logo, image, city-level address (Hurst, TX), real coordinates and a 40 mile GeoCircle. The old block had a GeoCoordinates with no coordinates.

`_headers` now noindexes `/dea-concierge/*` (Pages was serving the Worker source and the system prompt as pages) and gives images and video a 30 day cache and fonts a year. `robots.txt` has a Sitemap line. Every sitemap entry has a lastmod.

The 38 posts went through the copy standards for the first time (bundle 16, folded into 17).

## Still open, and needs a decision from Steve

1. **A named author on the posts.** Every post is authored by "Dallas Event Audio" the organization. The 2026 core updates reward a real person with visible experience. The fix is a byline on each post and a Person in the BlogPosting schema pointing at /our-story. I need the name to use (Steve, plus surname or not) and one sentence of bio.

2. **The Wix-era posts as a group.** 30 of the 38 posts are 1,100 to 1,300 words each, mention Dallas or Fort Worth four to six times, and read as general AV advice that could sit on any AV company's blog. The copy pass took the AI vocabulary out; it cannot add first-hand experience. None is thin, none is programmatic, and the domain is not at scaled-content risk, but they are not helping either. The eight posts written this year from real jobs and real data (the speakers-per-guest-count post, the cost post, the DV12 post, the fog post, the projector and uplighting posts, the ALR screen post, the plane post) are the model. Recommendation: leave the 30 indexed for now, and as each one comes up for a refresh, rewrite it around one real DFW job or fold it into the service page it shadows. Do not bulk-delete; several carry impressions.

3. **AI crawlers at go-live.** The staging `Disallow: /` comes out at cutover. Decide then whether GPTBot, ClaudeBot, PerplexityBot and Google-Extended are allowed. Allowing them is what gets the site cited in AI answers, which now sit above the organic results for most of the site's queries; blocking them keeps the copy out of training sets. My recommendation is allow.

4. **The review claim.** The homepage states 4.9 stars from 187 reviews. There is no aggregateRating markup, which is right, but the number should be checkable against Google and Yelp on the day it goes live, and refreshed when it changes.

5. **Street address.** The schema now carries Hurst, TX. If the Google Business Profile shows a street address, the schema should match it exactly; if the profile hides the address (service-area business), city-level is correct as is.

## Cutover checklist (from this review, in addition to the DNS work)

Delete the three staging lines in `_headers` and the `Disallow: /` in `robots.txt` in the same commit as the DNS switch. Remove `#paletteBar` from the chrome fragments. Submit the sitemap in Search Console once the domain resolves to Pages. Leave every Ads final URL untouched; nothing in this review changed a slug. Watch Search Console for two weeks for the 79 redirect rules and for the noindexed `/dea-concierge/` and `/tools/` paths.

## Sources

- [Search Engine Land, Google algorithm updates](https://searchengineland.com/library/platforms/google/google-algorithm-updates)
- [G-Squared Interactive, August 2026 spam update case studies](https://www.gsqi.com/marketing-blog/august-2026-google-spam-update-case-studies/)
- [Dataslayer, Google core updates 2026 timeline and recovery](https://www.dataslayer.ai/blog/google-core-update-december-2025-what-changed-and-how-to-fix-your-rankings)
- [Passionfruit, FAQ rich results deprecated May 2026](https://www.getpassionfruit.com/blog/what-changed-with-google-drops-faq-rich-results-and-what-to-do-now)
- [Digital Applied, structured data after I/O 2026](https://www.digitalapplied.com/blog/structured-data-after-io-2026-schema-updates)
