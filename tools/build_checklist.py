#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build site/ai-visibility-checklist/index.html, the AI Visibility Audit Checklist.

The checklist is the lead magnet offered on the Redaccel LinkedIn page (comment AUDIT,
get it by DM). It lives here so the link anyone gets opens without a login. Content is
the same as the version drafted in the Social Desk (claude.ai artifact VqA7o6abeBK9XszKukjFpM);
every house figure was checked against Peec project or_38dcd2ac on 2026-10-07/09.

Usage: python3 tools/build_checklist.py
"""
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import _parts  # noqa: E402

SLUG = "ai-visibility-checklist"
URL = "%s/%s/" % (_parts.SITE, SLUG)
TITLE = "The AI Visibility Audit Checklist: 12 checks before you trust a score"
DESC = ("The twelve checks we run on a brand before we will quote its AI visibility: is the "
        "measurement real, where the answers come from, and what they say about you.")

PARTS = [
    ("Part one: is your measurement real",
     "Six of these fail at the first hurdle. If your measurement is broken, everything downstream of it is decoration.",
     [
         ("01", "How many responses is your visibility number built on?",
          "Count the actual responses behind the figure, not the number of prompts. Engine output varies run to run on the same prompt, on the same day.",
          None,
          "Under a few hundred responses. You are reading noise and calling it a trend."),
         ("02", "What share of your prompt set names your brand?",
          "Branded prompts score high because the brand is in the question. They measure nothing about whether you get recommended. Report branded and non-branded separately, and treat the non-branded figure as the real one.",
          None,
          "More than about a fifth. Strip them and watch the number fall."),
         ("03", "Would a real buyer type these prompts?",
          "Read the set aloud. Buying-intent language, comparison language, and problem-first language should all be present. \"Best X for Y\" alone is a third of a prompt set.",
          None,
          "The set was written to be won rather than to be representative."),
         ("04", "How many engines, and are they reported separately?",
          "Engines do not read the same internet. Across one 30-day run of 31 prompts on three engines, the same three sources landed like this, measured as the share of that engine's own answers the domain was pulled into:",
          ("Share of each engine's answers the domain was pulled into",
           ["Source", "AI Overview", "ChatGPT", "Gemini"],
           [["Reddit", "43.4%", "19.1%", "24.3%"],
            ["YouTube", "38.9%", "2.0%", "1.7%"],
            ["LinkedIn", "36.3%", "5.1%", "0%"]]),
          "One engine, or several engines averaged into a single score. A blended number hides exactly the thing you need in order to spend."),
         ("05", "Do you have visibility and share of voice separately?",
          "Visibility is how often you appear at all. Share of voice is how much of the answer you own when you do. One number cannot tell you which you are short of.",
          None,
          "Your tool reports one figure and calls it AI visibility."),
         ("06", "Is anything tracked over time, on a fixed prompt set?",
          "A score is meaningless without a baseline, and a baseline is meaningless if the prompt set changed underneath it.",
          None,
          "Prompts were added or swapped mid-period. The movement is the prompt change, not your performance."),
     ]),
    ("Part two: where the answers actually come from",
     "This is the half almost nobody runs, and it is the half that tells you where to spend.",
     [
         ("07", "Which domains do the engines retrieve for your category?",
          "Rank them by the share of answers each is pulled into. The shape is a long tail: in the 30-day run above, we ranked the 120 most-retrieved domains and 12 of them cleared 5% retrieval. The other 108 did not.",
          None,
          "You have never built this table. You are guessing at where your buyers' answers come from."),
         ("08", "How much of it is community content?",
          "Across 2,780 tracked answers in that run, Reddit was retrieved in 28.9%, YouTube in 14.1% and LinkedIn in 13.7%. Google's own site was retrieved in 5.8%.",
          None,
          "Your plan is entirely owned-site content. You are competing for a minority of the source layer."),
         ("09", "When you are mentioned, what got retrieved?",
          "Look at the sources behind the answers that name you. Often a single page or thread is carrying the brand, and nobody internally knows it exists.",
          None,
          "One source is carrying you. That is a single point of failure, not a strategy."),
         ("10", "What is cited about your competitors that is not cited about you?",
          "Compare the retrieved-domain sets side by side. The gap is your work order, and it is usually shorter than people expect.",
          None,
          "You have never looked. This is the cheapest insight on this list."),
     ]),
    ("Part three: what the answers say about you",
     "Being mentioned is not the same as being recommended, and being retrieved is not the same as being mentioned.",
     [
         ("11", "What is your average position when you appear?",
          "First name in the answer and fourth name in the answer are different products commercially. Track the position, not just the mention.",
          None,
          "High mention count paired with a poor average position. You are the also-ran, and more placements will not fix it."),
         ("12", "What is the sentiment, and what is dragging it?",
          "Read the actual sentences. Then check whether review aggregators, complaint sites or scam-checker pages are among the sources the engines pull when they describe you. These climb quietly: in the run above, one scam-checking site was pulled into 4.5% of tracked answers, up from 1.9% in the preceding 30 days. Nobody in the category put it there on purpose.",
          None,
          "Sentiment sits below about 65, or any source in your retrieved set exists to accuse companies of things. That is a reputation job before it is a visibility job."),
     ]),
]

READING = [
    ("Low visibility, high share of voice.", "A distribution problem. The messaging works and almost nobody sees it. Get into more of the source material the engines read."),
    ("High visibility, low share of voice.", "A positioning problem. You are mentioned constantly and always as the also-ran. More placements will not move this."),
    ("Both low.", "Start with checks 07 and 10. You need to know where the answers come from before you spend anything."),
    ("Both healthy, sentiment low.", "Stop buying visibility. You are amplifying a reputation problem."),
]

METHOD = ("House figures come from a single 30-day run: 31 prompts, three engines (ChatGPT, Google AI "
          "Overview, Gemini), 2,780 responses, window ending 4 October 2026. The preceding 30-day window "
          "used for comparison ended 4 September 2026 across 2,714 responses. One category, one country. "
          "Your category will differ, which is the point of running it yourself.")

CTA = """    <aside class="cta-panel" aria-label="Free AI visibility audit">
      <p class="eyebrow">Free AI visibility audit</p>
      <h2>Rather have us run the checks?</h2>
      <p>We run this list on your brand: which engines mention you, which recommend competitors instead, and the exact pages behind those answers.</p>
      <div class="cta-actions">
        <a class="btn btn-primary btn-lg" href="%s">Get your free AI audit</a>
        <span class="cta-note">48 hours &middot; no call &middot; no mailing list</span>
      </div>
    </aside>""" % _parts.AUDIT_URL


def check_html(num, q, body, table, fails):
    e = _parts.esc
    out = ['    <h3 id="check-%s">%s. %s</h3>' % (num, num, e(q)), "    <p>%s</p>" % e(body)]
    if table:
        cap, head, rows = table
        out.append('    <div class="table-wrap">\n      <table>\n        <caption>%s</caption>' % e(cap))
        out.append("        <thead><tr>%s</tr></thead>" % "".join("<th>%s</th>" % e(h) for h in head))
        out.append("        <tbody>\n%s\n        </tbody>\n      </table>\n    </div>" % "\n".join(
            "          <tr>%s</tr>" % "".join("<td>%s</td>" % e(c) for c in r) for r in rows))
    out.append("    <p><strong>Fails if:</strong> %s</p>" % e(fails))
    return "\n".join(out)


def build():
    e = _parts.esc
    jsonld = json.dumps({
        "@context": "https://schema.org", "@type": "Article", "headline": TITLE, "description": DESC,
        "url": URL, "datePublished": "2026-10-09", "dateModified": "2026-10-09",
        "author": {"@type": "Organization", "name": "Redaccel", "url": _parts.SITE},
        "publisher": {"@type": "Organization", "name": "Redaccel", "url": _parts.SITE},
    }, indent=1)
    body = []
    for title, intro, checks in PARTS:
        body.append("    <h2>%s</h2>\n    <p>%s</p>" % (e(title), e(intro)))
        body.extend(check_html(*c) for c in checks)
    reading = "\n".join("    <p><strong>%s</strong> %s</p>" % (e(a), e(b)) for a, b in READING)
    html = "\n".join([
        _parts.head(TITLE, DESC, URL, og_type="article", jsonld=jsonld),
        "<body>",
        _parts.header(""),
        '<main id="main" class="article">',
        '  <div class="shell">',
        '    <nav class="crumbs" aria-label="Breadcrumb"><a href="/">redaccel.com</a> / ai-visibility-checklist</nav>',
        "    <h1>The AI Visibility Audit Checklist</h1>",
        '    <span class="dateline"><span class="flag">Updated October 2026</span> · 12 checks · about 3 hours end to end</span>',
        "    <p>The twelve checks we run on a brand before we will quote them. Most take under an hour. "
        "Together they tell you whether you have a distribution problem, a positioning problem, or no problem at all.</p>",
        "\n".join(body),
        "    <h2>How to read your results</h2>",
        reading,
        '    <p class="dateline">%s</p>' % e(METHOD),
        CTA,
        "  </div>",
        "</main>",
        _parts.FOOTER.format(updated="October 2026"),
        "</body>",
        "</html>",
    ]) + "\n"
    # The live pages load main.js?v=20261008a while _parts still says 20261007b; match the live pages.
    html = html.replace("/assets/js/main.js?v=%s" % _parts.ASSET_VERSION, "/assets/js/main.js?v=20261008a")
    for ch in ("—", "–"):
        assert ch not in html, "em or en dash in the page"
    out = os.path.join(ROOT, "site", SLUG, "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with io.open(out, "w", encoding="utf-8") as fh:
        fh.write(html)
    print("wrote", out, len(html), "bytes")


if __name__ == "__main__":
    build()
