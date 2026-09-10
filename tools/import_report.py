#!/usr/bin/env python3
"""Import one weekly report into the site.

Claude-Artifact HTML arrives as a fragment: it starts with <title>/<link>/<style>
and has no <!doctype>, so a browser opening the raw file falls into quirks mode
and renders it differently than it was designed. This wraps the fragment in a
real document, files it under reports/, registers it in reports.json, and
rebuilds index.html.

    python3 tools/import_report.py path/to/report.html \
        --date 2026-09-16 --title "Knee, Rope, Backpack" \
        --eyebrow "Real-world RL - MuJoCo as the real world" \
        --summary "One or two sentences for the landing page." \
        --tags "Booster T1,flow policy"
"""

import argparse
import json
import pathlib
import re
import subprocess
import sys
from datetime import date

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Mirrors the reset the Artifact runtime puts around a published page, so a
# fragment authored there looks the same when served as a standalone file.
RESET = """
:root { color-scheme: light; }
body { margin: 0; font: 14px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI",
       Roboto, Helvetica, Arial, sans-serif; background: #fbfbfa; }
img { max-width: 100%; }
[hidden] { display: none !important; }
"""


def slugify(text):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s or "report"


def wrap(fragment, title):
    """Split an artifact fragment into head/body and build a full document."""
    if re.match(r"\s*<!doctype", fragment, re.I):
        return fragment

    # Everything before the first layout element is head material
    # (<title>, <link>, <style>); the rest is the page body.
    m = re.search(r"<(div|main|section|header|article|nav|body)\b", fragment, re.I)
    split = m.start() if m else 0
    head_src, body_src = fragment[:split], fragment[split:]

    got_title = re.search(r"<title>(.*?)</title>", head_src, re.I | re.S)
    if not got_title:
        head_src = "<title>%s</title>\n" % title + head_src

    return (
        "<!doctype html>\n<html lang=\"en\">\n<head>\n"
        "<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        "<style>%s</style>\n" % RESET
        + head_src.strip()
        + "\n</head>\n<body>\n"
        + body_src.strip()
        + "\n</body>\n</html>\n"
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src", help="source .html (a Claude Artifact export is fine)")
    ap.add_argument("--title", required=True)
    ap.add_argument("--date", default=date.today().isoformat(), help="YYYY-MM-DD")
    ap.add_argument("--eyebrow", default="")
    ap.add_argument("--summary", default="")
    ap.add_argument("--tags", default="", help="comma-separated")
    ap.add_argument("--slug", default="", help="defaults to a slug of the title")
    ap.add_argument("--force", action="store_true", help="overwrite an existing entry")
    args = ap.parse_args()

    date.fromisoformat(args.date)  # reject a malformed date before writing anything

    slug = args.slug or slugify(args.title)
    rel = "reports/%s-%s.html" % (args.date, slug)
    dest = ROOT / rel

    manifest = json.loads((ROOT / "reports.json").read_text(encoding="utf-8"))
    existing = [r for r in manifest["reports"] if r["file"] == rel]
    if (dest.exists() or existing) and not args.force:
        sys.exit("%s already exists; pass --force to replace it, or change --slug" % rel)

    dest.write_text(wrap(pathlib.Path(args.src).read_text(encoding="utf-8"),
                         args.title), encoding="utf-8")

    entry = {
        "file": rel,
        "date": args.date,
        "title": args.title,
        "eyebrow": args.eyebrow,
        "summary": args.summary,
        "tags": [t.strip() for t in args.tags.split(",") if t.strip()],
    }
    manifest["reports"] = [r for r in manifest["reports"] if r["file"] != rel] + [entry]
    (ROOT / "reports.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print("wrote %s (%.1f MB)" % (rel, dest.stat().st_size / 1e6))
    subprocess.run([sys.executable, str(ROOT / "tools" / "build_index.py")], check=True)


if __name__ == "__main__":
    main()
