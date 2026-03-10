"""Visualization utilities for ReasonGap benchmark.

Provides consistent styling, color schemes, and utility functions for all plots.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import Dict, List, Optional, Tuple
from pathlib import Path


# Publication-ready settings
def setup_publication_style():
    """Configure matplotlib for publication-quality figures."""
    plt.rcParams.update({
        # Figure
        'figure.figsize': (8, 6),
        'figure.dpi': 300,
        'savefig.dpi': 300,
        'savefig.bbox': 'tight',
        'savefig.pad_inches': 0.1,

        # Font
        'font.family': 'serif',
        'font.serif': ['Times New Roman', 'DejaVu Serif'],
        'font.size': 10,
        'axes.labelsize': 11,
        'axes.titlesize': 12,
        'xtick.labelsize': 9,
        'ytick.labelsize': 9,
        'legend.fontsize': 9,

        # Lines and markers
        'lines.linewidth': 1.5,
        'lines.markersize': 6,
        'patch.linewidth': 0.5,

        # Axes
        'axes.linewidth': 0.8,
        'axes.grid': True,
        'axes.axisbelow': True,
        'grid.alpha': 0.3,
        'grid.linewidth': 0.5,

        # Legend
        'legend.frameon': True,
        'legend.framealpha': 0.9,
        'legend.edgecolor': '0.8',

        # Colors
        'axes.prop_cycle': plt.cycler(color=sns.color_palette("colorblind")),
    })


# Color schemes
GAP_TYPE_COLORS = {
    "Type 1: Sensitivity": "#e74c3c",  # Red
    "Type 2: Depth-bounded": "#3498db",  # Blue
    "Type 3: Serial": "#2ecc71",  # Green
    "Type 4: Counterfactual": "#f39c12",  # Orange
    "Type 5: Algorithmic": "#9b59b6",  # Purple
    "Type 6: Intractability": "#95a5a6"  # Gray
}

CONDITION_COLORS = {
    "direct": "#34495e",  # Dark gray
    "short_cot": "#3498db",  # Blue
    "budget_cot_log": "#52b3d9",  # Light blue
    "budget_cot_linear": "#73c6e3",  # Lighter blue
    "tool": "#e67e22"  # Orange
}

MODEL_FAMILY_COLORS = {
    "Claude": "#7b68ee",  # Medium slate blue
    "GPT": "#20b2aa",  # Light sea green
    "Llama": "#ff6347",  # Tomato
    "Mistral": "#ffa500",  # Orange
    "Qwen": "#9370db"  # Medium purple
}

MODEL_SIZE_MARKERS = {
    "small": "o",  # Circle
    "medium": "s",  # Square
    "large": "D"  # Diamond
}


def get_gap_type_color(gap_type: str) -> str:
    """Get color for gap type."""
    return GAP_TYPE_COLORS.get(gap_type, "#95a5a6")


def get_condition_color(condition: str) -> str:
    """Get color for condition."""
    return CONDITION_COLORS.get(condition, "#95a5a6")


def get_family_color(family: str) -> str:
    """Get color for model family."""
    return MODEL_FAMILY_COLORS.get(family, "#95a5a6")


def get_size_marker(size: str) -> str:
    """Get marker for model size."""
    return MODEL_SIZE_MARKERS.get(size, "o")


def add_significance_bars(
    ax: plt.Axes,
    x_positions: List[float],
    p_values: List[float],
    y_max: float,
    bar_height: float = 0.05,
    text_offset: float = 0.02
):
    """Add significance bars to plot.

    Args:
        ax: Matplotlib axes
        x_positions: List of [x1, x2] pairs for each comparison
        p_values: P-values for each comparison
        y_max: Maximum y value
        bar_height: Height of significance bar
        text_offset: Offset for significance text
    """
    for i, ((x1, x2), p) in enumerate(zip(x_positions, p_values)):
        y = y_max + bar_height * (i + 1)

        # Draw bar
        ax.plot([x1, x1, x2, x2], [y, y + bar_height, y + bar_height, y],
                'k-', linewidth=1)

        # Add significance text
        if p < 0.001:
            sig_text = "***"
        elif p < 0.01:
            sig_text = "**"
        elif p < 0.05:
            sig_text = "*"
        else:
            sig_text = "ns"

        ax.text((x1 + x2) / 2, y + bar_height + text_offset, sig_text,
                ha='center', va='bottom', fontsize=9)


def format_p_value(p: float) -> str:
    """Format p-value for display.

    Args:
        p: P-value

    Returns:
        Formatted string
    """
    if p < 0.001:
        return "p < 0.001"
    elif p < 0.01:
        return f"p = {p:.3f}"
    else:
        return f"p = {p:.2f}"


def add_effect_size_text(
    ax: plt.Axes,
    x: float,
    y: float,
    effect_size: float,
    effect_name: str = "d"
):
    """Add effect size annotation to plot.

    Args:
        ax: Matplotlib axes
        x: X position
        y: Y position
        effect_size: Effect size value
        effect_name: Name of effect size (e.g., "d", "η²", "r")
    """
    text = f"{effect_name} = {effect_size:.2f}"
    ax.text(x, y, text, fontsize=9, bbox=dict(boxstyle='round',
            facecolor='wheat', alpha=0.5))


def save_figure(
    fig: plt.Figure,
    output_path: Path,
    formats: List[str] = ["pdf", "png"]
):
    """Save figure in multiple formats.

    Args:
        fig: Matplotlib figure
        output_path: Output path (without extension)
        formats: List of formats to save
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    for fmt in formats:
        save_path = output_path.with_suffix(f".{fmt}")
        fig.savefig(save_path, format=fmt, bbox_inches='tight', dpi=300)
        print(f"Saved: {save_path}")


