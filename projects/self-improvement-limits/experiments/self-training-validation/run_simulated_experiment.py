#!/usr/bin/env python3
"""
Simulated Self-Training Experiment

This script runs a simulated version of the self-training convergence validation
that demonstrates the expected behavior based on Theorems 1-3, without making
expensive API calls.

This serves as:
1. A validation that the experimental methodology is sound
2. A demonstration of what results we expect to see
3. A baseline for comparing real experimental results

Usage:
    python run_simulated_experiment.py
"""

import json
import numpy as np
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List
import matplotlib.pyplot as plt


@dataclass
class TaskConfig:
    """Configuration for a simulated task"""
    id: str
    name: str
    nu_0: float  # Initial verification capability
    gamma_0: float  # Initial generation capability
    g_D: float  # Generation-verification gap
    epsilon: float  # Slack term
    noise_std: float = 0.02  # Measurement noise


@dataclass
class SimulatedMetrics:
    """Metrics from simulated iteration"""
    iteration: int
    gamma_t: float
    nu_t: float
    convergence_delta: float


class SimulatedExperiment:
    """Simulates self-training based on theoretical predictions"""

    def __init__(self, task: TaskConfig, iterations: int = 10):
        self.task = task
        self.iterations = iterations
        self.results: List[SimulatedMetrics] = []

        # Compute theoretical ceiling from Theorem 1
        self.gamma_ceiling = task.nu_0 + task.epsilon

        # Compute improvement function f(g_D) from Theorem 3
        # Using f(g) = C/(1 + α·g) with C=0.4, α=2
        self.f_g_D = 0.4 / (1 + 2 * task.g_D)

        print(f"\nTask: {task.name}")
        print(f"Initial: γ_0={task.gamma_0:.3f}, ν_0={task.nu_0:.3f}")
        print(f"Gap g_D={task.g_D:.2f}")
        print(f"Predicted ceiling: γ_∞ ≤ {self.gamma_ceiling:.3f}")
        print(f"Predicted improvement bound: f(g_D) = {self.f_g_D:.3f}")
        print(f"Expected final: γ_∞ ≈ {min(task.gamma_0 + self.f_g_D * (task.nu_0 - task.gamma_0), self.gamma_ceiling):.3f}")

    def simulate_iteration(self, t: int) -> SimulatedMetrics:
        """Simulate one iteration of self-training"""

        if t == 0:
            # Initial capabilities
            gamma_t = self.task.gamma_0
            nu_t = self.task.nu_0
        else:
            # Model convergence to ceiling with exponential approach
            # γ_t = γ_∞ - (γ_∞ - γ_0) * exp(-λt)
            # Using λ = 0.3 (converges in ~8-10 iterations)
            lambda_rate = 0.3
            gamma_inf = min(
                self.task.gamma_0 + self.f_g_D * (self.task.nu_0 - self.task.gamma_0),
                self.gamma_ceiling
            )

            progress = 1 - np.exp(-lambda_rate * t)
            gamma_t = self.task.gamma_0 + progress * (gamma_inf - self.task.gamma_0)

            # Verification improves slightly but is bounded
            nu_inf = min(self.task.nu_0 + 0.05, 1.0)  # Small improvement in verification
            nu_t = self.task.nu_0 + progress * (nu_inf - self.task.nu_0)

        # Add measurement noise
        gamma_t += np.random.normal(0, self.task.noise_std)
        nu_t += np.random.normal(0, self.task.noise_std)

        # Clamp to [0, 1]
        gamma_t = np.clip(gamma_t, 0, 1)
        nu_t = np.clip(nu_t, 0, 1)

        # Compute convergence delta
        if t > 0 and self.results:
            convergence_delta = abs(gamma_t - self.results[-1].gamma_t)
        else:
            convergence_delta = 0.0

        return SimulatedMetrics(
            iteration=t,
            gamma_t=gamma_t,
            nu_t=nu_t,
            convergence_delta=convergence_delta
        )

    def run(self):
        """Run simulated experiment"""
        print(f"\nRunning simulation for {self.iterations} iterations...")

        for t in range(self.iterations):
            metrics = self.simulate_iteration(t)
            self.results.append(metrics)

            if t > 0 and metrics.convergence_delta < 0.02:
                print(f"Converged at iteration {t}!")

    def analyze(self):
        """Analyze results and check theoretical predictions"""
        print(f"\n{'='*60}")
        print("ANALYSIS")
        print(f"{'='*60}")

        gamma_0 = self.results[0].gamma_t
        nu_0 = self.results[0].nu_t
        gamma_inf = self.results[-1].gamma_t

        improvement_abs = gamma_inf - gamma_0
        improvement_rel = improvement_abs / gamma_0 if gamma_0 > 0 else 0

        print(f"\nObserved Results:")
        print(f"  γ_0 = {gamma_0:.3f}")
        print(f"  ν_0 = {nu_0:.3f}")
        print(f"  γ_∞ = {gamma_inf:.3f}")
        print(f"  Improvement: {improvement_abs:.3f} ({improvement_rel:.1%})")

        print(f"\nTheorem 1 Validation (γ_∞ ≤ ν_0 + ε):")
        slack = gamma_inf - nu_0
        print(f"  γ_∞ - ν_0 = {slack:.3f}")
        print(f"  Expected ε ≤ {self.task.epsilon:.3f}")
        if slack <= self.task.epsilon + 0.05:  # Small tolerance for noise
            print(f"  ✓ Theorem 1 holds")
        else:
            print(f"  ✗ Theorem 1 violated")

        print(f"\nTheorem 3 Validation (improvement ≤ f(g_D) · (ν_0 - γ_0)):")
        predicted_improvement = self.f_g_D * (nu_0 - gamma_0)
        print(f"  Observed improvement: {improvement_abs:.3f}")
        print(f"  Predicted bound: {predicted_improvement:.3f}")
        if improvement_abs <= predicted_improvement + 0.05:
            print(f"  ✓ Theorem 3 holds")
        else:
            print(f"  ✗ Theorem 3 violated")

        # Check convergence
        convergence_iter = None
        for i, metrics in enumerate(self.results):
            if i > 0 and metrics.convergence_delta < 0.02:
                convergence_iter = i
                break

        if convergence_iter:
            print(f"\nConvergence: Iteration {convergence_iter}")
        else:
            print(f"\nConvergence: Not reached (Δ={self.results[-1].convergence_delta:.3f})")

    def save_results(self, output_dir: Path):
        """Save results to JSON"""
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"simulated_{self.task.id}.json"

        data = {
            "task": asdict(self.task),
            "iterations": self.iterations,
            "predicted_ceiling": self.gamma_ceiling,
            "f_g_D": self.f_g_D,
            "results": [asdict(m) for m in self.results]
        }

        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"\nResults saved to: {output_file}")

    def plot(self, ax):
        """Plot γ_t and ν_t trajectories"""
        iterations = [m.iteration for m in self.results]
        gammas = [m.gamma_t for m in self.results]
        nus = [m.nu_t for m in self.results]

        ax.plot(iterations, gammas, 'o-', label='γ_t (generation)', color='blue')
        ax.plot(iterations, nus, 's-', label='ν_t (verification)', color='green')

        # Plot theoretical ceiling
        ax.axhline(self.gamma_ceiling, color='red', linestyle='--',
                   label=f'Ceiling (ν_0 + ε = {self.gamma_ceiling:.2f})')

        ax.set_xlabel('Iteration')
        ax.set_ylabel('Capability')
        ax.set_title(f'{self.task.name}\n(gap g_D = {self.task.g_D:.2f})')
        ax.set_ylim(0, 1)
        ax.legend()
        ax.grid(True, alpha=0.3)


