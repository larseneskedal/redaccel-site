# Render Deployment Guide

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

