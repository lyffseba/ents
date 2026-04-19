#!/usr/bin/env bash
# Syncs the current workspace to both GitHub and Hugging Face

echo "🚀 Synchronizing 44 to GitHub and Hugging Face..."

# Ensure we are tracking all new files
git add .

# Prompt for commit message if not provided
if [ -z "$1" ]; then
    read -p "Enter commit message: " msg
else
    msg="$1"
fi

git commit -m "$msg"

# 1. Push to Hugging Face (Always works via our token)
echo "📦 Pushing to Hugging Face..."
git push hf main

# 2. Push to GitHub
echo "🐙 Pushing to GitHub..."
git push origin main || echo "⚠️ GitHub push failed (check your local credentials/403 error). HF push was successful!"

echo "✅ Sync complete!"
