# Supplementary Materials Plan for NeurIPS 2026 Submission

**Project**: reasoning-gaps
**Paper**: On the Reasoning Gaps of Large Language Models: A Formal Characterization
**Date created**: 2026-03-13
**Status**: Planning stage

---

## Overview

NeurIPS typically requires supplementary materials to ensure reproducibility and provide additional details that don't fit in the main paper. This document plans what to include and how to organize it.

## NeurIPS 2026 Supplementary Materials Requirements

Based on standard NeurIPS guidelines (to be verified with NeurIPS 2026 specific requirements):

1. **Format**: ZIP file or TAR.GZ archive
2. **Size limit**: Typically 100 MB (verify for 2026)
3. **Contents**: Code, data, additional results, extended proofs
4. **README**: Clear instructions for reproducing results
5. **License**: Specify code and data licenses

---

## Proposed Structure

```
reasoning-gaps-supplementary/
├── README.md                          # Main entry point with instructions
├── LICENSE.txt                        # Code and data license
├── requirements.txt                   # Python dependencies
│
├── benchmarks/                        # Benchmark suite code
│   ├── tasks/                         # Task generation code (B1-B9)
│   │   ├── task_b1_masked_majority.py
│   │   ├── task_b2_nested_boolean.py
│   │   ├── task_b3_iterated_permutation.py
│   │   ├── task_b4_state_tracking.py
│   │   ├── task_b5_graph_reachability.py
│   │   ├── task_b6_longest_increasing_subsequence.py
│   │   ├── task_b7_3sat.py
│   │   ├── task_b8_reversal_inference.py
│   │   └── task_b9_negation_sensitivity.py
│   ├── generate.py                    # Master generation script
│   ├── evaluate.py                    # Evaluation harness
│   ├── run_evaluation.py              # End-to-end evaluation script
│   └── README.md                      # Benchmark documentation
│
├── data/                              # Evaluation results
│   ├── raw/                           # Raw model outputs (JSON)
│   │   ├── haiku_4.5/
│   │   ├── gpt_4o_mini/
│   │   ├── gpt_4o/
│   │   ├── llama_3.1_8b/
│   │   ├── llama_3.1_70b/
│   │   ├── ministral_8b/
│   │   ├── mistral_small_24b/
│   │   ├── qwen_2.5_7b/
│   │   └── qwen_2.5_72b/
│   ├── analysis/                      # Processed analysis outputs
│   │   ├── primary_analysis.json
│   │   ├── statistical_tests.json
│   │   └── figures/
│   └── README.md                      # Data documentation
│
├── analysis/                          # Analysis pipeline
│   ├── run_full_analysis.py           # Main analysis script
│   ├── analysis/
│   │   ├── primary.py                 # Primary analyses (6 types)
│   │   └── stats_utils.py             # Statistical utilities
│   ├── visualizations/
│   │   ├── figures.py                 # Figure generation
│   │   └── viz_utils.py               # Visualization utilities
│   ├── test_with_synthetic_data.py    # Test suite
│   └── README.md                      # Analysis documentation
│
├── proofs/                            # Extended proofs (if not in appendix)
│   └── proposition_proofs.pdf         # Detailed proofs of all propositions
│
└── figures/                           # High-resolution figures
    ├── figure1_taxonomy.pdf
    ├── figure2_predictions.pdf
    ├── figure3_results_by_type.pdf
    └── figure4_scaling_analysis.pdf
```

---

## Key Components

### 1. README.md (Root)

**Contents**:
- Brief paper summary
- Repository structure overview
- Installation instructions
- Quick start guide
- How to reproduce main results
- How to generate benchmark data
- How to run evaluation on new models
- Citation information
- License information
- Contact information

**Example structure**:
```markdown
# Supplementary Materials: Reasoning Gaps of LLMs

This repository contains code, data, and analysis scripts for the paper:
"On the Reasoning Gaps of Large Language Models: A Formal Characterization"

## Repository Structure
[As above]

## Installation
```bash
pip install -r requirements.txt
```

## Quick Start

### Reproduce Main Results
```bash
cd analysis
python run_full_analysis.py --data-dir ../data/raw --output-dir ../data/analysis
```

### Generate Benchmark Data
```bash
cd benchmarks
python generate.py --task all --instances 1000 --output-dir ./generated
```

### Evaluate New Model
```bash
cd benchmarks
python run_evaluation.py --model your_model_name --api-key YOUR_KEY
```

[Continue with more detailed instructions]
```

### 2. Benchmarks Documentation

**File**: `benchmarks/README.md`

**Contents**:
- Overview of each task (B1-B9)
- Task specifications (input format, output format, difficulty parameters)
- Generation parameters used in paper
- Evaluation protocol
- How to add new tasks
- How to modify difficulty parameters
- Code organization and API documentation

### 3. Data Documentation

**File**: `data/README.md`

**Contents**:
- Dataset statistics (instances per task, per condition, per model)
- File format specifications
- Data schema for JSON files
- Instructions for loading and parsing data
- Data provenance (when collected, which API versions, etc.)
- Data quality metrics (failure rates, validation results)

