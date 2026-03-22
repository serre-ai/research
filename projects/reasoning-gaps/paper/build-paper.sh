#!/bin/bash
# Build the complete NeurIPS submission package from raw evaluation data.
# Usage: ./build-paper.sh [--skip-analysis] [--skip-compile] [--final]
#
# Steps:
#   1. Activate Python venv and set working directory
#   2. Run analysis pipeline (tables, figures, stats)
#   3. Compile LaTeX (pdflatex or tectonic)
#   4. Validate page count
#   5. Create submission.zip
#   6. Print summary
set -e

# ============================================================
# Configuration
# ============================================================

PAGE_LIMIT=9          # NeurIPS main content limit
WARN_PAGES=18         # Total pages (content + refs + appendix) above which to warn
BOOTSTRAP_N=10000     # Bootstrap resamples for CIs

# ============================================================
# Parse flags
# ============================================================

SKIP_ANALYSIS=false
SKIP_COMPILE=false
FINAL_MODE=false

for arg in "$@"; do
  case "$arg" in
    --skip-analysis) SKIP_ANALYSIS=true ;;
    --skip-compile)  SKIP_COMPILE=true ;;
    --final)         FINAL_MODE=true ;;
    --help|-h)
      echo "Usage: ./build-paper.sh [--skip-analysis] [--skip-compile] [--final]"
      echo ""
      echo "  --skip-analysis   Skip the Python analysis pipeline (reuse existing tables/figures)"
      echo "  --skip-compile    Skip LaTeX compilation (only regenerate analysis)"
      echo "  --final           Build camera-ready version (adds [final] option to style)"
      echo ""
      exit 0
      ;;
    *)
      echo "Unknown flag: $arg"
      exit 1
      ;;
  esac
done

# ============================================================
# Resolve directories
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PAPER_DIR="$SCRIPT_DIR"
PROJECT_DIR="$(cd "$PAPER_DIR/.." && pwd)"
BENCHMARKS_DIR="$PROJECT_DIR/benchmarks"
RESULTS_DIR="$BENCHMARKS_DIR/results"
ANALYSIS_DIR="$RESULTS_DIR/analysis"

echo "========================================"
echo "  NeurIPS Submission Build Pipeline"
echo "========================================"
echo ""
echo "Paper dir:     $PAPER_DIR"
echo "Benchmarks:    $BENCHMARKS_DIR"
echo "Results:       $RESULTS_DIR"
echo "Analysis:      $ANALYSIS_DIR"
if [ "$FINAL_MODE" = true ]; then
  echo "Mode:          CAMERA-READY (final)"
else
  echo "Mode:          submission (anonymous)"
fi
echo ""

# ============================================================
# Step 1: Activate Python venv
# ============================================================

VENV_PATHS=(
  "$PROJECT_DIR/../../.venv"        # repo-root .venv (local)
  "$HOME/deepwork/.venv"            # VPS standard path
  "$BENCHMARKS_DIR/.venv"           # benchmarks-local venv
)

VENV_FOUND=false
for vp in "${VENV_PATHS[@]}"; do
  if [ -f "$vp/bin/activate" ]; then
    echo "[1/6] Activating venv: $vp"
    source "$vp/bin/activate"
    VENV_FOUND=true
    break
  fi
done

if [ "$VENV_FOUND" = false ]; then
  echo "[1/6] WARNING: No Python venv found. Trying system Python..."
  echo "       Searched: ${VENV_PATHS[*]}"
fi

# ============================================================
# Step 2: Run analysis pipeline
# ============================================================

if [ "$SKIP_ANALYSIS" = true ]; then
  echo "[2/6] Skipping analysis (--skip-analysis)"
else
  echo "[2/6] Running analysis pipeline..."

  if [ ! -d "$RESULTS_DIR" ]; then
    echo "ERROR: Results directory not found: $RESULTS_DIR"
    exit 2
  fi

  # Run the figure generation via the plotting pipeline
  cd "$PROJECT_DIR"
  python3 -c "
import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'paper/supplementary/code')
from analysis.loader import load_results
from analysis.plots import generate_all_figures
df = load_results('$RESULTS_DIR')
print(f'Loaded {len(df)} records, {df[\"model\"].nunique()} models, {df[\"task\"].nunique()} tasks')
generate_all_figures(df, '$ANALYSIS_DIR/figures')
"

  # Run analyze.py if it exists (generates stats.tex and tables)
  if [ -f "$BENCHMARKS_DIR/analyze.py" ]; then
    cd "$BENCHMARKS_DIR"
    python3 analyze.py \
      --results-dir "$RESULTS_DIR" \
      --output-dir "$ANALYSIS_DIR" \
      --n-bootstrap "$BOOTSTRAP_N" 2>&1 || echo "WARNING: analyze.py failed, continuing with existing stats"
  fi

  echo ""
  echo "       Analysis complete. Output in $ANALYSIS_DIR"

  # Ensure stats.tex exists (the paper \input's it)
  STATS_FILE="$ANALYSIS_DIR/stats.tex"
  if [ ! -f "$STATS_FILE" ]; then
    echo "       Note: stats.tex not generated, creating empty stub"
    mkdir -p "$ANALYSIS_DIR"
    echo "% Auto-generated stats placeholder" > "$STATS_FILE"
  fi
