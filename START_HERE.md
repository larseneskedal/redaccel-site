# 🚀 START HERE - API Setup

## 📍 Where to Add Your API Keys

**File to edit:** `.env` (in this folder)

If the `.env` file doesn't exist, copy the template:
```bash
cp ENV_TEMPLATE.txt .env
```

---

## 🔗 Get Your API Keys (Click the Links)

### 1. Reddit API (Required)
**👉 https://www.reddit.com/prefs/apps**

Steps:
- Click "create another app" or "create app"
- Choose "script" type
- Copy the Client ID (under app name)
- Copy the Secret
- Format: `RedditCommentTool/1.0 by yourusername`

---

### 2. OpenAI API (Required)
**👉 https://platform.openai.com/api-keys**

Steps:
- Create new secret key
- Copy it immediately
- Add credits: https://platform.openai.com/account/billing

---

### 3. Ahrefs API (Optional)
**👉 https://ahrefs.com/api**

Steps:
- Sign up for Ahrefs
- Get API token
- (Tool works without this, but better with it)

---

## ✏️ Edit Your .env File

Open `.env` and replace these lines:

```env
REDDIT_CLIENT_ID=paste_here
REDDIT_CLIENT_SECRET=paste_here
REDDIT_USER_AGENT=RedditCommentTool/1.0 by yourusername

OPENAI_API_KEY=sk-paste_here

AHREFS_API_TOKEN=paste_here
```

---

## ✅ Verify Setup

1. Start server: `python3 app.py`
2. Open: http://localhost:5000
3. Check the status bar - it shows which APIs are configured

---

## 📚 More Help

- **Detailed Guide:** `API_SETUP.md`
- **Quick Reference:** `SETUP_QUICK_START.txt`

