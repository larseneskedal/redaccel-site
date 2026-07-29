// Cloudflare Pages Function: handles POST /api/audit
//
// Forwards audit requests to contact@redaccel.com via Resend (free tier: 100 emails/day).
// Setup (one time): create a free API key at https://resend.com, then in the
// Cloudflare Pages project set an environment variable RESEND_API_KEY.
// Until the key is set, submissions return 503 and the site's JS shows the
// email fallback, so no lead is ever silently lost.

export async function onRequestPost({ request, env }) {
  let data;
  try {
    data = await request.json();
  } catch {
    return json({ error: 'Invalid JSON' }, 400);
  }

  const brand = clean(data.brand);
  const website = clean(data.website);
  const category = clean(data.category);
  const competitors = clean(data.competitors);
  const email = clean(data.email);

  if (!brand || !website || !category || !competitors || !email || !email.includes('@')) {
    return json({ error: 'All fields are required' }, 400);
  }

  if (!env.RESEND_API_KEY) {
    return json({ error: 'Form backend not configured' }, 503);
  }

  const body = [
    'New free AI visibility audit request',
    '',
    `Brand:       ${brand}`,
    `Website:     ${website}`,
    `Category:    ${category}`,
    `Competitors: ${competitors}`,
    `Reply to:    ${email}`,
    '',
    `Received:    ${new Date().toISOString()} (48h clock starts now)`,
  ].join('\n');

  const res = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${env.RESEND_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      from: env.AUDIT_FROM || 'Redaccel Audit <onboarding@resend.dev>',
      to: [env.AUDIT_TO || 'contact@redaccel.com'],
      reply_to: email,
      subject: `Audit request: ${brand} (${category})`,
      text: body,
    }),
  });

  if (!res.ok) {
    return json({ error: 'Delivery failed' }, 502);
  }
  return json({ ok: true });
}

function clean(v) {
  return typeof v === 'string' ? v.trim().slice(0, 500) : '';
}

function json(obj, status = 200) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}
