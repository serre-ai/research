# NeurIPS 2026 Submission Package

## Title
On the Reasoning Gaps of Large Language Models: A Formal Characterization

## Submission Files

### Primary Files
- `main.pdf` — Complete paper (19 pages: 9 main + 10 appendix)
- `main.tex` — LaTeX source
- `neurips_2026.sty` — NeurIPS 2026 style file

### Supporting Materials
- `benchmarks/analysis_output/` — Analysis results, figures, and tables
  - `figures/` — All figures referenced in the paper (PDF and PNG formats)
  - `tables/` — LaTeX tables and raw CSV data
  - `stats.tex` — Auto-generated statistics

## Compilation Instructions

### Using Tectonic (Recommended)
```bash
tectonic main.tex
```

### Using pdflatex
```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

## Paper Structure

### Main Paper (9 pages)
1. Introduction
2. Related Work
3. Theoretical Framework
4. The ReasonGap Benchmark
5. Experimental Setup
6. Results
7. Discussion
8. Conclusion

### Appendix (10 pages)
A. Formal Definitions and Proofs
B. Complete Experimental Results
C. Benchmark Task Specifications
D. Additional Analyses

## Key Contributions

1. **Formal Framework**: A 6-type taxonomy of reasoning gaps grounded in computational complexity theory, with 5 propositions connecting transformer expressiveness to empirical failures.

2. **ReasonGap Benchmark**: 9 diagnostic tasks (B1-B9) designed to isolate specific reasoning gap types with controlled difficulty parameters.

3. **Empirical Validation**: Evaluation across 12 models (Claude 3.5 Haiku/Sonnet, Claude 4.6 Opus/Sonnet, GPT-4o-mini/4o/o3, Llama 3.1 8B/70B, Ministral 8B, Mistral Small 24B, Qwen 2.5 7B/72B) with 209,438 total instances.

4. **Intervention Analysis**: Systematic evaluation of chain-of-thought prompting, budget sensitivity, and tool-augmented reasoning.

## Key Results

- **Framework Validation**: Types 2,3 (depth/serial gaps) show CoT lift of +0.351, while Types 5,6 (intractability/architectural gaps) show CoT lift of +0.094, matching theoretical predictions.

- **Tool Use**: Type 4 (computational gap) shows tool-use lift of +0.635, 4× greater than CoT alone, validating the framework's prediction that external tools address computational bottlenecks.

- **Budget Sensitivity**: Budget sweep on B2 (exponential formula evaluation) reveals sharp threshold at 1.0× budget, while B3 (recursive Fibonacci) shows monotonic improvement, consistent with Proposition 2.

- **Model-Specific**: Claude 4.6 Opus achieves 100% on B3 (CoT) and 75% on B6 (CoT), 2× the next best model, demonstrating that larger capacity narrows but does not eliminate gaps.

## Reproducibility

All experimental code, evaluation data, and analysis scripts are available in the supplementary materials directory structure. The complete pipeline is automated via `build-paper.sh`.

### Dataset Statistics
- Total evaluations: 209,438 instances
- Base evaluation: 159,162 instances (12 models × 9 tasks × 3 conditions)
- Tool-use evaluation: 3,000 instances (3 models × 2 tasks × 1 condition)
- Budget sweep: 15,000 instances (3 models × 2 tasks × 5 multipliers)
- Additional conditions: 32,276 instances

### Confidence Intervals
All reported accuracies include 95% bootstrap confidence intervals (10,000 resamples). See `benchmarks/analysis_output/tables/confidence_intervals.csv` for complete data.

## Contact

For questions about this submission, please contact the authors via the NeurIPS submission system.

## Checklist

- [x] Paper compiles without errors
- [x] Page limit: 9 pages main content (within limit)
- [x] Anonymization: Verified (no author names, affiliations, or identifying URLs)
- [x] Figures: All referenced in text, proper captions
- [x] Tables: All referenced in text, proper formatting
- [x] Citations: Complete BibTeX entries, no broken references
- [x] Reproducibility: Code and data organization documented
- [x] Supplementary materials: Organized and documented
- [x] Submission package: Contains all required files

## Build Date
2026-03-21 10:05 UTC
