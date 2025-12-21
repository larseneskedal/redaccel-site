#!/bin/bash

# Simple deployment script for Redaccel website
# This will commit changes, push to GitHub, and Render will auto-deploy

set -e

echo "🚀 Starting deployment..."

# Check if git is initialized
if [ ! -d .git ]; then
    echo "📦 Initializing git repository..."
    git init
    echo "✅ Git initialized"
fi

# Check if remote exists
if ! git remote | grep -q origin; then
    echo ""
    echo "⚠️  No GitHub remote found!"
    echo "Please run: git remote add origin YOUR_GITHUB_REPO_URL"
    echo "Example: git remote add origin https://github.com/yourusername/redaccel-website.git"
    exit 1
fi

# Add all changes
echo "📝 Staging changes..."
git add .

# Check if there are changes to commit
if git diff --staged --quiet; then
    echo "✅ No changes to commit"
else
    # Commit changes
    echo "💾 Committing changes..."
    git commit -m "Update website: $(date +'%Y-%m-%d %H:%M:%S')" || {
        echo "⚠️  No changes to commit"
    }
fi

# Push to GitHub
echo "📤 Pushing to GitHub..."
git push origin main || git push origin master

echo ""
echo "✅ Deployment complete!"
echo "🔄 Render will automatically deploy in a few moments"
echo "📧 Check your Render dashboard for deployment status"

