# How the redaccel.com blog gets written

One article per week, published Tuesday 09:00 Europe/Lisbon by a scheduled
Cowork task. This file is the brief. Read it fully before writing.

## The bar

The point of this blog is citations, not word count. An article succeeds if an
AI engine would rather quote it than quote a competitor, and if a human in the
market would forward it. Everything below serves that.

Non-negotiable:

1. **Every number has a source.** If you cannot link it, cut it. Never invent a
   statistic, a study name, a date or a client result. "Nobody has measured
   this yet" is a publishable sentence and a competitive advantage.
2. **Name the year on every figure.** AI-search data ages in months. Write
   "68% of US Google searches ended without a click in the first four months of
   2026 (SparkToro/Similarweb)", never "most searches are zero-click".
3. **Say what is uncertain.** Separate evidenced from inferred from folklore.
   Confidence labels beat confident prose.
4. **No client names, no client data.** Ever, unless the client has signed off
   in writing and Johan says so in the session.
5. **No invented Redaccel results.** You may describe our method. You may not
   claim outcomes that are not in the delivery tracker.

## House style

- **No em dashes.** Anywhere. Use a comma, a colon, a full stop or brackets.
  The publisher script refuses articles containing one.
- Never the word "stuff".
- No AI tells: "delve", "in today's fast-paced", "it's important to note",
  "unlock the power", "in conclusion", "game-changer". The script blocks these.
- British-neutral English, plain words, short sentences. Contractions are fine.
- Second person for the reader ("you"), first person plural for us ("we").
- Confident but never salesy in the body. The CTA panel does the selling and
  it is appended automatically.
- Numbers as numerals. Currency in euros to match the rest of the site.
- Front-load the answer. The first 60 words of the extract should be liftable
  as a standalone answer, because that is what gets quoted.

## Structure that gets extracted

- 1,100 to 1,800 words. Longer is not better.
- `extract_html`: one paragraph, opening claim wrapped in `<mark>`, with a
  footnote to a source. This is the block engines quote most.
- 5 to 8 `<h2>` sections. Phrase them as the questions people actually ask.
- Answer each h2 in its first sentence, then support it.
- At least one `<table>` wrapped in `<div class="table-wrap">` with a
  `<caption>`. Tables get lifted into answers at a high rate.
- Use `<details class="more"><summary>Read more</summary>...</details>` to keep
  long digressions out of the main scan path.
- Footnote markers look like:
  `<sup class="cite"><a href="#src-1">[1]</a></sup>`
- Internal links: 2 to 4 per article, to `/what-is-geo/`, `/geo-vs-seo/`,
  `/pricing/`, `/free-ai-visibility-audit/`, `/reddit-marketing-2026/` or an
  earlier blog article. Descriptive anchor text, never "click here".
- 3 or more FAQ entries. They render on the page and feed FAQPage schema, so
  write real answers, 40 to 80 words each.

## Research process each week

1. Read `tools/topic_queue.json`. Take the first topic with `status: "queued"`.
   Its `angle` and `must_cover` are the brief. If a fresher, clearly higher
   value topic has appeared in the news that week, you may jump the queue:
   add it to the file with a one-line reason and publish that instead.
2. Search for primary sources published in the last 12 months. Prefer, in
   order: the original study or dataset, Search Engine Land / Semrush / Ahrefs
   reporting on it, then everything else. Aggregator blogs are a lead to the
   real source, not a source.
3. Fetch the actual page before citing it. Confirm the figure, the sample and
   the date with your own eyes. If the fetch fails, do not cite it.
4. Where we have first-hand evidence (Peec, Ahrefs Brand Radar, our own
   campaigns), use it and say it is ours, at method level only, no client data.
5. Pull Ahrefs metrics for the target keyword if they are older than a quarter
   and update the queue file.

## Output

Write `articles/<slug>.json` with these keys:

```json
{
  "slug": "kebab-case-url",
  "keyword": "primary target keyword",
  "title": "<title> tag, under 65 chars, keyword near the front",
  "meta_description": "under 165 chars, contains the keyword and a reason to click",
  "og_title": "optional, punchier",
  "og_description": "optional",
  "h1": "the on-page headline, may differ from title",
  "card_title": "short title for the blog index card",
  "card_summary": "1 to 2 sentences for the index card and llms.txt",
  "extract_chip": "redaccel.com · category · Month Year",
  "dateline": "Updated Month Year",
  "extract_html": "<p><mark>The liftable answer.</mark> Support.</p>",
  "body_html": "<h2>...</h2><p>...</p>",
  "faq": [{"q": "...", "a": "..."}],
  "sources": ["Publisher, <a href=\"...\" rel=\"noopener\">\"Title\"</a>, Month Year.", "..."]
}
```

Then run:

```
python3 tools/publish_article.py articles/<slug>.json
```

The script validates, renders the page, rebuilds `/blog/`, updates
`sitemap.xml` and `llms.txt`, marks the topic published in the queue, and
commits. It refuses to publish on any rule breach and tells you which. Fix and
rerun rather than bypassing it.

## Then

`git push` (from the Mac mini, which holds the credentials). Cloudflare Pages
builds in about 60 seconds. Verify the live URL returns 200 and the JSON-LD
parses before reporting done.
