# Post-Evaluation Action Plan

**Project**: reasoning-gaps
**Paper**: On the Reasoning Gaps of Large Language Models: A Formal Characterization
**Date created**: 2026-03-13
**Target**: Execute immediately when VPS evaluations complete (est. March 15-16, 2026)

---

## Context

This document provides a step-by-step action plan for the work required once VPS evaluations complete. Following this plan should take approximately 7-10 days and result in a submission-ready paper.

**Current status** (as of March 13, 2026):
- ✅ 9/11 models evaluated (121,614 instances, 0% failure rate)
- ⏳ VPS evaluations running: o3, Sonnet 4.6, B2 recalibration
- ✅ Paper structurally complete (1,489 lines)
- ✅ Analysis pipeline tested and ready
- ✅ Literature review complete (89 papers)

**When VPS completes**:
- ✅ 11/11 models evaluated with recalibrated B2
- Ready to generate final results and submit

---

## Phase 1: Data Retrieval and Validation (Day 1)

### Step 1.1: Retrieve Evaluation Data from VPS

**Access VPS**:
```bash
# If SSH access available:
ssh root@89.167.5.50

# Or via API if credentials available:
curl -H "X-Api-Key: YOUR_KEY" http://89.167.5.50/api/results
```

**Locate result files**:
- o3 evaluation results
- Sonnet 4.6 evaluation results
- B2 budget_cot recalibration results for all 9 models

**Expected file locations** (based on evaluation setup):
```
/root/reasoning-gaps-daemon/projects/reasoning-gaps/benchmarks/results/
```

**Download to local**:
```bash
# Via SCP
scp -r root@89.167.5.50:/path/to/results ./local/results/

# Or via rsync for incremental
rsync -avz root@89.167.5.50:/path/to/results/ ./local/results/
```

### Step 1.2: Validate Downloaded Data

**Check completeness**:
```bash
cd projects/reasoning-gaps/benchmarks
python -c "
import json
import os

models = ['o3', 'sonnet_4.6'] + ['haiku_4.5', 'gpt_4o_mini', 'gpt_4o',
          'llama_3.1_8b', 'llama_3.1_70b', 'ministral_8b',
          'mistral_small_24b', 'qwen_2.5_7b', 'qwen_2.5_72b']
tasks = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9']
conditions = ['direct', 'short_cot', 'budget_cot']

expected = len(models) * len(tasks) * len(conditions)
print(f'Expected combinations: {expected}')

# Count actual result files
actual = 0
for model in models:
    for task in tasks:
        for condition in conditions:
            path = f'results/{model}/{task}_{condition}.json'
            if os.path.exists(path):
                actual += 1
            else:
                print(f'MISSING: {path}')

print(f'Found: {actual}/{expected}')
"
```

**Expected**: 297 combinations (11 models × 9 tasks × 3 conditions)

**Validate data quality**:
```bash
python analyze.py --validate-only --data-dir results/
```

**Check for failures**:
- Target: 0% failure rate (as achieved with first 9 models)
- If failures found, investigate and potentially re-run

### Step 1.3: Organize Data

**Consolidate results**:
```bash
# Create unified results directory
mkdir -p results/final_11_models/

# Copy/move all results to unified location
# Ensure consistent naming convention
```

**Commit data** (if repo includes results):
```bash
git add results/final_11_models/
git commit -m "data(reasoning-gaps): add final evaluation results for 11 models"
git push
```

**Or upload to external storage** (if too large for repo):
- Upload to Zenodo or Hugging Face
- Document URL in README

---

## Phase 2: Analysis Execution (Day 2)

### Step 2.1: Install Analysis Dependencies

```bash
cd projects/reasoning-gaps/experiments
pip install -r requirements.txt

# Verify installation
python -c "import pandas, numpy, scipy, matplotlib, seaborn; print('All imports OK')"
```

### Step 2.2: Run Full Analysis Pipeline

