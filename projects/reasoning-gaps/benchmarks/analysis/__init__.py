"""ReasonGap analysis pipeline.

Transforms raw evaluation results into paper-ready tables, figures,
and statistical summaries for the NeurIPS submission.
"""

from analysis.loader import load_results, TASK_GAP_TYPE, MODEL_FAMILIES
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
from analysis.statistics import (
    bootstrap_ci,
    mcnemar_test,
    compute_all_cis,
    pairwise_model_comparison,
)

__all__ = [
    "load_results",
    "TASK_GAP_TYPE",
    "MODEL_FAMILIES",
    "main_accuracy_table",
    "accuracy_by_condition_table",
    "cot_lift_table",
    "scale_analysis_table",
    "to_latex",
    "plot_accuracy_vs_difficulty",
    "plot_cot_lift_heatmap",
    "plot_phase_transition",
    "plot_scale_sensitivity",
    "plot_intervention_comparison",
    "bootstrap_ci",
    "mcnemar_test",
    "compute_all_cis",
    "pairwise_model_comparison",
]
