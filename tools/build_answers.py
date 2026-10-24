#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the answer pages (site/<slug>/) and the /guides/ hub from answers/*.json.

Usage: python3 tools/build_answers.py [--check]

Each answer page answers one cluster of the unbranded buyer questions tracked in Peec
(redaccel/context/geo-own-campaign.md). The JSON keeps the prompts it covers so the
coverage can be read off the files. Same house rules as articles: no em dashes, no
"stuff", every figure sourced, at least three FAQ pairs (they feed FAQPage schema).

Fields: slug, kind (guide|service), title, meta_description, h1, dateline, extract_chip,
extract_html, body_html, faq [{q, a}], sources [html], prompts [str], related [[href,
label]], date_published, date_modified, hub_summary.

Writes site/<slug>/index.html with a .answer marker (build_sitemap.py and
build_search.py read it), site/guides/index.html, and the "## Guides and answers"
section of site/llms.txt. Then run tools/schema_sync.py, build_sitemap.py and
build_search.py (or just `make`-style: python3 tools/build_all.py).
"""
import glob
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SITE_DIR = os.path.join(ROOT, "site")
ANS_DIR = os.path.join(ROOT, "answers")
sys.path.insert(0, HERE)
import _parts  # noqa: E402
from publish_article import esc, strip_tags, month_year, pretty_date  # noqa: E402

SITE = _parts.SITE
GUIDES = [  # the hand-written guides that share the hub, in display order
    ("/what-is-geo/", "What is generative engine optimization (GEO)?",
     "The plain definition, how engines choose citations, measurement, timeline and cost."),
    ("/geo-vs-seo/", "GEO vs SEO: what's the difference, and which do you need?",
     "Side by side: only about 12 percent of AI-cited URLs rank in Google's top 10."),
    ("/reddit-marketing-2026/", "Is Reddit marketing still worth it in 2026?",
     "Reddit's July 2026 LLM-detection crackdown, what survives it, organic versus Reddit Ads."),
    ("/geo-agencies-compared/", "Which GEO agencies do AI engines actually recommend?",
     "30 days of citation data on 28 buyer questions, and the pages the names are copied from."),
    ("/ai-visibility-checklist/", "The AI Visibility Audit Checklist",
     "Twelve checks to run before trusting an AI visibility score."),
]

PAGE_TMPL = u"""{head}
<body>
{header}

<main id="main" class="article">
  <div class="shell">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="/">redaccel.com</a> <span aria-hidden="true">/</span> <a href="/guides/">guides</a> <span aria-hidden="true">/</span> <span>{slug}</span></nav>
    <article>
    <h1>{h1}</h1>
    <div class="dateline"><span class="flag">{dateline}</span> <span>{read_minutes} min read</span> <span>By Redaccel</span></div>

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
    </article>

    <div class="byline-box">{mark}<p>Written by Redaccel, a Reddit and AI visibility agency in Oslo. Every figure links to where it came from. Spotted something wrong? <a href="mailto:contact@redaccel.com">contact@redaccel.com</a></p></div>

    <nav class="related" aria-label="Related pages">
      <p class="chip-label">Related</p>
      <ul class="chips chips-plain">
{related_html}
      </ul>
    </nav>

{cta}
  </div>
</main>

{footer}
</body>
</html>
"""

HUB_TMPL = u"""{head}
<body>
{header}

<main id="main" class="blog-hub">
  <section class="page-hero">
    <div class="shell">
      <nav class="crumbs" aria-label="Breadcrumb"><a href="/">redaccel.com</a> <span aria-hidden="true">/</span> <span>guides</span></nav>
      <div class="hub-head">
        <h1>Guides and straight answers</h1>
        <p class="lede">The questions buyers ask AI engines about GEO, Reddit marketing and AI visibility, answered in plain words with the sources attached.</p>
        <div class="dateline"><span class="flag">Updated {updated}</span> <span>{count} pages</span></div>
      </div>
    </div>
  </section>

  <section class="section section-tight">
    <div class="shell">
      <h2 class="faq-title">Straight answers</h2>
      <div class="post-list">
{answers}
      </div>
      <h2 class="faq-title section-head-sub">The guides</h2>
      <div class="post-list">
{guides}
      </div>
{cta}
    </div>
  </section>
</main>

