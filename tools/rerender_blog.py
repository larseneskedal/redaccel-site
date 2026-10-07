#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Re-render every published blog article and the /blog/ hub with the current templates.

Usage: python3 tools/rerender_blog.py

Use after a template or design change. It changes no dates, no sitemap, no llms.txt and
no queue: dates come from tools/articles.json, content from articles/<slug>.json.
It does not commit.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import publish_article as pa  # noqa: E402


def main():
    index = pa.load_json(pa.INDEX_PATH, {"articles": []})
    for entry in index["articles"]:
        src = os.path.join(pa.ROOT, "articles", "%s.json" % entry["slug"])
        a = pa.load_json(src)
        if not a:
            print("skip %s: no articles/%s.json" % (entry["slug"], entry["slug"]))
            continue
        a["date_published"] = entry["date_published"]
        a["date_modified"] = entry["date_modified"]
        a["read_minutes"] = entry["read_minutes"]
        a.setdefault("card_title", entry.get("card_title") or a.get("h1", ""))
        pa.write(os.path.join(pa.SITE_DIR, "blog", entry["slug"], "index.html"), pa.render_article(a))
        print("rendered /blog/%s/" % entry["slug"])
    pa.write(os.path.join(pa.SITE_DIR, "blog", "index.html"), pa.render_hub(index["articles"]))
    print("rendered /blog/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
