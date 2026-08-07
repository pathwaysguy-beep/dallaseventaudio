# dallaseventaudio.com — staging build

Static site. No build step, no dependencies. Every page is a finished HTML file
at the exact slug it will live on, so what you click here is what visitors get.

**This is staging, not production.** 39 of the site's 77 URLs are rebuilt.
`robots.txt` disallows everything and `_headers` sends `X-Robots-Tag: noindex`,
so this preview cannot compete with the live Wix site for the same URLs. Both
come off at go-live and not before.

## Connect it to Cloudflare Pages

Once, in the browser. No tokens, no command line.

1. Push this folder to a new GitHub repo.
2. Cloudflare dashboard → **Workers & Pages** → **Create** → **Pages** →
   **Connect to Git**, pick the repo.
3. Build settings:
   - Framework preset: **None**
   - Build command: **leave empty**
   - Build output directory: **/**
4. Save and deploy.

Every `git push` to `main` publishes after that, and every pull request gets its
own preview URL. Nothing to run locally.

### On tokens

The Git integration uses OAuth and needs no API token. If you later want a job to
deploy without GitHub, that path uses Wrangler and a Cloudflare API token with
the **Cloudflare Pages: Edit** permission. Create it yourself in the Cloudflare
dashboard and put it in the repo's **Settings → Secrets and variables → Actions**.
Never paste a token into chat.

## Layout

```
index.html                    /
contact/index.html            /contact
...
images/                       AVIF + WebP + JPEG at four widths
fonts/                        self-hosted Unbounded and Space Grotesk
_headers                      caching + the staging noindex
_redirects                    301s for retired Wix URLs
404.html                      anything not rebuilt yet
_pages.json                   which draft each page came from
```

## Still missing

Real pages not yet rebuilt: `/blog`, `/photography-videography`,
`/rent-lighting-equipment`, and 37 posts under `/post/`. Links to them resolve
to `404.html` in staging.

`/rent-photobooth`, `/rent-pa-speakers-lighting-video` and
`/corporate-event-av-rental` are retired and already have 301s in `_redirects`.

119 image slots have no photo yet. They render as empty boxes, not broken icons.

## Before this becomes the real site

- [ ] Rebuild `/blog`, the 37 posts, `/photography-videography`,
      `/rent-lighting-equipment`.
- [ ] Fill the 119 empty image slots, or remove the slots.
- [ ] Delete the staging block from `_headers` and replace `robots.txt`.
- [ ] Add `sitemap.xml`, and leave `/thank-you` out of it.
- [ ] Upload `llms.txt`.
- [x] Palette switcher stays. It is a live feature, not a review tool: the
      bottom-left pill on all 40 pages, with the choice remembered per visitor.
- [ ] Confirm `form_submit_thankyou` fires on the real domain. The Google Ads
      conversion is a GA4 import and that event is the number that moves.
- [ ] Check all 77 URLs resolve before switching DNS.
