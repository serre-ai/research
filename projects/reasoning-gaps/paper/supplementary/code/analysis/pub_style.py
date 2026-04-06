"""Publication-quality figure style for NeurIPS submission.

Single source of truth for all visualization styling. Both plotting codebases
(experiments/visualizations/ and paper/supplementary/code/analysis/) import
from here.

Design principles:
  - Computer Modern typography via LaTeX rendering (matches paper body)
  - Okabe-Ito colorblind-safe palette as base
  - Minimal chrome: no top/right spines, y-grid only, thin axes
  - NeurIPS-compliant sizing (column: 3.25in, full: 6.75in)
  - PDF vector output for LaTeX inclusion
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

# ---------------------------------------------------------------------------
# NeurIPS geometry
# ---------------------------------------------------------------------------

COL_W = 3.25    # single column width (inches)
FULL_W = 6.75   # full text width (inches)
DPI = 300

# Golden ratio for default aspect
_PHI = (1 + np.sqrt(5)) / 2


# ---------------------------------------------------------------------------
# Colorblind-safe palettes
# ---------------------------------------------------------------------------

# Okabe-Ito (2008) — the gold standard for colorblind accessibility.
# Dropped black; order tuned for our use case.
_OI = {
    "blue":       "#0072B2",
    "vermillion": "#D55E00",
    "green":      "#009E73",
    "orange":     "#E69F00",
    "skyblue":    "#56B4E9",
    "purple":     "#CC79A7",
    "yellow":     "#F0E442",
    "grey":       "#999999",
}

# --- Model family palette (5 families) ---
FAMILY_COLORS: dict[str, str] = {
    "Claude":  _OI["blue"],
    "GPT":     _OI["vermillion"],
    "Llama":   _OI["green"],
    "Mistral": _OI["orange"],
    "Qwen":    _OI["purple"],
    "Other":   _OI["grey"],
}

# --- Gap type palette (6 types) ---
# Keys must match loader.py GAP_TYPE_ORDER exactly.
GAP_TYPE_COLORS: dict[str, str] = {
    "Type 1: Sensitivity":     _OI["blue"],
    "Type 2: Depth":           _OI["vermillion"],
    "Type 3: Serial":          _OI["green"],
    "Type 4: Algorithmic":     _OI["orange"],
    "Type 5: Intractability":  _OI["purple"],
    "Type 6: Architectural":   _OI["grey"],
}

# Short-name variants for compact legends
GAP_TYPE_COLORS_SHORT: dict[str, str] = {
    k.split(": ")[1]: v for k, v in GAP_TYPE_COLORS.items()
}

# --- Condition palette ---
CONDITION_COLORS: dict[str, str] = {
    "direct":     "#2C3E50",      # near-black (baseline)
    "short_cot":  _OI["blue"],    # blue
    "budget_cot": _OI["orange"],  # orange (distinct from blue)
    "tool_use":   _OI["green"],   # green
}

CONDITION_LABELS: dict[str, str] = {
    "direct":     "Direct",
    "short_cot":  "Short CoT",
    "budget_cot": "Budget CoT",
    "tool_use":   "Tool Use",
}

# --- Model size markers ---
SIZE_MARKERS: dict[str, str] = {
    "small":  "o",
    "medium": "s",
    "large":  "D",
}

# --- Model display names (short, human-readable) ---
MODEL_DISPLAY: dict[str, str] = {
    "claude-haiku-4-5-20251001":                   "Haiku 4.5",
    "claude-sonnet-4-20250514":                    "Sonnet 4.6",
    "claude-opus-4-6":                             "Opus 4.6",
    "gpt-4o":                                      "GPT-4o",
    "gpt-4o-mini":                                 "GPT-4o-m",
    "o3":                                          "o3",
    "meta-llama/llama-3.1-8b-instruct":            "Llama 8B",
    "meta-llama/llama-3.1-70b-instruct":           "Llama 70B",
    "mistralai/ministral-8b-2512":                 "Ministral 8B",
    "mistralai/mistral-small-24b-instruct-2501":   "Mistral 24B",
    "qwen/qwen-2.5-72b-instruct":                 "Qwen 72B",
    "qwen/qwen-2.5-7b-instruct":                  "Qwen 7B",
}

# Map model → family
MODEL_FAMILY: dict[str, str] = {
    "claude-haiku-4-5-20251001":                   "Claude",
    "claude-sonnet-4-20250514":                    "Claude",
    "claude-opus-4-6":                             "Claude",
    "gpt-4o":                                      "GPT",
    "gpt-4o-mini":                                 "GPT",
    "o3":                                          "GPT",
    "meta-llama/llama-3.1-8b-instruct":            "Llama",
    "meta-llama/llama-3.1-70b-instruct":           "Llama",
    "mistralai/ministral-8b-2512":                 "Mistral",
    "mistralai/mistral-small-24b-instruct-2501":   "Mistral",
    "qwen/qwen-2.5-72b-instruct":                 "Qwen",
    "qwen/qwen-2.5-7b-instruct":                  "Qwen",
}


def get_model_display(model: str) -> str:
    """Short display name for a model."""
    return MODEL_DISPLAY.get(model, model.split("/")[-1])


def get_model_color(model: str) -> str:
    """Consistent color for a model based on its family."""
    family = MODEL_FAMILY.get(model, "Other")
    return FAMILY_COLORS.get(family, FAMILY_COLORS["Other"])


def get_model_family(model: str) -> str:
    """Extract family name for a model."""
    return MODEL_FAMILY.get(model, "Other")


# ---------------------------------------------------------------------------
# Conference-aware configuration
# ---------------------------------------------------------------------------

def load_conference(name: str = "neurips2026") -> dict:
    """Load conference config from shared/templates/paper/conferences.yaml.

    Falls back to built-in NeurIPS defaults if the file isn't found.
    """
    import yaml

    # Search for conferences.yaml up the directory tree
    base = Path(__file__).resolve().parent
    candidates = []
    for _ in range(5):
        candidates.append(base / "shared" / "templates" / "paper" / "conferences.yaml")
        base = base.parent

    for p in candidates:
        if p.exists():
            with open(p) as f:
                data = yaml.safe_load(f)
            confs = data.get("conferences", {})
            if name in confs:
                return confs[name]

    # Built-in fallback (NeurIPS defaults)
    return {
        "pub_style": {
            "col_width": 3.25,
            "full_width": 6.75,
            "font_size": 8,
            "title_size": 9,
            "tick_size": 7,
            "legend_size": 7,
        }
    }


# ---------------------------------------------------------------------------
# Style setup
# ---------------------------------------------------------------------------

def setup(*, usetex: bool = True, conference: str = "neurips2026") -> None:
    """Configure matplotlib for publication-quality figures.

    Adapts sizing and typography to the target conference.

    Args:
        usetex: Use LaTeX for text rendering (Computer Modern font).
                Set False if LaTeX is not installed.
        conference: Conference name (e.g. "neurips2026", "icml2025", "acl2025").
                    Loads sizing from shared/templates/paper/conferences.yaml.
    """
    global COL_W, FULL_W

    # Load conference-specific sizing
    try:
        conf = load_conference(conference)
        ps = conf.get("pub_style", {})
        COL_W = ps.get("col_width", COL_W)
        FULL_W = ps.get("full_width", FULL_W)
        _font_size = ps.get("font_size", 8)
        _title_size = ps.get("title_size", 9)
        _tick_size = ps.get("tick_size", 7)
        _legend_size = ps.get("legend_size", 7)
    except Exception:
        _font_size, _title_size, _tick_size, _legend_size = 8, 9, 7, 7

    plt.rcParams.update({
        # --- TeX rendering ---
        "text.usetex":           usetex,
        "text.latex.preamble":   r"\usepackage{amsmath}\usepackage{amssymb}" if usetex else "",

        # --- Font ---
        "font.family":           "serif",
        "font.serif":            ["Computer Modern Roman", "cmr10", "Times New Roman", "DejaVu Serif"],
        "font.size":             _font_size,
        "axes.labelsize":        _font_size,
        "axes.titlesize":        _title_size,
        "xtick.labelsize":       _tick_size,
        "ytick.labelsize":       _tick_size,
        "legend.fontsize":       _legend_size,
        "legend.title_fontsize": _legend_size,

        # --- Figure ---
        "figure.figsize":        (FULL_W, FULL_W / _PHI),
        "figure.dpi":            150,       # screen preview
        "figure.constrained_layout.use": True,

        # --- Save ---
        "savefig.dpi":           DPI,
        "savefig.bbox":          "tight",
        "savefig.pad_inches":    0.02,
        "savefig.transparent":   False,

        # --- Axes ---
        "axes.linewidth":        0.6,
        "axes.grid":             True,
        "axes.grid.axis":        "y",       # y-grid only
        "axes.axisbelow":        True,
        "axes.spines.top":       False,
        "axes.spines.right":     False,
        "axes.prop_cycle":       plt.cycler(color=list(_OI.values())),
        "axes.titleweight":      "bold",
        "axes.labelpad":         3,

        # --- Grid ---
        "grid.alpha":            0.25,
        "grid.linewidth":        0.4,
        "grid.linestyle":        "-",
        "grid.color":            "#CCCCCC",

        # --- Lines & markers ---
        "lines.linewidth":       1.2,
        "lines.markersize":      4,
        "lines.markeredgewidth": 0.5,
        "lines.markeredgecolor": "white",
        "patch.linewidth":       0.5,

        # --- Legend ---
        "legend.frameon":        True,
        "legend.framealpha":     0.9,
        "legend.edgecolor":      "0.85",
        "legend.fancybox":       False,
        "legend.borderpad":      0.4,
        "legend.handlelength":   1.5,
        "legend.handleheight":   0.7,
        "legend.labelspacing":   0.3,
        "legend.columnspacing":  1.0,

        # --- Ticks ---
        "xtick.major.width":     0.6,
        "ytick.major.width":     0.6,
        "xtick.major.size":      3,
        "ytick.major.size":      3,
        "xtick.minor.size":      1.5,
        "ytick.minor.size":      1.5,
        "xtick.direction":       "out",
        "ytick.direction":       "out",
        "axes.formatter.use_mathtext": True,

        # --- Errorbar ---
        "errorbar.capsize":      2,

        # --- Hatch ---
        "hatch.linewidth":       0.5,
    })


# ---------------------------------------------------------------------------
# Figure creation helpers
# ---------------------------------------------------------------------------

def figure(
    width: str = "full",
    aspect: float | None = None,
    height: float | None = None,
    nrows: int = 1,
    ncols: int = 1,
    **kwargs,
) -> tuple[plt.Figure, np.ndarray | plt.Axes]:
    """Create a figure with NeurIPS-compliant sizing.

    Args:
        width: "col" for single column, "full" for full width.
        aspect: Height/width ratio. Default: 1/golden ratio.
        height: Explicit height in inches (overrides aspect).
        nrows, ncols: Subplot grid dimensions.
        **kwargs: Passed to plt.subplots().

    Returns:
        (fig, axes) tuple.
    """
    w = COL_W if width == "col" else FULL_W

    if height is not None:
        h = height
    elif aspect is not None:
        h = w * aspect
    else:
        h = w / _PHI
        if nrows > 1:
            h = h * nrows / 1.5  # scale for multi-row

    fig, axes = plt.subplots(nrows, ncols, figsize=(w, h), **kwargs)
    return fig, axes


def panel_label(
    ax: plt.Axes,
    label: str,
    x: float = -0.12,
    y: float = 1.08,
) -> None:
    """Add bold panel label like (a), (b) to a subplot.

    Args:
        ax: Target axes.
        label: Label text, e.g. "a" (parentheses added automatically).
        x, y: Position in axes fraction coordinates.
    """
    ax.text(
        x, y, f"({label})",
        transform=ax.transAxes,
        fontsize=10,
        fontweight="bold",
        va="top",
        ha="right",
    )


def savefig(
    fig: plt.Figure,
    path: str | Path,
    formats: list[str] | None = None,
    close: bool = True,
) -> None:
    """Save figure in publication formats.

    Args:
        fig: Figure to save.
        path: Output path without extension.
        formats: List of formats. Default: ["pdf", "png"].
        close: Close figure after saving.
    """
    if formats is None:
        formats = ["pdf", "png"]

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    for fmt in formats:
        save_path = path.with_suffix(f".{fmt}")
        fig.savefig(save_path, format=fmt)
        print(f"  -> {save_path}")

    if close:
        plt.close(fig)


# ---------------------------------------------------------------------------
# Diverging colormap (colorblind-safe)
# ---------------------------------------------------------------------------

def diverging_cmap(
    neg: str = "#2166AC",   # dark blue
    zero: str = "#F7F7F7",  # near-white
    pos: str = "#B2182B",   # dark red
    name: str = "pub_diverging",
) -> mpl.colors.LinearSegmentedColormap:
    """Blue-white-red diverging colormap (colorblind-safe).

    Avoids the red-green scheme that fails for ~8% of male readers.
    """
    from matplotlib.colors import LinearSegmentedColormap
    return LinearSegmentedColormap.from_list(name, [neg, zero, pos], N=256)


# ---------------------------------------------------------------------------
# Annotation helpers
# ---------------------------------------------------------------------------

def significance_text(p: float) -> str:
    """Convert p-value to significance stars."""
    if p < 0.001:
        return "***"
    elif p < 0.01:
        return "**"
    elif p < 0.05:
        return "*"
    return "n.s."


def format_p(p: float) -> str:
    """Format p-value for display."""
    if p < 0.001:
        return r"$p < 0.001$"
    elif p < 0.01:
        return f"$p = {p:.3f}$"
    return f"$p = {p:.2f}$"


def add_significance_bracket(
    ax: plt.Axes,
    x1: float, x2: float,
    y: float,
    p: float,
    height: float = 0.02,
) -> None:
    """Add a significance bracket between two x positions."""
    ax.plot([x1, x1, x2, x2], [y, y + height, y + height, y],
            color="0.3", linewidth=0.8, clip_on=False)
    ax.text(
        (x1 + x2) / 2, y + height + 0.005,
        significance_text(p),
        ha="center", va="bottom", fontsize=7, color="0.3",
    )


def effect_size_annotation(
    ax: plt.Axes,
    x: float, y: float,
    d: float,
    name: str = "d",
) -> None:
    """Add effect size annotation with semi-transparent background."""
    ax.text(
        x, y, f"${name} = {d:.2f}$",
        fontsize=7,
        bbox=dict(
            boxstyle="round,pad=0.3",
            facecolor="white",
            edgecolor="0.8",
            alpha=0.85,
        ),
    )


# ---------------------------------------------------------------------------
# Tick formatting helpers
# ---------------------------------------------------------------------------

def percent_formatter(ax: plt.Axes, axis: str = "y") -> None:
    """Format tick labels as percentages (0.85 → 85%)."""
    fmt = mticker.FuncFormatter(lambda v, _: f"{v:.0%}")
    if axis in ("y", "both"):
        ax.yaxis.set_major_formatter(fmt)
    if axis in ("x", "both"):
        ax.xaxis.set_major_formatter(fmt)


def integer_ticks(ax: plt.Axes, axis: str = "x") -> None:
    """Force integer tick labels."""
    loc = mticker.MaxNLocator(integer=True)
    if axis in ("x", "both"):
        ax.xaxis.set_major_locator(loc)
    if axis in ("y", "both"):
        ax.yaxis.set_major_locator(loc)


# ---------------------------------------------------------------------------
# Caption templates — every figure gets a takeaway, not just axis labels
# ---------------------------------------------------------------------------

CAPTION_TEMPLATES: dict[str, str] = {
    "comparison_bar": "{metric} by {grouping}. {finding}. Error bars: 95\\% bootstrap CIs.",
    "scaling_curve": "{metric} vs {variable} for {conditions}. {finding}.",
    "heatmap": "{metric} across {rows} and {columns}. {finding}.",
    "phase_transition": "{metric} near {transition}. {finding}.",
    "scatter": "{x_metric} vs {y_metric} across {groups}. {finding}.",
    "distribution": "Distribution of {metric} across {grouping}. {finding}.",
}


def generate_caption(figure_type: str, **kwargs) -> str:
    """Generate a caption from template. Missing keys are left blank.

    Usage:
        caption = generate_caption("comparison_bar",
            metric="Verifier accuracy",
            grouping="task and VC class",
            finding="P-class tasks show 95%+ accuracy while coNP tasks drop to 64%",
        )
    """
    template = CAPTION_TEMPLATES.get(figure_type, "{finding}")
    # Fill known keys, leave unknown as empty
    filled = {}
    for key in ["metric", "grouping", "finding", "variable", "conditions",
                 "rows", "columns", "transition", "x_metric", "y_metric",
                 "groups", "correlation"]:
        filled[key] = kwargs.get(key, "")
    try:
        return template.format(**filled)
    except KeyError:
        return kwargs.get("finding", "")


# ---------------------------------------------------------------------------
# Standard figure layout helpers
# ---------------------------------------------------------------------------


def comparison_bar(
    data,
    x: str,
    y: str,
    hue: str | None = None,
    ci: float = 95,
    y_is_proportion: bool = True,
    title: str | None = None,
    width: str = "full",
    **kwargs,
) -> tuple[plt.Figure, plt.Axes]:
    """Grouped bar chart for comparing discrete categories.

    Use for: tasks vs accuracy, models vs score, conditions vs lift.

    Args:
        data: DataFrame with columns x, y, and optionally hue.
        x: Column for x-axis categories.
        y: Column for y-axis values.
        hue: Column for grouping (colored bars).
        ci: Confidence interval level (default 95).
        y_is_proportion: If True, format y-axis as percentage.
    """
    import seaborn as sns

    setup()
    fig, ax = figure(width=width)

    palette = None
    if hue:
        # Try to match hue values to known palettes
        unique_hues = sorted(data[hue].unique())
        if all(h in FAMILY_COLORS for h in unique_hues):
            palette = {h: FAMILY_COLORS[h] for h in unique_hues}
        elif all(h in GAP_TYPE_COLORS for h in unique_hues):
            palette = {h: GAP_TYPE_COLORS[h] for h in unique_hues}

    sns.barplot(data=data, x=x, y=y, hue=hue, errorbar=("ci", ci), palette=palette, ax=ax, **kwargs)

    if y_is_proportion:
        percent_formatter(ax, "y")

    if title:
        ax.set_title(title)

    ax.set_xlabel(ax.get_xlabel() or x)
    ax.set_ylabel(ax.get_ylabel() or y)

    return fig, ax


def scaling_curve(
    data,
    x: str,
    y: str,
    hue: str | None = None,
    style: str | None = None,
    y_is_proportion: bool = True,
    logx: bool = False,
    title: str | None = None,
    width: str = "full",
    **kwargs,
) -> tuple[plt.Figure, plt.Axes]:
    """Line chart for trends over a continuous variable.

    Use for: accuracy vs N (sample count), accuracy vs difficulty, cost vs model size.

    Args:
        data: DataFrame with columns x, y, and optionally hue/style.
        logx: If True, use log scale on x-axis.
    """
    import seaborn as sns

    setup()
    fig, ax = figure(width=width)

    sns.lineplot(data=data, x=x, y=y, hue=hue, style=style,
                 marker="o", ax=ax, **kwargs)

    if y_is_proportion:
        percent_formatter(ax, "y")
    if logx:
        ax.set_xscale("log", base=2)
        integer_ticks(ax, "x")

    if title:
        ax.set_title(title)

    return fig, ax


def task_heatmap(
    data,
    rows: str,
    columns: str,
    values: str,
    vmin: float = 0,
    vmax: float = 1,
    fmt: str = ".2f",
    title: str | None = None,
    width: str = "full",
    **kwargs,
) -> tuple[plt.Figure, plt.Axes]:
    """Heatmap for two-dimensional grids.

    Use for: model x task accuracy, condition x gap type lift.

    Args:
        data: DataFrame that will be pivoted to rows x columns.
        rows: Column to use as row index.
        columns: Column to use as column headers.
        values: Column containing the values to display.
    """
    import seaborn as sns

    setup()

    pivot = data.pivot_table(index=rows, columns=columns, values=values, aggfunc="mean")
    aspect = max(0.4, len(pivot.columns) / max(len(pivot.index), 1) * 0.5)
    fig, ax = figure(width=width, aspect=aspect)

    cmap = diverging_cmap() if vmin < 0 else "YlOrRd"
    sns.heatmap(pivot, annot=True, fmt=fmt, cmap=cmap,
                vmin=vmin, vmax=vmax, linewidths=0.5,
                cbar_kws={"shrink": 0.8}, ax=ax, **kwargs)

    if title:
        ax.set_title(title)

    return fig, ax


def phase_plot(
    data,
    x: str,
    y: str,
    conditions: str | None = None,
    y_is_proportion: bool = True,
    title: str | None = None,
    width: str = "col",
    **kwargs,
) -> tuple[plt.Figure, plt.Axes]:
    """Specialized plot for phase transition behavior.

    Use for: 3-SAT accuracy vs clause ratio, difficulty threshold effects.
    """
    import seaborn as sns

    setup()
    fig, ax = figure(width=width)

    if conditions:
        for cond in sorted(data[conditions].unique()):
            subset = data[data[conditions] == cond]
            color = CONDITION_COLORS.get(cond, None)
            label = CONDITION_LABELS.get(cond, cond)
            ls = "--" if "cot" in str(cond).lower() else "-"
            ax.plot(subset[x], subset[y], marker="o", color=color,
                    linestyle=ls, label=label, **kwargs)
        ax.legend()
    else:
        ax.plot(data[x], data[y], marker="o", **kwargs)

    if y_is_proportion:
        percent_formatter(ax, "y")

    if title:
        ax.set_title(title)

    return fig, ax
