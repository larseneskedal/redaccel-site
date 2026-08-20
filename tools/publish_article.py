#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render one article JSON into a live page on redaccel.com and update every index.

Usage:
    python3 tools/publish_article.py articles/<slug>.json [--no-git] [--dry-run]

Everything mechanical lives here so the weekly writing session only has to
produce good, sourced prose. Rerunning with the same slug updates the page
in place (dateModified bumps, datePublished is preserved).
"""
import io
import json
import os
import re
import subprocess
import sys
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SITE_DIR = os.path.join(ROOT, "site")
sys.path.insert(0, HERE)
import _parts  # noqa: E402

SITE = _parts.SITE
INDEX_PATH = os.path.join(HERE, "articles.json")
QUEUE_PATH = os.path.join(HERE, "topic_queue.json")

REQUIRED = ["slug", "keyword", "title", "meta_description", "h1",
            "card_summary", "extract_html", "body_html", "faq", "sources"]

MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]


def read(path):
    with io.open(path, encoding="utf-8") as fh:
        return fh.read()


def write(path, text):
    d = os.path.dirname(path)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    with io.open(path, "w", encoding="utf-8") as fh:
        fh.write(text)


def load_json(path, default=None):
    if not os.path.exists(path):
        return default
    return json.loads(read(path))


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


def strip_tags(s):
    return re.sub(r"<[^>]+>", "", s)


def json_text(s):
    """Plain text safe to drop inside a JSON-LD string value."""
    return json.dumps(strip_tags(s).strip())[1:-1]


def pretty_date(iso):
    y, m, d = [int(x) for x in iso.split("-")]
    return "%s %d, %d" % (MONTHS[m - 1], d, y)


def month_year(iso):
    y, m, _ = [int(x) for x in iso.split("-")]
    return "%s %d" % (MONTHS[m - 1], y)


# --------------------------------------------------------------------------
# validation
# --------------------------------------------------------------------------

def validate(a):
    errs = []
    for key in REQUIRED:
        if not a.get(key):
            errs.append("missing required field: %s" % key)
    slug = a.get("slug", "")
    if slug and not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug):
        errs.append("slug must be lowercase-hyphenated: %r" % slug)
    if len(a.get("meta_description", "")) > 165:
        errs.append("meta_description is %d chars, keep it under 165"
                    % len(a["meta_description"]))
    if len(a.get("title", "")) > 65:
        errs.append("title is %d chars, keep it under 65" % len(a["title"]))
    if "<script" in a.get("body_html", "").lower():
        errs.append("body_html must not contain <script>")
    if len(a.get("sources", [])) < 3:
        errs.append("at least 3 sources required — every stat needs one")
    if len(a.get("faq", [])) < 3:
        errs.append("at least 3 FAQ entries required (they feed FAQPage schema)")
    # every [n] footnote marker in the body must resolve to a source id
    ids = set()
    for i, _s in enumerate(a.get("sources", []), 1):
        ids.add("src-%d" % i)
    for ref in re.findall(r'href="#(src-\d+)"', a.get("body_html", "") + a.get("extract_html", "")):
        if ref not in ids:
            errs.append("body cites %s but there is no such source" % ref)
    prose = a.get("body_html", "") + a.get("extract_html", "") + a.get("meta_description", "") + a.get("h1", "")
    if u"\u2014" in prose:
        errs.append("em dash found in copy. House rule: no em dashes. Use a comma, colon or full stop.")
    if re.search(r"\bstuff\b", prose, re.I):
        errs.append("the word 'stuff' is banned in Redaccel copy")
    for tell in ["delve", "in today's fast-paced", "it's important to note",
                 "unlock the power", "in conclusion", "game-changer", "leverage the power"]:
        if tell in prose.lower():
            errs.append("AI tell found in copy: %r" % tell)
    words = len(strip_tags(a.get("body_html", "")).split())
    if words < 700:
        errs.append("body is only %d words — target 1,100–1,800" % words)
    return errs


# --------------------------------------------------------------------------
# rendering
# --------------------------------------------------------------------------

ARTICLE_TMPL = u"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{meta_description}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{og_title}">
<meta property="og:description" content="{og_description}">
<meta property="og:type" content="article">
<meta property="og:url" content="{url}">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="/assets/css/main.css">
<script defer src="/assets/js/main.js"></script>
<script type="application/ld+json">
{jsonld}
</script>
</head>
<body>
{header}

<main id="main" class="article">
  <div class="shell">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="/">redaccel.com</a> / <a href="/blog/">blog</a> / {slug}</nav>
    <h1>{h1}</h1>
    <span class="dateline"><span class="flag">{dateline_flag}</span> {read_minutes} min read</span>

    <div class="extract">
      <div class="extract-chip"><span class="tag">Extract</span> <span>{extract_chip}</span></div>
{extract_html}
    </div>

{body_html}

    <h2>Frequently asked</h2>
    <div class="faq-list">
{faq_html}
    </div>

    <details class="sources">
      <summary>Sources</summary>
      <ol>
{sources_html}
      </ol>
    </details>

{cta}
  </div>
</main>

{footer}
</body>
</html>
"""


