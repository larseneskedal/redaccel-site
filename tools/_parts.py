# -*- coding: utf-8 -*-
"""Shared HTML chunks for redaccel.com. Single source of truth for head assets, header,
footer and the audit CTA. The blog publisher and the page builders import this, and
tools/sync_chrome.py stamps the same head assets, header and footer into every
hand-written page. Design: redesign 2026-10 (redaccel/os-v2/site-redesign/DIRECTION.md)."""

SITE = "https://www.redaccel.com"

AUDIT_URL = "/free-ai-visibility-audit/"

# Main nav. "Learn" is a disclosure menu; its links are plain anchors in the HTML so
# crawlers and no-JS readers see every one of them.
NAV_ITEMS = [
    ("/what-we-do/", "What we do"),
    ("/case-studies/", "Case studies"),
    ("/pricing/", "Pricing"),
]
LEARN_ITEMS = [
    ("/what-is-geo/", "What is GEO?", "The plain definition, with sources"),
    ("/geo-vs-seo/", "GEO vs SEO", "What changes and what carries over"),
    ("/reddit-marketing-2026/", "Reddit in 2026", "Why engines cite Reddit, and what survives"),
    ("/geo-agencies-compared/", "GEO agencies compared", "30 days of citation data"),
    ("/blog/", "Blog", "One sourced article every Tuesday"),
]
TAIL_ITEMS = [
    ("/about/", "About"),
]

# Head assets every page carries, right after the viewport meta. Bump ASSET_VERSION
# whenever main.css or main.js changes so Cloudflare and browsers fetch the new file.
ASSET_VERSION = "20261007b"
HEAD_ASSETS = """<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta name="theme-color" content="#ffffff">
<link rel="preload" href="/assets/fonts/inter-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/css/main.css?v=%(v)s">
<script defer src="/assets/js/main.js?v=%(v)s"></script>""" % {"v": ASSET_VERSION}

_MARK = ('<svg class="wordmark-icon" width="26" height="26" viewBox="0 0 24 24" fill="none" aria-hidden="true" focusable="false">'
         '<rect width="24" height="24" rx="6.5" fill="currentColor"/>'
         '<path d="M6.8 6.5L12.3 12L6.8 17.5" stroke="%(c)s" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>'
         '<path d="M11.6 6.5L17.1 12L11.6 17.5" stroke="%(c)s" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" opacity=".55"/>'
         '</svg>')
LOGO = '<a class="wordmark" href="/" aria-label="Redaccel home">%s<span>redaccel</span></a>' % (_MARK % {"c": "#fff"})
LOGO_LIGHT = '<a class="wordmark wordmark-light" href="/" aria-label="Redaccel home">%s<span>redaccel</span></a>' % (_MARK % {"c": "#0B0C10"})


def _cur(active, href):
    return ' aria-current="page"' if active and href == active else ""


def header(active=""):
    """active: the path of the current section, e.g. "/blog/" or "/pricing/"."""
    learn_hrefs = [h for h, _l, _d in LEARN_ITEMS]
    main_links = "\n".join('        <a class="nav-link" href="%s"%s>%s</a>' % (h, _cur(active, h), l)
                           for h, l in NAV_ITEMS)
    learn_links = "\n".join(
        '            <a href="%s"%s><b>%s</b><span>%s</span></a>' % (h, _cur(active, h), l, d)
        for h, l, d in LEARN_ITEMS)
    tail_links = "\n".join('        <a class="nav-link" href="%s"%s>%s</a>' % (h, _cur(active, h), l)
                           for h, l in TAIL_ITEMS)
    learn_cur = ' data-current="true"' if active in learn_hrefs else ""
    return """<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header">
  <div class="shell header-row">
    %(logo)s
    <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="nav"><span class="nav-toggle-bars" aria-hidden="true"></span><span class="sr-only">Menu</span></button>
    <nav class="site-nav" id="nav" aria-label="Main">
      <div class="nav-links">
%(main)s
        <div class="nav-menu"%(learn_cur)s>
          <button class="nav-link nav-menu-btn" type="button" aria-expanded="false" aria-controls="nav-learn">Learn</button>
          <div class="nav-menu-panel" id="nav-learn">
%(learn)s
          </div>
        </div>
%(tail)s
      </div>
      <div class="nav-actions">
        <a class="nav-link" href="/contact/"%(contact_cur)s>Contact</a>
        <a class="btn btn-primary btn-sm" href="%(audit)s">Free AI audit</a>
      </div>
    </nav>
  </div>
</header>""" % {"logo": LOGO, "main": main_links, "learn": learn_links, "tail": tail_links,
                "learn_cur": learn_cur, "contact_cur": _cur(active, "/contact/"), "audit": AUDIT_URL}