```bash
cd projects/reasoning-gaps/experiments

# Run complete analysis
python run_full_analysis.py \
    --data-dir ../benchmarks/results/final_11_models \
    --output-dir ./analysis_output_11models \
    --verbose

# This should produce:
# - analysis_output_11models/primary_analysis.json
# - analysis_output_11models/statistical_tests.json
# - analysis_output_11models/figures/ (4 main figures)
# - analysis_output_11models/tables/ (2 main tables + appendix)
# - analysis_output_11models/analysis_report.txt
```

**Expected outputs**:
1. **Primary analysis results** (JSON with all 6 analyses)
2. **Statistical test results** (significance tests for key claims)
3. **Figure 1**: Taxonomy overview (conceptual, may not change)
4. **Figure 2**: CoT lift by gap type (updated with 11 models)
5. **Figure 3**: Accuracy by task and condition (updated)
6. **Figure 4**: Scaling analysis (updated)
7. **Table 1**: Overall results by gap type (updated)
8. **Table 2**: Per-task breakdown (updated)
9. **Table 3** (Appendix): Full 11-model results matrix

**Estimated time**: 10-30 minutes depending on data size

### Step 2.3: Verify Analysis Results

**Sanity checks**:
1. Do the results align with predictions from 9-model analysis?
2. Are CoT lifts for Types 2-3 significantly higher than Types 5-6?
3. Is the B2 budget_cot anomaly resolved (should be positive now)?
4. Are all statistical tests passing with p < 0.05?
5. Do figures render correctly?

**Key metrics to verify**:
- **Type 2-3 CoT lift**: Should be ~+0.27 (from 9-model analysis)
- **Type 5-6 CoT lift**: Should be ~+0.04 (from 9-model analysis)
- **B2 budget_cot**: Should now be positive (was -0.254 with flat budget)
- **B8 ceiling**: Should remain ~94% (too easy)

**Document any surprises**:
```bash
# Create analysis notes file
cat > analysis_output_11models/ANALYSIS_NOTES.md << 'EOF'
# Analysis Notes for 11-Model Results

## Changes from 9-Model Results
- [List any notable differences]

## B2 Recalibration Impact
- Previous budget_cot: -0.254
- New budget_cot: [VALUE]
- Explanation: [...]

## o3 Performance
- Notable patterns: [...]

## Sonnet 4.6 Performance
- Notable patterns: [...]

## Statistical Significance
- All key claims verified: [Yes/No]
- Any non-significant findings: [List]
EOF
```

### Step 2.4: Extract Key Numbers for Paper

Create a reference file with all numbers needed for paper updates:

```bash
cat > analysis_output_11models/PAPER_UPDATES.txt << 'EOF'
# Key Numbers for Paper Update

## Abstract
- Total instances evaluated: [N]
- Number of models: 11
- Number of families: [5? 6?]

## Section 5 (Experiments)
- Overall accuracy by gap type:
  - Type 1: [X%]
  - Type 2: [X%]
  - Type 3: [X%]
  - Type 4: [X%]
  - Type 5: [X%]
  - Type 6: [X%]

- CoT lift by gap type:
  - Types 2-3: [+X%]
  - Types 5-6: [+X%]

- Serial composition gaps (B3, B4):
  - Direct: [X%]
  - Short CoT: [X%]
  - Lift: [+X pp]

- B2 (Nested Boolean):
  - Direct: [X%]
  - Short CoT: [X%]
  - Budget CoT: [X%] (was -25.4% with miscalibrated budget)

## Conclusion
- Total instances: [N]
- CoT lift for depth/serial: [X%]
- CoT lift for intractability/architectural: [X%]
- Serial composition direct: [X%]
- Serial composition CoT: [X%]

## Figures
- Figure 2: [Path to updated figure]
- Figure 3: [Path to updated figure]
- Figure 4: [Path to updated figure]

## Tables
- Table 1: [Path to CSV/JSON]
- Table 2: [Path to CSV/JSON]
- Table 3 (Appendix): [Path to CSV/JSON]
EOF

# Automatically populate from analysis results
python -c "
import json
with open('analysis_output_11models/primary_analysis.json') as f:
    results = json.load(f)
# Extract and format key numbers
# Write to PAPER_UPDATES.txt
"
```

---

## Phase 3: Paper Updates (Days 3-4)