### 4. Analysis Documentation

**File**: `analysis/README.md`

**Contents**:
- Overview of analysis pipeline
- Description of each analysis type (1-6)
- Statistical methods used
- How to run full pipeline
- How to generate individual figures
- How to run robustness checks
- Expected outputs and how to interpret them

### 5. Extended Proofs

If space constraints prevented full proofs in the appendix:
- Complete proofs of all 5 propositions
- Additional lemmas and technical details
- Complexity-theoretic background
- LaTeX source or PDF

---

## Data to Include

### Raw Evaluation Results
- **What**: JSON files with model outputs for all evaluated instances
- **Size estimate**: ~121,614 instances × 11 models × ~1 KB = ~1.3 GB
- **Issue**: Likely exceeds 100 MB limit
- **Solution**:
  - Include only aggregated statistics in supplementary
  - Host full raw data on external repository (Zenodo, Hugging Face, GitHub releases)
  - Provide download script in supplementary materials

### Aggregated Data
- **What**: Summary statistics per task/condition/model
- **Format**: CSV or JSON
- **Size**: < 1 MB
- **Include**: Yes, in main supplementary archive

### Generated Benchmark Instances
- **What**: Sample of generated benchmark problems
- **Size**: ~1000 instances × 9 tasks × ~1 KB = ~9 MB
- **Include**: Yes, as examples (not full 121K instances)

---

## Code to Include

### Essential Code
1. ✅ Task generation code (all 9 tasks)
2. ✅ Evaluation harness
3. ✅ Analysis pipeline
4. ✅ Statistical utilities
5. ✅ Visualization code

### Optional Code
- Model API clients (may contain keys, sanitize first)
- VPS deployment scripts (infrastructure-specific)
- Cost monitoring utilities (nice-to-have)

---

## Licensing

**Recommended**:
- **Code**: MIT License (permissive, widely used)
- **Data**: CC BY 4.0 (allows reuse with attribution)
- **Paper**: NeurIPS copyright (standard for accepted papers)

**Action**: Create `LICENSE.txt` with MIT license for code and note CC BY 4.0 for data.

---

## External Data Hosting

For data exceeding size limits:

**Option 1: Zenodo**
- ✅ Citable DOI
- ✅ Long-term archival (CERN-backed)
- ✅ Free for datasets up to 50 GB per record
- ✅ Versioning support

**Option 2: Hugging Face Datasets**
- ✅ ML community standard
- ✅ Easy loading via `datasets` library
- ✅ Unlimited size
- ✅ Built-in viewer

**Option 3: GitHub Releases**
- ✅ Same repository as code
- ✅ Version-tagged
- ⚠️ 2 GB file size limit
- ⚠️ Not designed for long-term archival

**Recommendation**: Zenodo for permanence + Hugging Face for usability.

---

## Size Optimization Strategies

If supplementary materials approach size limit:

1. **Compress benchmark code** (exclude tests, examples)
2. **Sample evaluation data** (include full data externally)
3. **Reduce figure resolution** (300 DPI sufficient for supplementary)
4. **Exclude redundant analysis outputs** (include only final results)
5. **Link to GitHub repo** for full codebase

---

## Reproducibility Checklist

Ensure supplementary materials enable:
- [ ] Regenerating benchmark data with same parameters
- [ ] Re-running evaluation on provided data
- [ ] Re-running analysis pipeline to produce figures/tables
- [ ] Verifying statistical tests
- [ ] Extending to new models (clear API)
- [ ] Extending to new tasks (clear template)

---

## Timeline

Assuming VPS evaluations complete March 15-16:

- **March 17**: Organize code into supplementary structure
- **March 18**: Write README files for each component
- **March 19**: Package data and verify completeness
- **March 20**: Create LICENSE, finalize documentation
- **March 21**: Test reproducibility on clean environment
- **March 22**: Upload large datasets to Zenodo/Hugging Face
- **March 23**: Create final supplementary ZIP archive
- **March 24-31**: Submit with paper

---

## Pre-Submission Verification

Before packaging:
- [ ] All code runs on clean Python environment
- [ ] All dependencies listed in requirements.txt
- [ ] All data files referenced in READMEs exist
- [ ] All scripts have clear usage instructions
- [ ] No API keys or credentials in code
- [ ] No absolute paths (use relative paths)
- [ ] Code is reasonably commented
- [ ] README is clear to external reader

---

## Post-Acceptance Tasks

If paper accepted:
- [ ] Create public GitHub repository
- [ ] Upload datasets to Zenodo with DOI
- [ ] Create Hugging Face dataset card
- [ ] Add ArXiv link to repository
- [ ] Add NeurIPS paper link when published
- [ ] Consider blog post explaining benchmark

---

**Status**: Planning complete, ready to execute post-evaluation

**Next steps**:
1. Wait for VPS evaluations (est. March 15-16)
2. Run full analysis pipeline
3. Organize code into supplementary structure
4. Write documentation
5. Package and test reproducibility
