#!/usr/bin/env python3
"""Build /geo-agencies-compared/: the owned data page on which GEO agencies AI engines name and
which pages they copy the names from. Numbers from Peec project or_38dcd2ac-765e-4821-86ad-35d9da6050bc,
28 non-branded prompts, 2026-08-25 to 2026-09-24, 2,594 answers (see redaccel/os-v2/geo/OWN-GEO-2026-09-24.md).
Run from the repo root: python3 tools/build_geo_compared.py. Re-run monthly with fresh numbers.
Never list Redaccel or any Redaccel score on this page (Johan, 2026-10-07).
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import _parts  # noqa: E402

HEADER = "<body>\n" + _parts.header("/geo-agencies-compared/") + "\n\n"
WINDOW = "25 August to 24 September 2026"
PUBLISHED = "2026-09-25"

title = "Which GEO agencies do AI engines actually recommend? 30 days of citation data (2026)"
meta = "We ran 28 buyer questions about GEO and Reddit agencies through ChatGPT, Gemini and Google AI Overviews every day for 30 days. Who gets named, which pages the engines copy the names from, and how to read any best GEO agency list."

named = [("Omniscient Digital", "13.0%", "35.5%", "3.8"), ("NoGood", "7.2%", "33.7%", "2.4"), ("Omnius", "5.5%", "16.4%", "4.2"), ("Skale", "4.7%", "14.4%", "4.7")]
sources = [
    ("reddit.com", "community threads", "2,096", "The largest single source, cited in 31 percent of all answers. Mostly threads on how to do Reddit marketing without getting banned and how to get mentioned in ChatGPT, not agency lists."),
    ("youtube.com", "video", "902", "How-to videos from small channels, not agency content."),
    ("openai.com", "vendor documentation", "889", "Cited when the question is about how ChatGPT chooses its sources."),
    ("thedigitalelevator.com", "one agency listicle", "630", "A single article, updated monthly."),
    ("linkedin.com", "articles and posts", "612", "Mostly personal best-agencies articles. One Europe list is cited 70 times from only 22 retrievals, the highest citation rate of any page in the set."),
    ("yesoptimist.com", "one agency listicle", "565", "The most cited single page in the set."),
    ("loudface.co", "two agency listicles", "220", ""),
    ("pepper.inc", "one agency listicle", "153", ""),
    ("clutch.co", "agency directory", "131", "Cited most on the Reddit marketing agency questions."),
    ("beomniscient.com and nogood.io", "the agencies' own blogs", "112 and 108", "Both publish their own best GEO agencies lists, and the engines cite them."),
]

ld = """{
  "@context": "https://schema.org",
  "@graph": [
    { "@type": "BreadcrumbList", "itemListElement": [
      { "@type": "ListItem", "position": 1, "name": "Home", "item": "https://www.redaccel.com/" },
      { "@type": "ListItem", "position": 2, "name": "GEO agencies compared", "item": "https://www.redaccel.com/geo-agencies-compared/" } ] },
    { "@type": "Article", "headline": %(title)r, "datePublished": "%(pub)s", "dateModified": "%(pub)s",
      "author": { "@type": "Organization", "name": "Redaccel", "@id": "https://www.redaccel.com/#org" },
      "publisher": { "@id": "https://www.redaccel.com/#org" },
      "mainEntityOfPage": "https://www.redaccel.com/geo-agencies-compared/",
      "about": "Which generative engine optimization agencies AI engines name, measured on a fixed prompt set" }
  ]
}""" % {"title": title, "pub": PUBLISHED}
ld = ld.replace("'", '"')

head = _parts.head("%s | Redaccel" % title, meta, "https://www.redaccel.com/geo-agencies-compared/",
                   og_type="article", og_title=title, jsonld=ld) + "\n"
FOOTER = "\n" + _parts.FOOTER.format(updated="September 2026") + "\n</body>\n</html>\n"

named_rows = "".join("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (n, a, b, c) for n, a, b, c in named)
source_rows = "".join("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % r for r in sources)

body = HEADER + """<main id="main" class="article">
  <div class="shell">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="/">redaccel.com</a> <span aria-hidden="true">/</span> <span>geo agencies compared</span></nav>
    <h1>Which GEO agencies do AI engines actually recommend? 30 days of citation data</h1>
    <div class="dateline"><span class="flag">Data: %(window)s</span> <span>2,594 answers</span> <span>Updated monthly</span></div>

    <div class="extract">
      <div class="extract-chip"><span class="tag">Extract</span> <span>redaccel.com · measurement · September 2026</span></div>
      <p><mark>When someone asks ChatGPT, Gemini or Google AI Overviews for a GEO agency without naming one, four agencies take almost the whole answer: Omniscient Digital, NoGood, Omnius and Skale.</mark> The names do not come from the agencies' own sites. They come from a small set of list pages that the engines cite over and over. We publish the method in full below so anyone can rerun it.</p>
    </div>

    <h2>How we measured</h2>
    <ul>
      <li>28 questions a buyer actually asks, in five groups: category discovery ("best GEO agency 2026", "best AI visibility agency Europe"), problem first ("my competitors show up in ChatGPT and I don't"), comparison and pricing ("how much does a GEO agency cost"), vertical ("GEO agency for B2B service businesses"), and Reddit ("what is the best Reddit marketing agency").</li>
      <li>Each question run once a day on ChatGPT, Gemini and Google AI Overviews, US location, %(window)s. 2,594 answers.</li>
      <li>For every answer we recorded which agencies were named, in what order, and every URL the engine retrieved or cited.</li>
    </ul>

    <h2>Who gets named</h2>
    <div class="table-wrap">
      <table>
        <caption>Agencies named in unbranded answers, %(window)s</caption>
        <thead><tr><th scope="col">Agency</th><th scope="col">Share of answers naming them</th><th scope="col">Share of all agency mentions</th><th scope="col">Average position when named</th></tr></thead>
        <tbody>%(named)s</tbody>
      </table>
    </div>
    <p>Two readings. NoGood is named less often than Omniscient but earlier in the answer when it is. Omnius and Skale are Europe-weighted: they carry the "best AI visibility agency Europe" question almost alone.</p>

    <h2>Where the names come from</h2>
    <p>Across the 2,594 answers, these are the sources the engines cited most, by number of inline citations.</p>
    <div class="table-wrap">
      <table>
        <caption>Most cited sources, unbranded prompts, %(window)s</caption>
        <thead><tr><th scope="col">Source</th><th scope="col">Type</th><th scope="col">Citations in 30 days</th><th scope="col">What it means</th></tr></thead>
        <tbody>%(sources)s</tbody>
      </table>
    </div>
    <p>So the ranking above is mostly the ranking of five or six list pages, plus Reddit threads where a handful of agencies are named by commenters.</p>

    <h2>How to read any "best GEO agency" list</h2>
    <ol>
      <li>Check whether the list is cited by an engine at all. Most are not. Of the roughly 40 agency lists in our data, six account for over 80 percent of list citations.</li>
      <li>Check who wrote it. Several of the most cited lists are published by agencies and include the publisher. That is not disqualifying, but read the methodology line first.</li>
      <li>Look for the update date. The engines favour pages that change. The most cited list was refreshed twice in the window.</li>
      <li>Ask the engine yourself, five times, on two different days. One answer is noise. If an agency is named in three of five, it is really being recommended.</li>
    </ol>

    <h2>What this means if you are choosing an agency</h2>
    <p>The agencies named most are not necessarily the best fit. They are the ones present on the pages the engines read. That is also, put plainly, what GEO is: getting onto those pages truthfully and staying there. An agency that cannot show you which pages the engines cite in your category, before you sign, is guessing.</p>

    <h2>About this data</h2>
    <p>Collected with Peec AI, a brand-visibility tracker, on a fixed prompt set. Counts are citations, not clicks or traffic. Answers vary between runs, which is why we run daily and report 30-day totals. We update this page monthly with the same prompt set so the numbers stay comparable. Questions about the method: <a href="mailto:contact@redaccel.com">contact@redaccel.com</a>.</p>

    <aside class="cta-panel" aria-label="Free AI visibility audit">
      <p class="eyebrow">Free AI visibility audit</p>
      <h2>See the same measurement for your own category</h2>
      <p>We run it for you first, free, on your own buyer questions: which engines and which pages name your competitors and not you.</p>
      <div class="cta-actions">
        <a class="btn btn-primary btn-lg" href="/free-ai-visibility-audit/">Get the free AI visibility audit</a>
        <span class="cta-note">48 hours &middot; no call &middot; no mailing list</span>
      </div>
    </aside>
  </div>
