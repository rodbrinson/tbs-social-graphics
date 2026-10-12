# Metricool campaign tooling (brand-aware)

One repo, many brands. Each client lives in `brands/<slug>/`:

```
brands/<slug>/
  brand.json          palette, fonts, logo, Metricool ids, doors, voice rules, defaults
  logo-on-dark.png    logo-on-light.png
  photos/             the client's photos (keep this small in git; big shoots stay on Rod's Mac or Drive)
  content.json        the campaign's posts
  out/                rendered PNGs (ignored by git)
  2026-10/            exported JPGs that Metricool pulls (committed)
  schedule.json, payloads.json
```

Copy `brands/_template/` to start a new client. Fill `brand.json` from the client's brand guide. Fonts must exist as woff2 in `tools/assets/fonts` (download from fontsource) and be listed in `font_files`.

Pipeline:

```
python3 tools/build.py --brand brands/<slug> [post ids]      # content.json -> out/*.png
# export JPGs: PIL convert('RGB').save(quality=86) into brands/<slug>/<YYYY-MM>/ ; git push
python3 tools/make_schedule.py brands/<slug> <YYYY-MM>        # -> schedule.json (-ig / -fbli / -th per post, only networks in brand.json)
python3 tools/make_payloads.py brands/<slug> [--skip ids]     # -> payloads.json (info strings for the Metricool MCP createScheduledPost tool)
```

Then one `createScheduledPost(blogId, date, info)` call per payload. Verify with `getScheduledPosts` in 1 to 2 day windows.

- `build.py` templates: quote (photo/split), cover_bold, bold, photo (split/contain), editorial, editorial_text, call. Rich markup in copy: `*cta color*`, `_accent color_`, `**bold**`, `~italic~`.
- Palette roles in brand.json: `dark` (main background), `light` (alt background and text on dark), `accent` (flow line, accent words), `cta` (orange-role: badges, progress marker, CTA words), `white`, `ink`.
- Font roles: `display` (condensed caps headline stack), `serif` (editorial), `body`.
- `campaign.md` in `brands/_template/` is the brief a client drops into their connected folder alongside a `photos/` folder.

Setup: `pip install playwright pillow && playwright install chromium` (or use a preinstalled Chromium).
