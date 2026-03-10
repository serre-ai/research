"""Generate main figures for ReasonGap paper.

Implements 4 main figures as specified in empirical analysis plan:
1. Figure 1: 9-panel accuracy degradation curves (one per task)
2. Figure 2: CoT lift by gap type (box plots)
3. Figure 3: Scale dependence (scatter plot with trend lines)
4. Figure 4: Tool augmentation effectiveness (bar chart)
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import json

from .viz_utils import (
    get_gap_type_color,
    get_condition_color,
    get_family_color,
    get_size_marker,
    save_figure,
    create_subplot_grid,
    add_correlation_line,
    add_gridlines
)


def load_results(results_dir: Path) -> pd.DataFrame:
    """Load all evaluation results into a DataFrame."""
    results = []

    for result_file in results_dir.glob("*.json"):
        with open(result_file) as f:
            data = json.load(f)

        if isinstance(data, list):
            results.extend(data)
        else:
            results.append(data)

    return pd.DataFrame(results)


def figure_1_accuracy_degradation(
    df: pd.DataFrame,
    output_path: Path,
    condition: str = "direct"
):
    """Figure 1: 9-panel accuracy degradation curves.

    Shows accuracy vs difficulty for each task (9 tasks = 9 panels).
    Each panel shows multiple model families as different colored lines.

    Args:
        df: Results DataFrame
        output_path: Output file path
        condition: Which condition to plot
    """
    # Filter to specified condition
    cond_df = df[df["condition"] == condition]

    # Get unique tasks
    tasks = sorted(cond_df["task"].unique())

    # Create 3×3 grid
    fig, axes = create_subplot_grid(
        n_plots=len(tasks),
        ncols=3,
        figsize_per_plot=(4, 3.5)
    )

    for idx, task in enumerate(tasks):
        ax = axes[idx]
        task_df = cond_df[cond_df["task"] == task]

        # Aggregate by (model_family, difficulty)
        agg = task_df.groupby(["model_family", "difficulty"])["correct"].agg(["mean", "sem"]).reset_index()

        # Plot each family
        families = sorted(agg["model_family"].unique())

        for family in families:
            family_df = agg[agg["model_family"] == family]

            difficulties = family_df["difficulty"].values
            means = family_df["mean"].values
            sems = family_df["sem"].values

            color = get_family_color(family)

            ax.plot(difficulties, means, marker='o', label=family,
                   color=color, linewidth=2, markersize=6)
            ax.fill_between(difficulties, means - sems, means + sems,
                           alpha=0.2, color=color)

        # Formatting
        ax.set_xlabel("Difficulty")
        ax.set_ylabel("Accuracy")

        # Get gap type for task
        gap_type = task_df["gap_type"].iloc[0] if len(task_df) > 0 else ""
        ax.set_title(f"{task}: {gap_type.split(': ')[1] if ': ' in gap_type else gap_type}")

        ax.set_ylim([-0.05, 1.05])
        add_gridlines(ax)

        # Legend only on first plot
        if idx == 0:
            ax.legend(loc='upper right', fontsize=8)

    plt.tight_layout()
    save_figure(fig, output_path)
    plt.close(fig)


def figure_2_cot_lift_by_gap_type(
    df: pd.DataFrame,
    output_path: Path
):
    """Figure 2: CoT lift by gap type (box plots).

    Shows distribution of CoT lift (accuracy improvement over direct)
    for each gap type.

    Args:
        df: Results DataFrame
        output_path: Output file path
    """
    # Calculate CoT lift
    direct_df = df[df["condition"] == "direct"]
    cot_df = df[df["condition"] == "short_cot"]

    # Merge
    merged = pd.merge(
        direct_df,
        cot_df,
        on=["model", "task", "difficulty", "instance_id"],
        suffixes=("_direct", "_cot")
    )

    merged["cot_lift"] = merged["correct_cot"].astype(float) - merged["correct_direct"].astype(float)

    # Aggregate by (model, task)
    lift_df = merged.groupby(["model", "task", "gap_type_cot"]).agg({
        "cot_lift": "mean"
    }).reset_index()
    lift_df.rename(columns={"gap_type_cot": "gap_type"}, inplace=True)

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))

    # Sort gap types
    gap_types = sorted(lift_df["gap_type"].unique(), key=lambda x: int(x.split()[1].rstrip(':')))

    # Box plot
    positions = list(range(len(gap_types)))
    box_data = [lift_df[lift_df["gap_type"] == gt]["cot_lift"].values for gt in gap_types]

    bp = ax.boxplot(
        box_data,
        positions=positions,
        widths=0.6,
        patch_artist=True,
        showfliers=True,
        flierprops=dict(marker='o', markerfacecolor='gray', markersize=4, alpha=0.5)
    )

    # Color boxes by gap type
    for patch, gap_type in zip(bp['boxes'], gap_types):
        patch.set_facecolor(get_gap_type_color(gap_type))
        patch.set_alpha(0.7)

    # Formatting
    ax.set_xticks(positions)
    ax.set_xticklabels([gt.split(': ')[1] if ': ' in gt else gt for gt in gap_types],
                       rotation=45, ha='right')
    ax.set_xlabel("Gap Type")
    ax.set_ylabel("CoT Lift (Δ Accuracy)")
    ax.set_title("Chain-of-Thought Effectiveness by Gap Type")

    # Add horizontal line at 0
    ax.axhline(0, color='black', linestyle='--', linewidth=1, alpha=0.5)

    add_gridlines(ax, axis='y')

    plt.tight_layout()
    save_figure(fig, output_path)
    plt.close(fig)


def figure_3_scale_dependence(
    df: pd.DataFrame,
    output_path: Path
):
    """Figure 3: Scale dependence scatter plot.

    Shows accuracy vs model size for each gap type.
    Each gap type is a different color with trend line.

    Args:
        df: Results DataFrame
        output_path: Output file path
    """
    # Use direct condition
    direct_df = df[df["condition"] == "direct"]

    # Aggregate by (model, task, model_size, gap_type)
    agg = direct_df.groupby(["model", "task", "model_size", "gap_type", "model_family"])["correct"].mean().reset_index()

    # Convert size to numeric
    size_map = {"small": 1, "medium": 2, "large": 3}
    agg["size_numeric"] = agg["model_size"].map(size_map)

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 7))

    # Plot each gap type
    gap_types = sorted(agg["gap_type"].unique(), key=lambda x: int(x.split()[1].rstrip(':')))

    for gap_type in gap_types:
        gap_df = agg[agg["gap_type"] == gap_type]

        x = gap_df["size_numeric"].values
        y = gap_df["correct"].values

        color = get_gap_type_color(gap_type)
        label = gap_type.split(': ')[1] if ': ' in gap_type else gap_type

        # Scatter
        ax.scatter(x, y, color=color, alpha=0.6, s=80, label=label)

        # Trend line
        if len(x) > 1:
            add_correlation_line(ax, x, y, color=color, linestyle='--')

    # Formatting
    ax.set_xticks([1, 2, 3])
    ax.set_xticklabels(["Small\n(<20B)", "Medium\n(20-100B)", "Large\n(>100B)"])
    ax.set_xlabel("Model Size")
    ax.set_ylabel("Accuracy")
    ax.set_title("Scale Dependence of Reasoning Gaps")
    ax.set_ylim([-0.05, 1.05])

    ax.legend(loc='lower right', fontsize=9)
    add_gridlines(ax)

    plt.tight_layout()
    save_figure(fig, output_path)
    plt.close(fig)


def figure_4_tool_augmentation(
    df: pd.DataFrame,
    output_path: Path
):
    """Figure 4: Tool augmentation effectiveness.

    Bar chart comparing CoT vs Tool accuracy for tasks B5, B6, B7.

    Args:
        df: Results DataFrame
        output_path: Output file path
    """
    # Tool tasks only
    tool_tasks = ["B5", "B6", "B7"]
    task_df = df[df["task"].isin(tool_tasks)]

    # Filter to short_cot and tool conditions
    cot_df = task_df[task_df["condition"] == "short_cot"]
    tool_df = task_df[task_df["condition"] == "tool"]

    # Aggregate by task
    cot_agg = cot_df.groupby("task")["correct"].mean()
    tool_agg = tool_df.groupby("task")["correct"].mean()

    # Combine
    results_df = pd.DataFrame({
        "task": tool_tasks,
        "CoT": [cot_agg.get(t, 0) for t in tool_tasks],
        "Tool": [tool_agg.get(t, 0) for t in tool_tasks]
    })

    # Create figure
    fig, ax = plt.subplots(figsize=(8, 6))

    x = np.arange(len(tool_tasks))
    width = 0.35

    # Bars
    bars1 = ax.bar(x - width/2, results_df["CoT"], width,
                   label='CoT', color=get_condition_color("short_cot"), alpha=0.8)
    bars2 = ax.bar(x + width/2, results_df["Tool"], width,
                   label='Tool', color=get_condition_color("tool"), alpha=0.8)

    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.2f}',
                   ha='center', va='bottom', fontsize=9)

    # Formatting
    ax.set_xticks(x)

    # Get gap types for labels
    gap_type_map = {
        "B5": "Depth-bounded",
        "B6": "Algorithmic",
        "B7": "Intractability"
    }
    ax.set_xticklabels([f"{t}\n({gap_type_map[t]})" for t in tool_tasks])

    ax.set_ylabel("Accuracy")
    ax.set_title("Tool Augmentation Effectiveness")
    ax.set_ylim([0, 1.1])

    ax.legend()
    add_gridlines(ax, axis='y')

    plt.tight_layout()
    save_figure(fig, output_path)
    plt.close(fig)


def generate_all_figures(
    results_dir: Path,
    output_dir: Path
):
    """Generate all main figures.

    Args:
        results_dir: Directory with evaluation results
        output_dir: Directory to save figures
    """
    print("Loading results...")
    df = load_results(results_dir)

    # Add derived columns
    TASK_GAP_TYPES = {
        "B1": "Type 1: Sensitivity",
        "B2": "Type 2: Depth-bounded",
        "B3": "Type 3: Serial",
        "B4": "Type 3: Serial",
        "B5": "Type 2: Depth-bounded",
        "B6": "Type 5: Algorithmic",
        "B7": "Type 6: Intractability",
        "B8": "Type 4: Counterfactual",
        "B9": "Type 4: Counterfactual"
    }

    MODEL_SIZES = {
        "claude-haiku-3.5": "small",
        "claude-sonnet-3.5": "medium",
        "claude-opus-3": "large",
        "gpt-4o-mini": "small",
        "gpt-4o": "medium",
        "o3": "large",
        "llama-3.1-8b": "small",
        "llama-3.1-70b": "medium",
        "mistral-7b": "small",
        "mistral-large": "medium",
        "qwen-2.5-7b": "small",
        "qwen-2.5-72b": "medium"
    }

    MODEL_FAMILIES = {
        "claude-haiku-3.5": "Claude",
        "claude-sonnet-3.5": "Claude",
        "claude-opus-3": "Claude",
        "gpt-4o-mini": "GPT",
        "gpt-4o": "GPT",
        "o3": "GPT",
        "llama-3.1-8b": "Llama",
        "llama-3.1-70b": "Llama",
        "mistral-7b": "Mistral",
        "mistral-large": "Mistral",
        "qwen-2.5-7b": "Qwen",
        "qwen-2.5-72b": "Qwen"
    }

    df["gap_type"] = df["task"].map(TASK_GAP_TYPES)
    df["model_size"] = df["model"].map(MODEL_SIZES)
    df["model_family"] = df["model"].map(MODEL_FAMILIES)

    print(f"Loaded {len(df)} evaluation results")

    output_dir.mkdir(parents=True, exist_ok=True)

    print("\n" + "="*60)
    print("Generating Figure 1: Accuracy Degradation Curves")
    print("="*60)
    figure_1_accuracy_degradation(df, output_dir / "figure_1_degradation")

    print("\n" + "="*60)
    print("Generating Figure 2: CoT Lift by Gap Type")
    print("="*60)
    figure_2_cot_lift_by_gap_type(df, output_dir / "figure_2_cot_lift")

    print("\n" + "="*60)
    print("Generating Figure 3: Scale Dependence")
    print("="*60)
    figure_3_scale_dependence(df, output_dir / "figure_3_scale")

    print("\n" + "="*60)
    print("Generating Figure 4: Tool Augmentation")
    print("="*60)
    figure_4_tool_augmentation(df, output_dir / "figure_4_tools")

    print("\n" + "="*60)
    print("All figures generated!")
    print("="*60)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate figures for ReasonGap paper")
    parser.add_argument("--results-dir", type=Path, required=True,
                       help="Directory with evaluation results")
    parser.add_argument("--output-dir", type=Path, required=True,
                       help="Directory to save figures")

    args = parser.parse_args()

    generate_all_figures(args.results_dir, args.output_dir)
