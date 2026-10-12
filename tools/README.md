# Metricool campaign tooling

Pipeline used for the Oct 2026 Corporate Entrepreneur run. Reusable for any Metricool client.

```
content.json  ->  build.py  ->  out/{id}-{nn}.png  ->  JPG q86 in <YYYY-MM>/  (pushed to this repo)
content.json  ->  make_schedule.py <raw base url>  ->  schedule.json
schedule.json ->  make_payloads.py  ->  payloads.json  ->  Metricool createScheduledPost (one call per entry)
```

- `build.py`: Playwright/Chromium HTML renderer, 1080x1350. Templates: quote (photo/split), cover_bold, bold, photo (split/contain), editorial, editorial_text, call. Rich markup in copy: `*orange*`, `_teal_`, `**bold**`, `~italic~`. Expects `assets/fonts`, `assets/photos`, `assets/logo` next to it. Palette and logo paths are constants at the top; change them per client.
- `content.example.json`: three posts (quote, carousel, call) showing every field.
- `make_schedule.py`: one schedule entry per Metricool call: `-ig` (link in bio + hashtags as first comment), `-fbli` (full URL), `-th` (short text under 500 chars; skipped for `kind: call`). Edit `DOORS` per client.
- `make_payloads.py`: wraps schedule entries in the exact `info` JSON the Metricool MCP tool takes.

Setup: `pip install playwright && playwright install chromium` (or use the preinstalled Chromium), `pip install pillow`.
