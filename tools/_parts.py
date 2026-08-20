# -*- coding: utf-8 -*-
"""Shared HTML chunks for redaccel.com. Single source of truth for header/footer."""

SITE = "https://www.redaccel.com"

NAV_ITEMS = [
    ("/what-we-do/", "What we do"),
    ("/what-is-geo/", "What is GEO?"),
    ("/geo-vs-seo/", "GEO vs SEO"),
    ("/reddit-marketing-2026/", "Reddit in 2026"),
    ("/blog/", "Blog"),
    ("/pricing/", "Pricing"),
    ("/about/", "About"),
]


def header(active=""):
    links = []
    for href, label in NAV_ITEMS:
        cur = ' aria-current="page"' if active and href.startswith(active) else ""
        links.append('      <a href="%s"%s>%s</a>' % (href, cur, label))
    links.append('      <a class="btn btn-primary" href="/free-ai-visibility-audit/">Free AI audit</a>')
    return """<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header">
  <div class="shell">
    <a class="wordmark" href="/">redaccel<span class="dot">.</span></a>
    <button class="nav-toggle" aria-expanded="false" aria-controls="nav">menu</button>
    <nav class="site-nav" id="nav" aria-label="Main">
%s
    </nav>
  </div>
</header>""" % "\n".join(links)


FOOTER = """<footer class="site-footer">
  <div class="shell">
    <div class="footer-grid">
      <div>
        <a class="wordmark" href="/">redaccel<span class="dot">.</span></a>
        <p style="margin-top:.8rem;max-width:22rem">Generative engine optimization agency. Built by Reddit-marketing veterans, focused on one metric: share of voice in AI answers.</p>
      </div>
      <div>
        <h2>Answers</h2>
        <ul>
          <li><a href="/what-is-geo/">What is GEO?</a></li>
          <li><a href="/geo-vs-seo/">GEO vs SEO</a></li>
          <li><a href="/reddit-marketing-2026/">Reddit in 2026</a></li>
          <li><a href="/blog/">Blog</a></li>
          <li><a href="/pricing/">How much does GEO cost?</a></li>
        </ul>
      </div>
      <div>
        <h2>Company</h2>
        <ul>
          <li><a href="/what-we-do/">What we do</a></li>
          <li><a href="/about/">About</a></li>
          <li><a href="/contact/">Contact</a></li>
          <li><a href="/free-ai-visibility-audit/">Free AI audit</a></li>
        </ul>
      </div>
      <div>
        <h2>Contact</h2>
        <ul>
          <li><a href="mailto:contact@redaccel.com">contact@redaccel.com</a></li>
          <li><a href="https://calendly.com/redaccel/30min" rel="noopener">Book 30 minutes</a></li>
          <li><a href="https://t.me/chainarenn" rel="noopener">Telegram</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-meta">
      <span>&copy; 2026 Redaccel DA &middot; Org. 936133428 &middot; Oslo, Norway</span>
      <span>Updated {updated}</span>
      <span><a href="/llms.txt">/llms.txt</a></span>
    </div>
  </div>
</footer>"""

CTA = """    <div class="cta-panel">
      <h2>Find out if AI recommends you.</h2>
      <p>The free audit shows which engines mention you, which recommend competitors instead, and the exact pages behind those answers.</p>
      <a class="btn btn-primary btn-lg" href="/free-ai-visibility-audit/">Get the free audit</a>
      <p class="small">48 hours &middot; no call &middot; no mailing list</p>
    </div>"""
