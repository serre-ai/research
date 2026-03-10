#!/usr/bin/env python3
"""ReasonGap Analysis Pipeline — CLI entry point.

Generates paper-ready tables, figures, and statistical summaries from
evaluation results.

Usage:
    python analyze.py --results-dir results/ --output-dir analysis_output/

Generates:
    analysis_output/tables/main_accuracy.tex
    analysis_output/tables/accuracy_by_condition.tex
    analysis_output/tables/cot_lift.tex
    analysis_output/tables/scale_analysis.tex
    analysis_output/figures/accuracy_vs_difficulty.pdf
    analysis_output/figures/cot_lift_heatmap.pdf
    analysis_output/figures/phase_transition.pdf
    analysis_output/figures/scale_sensitivity.pdf
    analysis_output/figures/intervention_comparison.pdf
    analysis_output/summary.md
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

from analysis.loader import load_results, TASK_GAP_TYPE, GAP_TYPE_ORDER
from analysis.tables import (
    main_accuracy_table,
    accuracy_by_condition_table,
    cot_lift_table,
    scale_analysis_table,
    to_latex,
)
from analysis.plots import (
    plot_accuracy_vs_difficulty,
    plot_cot_lift_heatmap,
    plot_phase_transition,
    plot_scale_sensitivity,
    plot_intervention_comparison,
)
from analysis.statistics import compute_all_cis


def _write_table(
    df: pd.DataFrame,
    output_dir: Path,
    name: str,
    caption: str,
    label: str,
    **kwargs,
) -> None:
    """Write a table as both CSV and LaTeX."""
    tables_dir = output_dir / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)

    # CSV for inspection
    df.to_csv(tables_dir / f"{name}.csv")

    # LaTeX for paper
    latex = to_latex(df, caption=caption, label=label, **kwargs)
    (tables_dir / f"{name}.tex").write_text(latex)

    print(f"  -> {name}.csv, {name}.tex")


def _generate_summary(df: pd.DataFrame, ci_df: pd.DataFrame, output_dir: Path) -> None:
    """Generate a human-readable markdown summary of key findings."""
    lines = ["# ReasonGap Analysis Summary\n"]

    # Overall stats
    n_instances = len(df)
    n_tasks = df["task"].nunique()
    n_models = df["model"].nunique()
    n_conditions = df["condition"].nunique()

    lines.append("## Dataset Overview\n")
    lines.append(f"- **Instances**: {n_instances:,}")
    lines.append(f"- **Tasks**: {n_tasks}")
    lines.append(f"- **Models**: {n_models}")
    lines.append(f"- **Conditions**: {n_conditions}")
    lines.append(f"- **Models evaluated**: {', '.join(sorted(df['model'].unique()))}")
    lines.append("")

    # Overall accuracy by condition
    lines.append("## Overall Accuracy by Condition\n")
    cond_acc = df.groupby("condition")["correct"].mean()
    for cond, acc in cond_acc.items():
        lines.append(f"- **{cond}**: {acc:.3f}")
    lines.append("")

    # Per gap-type results
    lines.append("## Results by Gap Type\n")
    for gap_type in GAP_TYPE_ORDER:
        gap_df = df[df["gap_type"] == gap_type]
        if gap_df.empty:
            continue

        lines.append(f"### {gap_type}\n")
        gap_cond = gap_df.groupby("condition")["correct"].mean()
        for cond, acc in gap_cond.items():
            lines.append(f"- {cond}: {acc:.3f}")

        # CoT lift
        if "direct" in gap_cond.index:
            direct_acc = gap_cond["direct"]
            for cond, acc in gap_cond.items():
                if cond != "direct":
                    lift = acc - direct_acc
                    direction = "+" if lift > 0 else ""
                    lines.append(f"- CoT lift ({cond}): {direction}{lift:.3f}")
        lines.append("")

    # Key findings
    lines.append("## Key Predictions Check\n")

    # Check: CoT lift for types 2,3 vs types 5,6
    for label, types in [
        ("Types 2,3 (should benefit from CoT)", ["Type 2: Depth", "Type 3: Serial"]),
        ("Types 5,6 (should NOT benefit from CoT)", ["Type 5: Intractability", "Type 6: Architectural"]),
    ]:
        type_df = df[df["gap_type"].isin(types)]
        if type_df.empty:
            continue
        type_cond = type_df.groupby("condition")["correct"].mean()
        if "direct" in type_cond.index and "short_cot" in type_cond.index:
            lift = type_cond["short_cot"] - type_cond["direct"]
            lines.append(f"- **{label}**: CoT lift = {lift:+.3f}")
    lines.append("")

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "summary.md").write_text("\n".join(lines))
    print("  -> summary.md")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ReasonGap Analysis Pipeline: tables, figures, and statistics.",
    )
    parser.add_argument(
        "--results-dir",
        type=str,
        required=True,
        help="Directory containing evaluation result JSON/JSONL files.",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="analysis_output",
        help="Directory to write tables, figures, and summary (default: analysis_output/).",
    )
    parser.add_argument(
        "--skip-plots",
        action="store_true",
        help="Skip generating figures (useful for quick table generation).",
    )
    parser.add_argument(
        "--n-bootstrap",
        type=int,
        default=10000,
        help="Number of bootstrap samples for CIs (default: 10000).",
    )

    args = parser.parse_args()
    output_dir = Path(args.output_dir)

    # Load data
    print(f"Loading results from {args.results_dir}...")
    df = load_results(args.results_dir)

    if df.empty:
        print("No results found. Exiting.", file=sys.stderr)
        sys.exit(1)

    print(f"Loaded {len(df):,} instances across {df['task'].nunique()} tasks, "
          f"{df['model'].nunique()} models, {df['condition'].nunique()} conditions.")

    # Generate tables
    print("\nGenerating tables...")

    table1 = main_accuracy_table(df)
    _write_table(
        table1, output_dir, "main_accuracy",
        caption="Overall accuracy by task and model.",
        label="tab:main-accuracy",
        highlight_max=True,
    )

    table2 = accuracy_by_condition_table(df)
    _write_table(
        table2, output_dir, "accuracy_by_condition",
        caption="Accuracy by task and evaluation condition.",
        label="tab:accuracy-condition",
    )

    table3 = cot_lift_table(df)
    if not table3.empty:
        _write_table(
            table3, output_dir, "cot_lift",
            caption="CoT lift (accuracy improvement over direct) by gap type.",
            label="tab:cot-lift",
            float_format=".3f",
        )

    table4 = scale_analysis_table(df)
    if not table4.empty:
        _write_table(
            table4, output_dir, "scale_analysis",
            caption="Accuracy by model scale and gap type.",
            label="tab:scale-analysis",
        )

    # Confidence intervals
    print("\nComputing confidence intervals...")
    ci_df = compute_all_cis(df, n_bootstrap=args.n_bootstrap)
    ci_dir = output_dir / "tables"
    ci_dir.mkdir(parents=True, exist_ok=True)
    ci_df.to_csv(ci_dir / "confidence_intervals.csv", index=False)
    print(f"  -> confidence_intervals.csv ({len(ci_df)} groups)")

    # Generate figures
    if not args.skip_plots:
        figures_dir = str(output_dir / "figures")
        print(f"\nGenerating figures in {figures_dir}...")

        print("  - accuracy_vs_difficulty...")
        plot_accuracy_vs_difficulty(df, figures_dir)

        print("  - cot_lift_heatmap...")
        plot_cot_lift_heatmap(df, figures_dir)

        print("  - phase_transition...")
        plot_phase_transition(df, figures_dir)

        print("  - scale_sensitivity...")
        plot_scale_sensitivity(df, figures_dir)

        print("  - intervention_comparison...")
        plot_intervention_comparison(df, figures_dir)

    # Summary
    print("\nGenerating summary...")
    _generate_summary(df, ci_df, output_dir)

    print(f"\nDone. All outputs in {output_dir}/")


if __name__ == "__main__":
    main()
