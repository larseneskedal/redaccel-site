# Deploying the new redaccel.com (static site in `/site`)

The rebuilt site is fully static — no Python, no build step. It lives in `site/`.
The old Flask app remains untouched at the repo root until you're ready to retire it.

## Cloudflare Pages (recommended, free)

1. Cloudflare dashboard → **Workers & Pages → Create → Pages → Connect to Git** → pick this repo.
2. Settings:
   - **Production branch:** `main` (after merging) or this feature branch to preview
   - **Root directory:** `site`
   - **Build command:** *(leave empty)*
   - **Build output directory:** `/`
3. Deploy. You'll get a `*.pages.dev` preview URL immediately.
4. **Custom domain:** Pages project → Custom domains → add `redaccel.com` (and `www.redaccel.com`).

## Audit form (one-time, ~5 minutes)

The form POSTs to `/api/audit`, handled by `site/functions/api/audit.js` (a Pages
Function — deployed automatically with the site). It emails submissions via
Resend's free tier (100 emails/day):

1. Create a free account at https://resend.com → API Keys → create key.
2. Cloudflare Pages project → **Settings → Environment variables** → add
   `RESEND_API_KEY` = your key (Production).
3. Optional: verify your domain in Resend and set `AUDIT_FROM` to e.g.
   `Redaccel <audit@redaccel.com>`; set `AUDIT_TO` if you want a different inbox
   than contact@redaccel.com.

Until the key is set, the form shows visitors a mailto fallback to
contact@redaccel.com — no lead is silently lost.

## After go-live checklist

- Check https://redaccel.com/llms.txt and /llms-full.txt resolve.
- Validate structured data: https://validator.schema.org against each page.
- Submit https://redaccel.com/sitemap.xml in Google Search Console.
- Data points on the pages are sourced as of July 2026 — refresh them every
  quarter or two; they age fast and stale numbers cost credibility (and citations).
