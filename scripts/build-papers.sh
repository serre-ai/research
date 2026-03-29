#!/usr/bin/env bash
# Compile LaTeX papers and copy PDFs into site-next for serving.
# Run on VPS after git pull, before site build/restart.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SITE_PUBLIC="$REPO_ROOT/site-next/public/papers"
mkdir -p "$SITE_PUBLIC"

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