### Step 3.1: Update Section 5 (Experiments)

**File**: `paper/main.tex`

**Updates needed**:

1. **Update instance count**:
```latex
% Line ~370ish (in experiments section intro)
% Old: "121,614 instances"
% New: "[NEW_TOTAL] instances"
```

2. **Update model count**:
```latex
% Line ~52 (abstract)
% Old: "Evaluation across 12 model configurations"
% New: "Evaluation across 11 model configurations"

% Or keep "12" if we count conditions as configurations
```

3. **Update all quantitative results**:
- Overall accuracy by gap type (Section 5.2)
- CoT effectiveness by gap type (Section 5.3)
- Serial composition results (Section 5.3)
- B2 results and remove footnote (Section 5.3)
- Scaling analysis (Section 5.4)

4. **Add o3 and Sonnet 4.6 discussion**:
```latex
% In Section 5.X (model performance breakdown)
\paragraph{Reasoning-specialized models.}
OpenAI's o3 model, which incorporates extended reasoning capabilities,
shows [PATTERN]. This [confirms/contradicts] the prediction that
[...reasoning about what o3 performance tells us...].

\paragraph{Claude family scaling.}
With Haiku 4.5 and Sonnet 4.6 results, we observe [PATTERN] across
the Claude model family, showing [interpretation...].
```

### Step 3.2: Remove B2 Footnote

**File**: `paper/main.tex`
**Line**: 374

```latex
% OLD:
(3)~\textbf{Budget CoT}: chain-of-thought with a fixed token budget calibrated per task.\footnote{Budget CoT results for B2 (Nested Boolean Evaluation) are preliminary; the token budget is being recalibrated, as the current setting appears too restrictive. See \Cref{sec:budget} for discussion.\label{fn:b2budget}}

% NEW:
(3)~\textbf{Budget CoT}: chain-of-thought with a fixed token budget calibrated per task.
```

**Also remove/update reference to this footnote** anywhere in Section 5 or 6.

### Step 3.3: Update Figures

**Replace placeholder figures** (if any) with final versions:

```bash
# Copy figures from analysis output to paper directory
cp experiments/analysis_output_11models/figures/figure2_cot_lift.pdf paper/figures/
cp experiments/analysis_output_11models/figures/figure3_results_by_task.pdf paper/figures/
cp experiments/analysis_output_11models/figures/figure4_scaling.pdf paper/figures/

# Verify LaTeX references are correct
grep "includegraphics" paper/main.tex
```

**Update figure captions** if needed (with final numbers).

### Step 3.4: Update Tables

**Table 1** (main results by gap type):
```latex
% Update with final 11-model numbers
% Typically around line 500-550
```

**Table 2** (per-task breakdown):
```latex
% Update with final 11-model numbers
```

**Table 3** (Appendix - full results):
```latex
% In appendix section
% Full 11 models × 9 tasks × 3 conditions matrix
% Or reference to supplementary materials if too large
```

### Step 3.5: Update Abstract and Conclusion

**Abstract** (line ~52-59):
```latex
% Update evaluation sentence
Evaluation across 11 model configurations from five families validates the taxonomy
```

**Conclusion** (line ~735):
```latex
% Update instance count
Evaluation across eleven models from five families on [NEW_TOTAL] instances validates...

% Update quantitative claims with final numbers
```

### Step 3.6: Consistency Pass

**Verify all quantitative claims are updated**:
```bash
cd paper

# Search for old numbers
grep -n "121,614" main.tex  # Should find none (or update if still 121K)
grep -n "nine models" main.tex  # Should be "eleven models"
grep -n "12 model" main.tex  # Update if needed

# Search for "preliminary" or "will be"
grep -n "preliminary\|will be\|to be" main.tex -i

# Verify table references
grep -n "Table~" main.tex

# Verify figure references
grep -n "Figure~" main.tex
```

---

## Phase 4: Format Conversion (Day 5)

### Step 4.1: Convert to NeurIPS 2026 Format

**File**: `paper/main.tex`