{footer}
</body>
</html>
"""

TELLS = ["delve", "in today's fast-paced", "it's important to note", "unlock the power",
         "in conclusion", "game-changer", "leverage the power", "navigate the landscape"]


def validate(a):
    errs = []
    for key in ("slug", "kind", "title", "meta_description", "h1", "extract_html", "body_html",
                "faq", "sources", "prompts", "date_published", "date_modified", "hub_summary"):
        if not a.get(key):
            errs.append("missing %s" % key)
    if a.get("kind") not in ("guide", "service"):
        errs.append("kind must be guide or service")
    if len(a.get("title", "")) > 65:
        errs.append("title is %d chars, keep it under 65" % len(a["title"]))
    if len(a.get("meta_description", "")) > 165:
        errs.append("meta_description is %d chars, keep it under 165" % len(a["meta_description"]))
    if len(a.get("faq", [])) < 3:
        errs.append("at least 3 FAQ entries")
    if len(a.get("sources", [])) < 3:
        errs.append("at least 3 sources")
    ids = set("src-%d" % i for i in range(1, len(a.get("sources", [])) + 1))
    for ref in re.findall(r'href="#(src-\d+)"', a.get("body_html", "") + a.get("extract_html", "")):
        if ref not in ids:
            errs.append("cites %s but there is no such source" % ref)
    prose = " ".join([a.get("body_html", ""), a.get("extract_html", ""), a.get("meta_description", ""),
                      a.get("h1", ""), a.get("title", "")] + [f["q"] + " " + f["a"] for f in a.get("faq", [])])
    if u"\u2014" in prose:
        errs.append("em dash in copy")
    if re.search(r"\bstuff\b", prose, re.I):
        errs.append("the word 'stuff'")
    for tell in TELLS:
        if tell in prose.lower():
            errs.append("AI tell: %r" % tell)
    if re.search(r"\b0\.0 ?(%|percent)|share of voice of 0", prose):
        errs.append("own share-of-voice figure in copy")
    if re.search(r"[€£]|\bEUR\b|\bGBP\b|\bNOK\b", prose):
        errs.append("non-USD currency in copy")
    words = len(strip_tags(a.get("body_html", "")).split())
    if words < 600:
        errs.append("body is only %d words" % words)
    return errs


def jsonld(a, url):
    faq = [{"@type": "Question", "name": strip_tags(f["q"]).strip(),
            "acceptedAnswer": {"@type": "Answer", "text": strip_tags(f["a"]).strip()}} for f in a["faq"]]
    graph = []
    if a["kind"] == "service":
        graph.append({
            "@type": "Service",
            "@id": url + "#service",
            "name": a.get("service_name") or a["h1"],
            "serviceType": a.get("service_type", "AI visibility and generative engine optimization"),
            "provider": {"@id": SITE + "/#org"},
            "areaServed": "Worldwide",
            "description": a.get("schema_description") or a["meta_description"],
            "url": url,
            "dateModified": a["date_modified"],
        })
    graph.append({
        "@type": "Article" if a["kind"] == "guide" else "WebPage",
        "@id": url,
        "headline" if a["kind"] == "guide" else "name": a["h1"],
        "description": a.get("schema_description") or a["meta_description"],
        "author": {"@type": "Organization", "name": "Redaccel", "@id": SITE + "/#org"},
        "publisher": {"@id": SITE + "/#org"},
        "datePublished": a["date_published"],
        "dateModified": a["date_modified"],
        "mainEntityOfPage": url,
        "isPartOf": {"@id": SITE + "/#website"},
        "about": a.get("about") or a["prompts"][0],
    })
    graph.append({"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
        {"@type": "ListItem", "position": 2, "name": "Guides", "item": SITE + "/guides/"},
        {"@type": "ListItem", "position": 3, "name": a["h1"], "item": url},
    ]})
    graph.append({"@type": "FAQPage", "mainEntity": faq})
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, indent=2, ensure_ascii=False)


def render(a):
    url = "%s/%s/" % (SITE, a["slug"])
    faq_html = "\n".join(
        '      <details class="faq-item">\n        <summary>%s</summary>\n'
        '        <div class="faq-a"><p>%s</p></div>\n      </details>' % (esc(strip_tags(f["q"])), f["a"])
        for f in a["faq"])
    sources_html = "\n".join('        <li id="src-%d">%s</li>' % (i, s) for i, s in enumerate(a["sources"], 1))
    related_html = "\n".join('        <li><a href="%s">%s</a></li>' % (h, esc(l)) for h, l in a.get("related", []))
    words = len(strip_tags(a["body_html"]).split())
    head = _parts.head(a["title"], a["meta_description"], url, og_type="article",
                       og_title=a.get("og_title"), og_description=a.get("og_description"),
                       jsonld=jsonld(a, url))
    return PAGE_TMPL.format(
        head=head, header=_parts.header("/guides/"), slug=a["slug"], h1=a["h1"],
        dateline=a.get("dateline") or ("Updated " + month_year(a["date_modified"])),
        read_minutes=max(2, round(words / 220)),
        extract_chip=a.get("extract_chip") or ("redaccel.com &middot; " + month_year(a["date_published"])),
        extract_html=a["extract_html"], body_html=a["body_html"], faq_html=faq_html,
        sources_html=sources_html, mark=_parts._MARK % {"c": "#fff"}, related_html=related_html,
        cta=_parts.CTA, footer=_parts.FOOTER.format(updated=month_year(a["date_modified"])))


def card(href, title, summary, kicker, date=None):
    meta = '<div class="dateline"><span>%s</span></div>' % esc(date) if date else ""
    return ('        <article class="post"><span class="badge">%s</span><h3><a href="%s">%s</a></h3>'
            '<p>%s</p>%s</article>' % (esc(kicker), href, esc(title), esc(summary), meta))


def render_hub(answers):
    url = SITE + "/guides/"
    ld = json.dumps({"@context": "https://schema.org", "@graph": [
        {"@type": "CollectionPage", "@id": url, "url": url, "name": "Guides and straight answers",
         "isPartOf": {"@id": SITE + "/#website"}, "publisher": {"@id": SITE + "/#org"},
         "dateModified": max(a["date_modified"] for a in answers) if answers else "2026-10-24"},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Guides", "item": url}]},
    ]}, indent=2)
    head = _parts.head("Guides and straight answers on GEO, Reddit and AI visibility",
                       "Plain answers to the questions buyers ask AI engines about GEO agencies, Reddit "
                       "marketing and AI visibility, with the sources attached.", url, jsonld=ld)
    a_cards = "\n".join(card("/%s/" % a["slug"], a["h1"], a["hub_summary"],
                             "Service" if a["kind"] == "service" else "Answer",
                             "Updated " + month_year(a["date_modified"])) for a in answers)
    g_cards = "\n".join(card(h, t, s, "Guide") for h, t, s in GUIDES)
    newest = max(a["date_modified"] for a in answers) if answers else "2026-10-24"
    return HUB_TMPL.format(head=head, header=_parts.header("/guides/"), updated=month_year(newest),
                           count=len(answers) + len(GUIDES), answers=a_cards, guides=g_cards,
                           cta=_parts.CTA, footer=_parts.FOOTER.format(updated=month_year(newest)))


def update_llms(answers):
    path = os.path.join(SITE_DIR, "llms.txt")
    txt = io.open(path, encoding="utf-8").read()
    lines = ["## Guides and answers", "",
             "- [All guides](%s/guides/): Index of the guides and the straight answers below." % SITE]
    for a in answers:
        lines.append("- [%s](%s/%s/): %s" % (a["h1"], SITE, a["slug"], a["hub_summary"]))
    block = "\n".join(lines) + "\n"
    if "## Guides and answers" in txt:
        txt = re.sub(r"## Guides and answers\n(?:.*?\n)*?(?=\n## |\Z)", block, txt, count=1)
    else:
        txt = txt.replace("## Articles", block + "\n## Articles", 1)
    io.open(path, "w", encoding="utf-8").write(txt)


def load():
    answers = []
    for path in sorted(glob.glob(os.path.join(ANS_DIR, "*.json"))):
        a = json.load(io.open(path, encoding="utf-8"))
        errs = validate(a)
        if errs:
            raise SystemExit("%s:\n  " % os.path.basename(path) + "\n  ".join(errs))
        answers.append(a)
    answers.sort(key=lambda a: a.get("order", 99))
    return answers


def build():
    answers = load()
    for a in answers:
        out = os.path.join(SITE_DIR, a["slug"], "index.html")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        io.open(out, "w", encoding="utf-8").write(render(a))
        io.open(os.path.join(SITE_DIR, a["slug"], ".answer"), "w").write(a["slug"] + "\n")
        print("built /%s/ (%s, covers %d prompts)" % (a["slug"], a["kind"], len(a["prompts"])))
    hub = os.path.join(SITE_DIR, "guides", "index.html")
    os.makedirs(os.path.dirname(hub), exist_ok=True)
    io.open(hub, "w", encoding="utf-8").write(render_hub(answers))
    update_llms(answers)
    print("built /guides/ and llms.txt")
    return answers


def main(argv):
    if "--check" in argv:
        load()
        print("answers ok")
        return 0
    build()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
