#!/usr/bin/env python3
"""Build the case-study pages and patch the client-name passages, 2026-09-24.

Johan's decision (2026-09-24): name GPM Music Group, describe FanPro anonymously as a content
creator software company, add Peptide Bureau, and drop Kalshi and Roobet from the site.
Run from the repo root: python3 tools/build_case_studies.py
Idempotent: re-running rewrites the same files.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
TODAY = "2026-09-24"


def read(p):
    with open(os.path.join(ROOT, p)) as f:
        return f.read()


def write(p, s):
    full = os.path.join(ROOT, p)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(s)


about = read("site/about/index.html")
HEAD_END = about.index("<title>")
HEADER = about[about.index("<body>"):about.index("<main")]
HEADER = HEADER.replace('<a href="/about/" aria-current="page">About</a>', '<a href="/about/">About</a>')
FOOTER = about[about.index("<footer"):]
STYLES = about[about.index('<link rel="preconnect"'):about.index('<script type="application/ld+json">')]

CASES = [
    {
        "slug": "gpm-music-group",
        "name": "GPM Music Group",
        "short": "GPM Music Group",
        "category": "Music promotion and Spotify playlisting",
        "period": "Autumn 2025, 30 days",
        "deliverables": "4 posts and 60 or more comments on Reddit",
        "title": "Case study: GPM Music Group, 150,000 Reddit views and the number 2 Google result in 30 days",
        "meta": "How Redaccel built GPM Music Group's reputation on Reddit: 4 posts, 60 comments, 150,000 views in 30 days, the top 4 Reddit results and the number 2 Google result for the brand name.",
        "stats": [("150K+", "views on our posts in 30 days"), ("#2", "Google result for \"GPM music group\", after the official site"), ("4 of 4", "posts still live")],
        "objective": "Build GPM's reputation as a serious music promotion and Spotify playlisting service, and make sure that when an artist searches the name, on Google or on Reddit, what they find is a real conversation rather than silence.",
        "strategy": [
            "Posts in the subreddits where artists actually compare services: r/MusicPromotion, r/musicmarketing, r/WeAreTheMusicMakers, r/musicindustry.",
            "Comments from aged accounts with history in those communities, most of them general and useful, some of them recommending GPM where it fit the question.",
            "Threads written around the questions people type: \"has anyone used GPM Music Group\", \"Spotify playlisting that is not bots\", \"ranking the promo services I have tried\".",
            "Timing, early engagement and upvotes to hold top positions inside each subreddit.",
        ],
        "results": [
            "All 4 posts live at the end of the campaign and still live today.",
            "One post became the number 2 Google result for \"GPM music group\", directly under the official site.",
            "The top 4 Reddit results for the brand name were our 4 posts.",
            "More than 150,000 views on the posts during the 30 days, still climbing after the campaign ended.",
            "60 or more comments placed by us, including top comments in other relevant threads worth over 5,000 dollars a month in equivalent search traffic.",
        ],
        "impact": "Anyone researching GPM now lands on community discussion that answers their questions and recommends the service in the words artists use. The posts keep ranking, so the social proof compounds instead of expiring like an ad. The same threads are the kind of source AI engines cite when asked about music promotion services.",
    },
    {
        "slug": "content-creator-software",
        "name": "Content creator software company",
        "short": "Content creator software",
        "category": "High-ticket software for content creator businesses (client name withheld at their request)",
        "period": "Summer 2025, first 30 days, then extended and doubled",
        "deliverables": "6 posts, about 100 comments, inbound DM handling and reputation monitoring in month one",
        "title": "Case study: a content creator software company, 300,000 Reddit views, the number 1 Google result and paying customers from DMs",
        "meta": "How Redaccel took a content creator software company to 300,000 Reddit views in 30 days, the number 1 Google result for its brand name, and confirmed sales from Reddit DMs. Client name withheld.",
        "stats": [("300K+", "Reddit views in 30 days"), ("#1", "Google result for the brand name, above the company's own site"), ("40+", "inbound leads by DM in the first month")],
        "objective": "Establish a fast-growing, high-ticket software company as a trusted, community-endorsed option for people starting a content creator business, drive long-term Google and AI visibility for the brand name, and turn the inbound questions into customers.",
        "strategy": [
            "Experience-based posts in the communities where the buyers already are: r/SideProject, r/OnlineIncomeHustle, r/Entrepreneur and related subreddits.",
            "Natural comments from aged accounts to set the tone early and keep the threads honest and useful.",
            "Threads built around the brand name and the questions a buyer asks before a 30,000 dollar decision.",
            "Sentiment monitoring: hostile or misleading claims answered with facts, accurate narratives reinforced.",
            "Inbound Reddit DMs answered directly, with product questions and use cases explained, and interested people guided to the company.",
        ],
        "results": [
            "More than 300,000 Reddit views across posts and comments in the first 30 days; over 100,000 on our own posts alone.",
            "The number 1 Google result for the brand name, ranking above the company's own website, with nearly every high-ranking Reddit result for the brand created by the campaign.",
            "Around 40 leads who reached out by Reddit DM in the first month, and new DMs still arriving daily after posting stopped.",
            "Multiple confirmed purchases attributed to those DM conversations. In this category one sale is worth roughly 20 to 25 times the monthly campaign fee, so the campaign paid for itself at the first conversion.",
            "The client doubled the programme for month two: 12 posts and 200 comments.",
        ],
        "impact": "The threads act as permanent, Google-ranked social proof that shapes the first impression of anyone researching the brand, and the DM channel turned research into revenue. It is an acquisition channel that compounds over time and delivers what paid ads cannot: real conversations with people who are already convinced by other people.",
    },
    {
        "slug": "peptide-bureau",
        "name": "Peptide Bureau",
        "short": "Peptide Bureau",
        "category": "Our own brand, client zero: a peptide education site with an affiliate model",
        "period": "August to September 2026, ongoing",
        "deliverables": "More than 100 Reddit comment placements across 60 subreddits, run through our own delivery platform",
        "title": "Case study: Peptide Bureau, from zero to a 300 percent rise in AI visibility, built on Reddit",
        "meta": "Peptide Bureau is Redaccel's own brand and client zero. It was built from nothing with Reddit as the lead channel, and its AI visibility for buyer questions rose more than 300 percent once the campaign started.",
        "stats": [("300%+", "rise in AI visibility since the campaign began"), ("100+", "comment placements across 60 subreddits"), ("60", "subreddits worked, each placement logged and survival-checked")],
        "objective": "Prove the method on a brand we own before selling it. Peptide Bureau started with no audience, no links and no search presence. The work was Reddit: useful, disclosed comments in the threads where people compare peptide vendors and protocols, and where the AI engines go to build their answers.",
        "strategy": [
            "A fixed set of buyer questions measured across the AI engines on day zero, so the change could be attributed rather than assumed.",
            "Comment placements in the threads the engines already cite: more than 100 placements across 60 subreddits, each logged with its permalink and checked weekly for survival.",
            "Every placement written for the thread first and the brand second, with an honest note on what the site does and does not cover.",
            "Removals tracked and reported, not hidden. Reddit's moderation removed a large share, which is the normal cost of the channel; what survives is what compounds.",
        ],
        "results": [
            "AI visibility for Peptide Bureau's buyer questions is up more than 300 percent since the campaign began, on the same fixed prompt set.",
            "The brand went from zero presence anywhere to being named and cited, with Reddit as the channel that did the work.",
            "More than 100 comment placements across 60 subreddits, all logged and survival-checked.",
            "The campaign is still running, and the results page is updated as the measurement moves.",
        ],
        "impact": "This is the campaign we point to when a prospect asks whether Reddit can move what AI engines say. It can, and the numbers are ours, measured the same way we measure clients. It also taught us the removal rates and account rules that we now apply on every client campaign.",
    },
]


def case_page(c):
    stats = "".join('<div class="stat"><b>%s</b><span>%s</span></div>' % (b, s) for b, s in c["stats"])
    strategy = "".join("<li>%s</li>" % s for s in c["strategy"])
    results = "".join("<li>%s</li>" % s for s in c["results"])
    ld = """<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "BreadcrumbList",
      "itemListElement": [
        { "@type": "ListItem", "position": 1, "name": "Home", "item": "https://www.redaccel.com/" },
        { "@type": "ListItem", "position": 2, "name": "Case studies", "item": "https://www.redaccel.com/case-studies/" },
        { "@type": "ListItem", "position": 3, "name": "%(name)s", "item": "https://www.redaccel.com/case-studies/%(slug)s/" }
      ]
    },
    {
      "@type": "Article",
      "headline": "%(title)s",
      "datePublished": "%(today)s",
      "dateModified": "%(today)s",
      "author": { "@type": "Organization", "name": "Redaccel", "@id": "https://www.redaccel.com/#org" },
      "publisher": { "@id": "https://www.redaccel.com/#org" },
      "mainEntityOfPage": "https://www.redaccel.com/case-studies/%(slug)s/"
    }
  ]
}
</script>""" % {"name": c["name"], "slug": c["slug"], "title": c["title"].replace('"', '\\"'), "today": TODAY}
    head = about[:HEAD_END] + "<title>%s | Redaccel</title>\n" % c["title"] + \
        '<meta name="description" content="%s">\n' % c["meta"].replace('"', "&quot;") + \
        '<link rel="canonical" href="https://www.redaccel.com/case-studies/%s/">\n' % c["slug"] + \
        '<meta property="og:title" content="%s">\n<meta property="og:description" content="%s">\n<meta property="og:type" content="article">\n<meta property="og:url" content="https://www.redaccel.com/case-studies/%s/">\n' % (
            c["title"].replace('"', "&quot;"), c["meta"].replace('"', "&quot;"), c["slug"]) + \
        STYLES + ld + "\n</head>\n"
    body = HEADER + """<main id="main" class="article">
  <div class="shell">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="/">redaccel.com</a> / <a href="/case-studies/">case studies</a> / %(short_l)s</nav>
    <h1>%(title)s</h1>
    <span class="dateline"><span class="flag">Reddit campaign</span> · %(period)s · %(category)s</span>

    <div class="extract">
      <div class="extract-chip"><span class="tag">Extract</span> <span>redaccel.com · case study · %(short)s</span></div>
      <p><mark>%(extract)s</mark></p>
    </div>

    <div class="stat-strip">%(stats)s</div>

    <h2>Objective</h2>
    <p>%(objective)s</p>

    <h2>What we did</h2>
    <p>Deliverables: %(deliverables)s.</p>
    <ul>%(strategy)s</ul>

    <h2>Results</h2>
    <ul>%(results)s</ul>

    <h2>Why it worked</h2>
    <p>%(impact)s</p>

    <p class="small">Numbers are the client's own campaign report figures at the end of the period stated. Reddit views are the totals shown on the posts. Google positions were checked from a logged-out US browser at the time. References available on request through <a href="/contact/">contact</a>.</p>

    <div class="cta-panel">
      <h2>Find out where you stand</h2>
      <p>We run the same measurement for you first, free: which AI engines and which Reddit threads name your competitors and not you. <a class="btn btn-primary" href="/free-ai-visibility-audit/">Get the free AI visibility audit</a></p>
    </div>
  </div>