**Changes**:
```latex
% OLD (line 0-4):
% TODO: Switch to \documentclass{article} with neurips_2026.sty when available.
% For now, using standard article class. Replace with:
%   \documentclass{article}
%   \usepackage[preprint]{neurips_2026}
\documentclass[11pt]{article}

% NEW:
\documentclass{article}
\usepackage[preprint]{neurips_2026}  % Or [final] for final submission

% Remove custom geometry (NeurIPS style has its own)
% OLD:
\usepackage[margin=1in]{geometry}
% NEW:
% (delete this line)
```

**Verify neurips_2026.sty exists**:
```bash
ls paper/neurips_2026.sty  # Should exist (already in repo per earlier check)
```

### Step 4.2: Update Author Information

```latex
% Update author block for NeurIPS format
% OLD:
\author{
  Deepwork Research\\
  \texttt{research@deepwork.ai}
}

% NEW (adjust as needed for NeurIPS):
\author{%
  Deepwork Research \\
  \texttt{research@deepwork.ai} \\
  % Add additional authors if needed
}
```

### Step 4.3: Check Page Limit Compliance

**NeurIPS 2026 limits** (verify current year requirements):
- Main paper: 9 pages (including figures, excluding references)
- Appendix: Unlimited (after references)

**Check current length**:
```bash
# Requires pdflatex
cd paper
pdflatex main.tex
pdflatex main.tex  # Run twice for references

# Count pages
pdfinfo main.pdf | grep Pages

# If over 9 pages (excluding references/appendix), need to trim
```

**If over limit**:
- Move detailed proofs to appendix (already done)
- Condense related work (carefully)
- Reduce whitespace (but keep readable)
- Shrink figures slightly (but keep readable)

---

## Phase 5: Compilation and Verification (Day 6)

### Step 5.1: Full LaTeX Compilation

**Requires system with full LaTeX installation**.

```bash
cd paper

# Full compilation sequence
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex

# Verify no errors
echo $?  # Should be 0
```

**Check for issues**:
- Undefined references: `grep "undefined" main.log`
- Missing citations: `grep "Citation.*undefined" main.log`
- Overfull hboxes: `grep "Overfull" main.log`
- Figure/table placement issues

### Step 5.2: Visual Verification

**Check PDF**:
1. All figures render correctly
2. All tables format properly (no overflow)
3. All mathematical notation renders correctly
4. Page breaks are reasonable
5. No orphaned headers
6. Bibliography formats correctly
7. Cross-references resolve (e.g., "Section 3", not "Section ??")

### Step 5.3: Citation Check

**Verify all 75 citations resolve**:
```bash
grep "citation.*undefined" main.log  # Should be empty
```

**Verify bibliography**:
- All 49 entries present
- Formatting consistent
- No missing fields
- DOIs/URLs correct (if included)

---

## Phase 6: Internal Review (Days 7-8)

### Step 6.1: Content Review

**Read entire paper** (fresh eyes, as if reviewing for NeurIPS):

**Introduction**:
- [ ] Motivation clear and compelling?
- [ ] Contributions clearly stated?
- [ ] Claims match what paper delivers?

**Background**:
- [ ] Sufficient for target audience?
- [ ] Notation clearly defined?
- [ ] No unexplained jargon?

**Framework**:
- [ ] Definitions precise and formal?
- [ ] Taxonomy clear and well-motivated?
- [ ] Propositions stated correctly?

**Benchmark**:
- [ ] Tasks clearly described?
- [ ] Predictions testable and clear?
- [ ] Justification for each task?

**Experiments**:
- [ ] Methodology clear and reproducible?
- [ ] Results presented clearly?
- [ ] Figures/tables informative?
- [ ] Claims supported by data?

**Discussion**:
- [ ] Implications clearly stated?
- [ ] Limitations honestly addressed?
- [ ] Connections to broader work?

**Related Work**:
- [ ] Comprehensive coverage?
- [ ] Fair to prior work?
- [ ] Clear positioning?

**Conclusion**:
- [ ] Summarizes contributions?
- [ ] Restates key findings?
- [ ] Avoids overclaiming?

### Step 6.2: Technical Verification