def build_jsonld(a, url):
    faq = []
    for item in a["faq"]:
        faq.append({
            "@type": "Question",
            "name": strip_tags(item["q"]).strip(),
            "acceptedAnswer": {"@type": "Answer",
                               "text": strip_tags(item["a"]).strip()},
        })
    graph = [
        {
            "@type": "Article",
            "headline": a["h1"],
            "description": a.get("schema_description") or a["meta_description"],
            "author": {"@type": "Organization", "name": "Redaccel",
                       "@id": SITE + "/#org"},
            "publisher": {"@id": SITE + "/#org"},
            "datePublished": a["date_published"],
            "dateModified": a["date_modified"],
            "mainEntityOfPage": url,
            "about": a["keyword"],
        },
        {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home",
                 "item": SITE + "/"},
                {"@type": "ListItem", "position": 2, "name": "Blog",
                 "item": SITE + "/blog/"},
                {"@type": "ListItem", "position": 3, "name": a["h1"],
                 "item": url},
            ],
        },
        {"@type": "FAQPage", "mainEntity": faq},
    ]
    doc = {"@context": "https://schema.org", "@graph": graph}
    return json.dumps(doc, indent=2, ensure_ascii=False)


def render_article(a):
    url = "%s/blog/%s/" % (SITE, a["slug"])
    faq_html = []
    for item in a["faq"]:
        faq_html.append(
            '  <details class="faq-item">\n'
            '    <summary>%s</summary>\n'
            '    <div class="faq-a"><p>%s</p></div>\n'
            '  </details>' % (esc(strip_tags(item["q"])), item["a"]))
    sources_html = []
    for i, s in enumerate(a["sources"], 1):
        sources_html.append('        <li id="src-%d">%s</li>' % (i, s))
    return ARTICLE_TMPL.format(
        title=esc(a["title"]),
        meta_description=esc(a["meta_description"]),
        og_title=esc(a.get("og_title") or a["title"]),
        og_description=esc(a.get("og_description") or a["meta_description"]),
        url=url,
        jsonld=build_jsonld(a, url),
        header=_parts.header("/blog/"),
        slug=a["slug"],
        h1=a["h1"],
        dateline_flag=a.get("dateline") or ("Updated " + month_year(a["date_modified"])),
        read_minutes=a["read_minutes"],
        extract_chip=a.get("extract_chip") or ("redaccel.com &middot; " + month_year(a["date_published"])),
        extract_html=a["extract_html"],
        body_html=a["body_html"],
        faq_html="\n".join(faq_html),
        sources_html="\n".join(sources_html),
        cta=_parts.CTA,
        footer=_parts.FOOTER.format(updated=month_year(a["date_modified"])),
    )


