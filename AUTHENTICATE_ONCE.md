# One-Time Authentication Setup

To enable auto-deployment, you need to authenticate with GitHub **once**. After this, I can push automatically for you.

## Quick Setup (Choose One):

### Option 1: Personal Access Token (Recommended)
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Name it: "Redaccel Auto-Deploy"
4. Check: `repo` (full control of private repositories)
5. Click "Generate token"
6. Copy the token
7. Run this command (paste your token when prompted):
   ```bash
   git push origin main
   ```
   When asked for password, paste your token (not your GitHub password)

### Option 2: GitHub CLI (Easiest)
```bash
# Install GitHub CLI if needed: brew install gh
gh auth login
# Follow the prompts, then:
git push origin main
```

### Option 3: Manual Push Once
Just run this once in terminal:
```bash
cd /Users/johanlarsen/Redaccel-Website-Build
git push origin main
```
Enter your GitHub credentials when prompted. macOS will save them.

---

**After you authenticate once, I can push automatically for you!** 🚀