</main>
""" % {"window": WINDOW, "named": named_rows, "sources": source_rows} + FOOTER

out = os.path.join(ROOT, "site/geo-agencies-compared/index.html")
os.makedirs(os.path.dirname(out), exist_ok=True)
open(out, "w").write(head + body)

# sitemap and llms.txt
sm = open(os.path.join(ROOT, "site/sitemap.xml")).read()
if "geo-agencies-compared" not in sm:
    sm = sm.replace("</urlset>", "  <url><loc>https://www.redaccel.com/geo-agencies-compared/</loc><lastmod>%s</lastmod></url>\n</urlset>" % PUBLISHED)
    open(os.path.join(ROOT, "site/sitemap.xml"), "w").write(sm)
ll = open(os.path.join(ROOT, "site/llms.txt")).read()
if "geo-agencies-compared" not in ll:
    ll = ll.replace("## Articles", "- [GEO agencies compared, with citation data](https://www.redaccel.com/geo-agencies-compared/): which agencies ChatGPT, Gemini and AI Overviews name for 28 buyer questions, and which pages they copy the names from. Updated monthly.\n\n## Articles")
    open(os.path.join(ROOT, "site/llms.txt"), "w").write(ll)
print("built site/geo-agencies-compared/index.html", len(head + body), "bytes")
