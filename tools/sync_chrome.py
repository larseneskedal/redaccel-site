#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Stamp the shared head assets, header and footer from tools/_parts.py into every page.

Usage: python3 tools/sync_chrome.py [--check]

Hand-written pages keep their own <title>, meta, JSON-LD and <main>. This script only
rewrites the parts every page shares, so a nav or footer change is one edit in _parts.py
plus one run of this script. Idempotent. --check exits 1 if any page would change.
"""
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SITE_DIR = os.path.join(ROOT, "site")
sys.path.insert(0, HERE)
import _parts  # noqa: E402

ASSET_LINE = re.compile(
    r'^\s*(<link rel="icon"|<link rel="apple-touch-icon"|<link rel="preconnect" href="https://fonts\.gstatic\.com"'
    r'|<link rel="stylesheet" href="/assets/css/|<script defer src="/assets/js/main\.js'
    r'|<meta name="theme-color"|<link rel="preload" href="/assets/fonts/)[^\n]*\n', re.M)
HEADER_RE = re.compile(r'<a class="skip-link".*?</header>', re.S)
FOOTER_RE = re.compile(r'<footer class="site-footer">.*?</footer>', re.S)
UPDATED_RE = re.compile(r'<span>Updated ([A-Z][a-z]+ \d{4})</span>')


def active_for(rel):
    """site-relative path of the html file -> the nav href to mark current."""
    parts = rel.replace(os.sep, "/").split("/")
    if len(parts) < 2:
        return ""
    return "/%s/" % parts[0]


def stamp(html, rel):
    out = ASSET_LINE.sub("", html)
    out = out.replace('<meta name="viewport" content="width=device-width, initial-scale=1">\n',
                      '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
                      + _parts.HEAD_ASSETS + "\n", 1)
    if 'property="og:url"' in out and 'property="og:image"' not in out:
        out = re.sub(r'(<meta property="og:url"[^>]*>\n)',
                     r'\1<meta property="og:image" content="%s/assets/img/og.png">\n'
                     r'<meta name="twitter:card" content="summary_large_image">\n' % _parts.SITE, out, count=1)
    out = HEADER_RE.sub(lambda _m: _parts.header(active_for(rel)), out, count=1)
    m = FOOTER_RE.search(out)
    if m:
        um = UPDATED_RE.search(m.group(0))
        updated = um.group(1) if um else "October 2026"
        out = out[:m.start()] + _parts.FOOTER.format(updated=updated) + out[m.end():]
    return out


def main(argv):
    check = "--check" in argv
    changed = []
    for dirpath, _dirs, files in os.walk(SITE_DIR):
        if os.sep + "functions" in dirpath:
            continue
        for name in files:
            if not name.endswith(".html"):
                continue
            path = os.path.join(dirpath, name)
            rel = os.path.relpath(path, SITE_DIR)
            with io.open(path, encoding="utf-8") as fh:
                html = fh.read()
            new = stamp(html, rel)
            if new != html:
                changed.append(rel)
                if not check:
                    with io.open(path, "w", encoding="utf-8") as fh:
                        fh.write(new)
    for rel in sorted(changed):
        print(("would update " if check else "updated ") + rel)
    return 1 if (check and changed) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