</main>
""" % {
        "short": c["short"], "short_l": c["short"].lower(), "title": c["title"], "period": c["period"], "category": c["category"],
        "extract": c["results"][0] + " " + c["results"][1], "stats": stats, "objective": c["objective"],
        "deliverables": c["deliverables"], "strategy": strategy, "results": results, "impact": c["impact"],
    } + FOOTER
    return head + body


def hub_page():
    cards = "".join(
        '<tr><td><a href="/case-studies/%s/">%s</a></td><td>%s</td><td>%s</td></tr>' % (
            c["slug"], c["name"], c["category"].split(" (")[0], "; ".join(b + " " + s for b, s in c["stats"][:2]))
        for c in CASES)
    head = about[:HEAD_END] + "<title>Redaccel case studies: Reddit campaigns with the numbers</title>\n" + \
        '<meta name="description" content="Redaccel client work with the results stated plainly: GPM Music Group, a content creator software company, and Peptide Bureau. Views, Google positions and leads, per campaign.">\n' + \
        '<link rel="canonical" href="https://www.redaccel.com/case-studies/">\n' + STYLES + "</head>\n"
    body = HEADER + """<main id="main" class="article">
  <div class="shell">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="/">redaccel.com</a> / case studies</nav>
    <h1>Case studies</h1>
    <span class="dateline"><span class="flag">Updated September 2026</span> · Numbers from the campaign reports</span>
    <p>Client work with the results stated plainly. One of the clients asked not to be named, so it is described by what it sells. Peptide Bureau is our own brand and is run as client zero on the same method.</p>
    <div class="table-wrap">
      <table>
        <caption>Selected campaigns</caption>
        <thead><tr><th>Client</th><th>Category</th><th>Headline result</th></tr></thead>
        <tbody>%s</tbody>
      </table>
    </div>
    <p class="small">References available on request through <a href="/contact/">contact</a>.</p>
    <div class="cta-panel">
      <h2>Start with the audit</h2>
      <p>Before any contract we measure which sources the AI engines cite in your category and whether you are on them. <a class="btn btn-primary" href="/free-ai-visibility-audit/">Get the free AI visibility audit</a></p>
    </div>
  </div>
