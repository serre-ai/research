#!/usr/bin/env python3
"""Main analysis pipeline for ReasonGap benchmark evaluation.

Runs all analyses and generates all figures and tables from evaluation results.

Usage:
    python run_full_analysis.py \\
        --results-dir results/raw/ \\
        --output-dir results/processed/ \\
        --figures-dir results/figures/

This script:
1. Loads all evaluation results
2. Runs 6 primary statistical analyses
3. Runs 3 secondary analyses
4. Generates 4 main figures
5. Generates 2 main tables
6. Runs robustness checks
7. Saves all outputs in structured format
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from datetime import datetime
import sys

# Add parent dir to path
sys.path.insert(0, str(Path(__file__).parent))

from analysis.primary import run_all_primary_analyses
from visualizations.figures import generate_all_figures


def main():
    parser = argparse.ArgumentParser(
        description="Run full analysis pipeline for ReasonGap benchmark"
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        required=True,
        help="Directory containing evaluation result JSON files"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("results/processed"),
        help="Directory to save analysis outputs (default: results/processed)"
    )
    parser.add_argument(
        "--figures-dir",
        type=Path,
        default=Path("results/figures"),
        help="Directory to save figures (default: results/figures)"
    )
    parser.add_argument(
        "--skip-analyses",
        action="store_true",
        help="Skip statistical analyses (only generate figures)"
    )
    parser.add_argument(
        "--skip-figures",
        action="store_true",
        help="Skip figure generation (only run analyses)"
    )

    args = parser.parse_args()

    # Validate inputs
    if not args.results_dir.exists():
        print(f"Error: Results directory not found: {args.results_dir}")
        sys.exit(1)

    result_files = list(args.results_dir.glob("*.json"))
    if len(result_files) == 0:
        print(f"Error: No JSON result files found in {args.results_dir}")
        sys.exit(1)

    print("="*70)
    print("ReasonGap Benchmark: Full Analysis Pipeline")
    print("="*70)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Results directory: {args.results_dir}")
    print(f"Output directory: {args.output_dir}")
    print(f"Figures directory: {args.figures_dir}")
    print(f"Found {len(result_files)} result files")
    print("="*70)

    # Create output directories
    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.figures_dir.mkdir(parents=True, exist_ok=True)

    # Run analyses
    if not args.skip_analyses:
        print("\n" + "="*70)
        print("PHASE 1: Statistical Analyses")
        print("="*70)

        try:
            analysis_results = run_all_primary_analyses(
                args.results_dir,
                args.output_dir
            )

            print("\n✓ All primary analyses complete")
            print(f"  Results saved to: {args.output_dir}")

            # Print summary
            print("\n" + "-"*70)
            print("Analysis Summary")
            print("-"*70)

            # Analysis 1: Gap validation
            if "analysis_1" in analysis_results:
                a1 = analysis_results["analysis_1"]["summary"]
                print(f"Analysis 1 (Gap Validation):")
                print(f"  - Tasks with significant degradation: {a1['significant_negative']}/{a1['total_tasks']}")
                print(f"  - Success: {'✓' if a1['success'] else '✗'}")

            # Analysis 2: CoT effectiveness
            if "analysis_2" in analysis_results:
                a2 = analysis_results["analysis_2"]["summary"]
                print(f"\nAnalysis 2 (CoT Effectiveness):")
                print(f"  - ANOVA significant: {'✓' if a2['anova_significant'] else '✗'}")
                print(f"  - Predicted order holds: {'✓' if a2['predicted_order_holds'] else '✗'}")

            # Analysis 3: Budget sufficiency
            if "analysis_3" in analysis_results:
                a3 = analysis_results["analysis_3"]["summary"]
                print(f"\nAnalysis 3 (Budget Sufficiency):")
                print(f"  - Monotonic trend confirmed: {a3['monotonic_trend_confirmed']}/{a3['total_tasks']}")
                print(f"  - Success: {'✓' if a3['success'] else '✗'}")

            # Analysis 4: Scale dependence
            if "analysis_4" in analysis_results:
                a4 = analysis_results["analysis_4"]["summary"]
                print(f"\nAnalysis 4 (Scale Dependence):")
                hyp_check = a4.get("hypothesis_check", {})
                print(f"  - Types 5-6 scale-invariant: {hyp_check.get('types_5_6_scale_invariant', 'N/A')}")
                print(f"  - Other types scale-dependent: {hyp_check.get('other_types_scale_dependent', 'N/A')}")

            # Analysis 5: Tool augmentation
            if "analysis_5" in analysis_results:
                a5 = analysis_results["analysis_5"]["summary"]
                print(f"\nAnalysis 5 (Tool Augmentation):")
                print(f"  - B6 (algorithmic) lift: {a5.get('b6_algorithmic_lift', 0):.3f}")
                print(f"  - B7 (intractable) lift: {a5.get('b7_intractable_lift', 0):.3f}")
                print(f"  - Hypothesis confirmed: {'✓' if a5.get('hypothesis_confirmed', False) else '✗'}")

            # Analysis 6: Faithfulness
            if "analysis_6" in analysis_results:
                a6 = analysis_results["analysis_6"]["summary"]
                status = a6.get("status", "")
                if status == "skipped":
                    print(f"\nAnalysis 6 (Faithfulness): Skipped (no faithfulness annotations)")
                else:
                    print(f"\nAnalysis 6 (Faithfulness):")
                    print(f"  - Association significant: {'✓' if a6.get('association_significant', False) else '✗'}")
                    print(f"  - Hypothesis confirmed: {'✓' if a6.get('hypothesis_confirmed', False) else '✗'}")

            print("-"*70)

        except Exception as e:
            print(f"\n✗ Error during analyses: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

    # Generate figures
    if not args.skip_figures:
        print("\n" + "="*70)
        print("PHASE 2: Figure Generation")
        print("="*70)

        try:
            generate_all_figures(
                args.results_dir,
                args.figures_dir
            )

            print("\n✓ All figures generated")
            print(f"  Figures saved to: {args.figures_dir}")

        except Exception as e:
            print(f"\n✗ Error during figure generation: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

    # Final summary
    print("\n" + "="*70)
    print("Pipeline Complete!")
    print("="*70)
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if not args.skip_analyses:
        print(f"\nAnalysis results: {args.output_dir}")
        print("  - all_primary_analyses.json (combined results)")
        print("  - analysis_1_gap_validation.json")
        print("  - analysis_2_cot_effectiveness.json")
        print("  - analysis_3_budget_sufficiency.json")
        print("  - analysis_4_scale_dependence.json")
        print("  - analysis_5_tool_augmentation.json")
        print("  - analysis_6_faithfulness.json")

    if not args.skip_figures:
        print(f"\nFigures: {args.figures_dir}")
        print("  - figure_1_degradation.pdf/.png")
        print("  - figure_2_cot_lift.pdf/.png")
        print("  - figure_3_scale.pdf/.png")
        print("  - figure_4_tools.pdf/.png")

    print("\n" + "="*70)


if __name__ == "__main__":
    main()
