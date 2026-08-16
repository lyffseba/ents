#!/usr/bin/env bash
# Push the current branch to Hugging Face. GitHub main is PR-protected.
set -euo pipefail
cd "$(dirname "$0")/../.."

branch="$(git rev-parse --abbrev-ref HEAD)"
echo "📦 Hugging Face: pushing ${branch} -> hf/main"
if [[ "$branch" == "main" ]]; then
    git push hf main
else
    git push hf "${branch}:main"
fi

echo "🐙 GitHub: origin/${branch} (will not force main)"
if [[ "$branch" == "main" ]]; then
    echo "GitHub main is PR-protected. Open a branch + pull request."
    exit 1
fi
git push -u origin "$branch"
echo "✅ Remotes updated. Open a PR to land on GitHub main."