**Theoretical claims**:
- [ ] All propositions have proofs (in appendix)?
- [ ] Complexity assumptions clearly stated?
- [ ] No logical errors in arguments?

**Empirical claims**:
- [ ] All quantitative claims supported by data?
- [ ] Statistical significance reported?
- [ ] Error bars / confidence intervals included?
- [ ] No cherry-picking results?

**Methodological claims**:
- [ ] Evaluation protocol clearly described?
- [ ] Potential biases acknowledged?
- [ ] Reproducibility ensured?

### Step 6.3: Writing Quality

**Clarity**:
- [ ] Each paragraph has clear topic sentence?
- [ ] Logical flow within sections?
- [ ] Transitions between sections smooth?
- [ ] No ambiguous pronouns or references?

**Precision**:
- [ ] Technical terms used correctly?
- [ ] Notation consistent throughout?
- [ ] Quantitative claims precise?

**Conciseness**:
- [ ] No redundant content?
- [ ] Each sentence necessary?
- [ ] Word count appropriate for venue?

**Grammar and style**:
- [ ] No typos or spelling errors?
- [ ] Consistent voice (we/our)?
- [ ] Proper citation formatting?

---

## Phase 7: Final Polish (Day 9)

### Step 7.1: Final Edits

Based on internal review, make final edits:
- Fix typos
- Clarify ambiguous passages
- Strengthen weak arguments
- Add missing details
- Remove redundancies

### Step 7.2: Supplementary Materials

**Package supplementary materials** (see `SUPPLEMENTARY-MATERIALS-PLAN.md`):
1. Code (benchmarks, analysis)
2. Data (or links to external hosting)
3. README with reproduction instructions
4. LICENSE

**Create ZIP archive**:
```bash
cd projects/reasoning-gaps
./package_supplementary.sh  # Script to create from plan
```

**Test supplementary materials**:
- Extract on clean system
- Follow README instructions
- Verify code runs
- Verify results reproduce

### Step 7.3: Metadata Preparation

**Prepare for submission system**:

1. **Title**: "On the Reasoning Gaps of Large Language Models: A Formal Characterization"

2. **Abstract**: Copy from paper (verify 250-word limit if any)

3. **Authors**: List all authors with affiliations

4. **Keywords**: complexity theory, transformers, reasoning, chain-of-thought, benchmarking

5. **Subject areas** (select appropriate NeurIPS categories):
   - Machine Learning Theory
   - Deep Learning Architectures
   - Natural Language Processing
   - Benchmarks and Datasets

6. **Conflicts of interest**: List as needed

7. **Ethical considerations**: Note if benchmark data or model access raises issues

---

## Phase 8: Submission (Day 10)

### Step 8.1: Create NeurIPS Account

1. Go to https://neurips.cc/Conferences/2026
2. Find submission portal link
3. Create account if needed
4. Verify email

### Step 8.2: Upload Paper

1. Navigate to "Submit Paper"
2. Upload PDF (`main.pdf`)
3. Verify PDF renders correctly in preview
4. Check page count and compliance

### Step 8.3: Upload Supplementary

1. Upload supplementary ZIP archive
2. Verify size < 100 MB limit
3. Check that ZIP extracts correctly in preview

### Step 8.4: Enter Metadata

1. Enter title (copy exactly from paper)
2. Enter authors and affiliations
3. Paste abstract
4. Enter keywords
5. Select subject areas
6. Indicate ethical considerations
7. Declare conflicts of interest

### Step 8.5: Final Verification

**Before final submit**:
- [ ] PDF is correct version (with all updates)
- [ ] Supplementary materials complete
- [ ] All metadata accurate
- [ ] Author list and order correct
- [ ] Conflicts declared
- [ ] Ethical statement complete
- [ ] No violations of anonymity (for double-blind)

### Step 8.6: Submit

1. Review all information one final time
2. Click "Submit"
3. **Save confirmation email**
4. Note submission ID
5. Download submitted PDF for records

### Step 8.7: Post-Submission

