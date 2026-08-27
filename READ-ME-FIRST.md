# The positive-copy pass

41 pages. Two changes folded into one commit: the denial chains are gone, and
the phrase "customer pickup" is retired in favor of saying what is included.

**PowerShell**
```
Expand-Archive -Path $env:USERPROFILE\Downloads\dea-positive.zip -DestinationPath $env:USERPROFILE\Downloads\dea-positive -Force
Copy-Item "$env:USERPROFILE\Downloads\dea-positive\*" -Destination C:\DEA\ -Recurse -Force

cd C:\DEA
python tools\sync_chrome.py --check
git add -A
git commit -m "copy: say what is included, everywhere"
git push
```

`--check` must report **0 of 79 files drifted**. Nothing here touches the shared
chrome, so no re-sync is needed; if it reports drift, stop.

The full before-and-after is the review page, which is read straight from the
working tree rather than from a list kept by hand, so it is exactly what this
commit contains.

## Verified

- Keyword coverage held on all 41 pages. The only SEO gate failures are two blog
  post titles that were over length before any of this and are on the existing
  list.
- Every JSON-LD block parses, and every FAQ question in schema still matches the
  visible question on the page. Fourteen FAQ questions were reworded, so both
  copies moved together.
- `sync_chrome.py --check`: 0 of 79 drifted.
- Fourteen pages rendered at 1440 and 390 pixels: no overflow, no script errors.
- Search Console, sixteen months: pickup and self-service queries total **one
  impression**. Retiring the phrase costs nothing.
