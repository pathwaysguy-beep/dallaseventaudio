# tools/

Build tooling for the site, living inside the repo on purpose.

Everything here used to run out of a scratch directory in a cloud session. When
that session was reclaimed the scripts went with it, and the fragments they
depended on had to be recovered from the built pages. In the repo they are
versioned, they travel with a clone, and they survive any session ending.

Nothing here runs at deploy time. Cloudflare Pages still builds nothing: it
serves these files as they are. These are the scripts you run *before* a commit.

## sync_chrome.py

Brings all 40 pages up to the current shared chrome: header, mobile drawer, and
the bottom-left palette dock.

```
python tools/sync_chrome.py            # sync every page
python tools/sync_chrome.py --check    # report drift, change nothing, exit 1
```

Run it after editing anything in `chrome/`, and run `--check` before a commit if
you have hand-edited a page's `<style>` block.

It is idempotent: running it twice produces identical bytes. That is what makes
it safe to run habitually, and it is asserted rather than assumed.

Two behaviours worth knowing, because both were bugs first:

**Rules scoped under a body class are left alone.** `body.calm #paletteBar` on
`/sensory-friendly-event-services` is a deliberate override, not stale chrome.
Without the exemption the whole selector list gets dropped and the page loses
its chat-bubble, grain-overlay and marquee suppression too.

**Do not write literal HTML tags inside CSS comments.** The script anchors the
header on the real `<body>` after `</head>`, but a comment reading
`One class, on <body>` still confuses the tag-balance assertions. Write it in
words.

## image_gaps.py

Lists every image slot the pages declare that has no file in `/images`, with the
alt text already written for it.

```
python tools/image_gaps.py           # grouped report
python tools/image_gaps.py --csv     # for a spreadsheet
```

As of 23 Aug 2026: 71 photos live, 114 slots still empty.

## chrome/

The canonical shared chrome. These six files are the source of truth.

| file | what it is |
|---|---|
| `header.html` | desktop header and dropdown nav |
| `drawer.html` | mobile nav drawer |
| `palette.html` | bottom-left palette dock |
| `chrome.css` | all CSS for the three above |
| `palette_js.html` | palette dock behaviour, remembers the choice per visitor |
| `navdrawer_js.html` | drawer open/close, Escape, dropdown keyboard support |

Recovered from `rent-uplighting/index.html` on 23 Aug 2026 and verified: running
`sync_chrome.py` against the live site with these fragments changes zero bytes
across all 40 pages, which proves they are the exact set that built it.

If they are ever lost again, recover them the same way. Every built page carries
the entire chrome verbatim: the markup right after `<body>`, the CSS between
`<!-- chrome-sync:css -->` and its `</style>`, and both scripts after
`<!-- chrome-sync:js -->`. The site is its own backup.
