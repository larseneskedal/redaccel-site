# Render Deployment Guide

## If you can’t find the Redaccel service on Render

The site is deployed from this repo to Render; the service only exists in **your** Render account. If you don’t see it:

1. **Log in to the right account**  
   Go to [dashboard.render.com](https://dashboard.render.com). The Redaccel service may be under a different email (e.g. work vs personal) or a **team** – switch teams with the dropdown at the top if you’re in one.

2. **Check if the service was deleted**  
   Inactive or deleted services disappear from the dashboard. If it’s gone, create a new one (see “Create a new Web Service” below).

3. **Search**  
   Use the dashboard search for “redaccel” or “redaccel-site” (repo name: `larseneskedal/redaccel-site`).

### Create a new Web Service (if the old one is gone)

1. **Dashboard** → **New +** → **Web Service**.
2. **Connect repository**: choose **GitHub** and connect `larseneskedal/redaccel-site` (or the repo that contains this code). Authorize Render if asked.
3. **Settings:**
   - **Name**: e.g. `redaccel` or `redaccel-site`
   - **Branch**: `main`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn redaccel_app:app`
   - **Instance type**: Free or paid, as you prefer
4. **Environment**: Add the variables from section 2 below (MAIL_*, etc.).
5. **Create Web Service**. Render will build and deploy; you’ll get a URL like `https://redaccel-xxxx.onrender.com`.

### Point redaccel.com and www.redaccel.com at Render

- In **Render**: open your service → **Settings** → **Custom Domains** → **Add Custom Domain**. Add:
  - `www.redaccel.com` (recommended as primary)
  - `redaccel.com` (apex/root)
- Render will show the DNS records to use (CNAME for www, and A/ALIAS for apex if supported).
- In **your domain registrar** (where you bought redaccel.com): set the records Render gives you. For `www` you usually add a CNAME: `www` → `your-service-name.onrender.com` (or the exact host Render shows). For `redaccel.com` (apex), use the A record or ALIAS Render provides.
- After DNS propagates, Render will issue SSL for both. The app now **redirects `redaccel.com` → `https://www.redaccel.com`** (301), so once both domains point to Render, the redirect will work.

### Hostinger DNS: avoid multiple A records for root

If Render says it “verified” the domain but **cannot issue a certificate for redaccel.com**, the cause is often **multiple A records** for the root domain (`@`) in Hostinger:

- **Keep only one A record** for `@`: **216.24.57.1** (Render’s IP from the Custom Domain popup).
- **Delete any other A records** for `@` that point to other IPs (e.g. old Hostinger hosting like `3.136.232.26` or `3.137.108.170`). Having more than one A record sends traffic to different servers and breaks SSL issuance and the redirect.
- **www** should have a single CNAME: `www` → `redaccel-site.onrender.com` (no extra A records for `www`).
- After fixing DNS, wait for propagation (up to 24–48 hours, often less), then in Render use “Verify” or refresh the custom domain so it can issue the certificate for `redaccel.com`.

---

## Steps to Deploy to Render

### 1. Push Code to GitHub
Make sure all your code changes are committed and pushed to GitHub:
```bash
git add .
git commit -m "Update email configuration for Hostinger"
git push origin main
```

### 2. Configure Environment Variables in Render

Go to your Render dashboard and add these environment variables:

1. **MAIL_SERVER**: `smtp.hostinger.com`
2. **MAIL_PORT**: `465`
3. **MAIL_USERNAME**: `contact@redaccel.com`
4. **MAIL_PASSWORD**: *(set this in Render — do not store passwords in the repo)*
5. **MAIL_DEFAULT_SENDER**: `contact@redaccel.com`

**How to add environment variables in Render:**
- Go to your service in Render dashboard
- Click on "Environment" in the left sidebar
- Click "Add Environment Variable"
- Add each variable one by one

### 3. Render Service Configuration

Make sure your Render service is configured with:
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn redaccel_app:app`
- **Python Version**: 3.11 or 3.12 (check your requirements)

### 4. Important Notes

- **Never commit `.env` file to GitHub** - it contains sensitive passwords
- Render automatically sets the `PORT` environment variable - the app will use it
- The app will automatically use production settings when deployed (debug mode disabled)
- After adding environment variables, Render will automatically redeploy your service

### 5. Testing

After deployment:
1. Visit your Render URL
2. Fill out the "Get Started" form
3. Check `contact@redaccel.com` inbox for the email

## Troubleshooting

If emails aren't sending:
1. Check Render logs for error messages
2. Verify all environment variables are set correctly
3. Try changing `MAIL_PORT` to `587` if port 465 doesn't work
4. Make sure your Hostinger email password is correct

