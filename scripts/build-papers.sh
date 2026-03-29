#!/usr/bin/env bash
# Compile LaTeX papers and copy PDFs into site-next for serving.
# Run on VPS after git pull, before site build.
#
# Full deploy sequence:
#   git pull
#   bash scripts/build-papers.sh
#   cd site-next && npm run build
#   bash scripts/build-papers.sh --copy-standalone
#   sudo systemctl restart deepwork-site
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SITE_PUBLIC="$REPO_ROOT/site-next/public/papers"
STANDALONE_DIR="$REPO_ROOT/site-next/.next/standalone/site-next"

mkdir -p "$SITE_PUBLIC"

# If --copy-standalone flag is passed, copy public+static into standalone and exit.
# This is the post-build step needed because Next.js standalone excludes these.
if [ "${1:-}" = "--copy-standalone" ]; then
  echo "Copying static assets into standalone output..."
  mkdir -p "$STANDALONE_DIR/public" "$STANDALONE_DIR/.next/static"
  cp -r "$REPO_ROOT/site-next/public/"* "$STANDALONE_DIR/public/"
  cp -r "$REPO_ROOT/site-next/.next/static/"* "$STANDALONE_DIR/.next/static/"
  echo "Done."
  exit 0
fi

# --- reasoning-gaps ---
PAPER_DIR="$REPO_ROOT/projects/reasoning-gaps/paper"
if [ -f "$PAPER_DIR/main.tex" ]; then
  echo "Compiling reasoning-gaps paper..."
  cd "$PAPER_DIR"
  pdflatex -interaction=nonstopmode main.tex > /dev/null 2>&1
  pdflatex -interaction=nonstopmode main.tex > /dev/null 2>&1  # second pass for cross-refs
  cp main.pdf "$SITE_PUBLIC/reasoning-gaps.pdf"
  echo "  → reasoning-gaps.pdf ($(du -h main.pdf | cut -f1))"
fi

# Add future papers here following the same pattern.

echo "Done. Papers ready in $SITE_PUBLIC"
