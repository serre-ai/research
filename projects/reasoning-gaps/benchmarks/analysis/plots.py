"""Generate paper-ready figures for the NeurIPS submission.

Style: seaborn with monospace fonts, dark-theme compatible but print-readable.
Sizes: NeurIPS column width (3.25in) or full width (6.75in).
Output: PDF (vector) + PNG (300 DPI).
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import seaborn as sns

from analysis.loader import (
    TASK_ORDER,
    TASK_SHORT_LABELS,
    GAP_TYPE_ORDER,
    CONDITION_ORDER,
)
from analysis.statistics import bootstrap_ci


# ---------------------------------------------------------------------------
# Global style configuration
# ---------------------------------------------------------------------------

NEURIPS_COL_WIDTH = 3.25   # inches
NEURIPS_FULL_WIDTH = 6.75  # inches
DPI = 300

# Model family colors — colorblind-friendly palette
FAMILY_COLORS: dict[str, str] = {
    "GPT": "#1f77b4",
    "Claude": "#ff7f0e",
    "Llama": "#2ca02c",
    "Mistral": "#d62728",
    "Qwen": "#9467bd",
    "Other": "#7f7f7f",
}

# Condition colors
CONDITION_COLORS: dict[str, str] = {
    "direct": "#4c72b0",
    "short_cot": "#55a868",
    "budget_cot": "#c44e52",
    "tool": "#8172b2",
}

CONDITION_LABELS: dict[str, str] = {
    "direct": "Direct",
    "short_cot": "Short CoT",
    "budget_cot": "Budget CoT",
    "tool": "Tool Use",
}


def _setup_style() -> None:
    """Set up matplotlib/seaborn style for NeurIPS figures."""
    sns.set_theme(style="whitegrid", font_scale=0.8)
    plt.rcParams.update({
        "font.family": "monospace",
        "font.size": 8,
        "axes.labelsize": 8,
        "axes.titlesize": 9,
        "xtick.labelsize": 7,
        "ytick.labelsize": 7,
        "legend.fontsize": 7,
        "figure.dpi": DPI,
        "savefig.dpi": DPI,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.05,
        "axes.grid": True,
        "grid.alpha": 0.3,
    })


def _save_figure(fig: plt.Figure, output_dir: str, name: str) -> None:
    """Save figure as both PDF and PNG."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / f"{name}.pdf", format="pdf")
    fig.savefig(out / f"{name}.png", format="png", dpi=DPI)
    plt.close(fig)


def _get_model_color(model: str, family_map: dict[str, str] | None = None) -> str:
    """Get consistent color for a model based on its family."""
    if family_map is None:
        from analysis.loader import _extract_model_family
        family = _extract_model_family(model)
    else:
        family = family_map.get(model, "Other")
    return FAMILY_COLORS.get(family, FAMILY_COLORS["Other"])


def _compute_accuracy_with_ci(
    group: pd.DataFrame,
    n_bootstrap: int = 2000,
    seed: int = 42,
) -> tuple[float, float, float]:
    """Compute accuracy and 95% CI for a group."""
    correct = group["correct"].values.astype(float)
    if len(correct) == 0:
        return 0.0, 0.0, 0.0
    acc = correct.mean()
    ci_lo, ci_hi = bootstrap_ci(correct, n_bootstrap=n_bootstrap, seed=seed)
    return acc, ci_lo, ci_hi


# ---------------------------------------------------------------------------
# Figure 1: Accuracy vs Difficulty (3x3 grid)
# ---------------------------------------------------------------------------