</main>
""" % cards + FOOTER
    return head + body


for c in CASES:
    write("site/case-studies/%s/index.html" % c["slug"], case_page(c))
write("site/case-studies/index.html", hub_page())

# ---- about page
a = about
a = a.replace(
    "built on years of Reddit marketing for brands like Kalshi and Roobet.",
    "built on years of Reddit marketing for brands like GPM Music Group and a content creator software company.")
a = re.sub(
    r"We ran campaigns for <strong>Kalshi</strong>.*?among others\.",
    "We ran campaigns for <strong>GPM Music Group</strong> in music promotion, where our threads became the number 2 Google result for the brand name; for a <strong>content creator software company</strong> that took the number 1 Google result for its own name and closed sales from Reddit DMs; and for our own brand <strong>Peptide Bureau</strong>, which we run as client zero on the same method. The numbers are in the <a href=\"/case-studies/\">case studies</a>.",
    a, count=1, flags=re.S)
a = re.sub(
    r"<caption>Selected client work.*?</tbody>",
    """<caption>Selected client work, with the results</caption>
        <thead>
          <tr><th>Client</th><th>Category</th><th>Result</th></tr>
        </thead>
        <tbody>
          <tr><td><a href="/case-studies/gpm-music-group/">GPM Music Group</a></td><td>Music promotion</td><td>150,000 views in 30 days; the top 4 Reddit results and the number 2 Google result for the brand name</td></tr>
          <tr><td><a href="/case-studies/content-creator-software/">Content creator software company</a></td><td>High-ticket software for creator businesses</td><td>300,000 Reddit views in 30 days; the number 1 Google result for the brand name; confirmed sales from Reddit DMs</td></tr>
          <tr><td><a href="/case-studies/peptide-bureau/">Peptide Bureau</a></td><td>Our own brand, client zero</td><td>Built from zero on Reddit; AI visibility up more than 300 percent since the campaign began</td></tr>
        </tbody>""",
    a, count=1, flags=re.S)
a = a.replace('<span class="flag">Updated July 2026</span>', '<span class="flag">Updated September 2026</span>', 1)
a = a.replace('"dateModified": "2026-07-29"', '"dateModified": "%s"' % TODAY)
write("site/about/index.html", a)

# ---- home
h = read("site/index.html")
h = h.replace(
    """Some of the brands we've worked with: Kalshi, Roobet, GPM Music Group — <a href="/about/#track-record">case studies</a>""",
    """Some of the brands we've worked with: GPM Music Group, a content creator software company, Peptide Bureau. <a href="/case-studies/">The case studies, with numbers</a>""")