fi

# ============================================================
# Step 3: Compile LaTeX
# ============================================================

if [ "$SKIP_COMPILE" = true ]; then
  echo "[3/6] Skipping LaTeX compilation (--skip-compile)"
else
  echo "[3/6] Compiling LaTeX..."

  cd "$PAPER_DIR"

  # Ensure stats.tex exists before compilation
  STATS_FILE="$ANALYSIS_DIR/stats.tex"
  if [ ! -f "$STATS_FILE" ]; then
    mkdir -p "$ANALYSIS_DIR"
    echo "% Auto-generated stats placeholder" > "$STATS_FILE"
  fi

  # Select compiler: prefer tectonic, fall back to pdflatex
  if command -v tectonic &> /dev/null; then
    echo "       Using tectonic"
    tectonic main.tex
  elif command -v pdflatex &> /dev/null; then
    echo "       Using pdflatex (2 passes for references)"
    pdflatex -interaction=nonstopmode main.tex > /dev/null 2>&1
    pdflatex -interaction=nonstopmode main.tex > /dev/null 2>&1
  else
    echo "ERROR: No LaTeX compiler found (tried tectonic, pdflatex)"
    exit 3
  fi

  echo "       Compilation successful."
fi

# ============================================================
# Step 4: Validate page count
# ============================================================

echo "[4/6] Validating submission..."

if [ -f "main.pdf" ]; then
  # Get page count
  if command -v pdfinfo &> /dev/null; then
    PAGES=$(pdfinfo main.pdf 2>/dev/null | grep "Pages:" | awk '{print $2}')
  else
    # Fallback: count pages via strings
    PAGES=$(strings main.pdf | grep -c "/Type /Page" 2>/dev/null || echo "?")
  fi

  echo "       Total pages: $PAGES"

  if [ "$PAGES" != "?" ]; then
    if [ "$PAGES" -gt "$WARN_PAGES" ]; then
      echo "       WARNING: Paper has $PAGES pages (expected ~$WARN_PAGES)"
    fi
  fi

  # Check file size (NeurIPS limit: 50MB)
  PDF_BYTES=$(wc -c < main.pdf)
  PDF_MB=$((PDF_BYTES / 1048576))
  if [ "$PDF_MB" -gt 45 ]; then
    echo "       WARNING: PDF is ${PDF_MB}MB (NeurIPS limit: 50MB)"
  fi
fi

# ============================================================
# Step 5: Create submission package
# ============================================================

echo "[5/6] Creating submission package..."

cd "$PAPER_DIR"

SUBMISSION_ZIP="$PAPER_DIR/submission.zip"
rm -f "$SUBMISSION_ZIP"

ZIP_FILES=()

# main.pdf
if [ -f "main.pdf" ]; then
  ZIP_FILES+=("main.pdf")
else
  echo "       WARNING: main.pdf not found — was compilation skipped?"
fi

# Source files needed for compilation
ZIP_FILES+=("main.tex")
[ -f "neurips_2026.sty" ] && ZIP_FILES+=("neurips_2026.sty")
[ -f "main.bbl" ] && ZIP_FILES+=("main.bbl")

# Create zip with paper files
if [ ${#ZIP_FILES[@]} -gt 0 ]; then
  zip -q "$SUBMISSION_ZIP" "${ZIP_FILES[@]}"
fi

# Add analysis output (figures, tables, stats)
if [ -d "$ANALYSIS_DIR" ]; then
  cd "$PROJECT_DIR"
  zip -qr "$SUBMISSION_ZIP" "benchmarks/results/analysis/"
  cd "$PAPER_DIR"
else
  echo "       WARNING: analysis directory not found"
fi

echo "       Created: $SUBMISSION_ZIP"

# ============================================================
# Step 6: Summary
# ============================================================

echo ""
echo "[6/6] Build Summary"
echo "========================================"

if [ -f "main.pdf" ]; then
  PDF_SIZE=$(ls -lh main.pdf | awk '{print $5}')
  echo "  Pages:     ${PAGES:-?}"
  echo "  PDF size:  $PDF_SIZE"
fi

if [ -f "$SUBMISSION_ZIP" ]; then
  ZIP_SIZE=$(ls -lh "$SUBMISSION_ZIP" | awk '{print $5}')
  echo "  ZIP size:  $ZIP_SIZE"
fi

echo "  Timestamp: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo ""
echo "  Output files:"
[ -f "main.pdf" ] && echo "    - main.pdf"
[ -f "$SUBMISSION_ZIP" ] && echo "    - submission.zip"
echo ""

# Final checks
echo "  Pre-submission checks:"
if grep -q "\\\\todo{" main.tex 2>/dev/null; then
  echo "    WARNING: \\todo{} macros found in main.tex — remove before submission"
else
  echo "    [ok] No \\todo{} macros"
fi

if grep -q "answerTODO" main.tex 2>/dev/null; then
  echo "    WARNING: Unanswered checklist items found"
else
  echo "    [ok] All checklist items answered"
fi

if grep -q "\\\\begin{ack}" main.tex 2>/dev/null; then
  echo "    [ok] Acknowledgments section present"
else
  echo "    WARNING: No \\begin{ack} section"
fi

echo ""
echo "Done."
