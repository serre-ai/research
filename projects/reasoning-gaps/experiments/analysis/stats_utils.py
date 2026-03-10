"""Statistical test utilities for ReasonGap analysis.

Implements all statistical tests specified in empirical analysis plan:
- Correlation tests (Spearman, Pearson)
- ANOVA and post-hoc tests (Tukey HSD)
- Non-parametric tests (Friedman, Jonckheere-Terpstra)
- Mixed-effects models
- Effect size measures (Cohen's d, eta-squared)
- Bootstrap confidence intervals
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Optional, Tuple, List, Dict, Any
from scipy import stats
from scipy.stats import spearmanr, pearsonr, f_oneway, friedmanchisquare
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from statsmodels.formula.api import mixedlm
from statsmodels.stats.multitest import multipletests


@dataclass
class TestResult:
    """Standardized test result."""
    test_name: str
    statistic: float
    p_value: float
    effect_size: Optional[float] = None
    effect_size_name: Optional[str] = None
    df: Optional[float] = None
    interpretation: str = ""
    additional_info: Dict[str, Any] = None

    def __post_init__(self):
        if self.additional_info is None:
            self.additional_info = {}

    def is_significant(self, alpha: float = 0.05) -> bool:
        """Check if result is statistically significant."""
        return self.p_value < alpha

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "test": self.test_name,
            "statistic": float(self.statistic),
            "p_value": float(self.p_value),
            "effect_size": float(self.effect_size) if self.effect_size else None,
            "effect_size_name": self.effect_size_name,
            "df": float(self.df) if self.df else None,
            "significant": self.is_significant(),
            "interpretation": self.interpretation,
            **self.additional_info
        }


def spearman_correlation(
    x: np.ndarray,
    y: np.ndarray,
    alternative: str = "two-sided"
) -> TestResult:
    """Spearman rank correlation test.

    Args:
        x: First variable
        y: Second variable
        alternative: 'two-sided', 'greater', or 'less'

    Returns:
        TestResult with correlation coefficient and p-value
    """
    rho, p_value = spearmanr(x, y)

    # Interpretation
    if abs(rho) < 0.3:
        strength = "weak"
    elif abs(rho) < 0.7:
        strength = "moderate"
    else:
        strength = "strong"

    direction = "positive" if rho > 0 else "negative"

    return TestResult(
        test_name="Spearman correlation",
        statistic=rho,
        p_value=p_value,
        effect_size=rho,
        effect_size_name="rho",
        interpretation=f"{strength} {direction} correlation",
        additional_info={"n": len(x)}
    )


def one_way_anova(
    groups: List[np.ndarray],
    group_names: Optional[List[str]] = None
) -> TestResult:
    """One-way ANOVA test.

    Args:
        groups: List of arrays, one per group
        group_names: Optional names for groups

    Returns:
        TestResult with F-statistic and p-value
    """
    if group_names is None:
        group_names = [f"Group_{i+1}" for i in range(len(groups))]

    # Run ANOVA
    f_stat, p_value = f_oneway(*groups)

    # Calculate eta-squared (effect size)
    grand_mean = np.mean(np.concatenate(groups))
    ss_between = sum(len(g) * (np.mean(g) - grand_mean)**2 for g in groups)
    ss_total = sum(np.sum((g - grand_mean)**2) for g in groups)
    eta_squared = ss_between / ss_total if ss_total > 0 else 0

    # Degrees of freedom
    k = len(groups)
    n = sum(len(g) for g in groups)
    df_between = k - 1
    df_within = n - k

    # Interpretation
    if eta_squared < 0.01:
        strength = "negligible"
    elif eta_squared < 0.06:
        strength = "small"
    elif eta_squared < 0.14:
        strength = "medium"
    else:
        strength = "large"

    return TestResult(
        test_name="One-way ANOVA",
        statistic=f_stat,
        p_value=p_value,
        effect_size=eta_squared,
        effect_size_name="eta_squared",
        df=df_between,
        interpretation=f"{strength} effect",
        additional_info={
            "df_between": df_between,
            "df_within": df_within,
            "k": k,
            "n": n
        }
    )


def tukey_hsd_posthoc(
    data: pd.DataFrame,
    value_col: str,
    group_col: str,
    alpha: float = 0.05
) -> pd.DataFrame:
    """Tukey HSD post-hoc test for pairwise comparisons.

    Args:
        data: DataFrame with data
        value_col: Name of column with values
        group_col: Name of column with group labels
        alpha: Significance level

    Returns:
        DataFrame with pairwise comparison results
    """
    tukey = pairwise_tukeyhsd(
        endog=data[value_col],
        groups=data[group_col],
        alpha=alpha
    )

    # Convert to DataFrame
    results = pd.DataFrame(
        data=tukey.summary().data[1:],
        columns=tukey.summary().data[0]
    )

    return results


def friedman_test(
    *args: np.ndarray
) -> TestResult:
    """Friedman test (non-parametric repeated measures ANOVA).

    Args:
        *args: Multiple related samples (one per condition)

    Returns:
        TestResult with chi-square statistic and p-value
    """
    chi2, p_value = friedmanchisquare(*args)

    k = len(args)
    n = len(args[0])

    # Kendall's W (effect size)
    # W = chi2 / (n * (k - 1))
    w = chi2 / (n * (k - 1))

    # Interpretation
    if w < 0.1:
        strength = "negligible"
    elif w < 0.3:
        strength = "small"
    elif w < 0.5:
        strength = "medium"
    else:
        strength = "large"

    return TestResult(
        test_name="Friedman test",
        statistic=chi2,
        p_value=p_value,
        effect_size=w,
        effect_size_name="Kendall's W",
        df=k - 1,
        interpretation=f"{strength} effect",
        additional_info={
            "k": k,
            "n": n
        }
    )


def jonckheere_terpstra_test(
    groups: List[np.ndarray],
    alternative: str = "increasing"
) -> TestResult:
    """Jonckheere-Terpstra test for ordered alternatives.

    Tests if there is a monotonic trend across ordered groups.

    Args:
        groups: List of arrays in hypothesized order
        alternative: 'increasing' or 'decreasing'

    Returns:
        TestResult with J statistic and p-value
    """
    from scipy.stats import mannwhitneyu

    k = len(groups)
    n_total = sum(len(g) for g in groups)

    # Calculate J statistic (sum of Mann-Whitney U statistics)
    j_stat = 0
    for i in range(k):
        for j in range(i + 1, k):
            # Count pairs where groups[j] > groups[i]
            u_stat, _ = mannwhitneyu(groups[i], groups[j], alternative='less')
            j_stat += u_stat

    # Expected value and variance under null hypothesis
    n_i = [len(g) for g in groups]
    n_pairs = sum(n_i[i] * n_i[j] for i in range(k) for j in range(i+1, k))

    e_j = n_pairs / 2

    # Variance (simplified formula)
    var_j = 0
    for i in range(k):
        for j in range(i + 1, k):
            var_j += n_i[i] * n_i[j] * (n_i[i] + n_i[j] + 1) / 12

    # Z-score
    z_stat = (j_stat - e_j) / np.sqrt(var_j) if var_j > 0 else 0

    # P-value (one-tailed)
    if alternative == "increasing":
        p_value = 1 - stats.norm.cdf(z_stat)
    else:  # decreasing
        p_value = stats.norm.cdf(z_stat)

    return TestResult(
        test_name="Jonckheere-Terpstra test",
        statistic=j_stat,
        p_value=p_value,
        effect_size=z_stat,
        effect_size_name="Z-score",
        interpretation=f"{'increasing' if z_stat > 0 else 'decreasing'} trend",
        additional_info={
            "k": k,
            "n_total": n_total,
            "e_j": e_j
        }
    )


def cohens_d(
    group1: np.ndarray,
    group2: np.ndarray,
    paired: bool = False
) -> float:
    """Calculate Cohen's d effect size.

    Args:
        group1: First group
        group2: Second group
        paired: Whether groups are paired

    Returns:
        Cohen's d effect size
    """
    if paired:
        diff = group1 - group2
        return np.mean(diff) / np.std(diff, ddof=1)
    else:
        mean_diff = np.mean(group1) - np.mean(group2)
        pooled_std = np.sqrt(
            ((len(group1) - 1) * np.var(group1, ddof=1) +
             (len(group2) - 1) * np.var(group2, ddof=1)) /
            (len(group1) + len(group2) - 2)
        )
        return mean_diff / pooled_std if pooled_std > 0 else 0


def paired_t_test(
    group1: np.ndarray,
    group2: np.ndarray,
    alternative: str = "two-sided"
) -> TestResult:
    """Paired t-test with Cohen's d effect size.

    Args:
        group1: First group (before)
        group2: Second group (after)
        alternative: 'two-sided', 'greater', or 'less'

    Returns:
        TestResult with t-statistic, p-value, and Cohen's d
    """
    t_stat, p_value = stats.ttest_rel(group1, group2, alternative=alternative)
    d = cohens_d(group1, group2, paired=True)

    # Interpretation
    if abs(d) < 0.2:
        strength = "negligible"
    elif abs(d) < 0.5:
        strength = "small"
    elif abs(d) < 0.8:
        strength = "medium"
    else:
        strength = "large"

    return TestResult(
        test_name="Paired t-test",
        statistic=t_stat,
        p_value=p_value,
        effect_size=d,
        effect_size_name="Cohen's d",
        df=len(group1) - 1,
        interpretation=f"{strength} effect",
        additional_info={"n": len(group1)}
    )


def bootstrap_ci(
    data: np.ndarray,
    statistic: callable = np.mean,
    n_bootstrap: int = 1000,
    confidence_level: float = 0.95,
    random_seed: Optional[int] = None
) -> Tuple[float, float, float]:
    """Calculate bootstrap confidence interval.

    Args:
        data: Input data
        statistic: Function to compute statistic (default: mean)
        n_bootstrap: Number of bootstrap samples
        confidence_level: Confidence level (0-1)
        random_seed: Random seed for reproducibility

    Returns:
        Tuple of (point_estimate, lower_ci, upper_ci)
    """
    if random_seed is not None:
        np.random.seed(random_seed)

    point_estimate = statistic(data)

    bootstrap_stats = []
    n = len(data)

    for _ in range(n_bootstrap):
        sample = np.random.choice(data, size=n, replace=True)
        bootstrap_stats.append(statistic(sample))

    bootstrap_stats = np.array(bootstrap_stats)

    # Percentile method
    alpha = 1 - confidence_level
    lower_ci = np.percentile(bootstrap_stats, 100 * alpha / 2)
    upper_ci = np.percentile(bootstrap_stats, 100 * (1 - alpha / 2))

    return point_estimate, lower_ci, upper_ci


def bonferroni_correction(
    p_values: List[float],
    alpha: float = 0.05
) -> Tuple[List[bool], List[float]]:
    """Apply Bonferroni correction for multiple comparisons.

    Args:
        p_values: List of p-values
        alpha: Family-wise error rate

    Returns:
        Tuple of (reject_list, corrected_p_values)
    """
    reject, corrected_p, _, _ = multipletests(
        p_values,
        alpha=alpha,
        method='bonferroni'
    )
    return list(reject), list(corrected_p)


def mixed_effects_model(
    data: pd.DataFrame,
    formula: str,
    groups: str,
    re_formula: Optional[str] = None
) -> Dict[str, Any]:
    """Fit mixed-effects linear model.

    Args:
        data: DataFrame with data
        formula: R-style formula for fixed effects (e.g., "accuracy ~ size * gap_type")
        groups: Column name for grouping variable (random effect)
        re_formula: Optional formula for random effects structure

    Returns:
        Dictionary with model results
    """
    model = mixedlm(
        formula,
        data,
        groups=data[groups],
        re_formula=re_formula
    )

    result = model.fit()

    return {
        "params": result.params.to_dict(),
        "pvalues": result.pvalues.to_dict(),
        "conf_int": result.conf_int().to_dict(),
        "aic": result.aic,
        "bic": result.bic,
        "log_likelihood": result.llf,
        "summary": str(result.summary())
    }


def chi_square_test(
    contingency_table: np.ndarray
) -> TestResult:
    """Chi-square test of independence.

    Args:
        contingency_table: 2D array of observed frequencies

    Returns:
        TestResult with chi-square statistic and p-value
    """
    chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)

    # Cramér's V (effect size)
    n = contingency_table.sum()
    min_dim = min(contingency_table.shape) - 1
    cramers_v = np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 else 0

    # Interpretation
    if cramers_v < 0.1:
        strength = "negligible"
    elif cramers_v < 0.3:
        strength = "small"
    elif cramers_v < 0.5:
        strength = "medium"
    else:
        strength = "large"

    return TestResult(
        test_name="Chi-square test",
        statistic=chi2,
        p_value=p_value,
        effect_size=cramers_v,
        effect_size_name="Cramér's V",
        df=dof,
        interpretation=f"{strength} association",
        additional_info={"n": int(n)}
    )
