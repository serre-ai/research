"""Generate paper-ready figures for the NeurIPS submission.

Uses pub_style as the single source of truth for all styling.
Output: PDF (vector) + PNG (300 DPI).
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import seaborn as sns

# Ensure pub_style is importable (lives in analysis/ alongside this file, or project root)
_THIS_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _THIS_DIR.parents[2]  # benchmarks/analysis -> reasoning-gaps project root
for _p in [str(_THIS_DIR), str(_PROJECT_ROOT)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pub_style  # noqa: E402

from analysis.loader import (
    TASK_ORDER,
    TASK_SHORT_LABELS,
    GAP_TYPE_ORDER,
    CONDITION_ORDER,
    CONDITION_LABELS,
    _extract_model_family,
    get_display_name,
)
from analysis.statistics import bootstrap_ci


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

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


# Per-family linestyle so models in the same family remain distinguishable
# even in grayscale or for colorblind readers.
_FAMILY_LINESTYLES: dict[str, str] = {
    "Claude": "-",
    "GPT":    "--",
    "Llama":  "-.",
    "Mistral": ":",
    "Qwen":   (0, (3, 1, 1, 1)),  # dash-dot-dot
    "Other":  "-",
}

# Per-model marker (cycles within family by size)
_SIZE_MARKERS = ["o", "s", "D", "^", "v"]


def _model_marker(model: str, models_in_family: list[str]) -> str:
    """Get a unique marker for a model within its family."""
    idx = models_in_family.index(model) if model in models_in_family else 0
    return _SIZE_MARKERS[idx % len(_SIZE_MARKERS)]


# ---------------------------------------------------------------------------
# Figure 1: Accuracy vs Difficulty (3x3 grid)
# ---------------------------------------------------------------------------

def plot_accuracy_vs_difficulty(
    df: pd.DataFrame,
    output_dir: str,
    conditions: list[str] | None = None,
) -> None:
    """One subplot per task (3x3 grid). x=difficulty, y=accuracy, lines=models.

    Uses per-family colors with per-model markers/linestyles for
    disambiguation. Panel labels (a)-(i). Shared legend below.
    """
    pub_style.setup()

    if conditions is None:
        conditions = ["direct"]

    df_cond = df[df["condition"].isin(conditions)]
    tasks = [t for t in TASK_ORDER if t in df_cond["task"].unique()]
    if not tasks:
        return

    n_tasks = len(tasks)
    n_cols = 3
    n_rows = (n_tasks + n_cols - 1) // n_cols

    fig, axes = pub_style.figure(
        width="full",
        height=2.0 * n_rows + 0.6,  # extra for shared legend
        nrows=n_rows,
        ncols=n_cols,
    )
    if n_rows == 1:
        axes = np.array([axes])

    models = sorted(df_cond["model"].unique())
    family_map = {m: _extract_model_family(m) for m in models}

    # Group models by family for marker assignment
    from collections import defaultdict
    family_models: dict[str, list[str]] = defaultdict(list)
    for m in models:
        family_models[family_map[m]].append(m)

    panel_labels = "abcdefghijklmnop"

    for idx, task in enumerate(tasks):
        row, col = divmod(idx, n_cols)
        ax = axes[row][col] if n_rows > 1 else axes[col]

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

            family = family_map[model]
            color = pub_style.FAMILY_COLORS.get(family, pub_style.FAMILY_COLORS["Other"])
            marker = _model_marker(model, family_models[family])
            ls = _FAMILY_LINESTYLES.get(family, "-")

            ax.errorbar(
                diffs_present, accs,
                yerr=[ci_los, ci_his],
                marker=marker, markersize=3, linewidth=1.0,
                color=color, label=pub_style.get_model_display(model),
                capsize=2, linestyle=ls,
            )

        ax.set_title(TASK_SHORT_LABELS.get(task, task))
        ax.set_xlabel("Difficulty")
        ax.set_ylabel("Accuracy")
        ax.set_ylim(-0.05, 1.05)
        pub_style.integer_ticks(ax, "x")

        if idx < len(panel_labels):
            pub_style.panel_label(ax, panel_labels[idx])

    # Remove empty subplots
    for idx in range(n_tasks, n_rows * n_cols):
        row, col = divmod(idx, n_cols)
        (axes[row][col] if n_rows > 1 else axes[col]).set_visible(False)

    # Shared legend — deduplicate
    handles, labels = (axes[0][0] if n_rows > 1 else axes[0]).get_legend_handles_labels()
    if handles:
        # Deduplicate while preserving order
        seen = set()
        unique_h, unique_l = [], []
        for h, l in zip(handles, labels):
            if l not in seen:
                seen.add(l)
                unique_h.append(h)
                unique_l.append(l)

        fig.legend(
            unique_h, unique_l,
            loc="lower center",
            ncol=4,
            bbox_to_anchor=(0.5, -0.02),
            fontsize=6,
            handlelength=1.5,
            columnspacing=1.0,
        )

    pub_style.savefig(fig, Path(output_dir) / "accuracy_vs_difficulty")


# ---------------------------------------------------------------------------
# Figure 2: CoT Lift Heatmap
# ---------------------------------------------------------------------------

def plot_cot_lift_heatmap(df: pd.DataFrame, output_dir: str) -> None:
    """Heatmap: rows=gap types, columns=conditions, values=accuracy lift.

    Uses blue-white-red diverging colormap (colorblind-safe).
    """
    pub_style.setup()

    # Only CoT conditions for this heatmap (tool_use has its own figure)
    cot_conds = ["direct", "short_cot", "budget_cot"]
    standard_conds = [c for c in cot_conds if c in df["condition"].unique()]
    df_std = df[df["condition"].isin(standard_conds)]

    acc = df_std.pivot_table(
        values="correct", index="gap_type", columns="condition", aggfunc="mean",
    )
    if "direct" not in acc.columns:
        return

    lift = pd.DataFrame(index=acc.index)
    for cond in acc.columns:
        if cond != "direct":
            lift[CONDITION_LABELS.get(cond, cond)] = acc[cond] - acc["direct"]

    gap_order = [g for g in GAP_TYPE_ORDER if g in lift.index]
    lift = lift.reindex(gap_order)
    if lift.empty:
        return

    # Transpose: gap types as columns, conditions as rows → wide & compact
    lift_t = lift.T
    # Use short gap type names for column headers
    lift_t.columns = [g.split(": ")[1] if ": " in g else g for g in lift_t.columns]

    fig, ax = pub_style.figure(width="full", height=1.6)

    cmap = pub_style.diverging_cmap()
    vmax = max(abs(lift_t.values.min()), abs(lift_t.values.max()), 0.01)

    sns.heatmap(
        lift_t,
        annot=True,
        fmt=".3f",
        cmap=cmap,
        center=0,
        vmin=-vmax,
        vmax=vmax,
        linewidths=0.5,
        linecolor="white",
        ax=ax,
        cbar_kws={"label": "Accuracy Lift", "shrink": 0.6, "aspect": 12},
        annot_kws={"fontsize": 7},
    )

    ax.set_title("CoT Lift by Gap Type")
    ax.set_ylabel("")
    ax.set_xlabel("")
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=25, ha="right")

    pub_style.savefig(fig, Path(output_dir) / "cot_lift_heatmap")


# ---------------------------------------------------------------------------
# Figure 3: Phase Transition (B7 specific)
# ---------------------------------------------------------------------------

def plot_phase_transition(df: pd.DataFrame, output_dir: str) -> None:
    """B7-specific: accuracy vs difficulty (proxy for alpha).

    Shows sharp cliff at the SAT/UNSAT phase transition.
    Compact legend using short model names.
    """
    pub_style.setup()

    b7_df = df[df["task"] == "B7_3sat"]
    if b7_df.empty:
        return

    models = sorted(b7_df["model"].unique())
    family_map = {m: _extract_model_family(m) for m in models}

    fig, ax = pub_style.figure(width="col", height=2.5)

    from collections import defaultdict
    family_models: dict[str, list[str]] = defaultdict(list)
    for m in models:
        family_models[family_map[m]].append(m)

    for model in models:
        model_df = b7_df[(b7_df["model"] == model) & (b7_df["condition"] == "direct")]
        if model_df.empty:
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

        family = family_map[model]
        color = pub_style.FAMILY_COLORS.get(family, pub_style.FAMILY_COLORS["Other"])
        marker = _model_marker(model, family_models[family])
        ls = _FAMILY_LINESTYLES.get(family, "-")

        ax.errorbar(
            difficulties, accs,
            yerr=[ci_los, ci_his],
            marker=marker, markersize=3, linewidth=1.0,
            color=color, label=pub_style.get_model_display(model),
            capsize=2, linestyle=ls,
        )

    # Phase transition annotation
    ax.axvline(x=3, color="0.6", linestyle="--", linewidth=0.6)
    ax.annotate(
        r"$\alpha \approx 4.27$",
        xy=(3, 0.5), fontsize=7, color="0.5", ha="center",
    )

    ax.set_title("B7: 3-SAT Phase Transition")
    ax.set_xlabel(r"Difficulty (proxy for $\alpha$)")
    ax.set_ylabel("Accuracy")
    ax.set_ylim(-0.05, 1.05)
    ax.legend(loc="upper right", fontsize=5.5, ncol=2, handlelength=1.2)

    pub_style.savefig(fig, Path(output_dir) / "phase_transition")


# ---------------------------------------------------------------------------
# Figure 4: Scale Sensitivity
# ---------------------------------------------------------------------------

def plot_scale_sensitivity(df: pd.DataFrame, output_dir: str) -> None:
    """Accuracy by model size grouped by gap type.

    Uses Okabe-Ito colors per gap type with distinct markers.
    """
    pub_style.setup()

    df_sized = df[df["model_size"].notna()].copy()
    if df_sized.empty:
        return

    gap_types = [g for g in GAP_TYPE_ORDER if g in df_sized["gap_type"].unique()]
    if not gap_types:
        return

    fig, ax = pub_style.figure(width="col", height=2.8)

    gap_markers = ["o", "s", "D", "^", "v", "P"]

    for i, gap_type in enumerate(gap_types):
        gap_df = df_sized[df_sized["gap_type"] == gap_type]
        sizes = sorted(gap_df["model_size"].unique())
        accs, ci_los, ci_his = [], [], []

        for size in sizes:
            size_df = gap_df[gap_df["model_size"] == size]
            acc, ci_lo, ci_hi = _compute_accuracy_with_ci(size_df)
            accs.append(acc)
            ci_los.append(acc - ci_lo)
            ci_his.append(ci_hi - acc)

        color = pub_style.GAP_TYPE_COLORS.get(gap_type, pub_style.FAMILY_COLORS["Other"])
        short_label = gap_type.split(": ")[1] if ": " in gap_type else gap_type

        ax.errorbar(
            sizes, accs,
            yerr=[ci_los, ci_his],
            marker=gap_markers[i % len(gap_markers)],
            markersize=4, linewidth=1.2,
            color=color, label=short_label, capsize=2,
        )

    ax.set_xscale("log")
    ax.set_xlabel("Model Size (B params)")
    ax.set_ylabel("Accuracy")
    ax.set_ylim(-0.05, 1.05)
    ax.set_title("Scale Sensitivity by Gap Type")
    ax.legend(loc="lower right", fontsize=6)

    pub_style.savefig(fig, Path(output_dir) / "scale_sensitivity")


# ---------------------------------------------------------------------------
# Figure 5: Intervention Comparison
# ---------------------------------------------------------------------------

def plot_intervention_comparison(df: pd.DataFrame, output_dir: str) -> None:
    """Bar chart: for each gap type, bars for each condition.

    Uses condition colors from pub_style with hatching for extra distinction.
    """
    pub_style.setup()

    gap_types = [g for g in GAP_TYPE_ORDER if g in df["gap_type"].unique()]
    conditions = [c for c in CONDITION_ORDER if c in df["condition"].unique()]
    if not gap_types or not conditions:
        return

    fig, ax = pub_style.figure(width="full", height=2.8)

    n_gaps = len(gap_types)
    n_conds = len(conditions)
    bar_width = 0.8 / n_conds
    x = np.arange(n_gaps)

    hatches = ["", "//", "\\\\", "xx", ".."]

    for i, cond in enumerate(conditions):
        accs, ci_los, ci_his = [], [], []

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

        color = pub_style.CONDITION_COLORS.get(cond, "#333333")
        label = CONDITION_LABELS.get(cond, cond)
        offset = (i - n_conds / 2 + 0.5) * bar_width

        bars = ax.bar(
            x + offset, accs,
            width=bar_width,
            yerr=[ci_los, ci_his],
            color=color, label=label,
            capsize=2, alpha=0.85,
            edgecolor="white", linewidth=0.3,
            hatch=hatches[i % len(hatches)],
        )

    # Descriptive gap type labels
    short_labels = [g.split(": ")[1] if ": " in g else g for g in gap_types]
    ax.set_xticks(x)
    ax.set_xticklabels(short_labels)
    ax.set_ylabel("Accuracy")
    ax.set_ylim(0, 1.05)
    ax.set_title("Intervention Effectiveness by Gap Type")
    ax.legend(loc="upper right")

    pub_style.savefig(fig, Path(output_dir) / "intervention_comparison")


# ---------------------------------------------------------------------------
# Figure 6: Tool Use Comparison
# ---------------------------------------------------------------------------

def plot_tool_use_comparison(df: pd.DataFrame, output_dir: str) -> None:
    """Bar chart comparing conditions on tasks with tool_use data."""
    pub_style.setup()

    tool_use_tasks = df[df["condition"] == "tool_use"]["task"].unique()
    if len(tool_use_tasks) == 0:
        return

    tasks = [t for t in TASK_ORDER if t in tool_use_tasks]
    if not tasks:
        return

    tool_use_models = df[df["condition"] == "tool_use"]["model"].unique()
    df_sub = df[(df["model"].isin(tool_use_models)) & (df["task"].isin(tasks))]

    conditions = [c for c in CONDITION_ORDER if c in df_sub["condition"].unique()]

    fig, ax = pub_style.figure(width="full", height=2.8)

    n_tasks = len(tasks)
    n_conds = len(conditions)
    bar_width = 0.8 / n_conds
    x = np.arange(n_tasks)

    hatches = ["", "//", "\\\\", "xx"]

    for i, cond in enumerate(conditions):
        accs, ci_los, ci_his = [], [], []

        for task in tasks:
            mask = (df_sub["task"] == task) & (df_sub["condition"] == cond)
            group = df_sub[mask]
            if group.empty:
                accs.append(0.0)
                ci_los.append(0.0)
                ci_his.append(0.0)
            else:
                acc, ci_lo, ci_hi = _compute_accuracy_with_ci(group)
                accs.append(acc)
                ci_los.append(acc - ci_lo)
                ci_his.append(ci_hi - acc)

        color = pub_style.CONDITION_COLORS.get(cond, "#333333")
        label = CONDITION_LABELS.get(cond, cond)
        offset = (i - n_conds / 2 + 0.5) * bar_width

        ax.bar(
            x + offset, accs,
            width=bar_width,
            yerr=[ci_los, ci_his],
            color=color, label=label,
            capsize=2, alpha=0.85,
            edgecolor="white", linewidth=0.3,
            hatch=hatches[i % len(hatches)],
        )

    task_labels = [TASK_SHORT_LABELS.get(t, t) for t in tasks]
    ax.set_xticks(x)
    ax.set_xticklabels(task_labels)
    ax.set_ylabel("Accuracy")
    ax.set_ylim(0, 1.05)
    ax.set_title("Tool Use vs.\\ Other Conditions")
    ax.legend(loc="upper right")

    pub_style.savefig(fig, Path(output_dir) / "tool_use_comparison")


# ---------------------------------------------------------------------------
# Figure 7: Budget Sensitivity
# ---------------------------------------------------------------------------

def plot_budget_sensitivity(df: pd.DataFrame, output_dir: str) -> None:
    """Line plot of accuracy vs budget multiplier for B2 and B3.

    Two subplots with panel labels. Lines colored by model family.
    """
    pub_style.setup()

    budget_sweep_conds = sorted(
        c for c in df["condition"].unique()
        if c.startswith("budget_cot_") and c.endswith("x")
    )
    if not budget_sweep_conds:
        return

    def _parse_mult(cond: str) -> float:
        return float(cond.replace("budget_cot_", "").rstrip("x"))

    mult_map = {c: _parse_mult(c) for c in budget_sweep_conds}

    target_tasks = ["B2_nested_boolean", "B3_permutation_composition"]
    tasks_present = [t for t in target_tasks if t in df["task"].unique()]
    if not tasks_present:
        return

    n_plots = len(tasks_present)
    fig, axes = pub_style.figure(
        width="full",
        height=2.8,
        nrows=1,
        ncols=n_plots,
        squeeze=False,
    )

    models = sorted(df[df["condition"].isin(budget_sweep_conds)]["model"].unique())
    family_map = {m: _extract_model_family(m) for m in models}

    panel_labels = "ab"

    for col_idx, task in enumerate(tasks_present):
        ax = axes[0][col_idx]
        task_df = df[(df["task"] == task) & (df["condition"].isin(budget_sweep_conds))]

        for model in models:
            model_df = task_df[task_df["model"] == model]
            if model_df.empty:
                continue

            mults, accs, ci_los, ci_his = [], [], [], []

            for cond in sorted(budget_sweep_conds, key=lambda c: mult_map[c]):
                cond_df = model_df[model_df["condition"] == cond]
                if cond_df.empty:
                    continue
                acc, ci_lo, ci_hi = _compute_accuracy_with_ci(cond_df)
                mults.append(mult_map[cond])
                accs.append(acc)
                ci_los.append(acc - ci_lo)
                ci_his.append(ci_hi - acc)

            if not mults:
                continue

            family = family_map[model]
            color = pub_style.FAMILY_COLORS.get(family, pub_style.FAMILY_COLORS["Other"])

            ax.errorbar(
                mults, accs,
                yerr=[ci_los, ci_his],
                marker="o", markersize=3, linewidth=1.0,
                color=color, label=pub_style.get_model_display(model),
                capsize=2,
            )

        short_label = TASK_SHORT_LABELS.get(task, task)
        ax.set_title(short_label)
        ax.set_xlabel("Budget Multiplier")
        ax.set_ylabel("Accuracy")
        ax.set_ylim(-0.05, 1.05)
        ax.set_xscale("log", base=2)
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v}x"))
        ax.legend(loc="best", fontsize=5.5, ncol=1, handlelength=1.2)

        if col_idx < len(panel_labels):
            pub_style.panel_label(ax, panel_labels[col_idx])

    pub_style.savefig(fig, Path(output_dir) / "budget_sensitivity")


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def generate_all_figures(df: pd.DataFrame, output_dir: str) -> None:
    """Generate all paper figures from a loaded DataFrame."""
    print("Generating Figure 1: Accuracy vs Difficulty...")
    plot_accuracy_vs_difficulty(df, output_dir)

    print("Generating Figure 2: CoT Lift Heatmap...")
    plot_cot_lift_heatmap(df, output_dir)

    print("Generating Figure 3: Phase Transition...")
    plot_phase_transition(df, output_dir)

    print("Generating Figure 4: Scale Sensitivity...")
    plot_scale_sensitivity(df, output_dir)

    print("Generating Figure 5: Intervention Comparison...")
    plot_intervention_comparison(df, output_dir)

    print("Generating Figure 6: Tool Use...")
    plot_tool_use_comparison(df, output_dir)

    print("Generating Figure 7: Budget Sensitivity...")
    plot_budget_sensitivity(df, output_dir)

    print("All figures generated.")