HUB_TMPL = u"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>GEO and AI search: field notes from Redaccel</title>
<meta name="description" content="Weekly, sourced writing on generative engine optimization: how AI engines pick citations, how to measure AI visibility, and what actually moves share of voice. New article every Tuesday.">
<link rel="canonical" href="{site}/blog/">
<meta property="og:title" content="Redaccel blog: GEO and AI search, evidenced">
<meta property="og:description" content="One sourced article a week on getting brands cited in AI answers.">
<meta property="og:type" content="website">
<meta property="og:url" content="{site}/blog/">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="/assets/css/main.css">
<script defer src="/assets/js/main.js"></script>
<script type="application/ld+json">
{jsonld}
</script>
</head>
<body>
{header}

<main id="main" class="article">
  <div class="shell">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="/">redaccel.com</a> / blog</nav>
    <h1>Field notes on GEO</h1>
    <span class="dateline"><span class="flag">New article every Tuesday</span> {count} published</span>

    <div class="extract">
      <div class="extract-chip"><span class="tag">What this is</span> <span>redaccel.com &middot; blog &middot; {updated}</span></div>
      <p><mark>One sourced article a week on how AI engines choose what to cite, and what that means for your brand.</mark> No recycled SEO advice, no unsourced statistics. Every figure links to where it came from, and we say plainly when the honest answer is "nobody knows yet".</p>
    </div>

    <div class="card-grid">
{cards}
    </div>

{cta}
  </div>
</main>

