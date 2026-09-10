#!/usr/bin/env python3
"""Regenerate index.html from reports.json.

Single source of truth is reports.json; index.html is generated output and
should never be hand-edited. Usage, from the repo root:

    python3 tools/build_index.py
"""

import html
import json
import pathlib
import sys
from datetime import date

ROOT = pathlib.Path(__file__).resolve().parent.parent

CSS = """
:root {
  color-scheme: light;
  --ground: #f6f7f8;
  --panel: #ffffff;
  --panel-2: #f0f2f4;
  --ink: #12161a;
  --ink-2: #525c66;
  --ink-3: #767f89;
  --rule: #dee2e7;
  --rule-strong: #c4ccd3;
  --accent: #2a78d6;
  --shadow: 0 1px 2px rgba(18,22,26,.06), 0 8px 24px rgba(18,22,26,.05);
  --shadow-lift: 0 2px 4px rgba(18,22,26,.08), 0 14px 32px rgba(18,22,26,.10);
  --f-disp: "IBM Plex Sans Condensed", "Helvetica Neue", Arial, sans-serif;
  --f-body: "IBM Plex Sans", "Helvetica Neue", Arial, sans-serif;
  --f-mono: "IBM Plex Mono", ui-monospace, "SF Mono", Menlo, monospace;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    color-scheme: dark;
    --ground: #16191c;
    --panel: #1d2126;
    --panel-2: #24292f;
    --ink: #f1f3f5;
    --ink-2: #a6afb8;
    --ink-3: #7c858e;
    --rule: #2c3238;
    --rule-strong: #3d454d;
    --accent: #3987e5;
    --shadow: 0 1px 2px rgba(0,0,0,.35), 0 8px 24px rgba(0,0,0,.28);
    --shadow-lift: 0 2px 4px rgba(0,0,0,.40), 0 14px 32px rgba(0,0,0,.34);
  }
}
:root[data-theme="dark"] {
  color-scheme: dark;
  --ground: #16191c;
  --panel: #1d2126;
  --panel-2: #24292f;
  --ink: #f1f3f5;
  --ink-2: #a6afb8;
  --ink-3: #7c858e;
  --rule: #2c3238;
  --rule-strong: #3d454d;
  --accent: #3987e5;
  --shadow: 0 1px 2px rgba(0,0,0,.35), 0 8px 24px rgba(0,0,0,.28);
  --shadow-lift: 0 2px 4px rgba(0,0,0,.40), 0 14px 32px rgba(0,0,0,.34);
}

* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--ground);
  color: var(--ink);
  font-family: var(--f-body);
  font-size: 15px;
  line-height: 1.55;
  -webkit-font-smoothing: antialiased;
}
.wrap {
  max-width: 880px;
  margin: 0 auto;
  padding-inline: 24px;
  padding-block: 64px 96px;
}

header { border-bottom: 1px solid var(--rule); padding-bottom: 28px; margin-bottom: 8px; }
.mark {
  font-family: var(--f-disp);
  font-weight: 700;
  font-size: clamp(40px, 9vw, 58px);
  letter-spacing: .04em;
  line-height: 1;
  margin: 0;
}
.tagline {
  margin: 12px 0 0;
  color: var(--ink-2);
  font-size: 15px;
}
.count {
  margin: 18px 0 0;
  font-family: var(--f-mono);
  font-size: 12px;
  letter-spacing: .06em;
  text-transform: uppercase;
  color: var(--ink-3);
}

.feed { list-style: none; margin: 0; padding: 0; }
.year {
  font-family: var(--f-mono);
  font-size: 12px;
  letter-spacing: .12em;
  color: var(--ink-3);
  padding: 36px 0 12px;
}
.entry { margin-top: 20px; }

.card {
  display: grid;
  grid-template-columns: 96px 1fr;
  gap: 24px;
  padding: 22px 24px;
  background: var(--panel);
  border: 1px solid var(--rule);
  border-radius: 10px;
  box-shadow: var(--shadow);
  color: inherit;
  text-decoration: none;
  transition: box-shadow .16s ease, border-color .16s ease, transform .16s ease;
}
.card:hover {
  border-color: var(--rule-strong);
  box-shadow: var(--shadow-lift);
  transform: translateY(-1px);
}
.card:focus-visible { outline: 2px solid var(--accent); outline-offset: 3px; }

.when { font-family: var(--f-mono); font-size: 12.5px; color: var(--ink-3); padding-top: 4px; }
.when .d { display: block; color: var(--ink-2); font-weight: 500; }

.eyebrow {
  font-family: var(--f-mono);
  font-size: 11.5px;
  letter-spacing: .05em;
  text-transform: uppercase;
  color: var(--accent);
  margin: 0 0 6px;
}
.card h2 {
  font-family: var(--f-disp);
  font-weight: 600;
  font-size: 24px;
  line-height: 1.2;
  margin: 0;
}
.summary { margin: 8px 0 0; color: var(--ink-2); font-size: 14.5px; }
.tags { list-style: none; display: flex; flex-wrap: wrap; gap: 6px; margin: 14px 0 0; padding: 0; }
.tags li {
  font-family: var(--f-mono);
  font-size: 11px;
  letter-spacing: .02em;
  color: var(--ink-3);
  background: var(--panel-2);
  border: 1px solid var(--rule);
  border-radius: 999px;
  padding: 2px 9px;
}

.empty {
  margin-top: 32px;
  padding: 32px 24px;
  border: 1px dashed var(--rule-strong);
  border-radius: 10px;
  color: var(--ink-3);
  text-align: center;
}

footer {
  margin-top: 64px;
  padding-top: 24px;
  border-top: 1px solid var(--rule);
  font-family: var(--f-mono);
  font-size: 11.5px;
  color: var(--ink-3);
  display: flex;
  flex-wrap: wrap;
  gap: 8px 20px;
  justify-content: space-between;
}
footer a { color: var(--ink-3); }

@media (max-width: 640px) {
  .wrap { padding-block: 44px 64px; }
  .card { grid-template-columns: 1fr; gap: 10px; padding: 20px; }
  .when { padding-top: 0; }
  .when .d { display: inline; }
  .card h2 { font-size: 21px; }
}
"""

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def parse_date(s):
    y, m, d = (int(p) for p in s.split("-"))
    return date(y, m, d)


