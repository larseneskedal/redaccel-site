# 🔑 API Setup Guide

Quick guide to get all the API keys you need for the Reddit Comment Tool.

## 📋 Required APIs

### 1. Reddit API (Required)
**Get your credentials here:** https://www.reddit.com/prefs/apps

**Steps:**
1. Go to https://www.reddit.com/prefs/apps
2. Scroll down and click **"create another app..."** or **"create app"**
3. Fill in:
   - **Name:** RedditCommentTool (or any name)
   - **App type:** Select **"script"**
   - **Description:** (optional)
   - **About URL:** (leave blank)
   - **Redirect URI:** `http://localhost:8080` (required but not used)
4. Click **"create app"**
5. You'll see:
   - **Client ID:** The string under your app name (looks like: `abc123def456`)
   - **Client Secret:** The "secret" field (looks like: `xyz789_secret_key`)
6. **User Agent:** Format: `YourAppName/1.0 by YourRedditUsername`
   - Example: `RedditCommentTool/1.0 by johndoe`

**Direct Link:** https://www.reddit.com/prefs/apps

---

### 2. OpenAI API (Required for Comment Generation)
**Get your API key here:** https://platform.openai.com/api-keys

**Steps:**
1. Go to https://platform.openai.com/api-keys
2. Sign up or log in to your OpenAI account
3. Click **"Create new secret key"**
4. Give it a name (e.g., "Reddit Comment Tool")
5. Copy the key immediately (you won't see it again!)
6. Make sure you have credits in your account: https://platform.openai.com/account/billing

**Direct Link:** https://platform.openai.com/api-keys
**Billing/Credits:** https://platform.openai.com/account/billing

---

### 3. Ahrefs API (Optional - for Search Traffic Data)
**Get your API token here:** https://ahrefs.com/api

**Steps:**
1. Go to https://ahrefs.com/api
2. Sign up for an Ahrefs account (they have free trials)
3. Navigate to API settings
4. Generate an API token
5. Copy the token

**Note:** This is optional. The tool works without it, but you'll only get engagement-based rankings instead of search traffic rankings.

**Direct Link:** https://ahrefs.com/api
**Ahrefs Pricing:** https://ahrefs.com/pricing

---

## 🚀 Quick Setup

### Option 1: Edit .env file directly

1. Open the `.env` file in this folder
2. Replace the placeholder values with your actual API keys:

```env
# Reddit API
REDDIT_CLIENT_ID=your_actual_client_id_here
REDDIT_CLIENT_SECRET=your_actual_secret_here
REDDIT_USER_AGENT=RedditCommentTool/1.0 by yourusername

# OpenAI API
OPENAI_API_KEY=sk-your_actual_openai_key_here

# Ahrefs API (optional)
AHREFS_API_TOKEN=your_ahrefs_token_here
```

3. Save the file
4. Restart the server if it's running

### Option 2: Use the web interface

The web interface will show you which APIs are configured. You can also set promotion info directly in the UI without editing files.

---

## ✅ Verification

After adding your keys, the web interface will show:
- ✓ Green checkmark = API configured
- ⚠️ Warning = API not configured

---

## 💡 Tips

- **Reddit API:** Free, but has rate limits (60 requests per minute)
- **OpenAI API:** Pay-as-you-go, very cheap for this use case (~$0.01 per 100 comments)
- **Ahrefs API:** Paid service, but optional - tool works without it

---

## 🔗 Quick Links Summary

| API | Link | Required? |
|-----|------|-----------|
| Reddit | https://www.reddit.com/prefs/apps | ✅ Yes |
| OpenAI | https://platform.openai.com/api-keys | ✅ Yes |
| Ahrefs | https://ahrefs.com/api | ⚪ Optional |

---

## 🆘 Need Help?

- **Reddit API Issues:** Check https://www.reddit.com/r/redditdev
- **OpenAI Issues:** Check https://help.openai.com
- **Ahrefs Issues:** Check https://ahrefs.com/support

