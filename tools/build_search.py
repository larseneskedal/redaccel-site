#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the site search: site/search-index.json and site/search/index.html.

Usage: python3 tools/build_search.py

The index holds every indexable page's title, URL, description, headings and the first
part of its main text. The search page loads it and matches in the browser, so there is
no server and nothing to break. It exists so the SearchAction the home page declares
(Peec action "Declare your site search in schema", 2026-10-05) points at a search that
returns something useful. Run it after adding or changing pages; the blog publisher
calls build() after each post.
"""
import io
import json
import os
import re
import sys
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SITE_DIR = os.path.join(ROOT, "site")
sys.path.insert(0, HERE)
import _parts  # noqa: E402

SITE = _parts.SITE
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.S)
DESC_RE = re.compile(r'<meta name="description" content="(.*?)">', re.S)
MAIN_RE = re.compile(r"<main\b.*?</main>", re.S)
SKIP_DIRS = ("assets", "functions", "search")


class _Main(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self, convert_charrefs=True)
        self.heads, self.text = [], []
        self._h = None
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("h2", "h3"):
            self._h = []
        if tag in ("script", "style", "nav") or "faq-a" in a.get("class", "") and False:
            self._skip += 1

    def handle_endtag(self, tag):
        if tag in ("h2", "h3") and self._h is not None:
            h = " ".join("".join(self._h).split())
            if h and h not in ("Frequently asked", "Sources", "Services", "Learn", "Company"):
                self.heads.append(h)
            self._h = None
        if tag in ("script", "style", "nav") and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if self._skip:
            return
        if self._h is not None:
            self._h.append(data)
        self.text.append(data)


def unesc(s):
    return (s.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
             .replace("&quot;", '"').replace("&#39;", "'"))


def collect():
    rows = []
    for dirpath, dirs, files in os.walk(SITE_DIR):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        if "index.html" not in files:
            continue
        path = os.path.join(dirpath, "index.html")
        html = io.open(path, encoding="utf-8").read()
        if "noindex" in html[:4000]:
            continue
        rel = os.path.relpath(dirpath, SITE_DIR).replace(os.sep, "/")
        url = "/" if rel == "." else "/%s/" % rel
        tm, dm, mm = TITLE_RE.search(html), DESC_RE.search(html), MAIN_RE.search(html)
        p = _Main()
        p.feed(mm.group(0) if mm else html)
        text = " ".join(" ".join(p.text).split())
        kind = ("Article" if url.startswith("/blog/") and url != "/blog/"
                else "Case study" if url.startswith("/case-studies/") and url != "/case-studies/"
                else "Guide" if os.path.exists(os.path.join(dirpath, ".answer")) or rel in (
                    "what-is-geo", "geo-vs-seo", "reddit-marketing-2026", "geo-agencies-compared",
                    "ai-visibility-checklist")
                else "Page")
        rows.append({"u": url, "t": unesc(tm.group(1)) if tm else url,
                     "d": unesc(dm.group(1)) if dm else "", "h": p.heads[:12],
                     "x": text[:1500], "k": kind})
    rows.sort(key=lambda r: (r["k"] != "Page", r["u"]))
    return rows


PAGE_TMPL = u"""{head}
<body>
{header}

<main id="main" class="article">
  <div class="shell">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="/">redaccel.com</a> <span aria-hidden="true">/</span> <span>search</span></nav>
    <h1>Search redaccel.com</h1>
    <p class="lede">Every page, guide, case study and article on the site. Runs in your browser; nothing is sent anywhere.</p>
    <form class="audit-form search-form" role="search" action="/search/" method="get">
      <div class="field">
        <label for="q">What are you looking for?</label>
        <input id="q" name="q" type="search" placeholder="for example: Reddit threads ChatGPT cites" autocomplete="off" autofocus>
      </div>
      <button class="btn btn-primary" type="submit">Search</button>
    </form>
    <p class="form-status search-status" role="status" aria-live="polite"></p>
    <ol class="search-results" aria-label="Results"></ol>
    <noscript><p>Search needs JavaScript. The <a href="/sitemap.xml">sitemap</a> lists every page, and <a href="/llms.txt">llms.txt</a> has a one-line summary of each.</p></noscript>
{cta}
  </div>
</main>