write("site/index.html", h)

# ---- reddit page
r = read("site/reddit-marketing-2026/index.html")
r = r.replace("for clients including Kalshi, Roobet and GPM Music Group,",
              "for clients including GPM Music Group and a content creator software company,")
write("site/reddit-marketing-2026/index.html", r)

# ---- llms files
lf = read("site/llms-full.txt")
lf = lf.replace(
    "earned-visibility campaigns for paying clients including Kalshi (regulated prediction markets), Roobet (online gaming), GPM Music Group (music licensing) and a creator-management platform.",
    "earned-visibility campaigns for paying clients including GPM Music Group (music promotion: 150,000 Reddit views in 30 days, number 2 Google result for the brand name) and a content creator software company (300,000 Reddit views in 30 days, number 1 Google result for the brand name, confirmed sales from Reddit DMs), plus Redaccel's own brand Peptide Bureau, run as client zero (built from zero on Reddit, AI visibility up more than 300 percent since the campaign began). Case studies: https://www.redaccel.com/case-studies/")
write("site/llms-full.txt", lf)
l = read("site/llms.txt")
l = l.replace("Reddit marketing for brands including Kalshi, Roobet and GPM Music Group",
              "Reddit marketing for brands including GPM Music Group and a content creator software company")
if "/case-studies/" not in l:
    l = l.replace("- [About](https://www.redaccel.com/about/)",
                  "- [Case studies](https://www.redaccel.com/case-studies/): GPM Music Group, a content creator software company and Peptide Bureau, with the numbers.\n- [About](https://www.redaccel.com/about/)")
write("site/llms.txt", l)

# ---- sitemap
s = read("site/sitemap.xml")
s = s.replace("<url><loc>https://www.redaccel.com/about/</loc><lastmod>2026-07-29</lastmod></url>",
              "<url><loc>https://www.redaccel.com/about/</loc><lastmod>%s</lastmod></url>" % TODAY)
for u in ["case-studies/", "case-studies/gpm-music-group/", "case-studies/content-creator-software/", "case-studies/peptide-bureau/"]:
    line = "  <url><loc>https://www.redaccel.com/%s</loc><lastmod>%s</lastmod></url>\n" % (u, TODAY)
    if u not in s:
        s = s.replace("</urlset>", line + "</urlset>")
write("site/sitemap.xml", s)

# ---- flask legacy redirects: the case-study URLs are real pages again
app = read("redaccel_app.py")
app = app.replace('    "/case-studies/gpm-music-group": "/about/",\n', "")
app = app.replace('    "/case-studies/creator-management-platform": "/about/",',
                  '    "/case-studies/creator-management-platform": "/case-studies/content-creator-software/",')
write("redaccel_app.py", app)

left = []
for p in ["site/about/index.html", "site/index.html", "site/reddit-marketing-2026/index.html", "site/llms-full.txt", "site/llms.txt"]:
    t = read(p)
    for w in ("Kalshi", "Roobet"):
        if w in t:
            left.append((p, w))
print("built 4 pages, patched 7 files; Kalshi/Roobet left in:", left or "none")