def plot_accuracy_vs_difficulty(
    df: pd.DataFrame,
    output_dir: str,
    conditions: list[str] | None = None,
) -> None:
    """One subplot per task (3x3 grid), x=difficulty, y=accuracy, lines=models.

    Uses consistent colors per model family. Includes 95% CI error bars.
    """
    _setup_style()

    if conditions is None:
        conditions = ["direct"]

    df_cond = df[df["condition"].isin(conditions)]
    tasks = [t for t in TASK_ORDER if t in df_cond["task"].unique()]

    if not tasks:
        return

    n_tasks = len(tasks)
    n_cols = 3
    n_rows = (n_tasks + n_cols - 1) // n_cols

    fig, axes = plt.subplots(
        n_rows, n_cols,
        figsize=(NEURIPS_FULL_WIDTH, 2.0 * n_rows),
        squeeze=False,
    )

    models = sorted(df_cond["model"].unique())
    # Build family map for coloring
    from analysis.loader import _extract_model_family
    family_map = {m: _extract_model_family(m) for m in models}

    for idx, task in enumerate(tasks):
        row, col = divmod(idx, n_cols)
        ax = axes[row][col]

        task_df = df_cond[df_cond["task"] == task]
        difficulties = sorted(task_df["difficulty"].unique())

        for model in models:
            model_df = task_df[task_df["model"] == model]
            if model_df.empty:
                continue

            accs, ci_los, ci_his = [], [], []
            diffs_present = []

            for d in difficulties:
                d_df = model_df[model_df["difficulty"] == d]
                if d_df.empty:
                    continue
                acc, ci_lo, ci_hi = _compute_accuracy_with_ci(d_df)
                accs.append(acc)
                ci_los.append(acc - ci_lo)
                ci_his.append(ci_hi - acc)
                diffs_present.append(d)

            if not diffs_present:
                continue

            color = FAMILY_COLORS.get(family_map[model], FAMILY_COLORS["Other"])
            # Strip provider prefix for label
            label = model.split(":")[-1] if ":" in model else model
            ax.errorbar(
                diffs_present, accs,
                yerr=[ci_los, ci_his],
                marker="o", markersize=3, linewidth=1.2,
                color=color, label=label, capsize=2,
            )

        ax.set_title(TASK_SHORT_LABELS.get(task, task), fontweight="bold")
        ax.set_xlabel("Difficulty")
        ax.set_ylabel("Accuracy")
        ax.set_ylim(-0.05, 1.05)
        ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))

    # Remove empty subplots
    for idx in range(n_tasks, n_rows * n_cols):
        row, col = divmod(idx, n_cols)
        axes[row][col].set_visible(False)

    # Shared legend
    handles, labels = axes[0][0].get_legend_handles_labels()
    if handles:
        fig.legend(
            handles, labels,
            loc="lower center",
            ncol=min(len(models), 5),
            bbox_to_anchor=(0.5, -0.02),
            frameon=True,
        )

    fig.suptitle("Accuracy vs. Difficulty by Task", fontweight="bold", y=1.02)
    fig.tight_layout()
    _save_figure(fig, output_dir, "accuracy_vs_difficulty")


# ---------------------------------------------------------------------------
# Figure 2: CoT Lift Heatmap
# ---------------------------------------------------------------------------

def plot_cot_lift_heatmap(df: pd.DataFrame, output_dir: str) -> None:
    """Heatmap: rows=gap types, columns=conditions, values=accuracy lift over direct.

    Red=negative lift, green=positive lift.
    """
    _setup_style()

    # Compute per-gap-type accuracy by condition
    acc = df.pivot_table(
        values="correct",
        index="gap_type",
        columns="condition",
        aggfunc="mean",
    )

    if "direct" not in acc.columns:
        return

    # Compute lift
    lift = pd.DataFrame(index=acc.index)
    for cond in acc.columns:
        if cond != "direct":
            lift[CONDITION_LABELS.get(cond, cond)] = acc[cond] - acc["direct"]

    # Reindex
    gap_order = [g for g in GAP_TYPE_ORDER if g in lift.index]
    lift = lift.reindex(gap_order)

    if lift.empty:
        return

    fig, ax = plt.subplots(figsize=(NEURIPS_COL_WIDTH + 1, 3.0))

    # Diverging colormap: red=negative, white=0, green=positive
    cmap = sns.diverging_palette(10, 130, as_cmap=True)
    vmax = max(abs(lift.values.min()), abs(lift.values.max()), 0.01)

    sns.heatmap(
        lift,
        annot=True,
        fmt=".3f",
        cmap=cmap,
        center=0,
        vmin=-vmax,
        vmax=vmax,
        linewidths=0.5,
        ax=ax,
        cbar_kws={"label": "Accuracy Lift", "shrink": 0.8},
    )

    ax.set_title("CoT Lift by Gap Type", fontweight="bold")
    ax.set_ylabel("")
    ax.set_xlabel("")

    fig.tight_layout()
    _save_figure(fig, output_dir, "cot_lift_heatmap")


