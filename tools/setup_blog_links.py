#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""One-time, idempotent: add the Blog link to the nav and footer of every page.

Safe to rerun. Only touches files that do not already link to /blog/ in the
relevant block, so it never doubles up and never rewrites anything else.
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")

NAV_LINK = '      <a href="/blog/">Blog</a>\n'
FOOT_LINK = '          <li><a href="/blog/">Blog</a></li>\n'


def patch(path):
    s = io.open(path, encoding="utf-8").read()
    orig = s
    # 1. main nav: insert before the Pricing link inside <nav class="site-nav">
    m = re.search(r'(<nav class="site-nav".*?</nav>)', s, re.S)
    if m and '/blog/' not in m.group(1):
        block = m.group(1)
        new = re.sub(r'(\n\s*<a href="/pricing/")', "\n" + NAV_LINK.rstrip("\n") + r"\1",
                     block, count=1)
        if new == block:  # no pricing link on this page's nav, put it before the CTA
            new = block.replace('      <a class="btn btn-primary"',
                                NAV_LINK + '      <a class="btn btn-primary"', 1)
        s = s.replace(block, new, 1)
    # 2. footer "Answers" column
    m = re.search(r'(<h2>Answers</h2>\s*<ul>.*?</ul>)', s, re.S)
    if m and '/blog/' not in m.group(1):
        block = m.group(1)
        new = re.sub(r'(\n\s*<li><a href="/pricing/")',
                     "\n" + FOOT_LINK.rstrip("\n") + r"\1", block, count=1)
        if new == block:
            new = block.replace('</ul>', FOOT_LINK + '        </ul>', 1)
        s = s.replace(block, new, 1)
    if s != orig:
        io.open(path, "w", encoding="utf-8").write(s)
        return True
    return False


def main():
    changed = []
    for dirpath, _dirs, files in os.walk(SITE):
        for f in files:
            if f != "index.html" and f != "404.html":
                continue
            p = os.path.join(dirpath, f)
            if os.path.sep + "blog" + os.path.sep in p:
                continue
            if patch(p):
                changed.append(os.path.relpath(p, ROOT))
    for c in sorted(changed):
        print("patched " + c)
    if not changed:
        print("nothing to do, all pages already link to /blog/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