def main():
    """Run simulated experiments for all three tasks"""

    # Define tasks matching spec.yaml
    tasks = [
        TaskConfig(
            id="gsm8k",
            name="GSM8K (Moderate Gap)",
            nu_0=0.75,  # Initial verification: 75% accuracy
            gamma_0=0.55,  # Initial generation: 55% accuracy
            g_D=0.20,  # Moderate gap (verification easier)
            epsilon=0.15  # Expected slack
        ),
        TaskConfig(
            id="humaneval",
            name="HumanEval (Small Gap)",
            nu_0=0.80,  # Can verify code easily (run tests)
            gamma_0=0.50,  # Harder to generate correct code
            g_D=0.10,  # Small gap (tests provide strong signal)
            epsilon=0.10
        ),
        TaskConfig(
            id="writingprompts",
            name="WritingPrompts (Large Gap)",
            nu_0=0.60,  # Hard to judge quality
            gamma_0=0.55,  # Slightly harder to generate quality
            g_D=0.50,  # Large gap (judgment unreliable)
            epsilon=0.20
        )
    ]

    # Run experiments
    experiments = []
    for task in tasks:
        exp = SimulatedExperiment(task, iterations=10)
        exp.run()
        exp.analyze()
        experiments.append(exp)

    # Save all results
    output_dir = Path("experiments/self-training-validation/results/simulated")
    for exp in experiments:
        exp.save_results(output_dir)

    # Create combined visualization
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    for i, exp in enumerate(experiments):
        exp.plot(axes[i])

    plt.tight_layout()
    fig_path = output_dir / "convergence_trajectories.png"
    plt.savefig(fig_path, dpi=300, bbox_inches='tight')
    print(f"\nFigure saved to: {fig_path}")

    # Cross-task analysis
    print(f"\n{'='*60}")
    print("CROSS-TASK ANALYSIS (Theorem 3)")
    print(f"{'='*60}")

    print("\nCorrelation between gap size and improvement:")
    gaps = [task.g_D for task in tasks]
    improvements = [
        (exp.results[-1].gamma_t - exp.results[0].gamma_t) / exp.results[0].gamma_t
        for exp in experiments
    ]

    print(f"\n{'Task':<30} {'Gap g_D':<10} {'Improvement':<12}")
    print("-" * 52)
    for task, gap, imp in zip(tasks, gaps, improvements):
        print(f"{task.name:<30} {gap:<10.2f} {imp:<12.1%}")

    # Check monotonicity (smaller gap → larger improvement)
    sorted_by_gap = sorted(zip(gaps, improvements), key=lambda x: x[0])
    is_monotonic = all(
        sorted_by_gap[i][1] >= sorted_by_gap[i+1][1]
        for i in range(len(sorted_by_gap)-1)
    )

    print(f"\nMonotonicity (f(g_D) decreasing): {'✓ Yes' if is_monotonic else '✗ No'}")
    print(f"Prediction: Smaller gap → larger improvement")

    # Correlation analysis
    if len(gaps) > 2:
        from scipy.stats import spearmanr
        correlation, p_value = spearmanr(gaps, improvements)
        print(f"Spearman correlation: r = {-correlation:.3f} (p={p_value:.3f})")
        print(f"  (Negative correlation expected: larger gap → smaller improvement)")

    print(f"\n{'='*60}")
    print("All simulations complete!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    # Set random seed for reproducibility
    np.random.seed(42)

    try:
        from scipy.stats import spearmanr
    except ImportError:
        print("Note: scipy not installed. Skipping correlation analysis.")
        print("Install with: pip install scipy")

    main()