{footer}
<script>
(function () {{
  var form = document.querySelector('.search-form');
  var input = document.getElementById('q');
  var out = document.querySelector('.search-results');
  var status = document.querySelector('.search-status');
  var index = null;
  function esc(s) {{ return s.replace(/[&<>"]/g, function (c) {{ return {{'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}}[c]; }}); }}
  function terms(q) {{ return q.toLowerCase().split(/[^a-z0-9]+/).filter(function (t) {{ return t.length > 1; }}); }}
  function score(row, ts) {{
    var t = row.t.toLowerCase(), d = row.d.toLowerCase(), h = row.h.join(' ').toLowerCase(), x = row.x.toLowerCase();
    var s = 0, hit = 0;
    ts.forEach(function (w) {{
      var any = false;
      if (t.indexOf(w) > -1) {{ s += 6; any = true; }}
      if (h.indexOf(w) > -1) {{ s += 3; any = true; }}
      if (d.indexOf(w) > -1) {{ s += 2; any = true; }}
      if (x.indexOf(w) > -1) {{ s += 1; any = true; }}
      if (any) hit++;
    }});
    if (hit < ts.length) s = s * hit / (ts.length * 2);
    return s;
  }}
  function snippet(row, ts) {{
    var x = row.x, lx = x.toLowerCase(), i = -1;
    for (var k = 0; k < ts.length && i < 0; k++) i = lx.indexOf(ts[k]);
    if (i < 0) return row.d;
    var a = Math.max(0, i - 90), b = Math.min(x.length, i + 150);
    return (a > 0 ? '\\u2026' : '') + x.slice(a, b) + (b < x.length ? '\\u2026' : '');
  }}
  function render(q) {{
    var ts = terms(q);
    out.innerHTML = '';
    if (!ts.length) {{ status.textContent = ''; return; }}
    var rows = index.map(function (r) {{ return [score(r, ts), r]; }})
      .filter(function (p) {{ return p[0] > 0; }})
      .sort(function (a, b) {{ return b[0] - a[0]; }}).slice(0, 20);
    status.textContent = rows.length ? rows.length + (rows.length === 1 ? ' result' : ' results') + ' for "' + q + '"'
      : 'Nothing matched "' + q + '". Try fewer words, or ask us: contact@redaccel.com';
    rows.forEach(function (p) {{
      var r = p[1], li = document.createElement('li');
      li.innerHTML = '<span class="badge">' + esc(r.k) + '</span> <a href="' + esc(r.u) + '"><b>' + esc(r.t) + '</b></a>' +
        '<p>' + esc(snippet(r, ts)) + '</p><span class="small">' + esc('redaccel.com' + r.u) + '</span>';
      out.appendChild(li);
    }});
  }}
  function load(cb) {{
    if (index) return cb();
    fetch('/search-index.json').then(function (r) {{ return r.json(); }}).then(function (j) {{ index = j; cb(); }})
      .catch(function () {{ status.textContent = 'The search index did not load. The sitemap at /sitemap.xml lists every page.'; }});
  }}
  var params = new URLSearchParams(location.search);
  if (params.get('q')) {{ input.value = params.get('q'); load(function () {{ render(input.value); }}); }}
  form.addEventListener('submit', function (e) {{
    e.preventDefault();
    var q = input.value.trim();
    history.replaceState(null, '', q ? '/search/?q=' + encodeURIComponent(q) : '/search/');
    load(function () {{ render(q); }});
  }});
  input.addEventListener('input', function () {{ load(function () {{ render(input.value.trim()); }}); }});
}})();
</script>
</body>
</html>
"""


def build():
    rows = collect()
    with io.open(os.path.join(SITE_DIR, "search-index.json"), "w", encoding="utf-8") as fh:
        json.dump(rows, fh, ensure_ascii=False, separators=(",", ":"))
    url = SITE + "/search/"
    jsonld = json.dumps({
        "@context": "https://schema.org",
        "@type": "SearchResultsPage",
        "@id": url, "url": url, "name": "Search redaccel.com",
        "isPartOf": {"@id": SITE + "/#website"},
    }, indent=2)
    head = _parts.head("Search redaccel.com", "Search every page, guide, case study and article on redaccel.com.",
                       url, jsonld=jsonld)
    head = head.replace("</head>", '<meta name="robots" content="noindex, follow">\n</head>', 1)
    html = PAGE_TMPL.format(head=head, header=_parts.header(""), cta=_parts.CTA,
                            footer=_parts.FOOTER.format(updated="October 2026"))
    out = os.path.join(SITE_DIR, "search", "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with io.open(out, "w", encoding="utf-8") as fh:
        fh.write(html)
    return rows


def main():
    rows = build()
    print("search index: %d pages" % len(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
