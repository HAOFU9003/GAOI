# GAOI

Weekly experiment reports, published as a static site with GitHub Pages:

**https://haofu9003.github.io/GAOI/**

Each report is one self-contained HTML file under `reports/` — plots, tables and
videos are inlined, so a report needs no assets and keeps working forever, even
if the code that produced it moves on.

## Layout

```
index.html      generated landing page  — do not edit by hand
reports.json    the manifest; single source of truth for the landing page
reports/        one HTML file per report, named <date>-<slug>.html
tools/          import_report.py, build_index.py
.nojekyll       serve files verbatim; skip Jekyll processing
```

## Adding this week's report

From the repo root:

```bash
python3 tools/import_report.py ~/path/to/report.html \
    --date 2026-09-16 \
    --title "This week's title" \
    --eyebrow "Project · one-line context" \
    --summary "One or two sentences shown on the landing page." \
    --tags "Booster T1,flow policy"

git add -A && git commit -m "report: this week's title" && git push
```

Pages redeploys on push; the new page is live in under a minute.

`import_report.py` wraps the source file in a real `<!doctype html>` document.
Claude Artifact exports start straight at `<title>`, and a browser opening such
a fragment falls into quirks mode and renders it differently than it was
designed — the wrapper reproduces the head and reset the Artifact runtime
supplied. It then registers the report in `reports.json` and regenerates
`index.html`.

To change a title, summary or tag after the fact, edit `reports.json` and run
`python3 tools/build_index.py`.

## Size

Reports with inlined video run a few MB each. Git keeps every version forever,
so at roughly one 3 MB report a week the repo grows about 150 MB a year. When
clones start to drag, the fix is to stop inlining video: upload the mp4s as
release assets and point the report at their URLs.