def esc(s):
    return html.escape(str(s), quote=True)


def render_entry(r):
    when = parse_date(r["date"])
    out = ['  <li class="entry">']
    out.append('    <a class="card" href="%s">' % esc(r["file"]))
    out.append('      <div class="when"><span class="d">%s %d</span>%d</div>'
               % (MONTHS[when.month - 1], when.day, when.year))
    out.append('      <div class="body">')
    if r.get("eyebrow"):
        out.append('        <p class="eyebrow">%s</p>' % esc(r["eyebrow"]))
    out.append('        <h2>%s</h2>' % esc(r["title"]))
    if r.get("summary"):
        out.append('        <p class="summary">%s</p>' % esc(r["summary"]))
    if r.get("tags"):
        tags = "".join("<li>%s</li>" % esc(t) for t in r["tags"])
        out.append('        <ul class="tags">%s</ul>' % tags)
    out.append('      </div>')
    out.append('    </a>')
    out.append('  </li>')
    return out


def build(manifest):
    site = manifest.get("site", {})
    title = site.get("title", "GAOI")
    reports = sorted(manifest.get("reports", []),
                     key=lambda r: parse_date(r["date"]), reverse=True)

    lines = [
        "<!doctype html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>%s</title>" % esc(title),
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
        'family=IBM+Plex+Sans+Condensed:wght@600;700'
        '&family=IBM+Plex+Sans:wght@400;500;600'
        '&family=IBM+Plex+Mono:wght@400;500&display=swap">',
        "<style>%s</style>" % CSS,
        "</head>",
        "<body>",
        '<div class="wrap">',
        "  <header>",
        '    <h1 class="mark">%s</h1>' % esc(title),
    ]
    if site.get("tagline"):
        lines.append('    <p class="tagline">%s</p>' % esc(site["tagline"]))
    if reports:
        newest = parse_date(reports[0]["date"])
        lines.append('    <p class="count">%d report%s · latest %s %d, %d</p>'
                     % (len(reports), "" if len(reports) == 1 else "s",
                        MONTHS[newest.month - 1], newest.day, newest.year))
    lines.append("  </header>")

    if not reports:
        lines.append('  <p class="empty">No reports yet.</p>')
    else:
        lines.append('  <ol class="feed">')
        year = None
        for r in reports:
            y = parse_date(r["date"]).year
            if y != year:
                lines.append('  <li class="year" aria-hidden="true">%d</li>' % y)
                year = y
            lines.extend(render_entry(r))
        lines.append("  </ol>")

    lines.append("  <footer>")
    lines.append('    <span>Generated from reports.json by tools/build_index.py</span>')
    lines.append('    <a href="https://github.com/HAOFU9003/GAOI">github.com/HAOFU9003/GAOI</a>')
    lines.append("  </footer>")
    lines.append("</div>")
    lines.append("</body>")
    lines.append("</html>")
    return "\n".join(lines) + "\n"


def main():
    manifest = json.loads((ROOT / "reports.json").read_text(encoding="utf-8"))
    missing = [r["file"] for r in manifest.get("reports", [])
               if not (ROOT / r["file"]).exists()]
    if missing:
        sys.exit("reports.json points at files that do not exist: %s"
                 % ", ".join(missing))
    (ROOT / "index.html").write_text(build(manifest), encoding="utf-8")
    print("index.html: %d report(s)" % len(manifest.get("reports", [])))


if __name__ == "__main__":
    main()