# ---------------------------------------------------------------------------
# Figure 3: Phase Transition (B7 specific)
# ---------------------------------------------------------------------------

def plot_phase_transition(df: pd.DataFrame, output_dir: str) -> None:
    """B7-specific: accuracy vs alpha (clause/variable ratio) for different models.

    Shows sharp cliff at alpha ~ 4.27.
    The difficulty parameter encodes alpha ranges.
    """
    _setup_style()

    # Filter to B7
    b7_df = df[df["task"] == "B7_3sat"]
    if b7_df.empty:
        return

    # Use difficulty as proxy for alpha.
    # In the benchmark design, difficulty levels map to alpha ranges.
    # We'll plot accuracy vs difficulty with annotation.
    models = sorted(b7_df["model"].unique())
    from analysis.loader import _extract_model_family
    family_map = {m: _extract_model_family(m) for m in models}

    conditions = sorted(b7_df["condition"].unique())

    fig, ax = plt.subplots(figsize=(NEURIPS_COL_WIDTH + 0.5, 2.5))

    for model in models:
        model_df = b7_df[(b7_df["model"] == model) & (b7_df["condition"] == "direct")]
        if model_df.empty:
            # Try any condition
            model_df = b7_df[b7_df["model"] == model]
        if model_df.empty:
            continue

        difficulties = sorted(model_df["difficulty"].unique())
        accs, ci_los, ci_his = [], [], []

        for d in difficulties:
            d_df = model_df[model_df["difficulty"] == d]
            acc, ci_lo, ci_hi = _compute_accuracy_with_ci(d_df)
            accs.append(acc)
            ci_los.append(acc - ci_lo)
            ci_his.append(ci_hi - acc)

        color = FAMILY_COLORS.get(family_map[model], FAMILY_COLORS["Other"])
        label = model.split(":")[-1] if ":" in model else model

        ax.errorbar(
            difficulties, accs,
            yerr=[ci_los, ci_his],
            marker="o", markersize=3, linewidth=1.2,
            color=color, label=label, capsize=2,
        )

    # Mark the phase transition point
    ax.axvline(x=3, color="gray", linestyle="--", alpha=0.5, linewidth=0.8)
    ax.annotate(
        r"$\alpha \approx 4.27$",
        xy=(3, 0.5), fontsize=7, color="gray",
        ha="center",
    )

    ax.set_title("B7: 3-SAT Phase Transition", fontweight="bold")
    ax.set_xlabel(r"Difficulty (proxy for $\alpha$)")
    ax.set_ylabel("Accuracy")
    ax.set_ylim(-0.05, 1.05)
    ax.legend(loc="best", frameon=True)

    fig.tight_layout()
    _save_figure(fig, output_dir, "phase_transition")


# ---------------------------------------------------------------------------
# Figure 4: Scale Sensitivity
# ---------------------------------------------------------------------------