def create_legend_outside(
    ax: plt.Axes,
    **legend_kwargs
):
    """Create legend outside plot area.

    Args:
        ax: Matplotlib axes
        **legend_kwargs: Additional arguments for legend
    """
    default_kwargs = {
        'bbox_to_anchor': (1.05, 1),
        'loc': 'upper left',
        'frameon': True
    }
    default_kwargs.update(legend_kwargs)
    ax.legend(**default_kwargs)


def add_gridlines(
    ax: plt.Axes,
    which: str = "both",
    axis: str = "both",
    alpha: float = 0.3
):
    """Add gridlines to plot.

    Args:
        ax: Matplotlib axes
        which: 'major', 'minor', or 'both'
        axis: 'x', 'y', or 'both'
        alpha: Grid transparency
    """
    ax.grid(True, which=which, axis=axis, alpha=alpha, linestyle='--')


def annotate_points(
    ax: plt.Axes,
    x: np.ndarray,
    y: np.ndarray,
    labels: List[str],
    offset: Tuple[float, float] = (5, 5),
    fontsize: int = 8
):
    """Annotate points with labels.

    Args:
        ax: Matplotlib axes
        x: X coordinates
        y: Y coordinates
        labels: Point labels
        offset: Offset in points (x, y)
        fontsize: Font size
    """
    for xi, yi, label in zip(x, y, labels):
        ax.annotate(
            label,
            (xi, yi),
            xytext=offset,
            textcoords='offset points',
            fontsize=fontsize,
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                     edgecolor='gray', alpha=0.7),
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0',
                          color='gray', lw=0.5)
        )


def create_heatmap_with_annotations(
    data: np.ndarray,
    row_labels: List[str],
    col_labels: List[str],
    ax: Optional[plt.Axes] = None,
    cmap: str = "RdYlGn",
    vmin: float = 0,
    vmax: float = 1,
    annot: bool = True,
    fmt: str = ".2f",
    cbar_label: str = ""
) -> plt.Axes:
    """Create annotated heatmap.

    Args:
        data: 2D array of values
        row_labels: Labels for rows
        col_labels: Labels for columns
        ax: Matplotlib axes (created if None)
        cmap: Colormap name
        vmin: Minimum value for colormap
        vmax: Maximum value for colormap
        annot: Whether to annotate cells
        fmt: Format string for annotations
        cbar_label: Label for colorbar

    Returns:
        Matplotlib axes
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 8))

    im = ax.imshow(data, cmap=cmap, vmin=vmin, vmax=vmax, aspect='auto')

    # Set ticks and labels
    ax.set_xticks(np.arange(len(col_labels)))
    ax.set_yticks(np.arange(len(row_labels)))
    ax.set_xticklabels(col_labels)
    ax.set_yticklabels(row_labels)

    # Rotate x labels
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    # Annotate cells
    if annot:
        for i in range(len(row_labels)):
            for j in range(len(col_labels)):
                text = ax.text(j, i, format(data[i, j], fmt),
                             ha="center", va="center", color="black" if data[i, j] > (vmax - vmin) / 2 else "white")

    # Colorbar
    cbar = plt.colorbar(im, ax=ax)
    if cbar_label:
        cbar.set_label(cbar_label)

    return ax


def create_subplot_grid(
    n_plots: int,
    ncols: int = 3,
    figsize_per_plot: Tuple[float, float] = (4, 3),
    **subplot_kwargs
) -> Tuple[plt.Figure, List[plt.Axes]]:
    """Create grid of subplots.

    Args:
        n_plots: Number of plots
        ncols: Number of columns
        figsize_per_plot: Size of each subplot
        **subplot_kwargs: Additional arguments for subplots

    Returns:
        Tuple of (figure, list of axes)
    """
    nrows = int(np.ceil(n_plots / ncols))
    figsize = (figsize_per_plot[0] * ncols, figsize_per_plot[1] * nrows)

    fig, axes = plt.subplots(nrows, ncols, figsize=figsize, **subplot_kwargs)

    # Flatten axes array
    if nrows == 1 and ncols == 1:
        axes = [axes]
    elif nrows == 1 or ncols == 1:
        axes = axes.flatten()
    else:
        axes = axes.flatten()

    # Hide extra subplots
    for i in range(n_plots, len(axes)):
        axes[i].set_visible(False)

    return fig, axes


def add_correlation_line(
    ax: plt.Axes,
    x: np.ndarray,
    y: np.ndarray,
    color: str = 'red',
    linestyle: str = '--',
    label: Optional[str] = None
):
    """Add correlation line to scatter plot.

    Args:
        ax: Matplotlib axes
        x: X data
        y: Y data
        color: Line color
        linestyle: Line style
        label: Line label
    """
    # Fit line
    z = np.polyfit(x, y, 1)
    p = np.poly1d(z)

    # Plot line
    x_line = np.linspace(x.min(), x.max(), 100)
    ax.plot(x_line, p(x_line), color=color, linestyle=linestyle,
            linewidth=1.5, label=label, alpha=0.7)


# Initialize style on import
setup_publication_style()
