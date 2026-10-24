#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the sitemap index and one sitemap per page type from the files in site/.

Usage: python3 tools/build_sitemap.py

Writes site/sitemap.xml (a sitemapindex) and
  site/sitemap-pages.xml         home, services, pricing, audit, about, contact, search
  site/sitemap-guides.xml        the evergreen guides and answer pages
  site/sitemap-blog.xml          /blog/ and every article
  site/sitemap-case-studies.xml  /case-studies/ and every case study

Peec action "Split the sitemap by page type" (2026-09-14). Replaces the old flat file,
which had grown duplicate entries because the blog publisher appended on every run.
lastmod is the last commit date of the file; a file with uncommitted changes gets today.
publish_article.py calls build() after writing a post, so the weekly automation keeps
the split sitemaps current without any extra step.
"""
import datetime
import io
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SITE_DIR = os.path.join(ROOT, "site")
sys.path.insert(0, HERE)
import _parts  # noqa: E402

SITE = _parts.SITE
GUIDES = {"what-is-geo", "geo-vs-seo", "reddit-marketing-2026", "geo-agencies-compared",
          "ai-visibility-checklist"}
SKIP = {"404.html"}


def lastmod(path):
    rel = os.path.relpath(path, ROOT)
    try:
        dirty = subprocess.run(["git", "status", "--porcelain", "--", rel], cwd=ROOT,
                               capture_output=True, text=True, timeout=20).stdout.strip()
        if dirty:
            return datetime.date.today().isoformat()
        out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", rel], cwd=ROOT,
                             capture_output=True, text=True, timeout=20).stdout.strip()
        if out:
            return out
    except Exception:
        pass
    return datetime.date.fromtimestamp(os.path.getmtime(path)).isoformat()


def classify(url_path):
    """url_path like '/blog/x/' -> sitemap name."""
    parts = [p for p in url_path.split("/") if p]
    if not parts:
        return "pages"
    if parts[0] == "blog":
        return "blog"
    if parts[0] == "case-studies":
        return "case-studies"
    if parts[0] in GUIDES or parts[0] == "answers" or is_answer(parts[0]):
        return "guides"
    return "pages"


def is_answer(slug):
    """Answer pages built by tools/build_answers.py carry a marker file."""
    return os.path.exists(os.path.join(SITE_DIR, slug, ".answer"))


def collect():
    groups = {"pages": [], "guides": [], "blog": [], "case-studies": []}
    for dirpath, dirs, files in os.walk(SITE_DIR):
        dirs[:] = [d for d in dirs if d not in ("assets", "functions")]
        for name in files:
            if name != "index.html":
                continue
            path = os.path.join(dirpath, name)
            rel = os.path.relpath(dirpath, SITE_DIR).replace(os.sep, "/")
            url_path = "/" if rel == "." else "/%s/" % rel
            if "noindex" in io.open(path, encoding="utf-8").read(4000):
                continue
            groups[classify(url_path)].append((SITE + url_path, lastmod(path)))
    for g in groups.values():
        g.sort(key=lambda t: (t[0].count("/"), t[0]))
    return groups


def xml_urlset(rows):
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, mod in rows:
        out.append("  <url><loc>%s</loc><lastmod>%s</lastmod></url>" % (loc, mod))
    out.append("</urlset>\n")
    return "\n".join(out)


def build():
    groups = collect()
    index = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for name in ("pages", "guides", "blog", "case-studies"):
        rows = groups[name]
        if not rows:
            continue
        fname = "sitemap-%s.xml" % name
        with io.open(os.path.join(SITE_DIR, fname), "w", encoding="utf-8") as fh:
            fh.write(xml_urlset(rows))
        newest = max(m for _l, m in rows)
        index.append("  <sitemap><loc>%s/%s</loc><lastmod>%s</lastmod></sitemap>" % (SITE, fname, newest))
    index.append("</sitemapindex>\n")
    with io.open(os.path.join(SITE_DIR, "sitemap.xml"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(index))
    return groups


def main():
    groups = build()
    for name in ("pages", "guides", "blog", "case-studies"):
        print("sitemap-%s.xml: %d urls" % (name, len(groups[name])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