def plot_scale_sensitivity(df: pd.DataFrame, output_dir: str) -> None:
    """Accuracy by model size (x=params, y=accuracy) grouped by gap type.

    Shows which gaps are scale-sensitive.
    """
    _setup_style()

    df_sized = df[df["model_size"].notna()].copy()
    if df_sized.empty:
        return

    gap_types = [g for g in GAP_TYPE_ORDER if g in df_sized["gap_type"].unique()]
    if not gap_types:
        return

    fig, ax = plt.subplots(figsize=(NEURIPS_COL_WIDTH + 1, 3.0))

    gap_colors = sns.color_palette("husl", len(gap_types))

    for gap_type, color in zip(gap_types, gap_colors):
        gap_df = df_sized[df_sized["gap_type"] == gap_type]

        # Aggregate by model_size
        sizes = sorted(gap_df["model_size"].unique())
        accs, ci_los, ci_his = [], [], []

        for size in sizes:
            size_df = gap_df[gap_df["model_size"] == size]
            acc, ci_lo, ci_hi = _compute_accuracy_with_ci(size_df)
            accs.append(acc)
            ci_los.append(acc - ci_lo)
            ci_his.append(ci_hi - acc)

        # Short label for gap type
        short = gap_type.split(":")[0].strip()
        ax.errorbar(
            sizes, accs,
            yerr=[ci_los, ci_his],
            marker="o", markersize=4, linewidth=1.2,
            color=color, label=short, capsize=2,
        )

    ax.set_xscale("log")
    ax.set_xlabel("Model Size (B params)")
    ax.set_ylabel("Accuracy")
    ax.set_ylim(-0.05, 1.05)
    ax.set_title("Scale Sensitivity by Gap Type", fontweight="bold")
    ax.legend(loc="best", frameon=True, fontsize=6)

    fig.tight_layout()
    _save_figure(fig, output_dir, "scale_sensitivity")


# ---------------------------------------------------------------------------
# Figure 5: Intervention Comparison
# ---------------------------------------------------------------------------

def plot_intervention_comparison(df: pd.DataFrame, output_dir: str) -> None:
    """Bar chart: for each gap type, bars for each condition.

    Shows the differential effectiveness of interventions.
    """
    _setup_style()

    gap_types = [g for g in GAP_TYPE_ORDER if g in df["gap_type"].unique()]
    conditions = [c for c in CONDITION_ORDER if c in df["condition"].unique()]

    if not gap_types or not conditions:
        return

    fig, ax = plt.subplots(figsize=(NEURIPS_FULL_WIDTH, 3.0))

    n_gaps = len(gap_types)
    n_conds = len(conditions)
    bar_width = 0.8 / n_conds
    x = np.arange(n_gaps)

    for i, cond in enumerate(conditions):
        accs = []
        ci_los = []
        ci_his = []

        for gap_type in gap_types:
            mask = (df["gap_type"] == gap_type) & (df["condition"] == cond)
            group = df[mask]
            if group.empty:
                accs.append(0.0)
                ci_los.append(0.0)
                ci_his.append(0.0)
            else:
                acc, ci_lo, ci_hi = _compute_accuracy_with_ci(group)
                accs.append(acc)
                ci_los.append(acc - ci_lo)
                ci_his.append(ci_hi - acc)

        color = CONDITION_COLORS.get(cond, "#333333")
        label = CONDITION_LABELS.get(cond, cond)
        offset = (i - n_conds / 2 + 0.5) * bar_width

        ax.bar(
            x + offset, accs,
            width=bar_width,
            yerr=[ci_los, ci_his],
            color=color, label=label,
            capsize=2, alpha=0.85,
        )

    # Short gap type labels for x-axis
    short_labels = [g.split(":")[0].strip() for g in gap_types]
    ax.set_xticks(x)
    ax.set_xticklabels(short_labels, rotation=0)
    ax.set_ylabel("Accuracy")
    ax.set_ylim(0, 1.05)
    ax.set_title("Intervention Effectiveness by Gap Type", fontweight="bold")
    ax.legend(loc="upper right", frameon=True)

    fig.tight_layout()
    _save_figure(fig, output_dir, "intervention_comparison")