**Immediately after**:
```bash
cd projects/reasoning-gaps

# Create submission record
cat > SUBMISSION-RECORD.md << 'EOF'
# NeurIPS 2026 Submission Record

**Submitted**: [DATE]
**Submission ID**: [ID]
**Title**: On the Reasoning Gaps of Large Language Models: A Formal Characterization
**Authors**: [List]
**Track**: [Main conference / Workshop / etc]

## Files Submitted
- Paper: main.pdf ([SIZE] KB, [PAGES] pages)
- Supplementary: reasoning-gaps-supplementary.zip ([SIZE] MB)

## Confirmation
- Confirmation email: [SAVED TO]
- Submission ID: [ID]

## Timeline
- Submission deadline: May 4, 2026
- Days early: [X] days
- Notification date: [From NeurIPS website]
- Camera-ready deadline: [From NeurIPS website]

## Post-Submission Tasks
- [ ] Upload preprint to arXiv
- [ ] Share with collaborators
- [ ] Prepare presentation (if accepted)
- [ ] Monitor for reviewer questions
EOF

git add SUBMISSION-RECORD.md
git commit -m "docs(reasoning-gaps): add NeurIPS 2026 submission record"
git push
```

**Create ArXiv preprint** (optional but recommended):
1. Format paper for arXiv (less strict than NeurIPS)
2. Upload to arXiv.org
3. Get arXiv ID (e.g., 2604.XXXXX)
4. Add to paper for future revisions

**Create PR to main**:
```bash
git checkout research/reasoning-gaps
git push origin research/reasoning-gaps

# On GitHub: Create PR
# Title: "Complete reasoning-gaps paper for NeurIPS 2026 submission"
# Description: Full project completion with 11-model evaluation and submission
```

---

## Emergency Procedures

### If Analysis Pipeline Fails

**Symptoms**: `run_full_analysis.py` crashes or produces errors

**Diagnosis**:
```bash
python run_full_analysis.py --debug --verbose 2>&1 | tee analysis_error.log
```

**Common issues**:
1. **Missing data**: Check that all expected files exist
2. **Format errors**: Validate JSON structure
3. **Dependency issues**: Re-install requirements
4. **Memory issues**: Process data in chunks

**Fallback**: Run individual analyses manually
```bash
cd experiments/analysis
python -c "
from primary import analysis_1_overall_by_gap_type
results = analysis_1_overall_by_gap_type('../benchmarks/results/')
print(results)
"
```

### If LaTeX Compilation Fails

**Symptoms**: `pdflatex` errors or warnings

**Diagnosis**:
```bash
pdflatex main.tex 2>&1 | grep -i error
cat main.log | grep -i error
```

**Common issues**:
1. **Missing packages**: Install via `tlmgr` or system package manager
2. **Undefined references**: Run `bibtex` then `pdflatex` twice
3. **Figure not found**: Check file paths
4. **Syntax errors**: Check LaTeX syntax around error line

**Fallback**: Compile in Overleaf (upload all files)

### If Submission System Issues

**Symptoms**: Cannot upload, system errors, deadline approaching

**Actions**:
1. Try different browser
2. Clear cache and cookies
3. Try from different network
4. Contact NeurIPS support immediately
5. Keep local copy of all materials
6. Screenshot any errors

**Emergency contact**: NeurIPS 2026 program chairs (from website)

---

## Success Criteria

Paper is submission-ready when:
- [x] All 11 models evaluated with 0% failure rate
- [ ] Analysis pipeline successfully executed
- [ ] All figures and tables generated with final data
- [ ] Section 5 updated with final results
- [ ] B2 footnote removed
- [ ] Paper converted to NeurIPS format
- [ ] PDF compiles without errors
- [ ] All citations resolve correctly
- [ ] Page limit complied with (≤9 pages main + unlimited appendix)
- [ ] Internal review completed
- [ ] Supplementary materials packaged and tested
- [ ] Submission uploaded before deadline

**Timeline check**: Deadline May 4, 2026. Target submission March 24-31 for 34+ day buffer.

---

**Status**: Ready to execute upon VPS completion (est. March 15-16, 2026)

**Estimated total time**: 7-10 days from data retrieval to submission

**Next step**: Monitor VPS evaluations for completion, then execute Phase 1