FOOTER = """<footer class="site-footer">
  <div class="shell">
    <div class="footer-cta">
      <div>
        <p class="eyebrow">Free &middot; 48 hours &middot; no call</p>
        <p class="footer-cta-line">See which AI engines recommend you, and which recommend your competitors instead.</p>
      </div>
      <a class="btn btn-primary btn-lg" href="/free-ai-visibility-audit/">Get the free AI audit</a>
    </div>
    <div class="footer-grid">
      <div class="footer-brand">
        """ + LOGO_LIGHT + """
        <p>Reddit and AI visibility agency. We measure which sources AI engines cite in your category, then earn you a place in them.</p>
      </div>
      <div>
        <h2>Services</h2>
        <ul>
          <li><a href="/what-we-do/">What we do</a></li>
          <li><a href="/pricing/">Pricing</a></li>
          <li><a href="/case-studies/">Case studies</a></li>
          <li><a href="/free-ai-visibility-audit/">Free AI audit</a></li>
        </ul>
      </div>
      <div>
        <h2>Learn</h2>
        <ul>
          <li><a href="/what-is-geo/">What is GEO?</a></li>
          <li><a href="/geo-vs-seo/">GEO vs SEO</a></li>
          <li><a href="/reddit-marketing-2026/">Reddit in 2026</a></li>
          <li><a href="/geo-agencies-compared/">GEO agencies compared</a></li>
          <li><a href="/blog/">Blog</a></li>
        </ul>
      </div>
      <div>
        <h2>Company</h2>
        <ul>
          <li><a href="/about/">About</a></li>
          <li><a href="/contact/">Contact</a></li>
          <li><a href="mailto:contact@redaccel.com">contact@redaccel.com</a></li>
          <li><a href="https://calendly.com/redaccel/30min" rel="noopener">Book 30 minutes</a></li>
          <li><a href="https://www.linkedin.com/company/redaccel" rel="noopener">LinkedIn</a></li>
          <li><a href="https://www.designrush.com/agency/search-engine-optimization" rel="noopener">Listed on DesignRush</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-meta">
      <span>&copy; 2026 Redaccel DA &middot; Org. 936133428 &middot; Oslo, Norway</span>
      <span>Updated {updated}</span>
      <span><a href="/llms.txt">llms.txt</a> &middot; <a href="/sitemap.xml">Sitemap</a></span>
    </div>
  </div>
</footer>"""
# FOOTER is filled with str.format(updated=...), so it must never contain other braces.

CTA = """    <aside class="cta-panel" aria-label="Free AI visibility audit">
      <p class="eyebrow">Free AI visibility audit</p>
      <h2>Find out if AI recommends you.</h2>
      <p>Which engines mention you, which recommend competitors instead, and the exact pages behind those answers.</p>
      <div class="cta-actions">
        <a class="btn btn-primary btn-lg" href="/free-ai-visibility-audit/">Get the free audit</a>
        <span class="cta-note">48 hours &middot; no call &middot; no mailing list</span>
      </div>
    </aside>"""


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;"))


def head(title, description, canonical, og_type="website", og_title=None, og_description=None,
         jsonld=None):
    """Everything from <!DOCTYPE> to </head> for a generated page. jsonld is a ready string."""
    out = ["<!DOCTYPE html>", '<html lang="en">', "<head>", '<meta charset="utf-8">',
           '<meta name="viewport" content="width=device-width, initial-scale=1">',
           HEAD_ASSETS,
           "<title>%s</title>" % esc(title),
           '<meta name="description" content="%s">' % esc(description),
           '<link rel="canonical" href="%s">' % canonical,
           '<meta property="og:title" content="%s">' % esc(og_title or title),
           '<meta property="og:description" content="%s">' % esc(og_description or description),
           '<meta property="og:type" content="%s">' % og_type,
           '<meta property="og:url" content="%s">' % canonical,
           '<meta property="og:image" content="%s/assets/img/og.png">' % SITE,
           '<meta name="twitter:card" content="summary_large_image">']
    if jsonld:
        out.append('<script type="application/ld+json">\n%s\n</script>' % jsonld)
    out.append("</head>")
    return "\n".join(out)