{footer}
</body>
</html>
"""


def render_hub(articles):
    cards = []
    for i, a in enumerate(articles):
        featured = ' card-featured' if i == 0 else ''
        flag = ('      <div class="card-flag">Latest</div>\n' if i == 0 else '')
        cards.append(
            '      <div class="card%s">\n%s'
            '        <h3><a href="/blog/%s/">%s</a></h3>\n'
            '        <p>%s</p>\n'
            '        <p class="card-cta"><a href="/blog/%s/">Read &rarr;</a> '
            '<span class="small">%s &middot; %s min</span></p>\n'
            '      </div>' % (featured, flag, a["slug"], esc(a["card_title"]),
                              esc(a["card_summary"]), a["slug"],
                              pretty_date(a["date_published"]),
                              a["read_minutes"]))
    items = []
    for i, a in enumerate(articles, 1):
        items.append({"@type": "ListItem", "position": i,
                      "url": "%s/blog/%s/" % (SITE, a["slug"]),
                      "name": a["card_title"]})
    jsonld = json.dumps({
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "Blog", "name": "Redaccel field notes",
             "description": "Weekly sourced writing on generative engine optimization.",
             "url": SITE + "/blog/",
             "publisher": {"@id": SITE + "/#org"}},
            {"@type": "ItemList", "itemListElement": items},
        ]}, indent=2, ensure_ascii=False)
    updated = month_year(articles[0]["date_published"]) if articles else "August 2026"
    return HUB_TMPL.format(site=SITE, header=_parts.header("/blog/"),
                           jsonld=jsonld, cards="\n".join(cards),
                           count=("%d article%s" % (len(articles), "" if len(articles) == 1 else "s")),
                           updated=updated, cta=_parts.CTA,
                           footer=_parts.FOOTER.format(updated=updated))


# --------------------------------------------------------------------------
# indexes
# --------------------------------------------------------------------------

def update_sitemap(articles):
    path = os.path.join(SITE_DIR, "sitemap.xml")
    xml = read(path)
    body = re.sub(r"\s*<url><loc>%s/blog/[^<]*</loc>[^<]*</url>" % re.escape(SITE),
                  "", xml)
    rows = ["  <url><loc>%s/blog/</loc><lastmod>%s</lastmod></url>"
            % (SITE, articles[0]["date_published"] if articles else "2026-08-20")]
    for a in articles:
        rows.append("  <url><loc>%s/blog/%s/</loc><lastmod>%s</lastmod></url>"
                    % (SITE, a["slug"], a["date_modified"]))
    body = body.replace("</urlset>", "\n".join(rows) + "\n</urlset>")
    write(path, body)


def update_llms(articles):
    path = os.path.join(SITE_DIR, "llms.txt")
    txt = read(path)
    lines = ["## Articles", "",
             "One sourced article a week on GEO and AI search. Index: %s/blog/"
             % SITE, ""]
    for a in articles:
        lines.append("- [%s](%s/blog/%s/): %s"
                     % (a["card_title"], SITE, a["slug"], a["card_summary"]))
    block = "\n".join(lines) + "\n"
    if "## Articles" in txt:
        txt = re.sub(r"## Articles\n(?:.*?\n)*?(?=\n## |\Z)", block, txt, count=1)
    else:
        txt = txt.replace("## Company", block + "\n## Company", 1)
    write(path, txt)


def mark_queue_done(a):
    queue = load_json(QUEUE_PATH)
    if not queue:
        return
    for item in queue.get("topics", []):
        if item.get("slug") == a["slug"] or item.get("keyword") == a["keyword"]:
            item["status"] = "published"
            item["published"] = a["date_published"]
            item["url"] = "%s/blog/%s/" % (SITE, a["slug"])
    write(QUEUE_PATH, json.dumps(queue, indent=2, ensure_ascii=False) + "\n")


def git(*args):
    return subprocess.call(["git", "-C", ROOT] + list(args))


# --------------------------------------------------------------------------

def main(argv):
    args = [x for x in argv[1:] if not x.startswith("--")]
    flags = set(x for x in argv[1:] if x.startswith("--"))
    if not args:
        print("usage: publish_article.py <article.json> [--no-git] [--dry-run]")
        return 2
    path = args[0]
    if not os.path.isabs(path):
        path = os.path.join(ROOT, path)
    a = load_json(path)

    today = datetime.date.today().isoformat()
    a.setdefault("date_published", today)
    a["date_modified"] = today
    a.setdefault("card_title", a.get("h1", ""))
    if not a.get("read_minutes"):
        words = len(strip_tags(a.get("body_html", "")).split())
        a["read_minutes"] = max(3, int(round(words / 220.0)))

    errs = validate(a)
    if errs:
        print("REFUSED TO PUBLISH — fix these first:")
        for e in errs:
            print("  - " + e)
        return 1

    index = load_json(INDEX_PATH, {"articles": []})
    kept = [x for x in index["articles"] if x["slug"] != a["slug"]]
    for x in index["articles"]:
        if x["slug"] == a["slug"]:
            a["date_published"] = x["date_published"]  # never rewrite history
    entry = {k: a[k] for k in ("slug", "keyword", "card_title", "card_summary",
                               "date_published", "date_modified", "read_minutes")}
    index["articles"] = [entry] + kept
    index["articles"].sort(key=lambda x: x["date_published"], reverse=True)

    page = render_article(a)
    hub = render_hub(index["articles"])

    if "--dry-run" in flags:
        print(page[:1500])
        print("... [%d chars] ..." % len(page))
        return 0

    write(os.path.join(SITE_DIR, "blog", a["slug"], "index.html"), page)
    write(os.path.join(SITE_DIR, "blog", "index.html"), hub)
    write(INDEX_PATH, json.dumps(index, indent=2, ensure_ascii=False) + "\n")
    update_sitemap(index["articles"])
    update_llms(index["articles"])
    mark_queue_done(a)

    print("published: /blog/%s/  (%d words, %d min)"
          % (a["slug"], len(strip_tags(a["body_html"]).split()), a["read_minutes"]))

    if "--no-git" not in flags:
        git("add", "-A")
        git("commit", "-m", "Publish: %s" % a["card_title"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
