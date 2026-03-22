#!/usr/bin/env python3
"""
Self-Training Convergence Validation Experiment

This script implements the self-training loop described in spec.yaml to empirically
validate Theorems 1-3 from the self-improvement-limits paper.

Usage:
    python run_experiment.py --task gsm8k --mode canary
    python run_experiment.py --task humaneval --mode full
    python run_experiment.py --task writingprompts --mode full

Requirements:
    - anthropic (for Claude API)
    - openai (optional, for GPT-4)
    - numpy, pandas (for data handling)
    - datasets (for loading GSM8K, HumanEval)
"""

import argparse
import json
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import time
from dataclasses import dataclass, asdict
import yaml

# Try to import required libraries
try:
    import anthropic
except ImportError:
    print("Warning: anthropic library not found. Install with: pip install anthropic")
    anthropic = None

try:
    import numpy as np
    import pandas as pd
except ImportError:
    print("Warning: numpy/pandas not found. Install with: pip install numpy pandas")
    np = None
    pd = None


@dataclass
class IterationMetrics:
    """Metrics collected at each iteration of self-training"""
    iteration: int
    gamma_t: float  # Generation accuracy
    nu_t: float  # Verification accuracy
    num_generated: int
    num_filtered: int
    convergence_delta: Optional[float]
    timestamp: str


@dataclass
class ExperimentConfig:
    """Configuration for a self-training experiment"""
    task_id: str
    task_name: str
    mode: str  # 'canary' or 'full'
    test_size: int
    train_size: int
    iterations: int
    temperature: float
    verification_temperature: float
    filter_threshold: float
    model_name: str


class SelfTrainingExperiment:
    """Runs a self-training convergence validation experiment"""

    def __init__(self, config: ExperimentConfig, api_key: Optional[str] = None):
        self.config = config
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")

        if anthropic and self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        else:
            self.client = None
            print("Warning: Running in simulation mode (no API client)")

        self.results: List[IterationMetrics] = []
        self.test_set: List[Dict] = []
        self.train_set: List[Dict] = []
        self.few_shot_examples: List[Dict] = []

    def load_data(self):
        """Load test and train data for the specified task"""
        print(f"Loading data for task: {self.config.task_id}")

        if self.config.task_id == "gsm8k":
            self._load_gsm8k()
        elif self.config.task_id == "humaneval":
            self._load_humaneval()
        elif self.config.task_id == "writingprompts":
            self._load_writingprompts()
        else:
            raise ValueError(f"Unknown task: {self.config.task_id}")

    def _load_gsm8k(self):
        """Load GSM8K dataset"""
        # In a real implementation, we would load from the datasets library:
        # from datasets import load_dataset
        # dataset = load_dataset("gsm8k", "main")
        # For now, create placeholder data
        print("Note: Using placeholder GSM8K data. Full implementation requires datasets library.")

        # Example GSM8K problem format:
        # {"question": "Janet's ducks lay 16 eggs per day...", "answer": "18"}
        self.test_set = [
            {
                "id": f"gsm8k_test_{i}",
                "question": f"Math problem {i} (placeholder)",
                "answer": str(i % 100)
            }
            for i in range(self.config.test_size)
        ]

        self.train_set = [
            {
                "id": f"gsm8k_train_{i}",
                "question": f"Math problem {i} (placeholder)",
                "answer": str(i % 100)
            }
            for i in range(self.config.train_size)
        ]

    def _load_humaneval(self):
        """Load HumanEval dataset"""
        # In a real implementation: load_dataset("openai_humaneval")
        print("Note: Using placeholder HumanEval data.")

        self.test_set = [
            {
                "id": f"humaneval_test_{i}",
                "prompt": f"def function_{i}(x):\n    \"\"\"Docstring\"\"\"",
                "canonical_solution": f"    return x * {i}",
                "test": f"assert function_{i}(2) == {i*2}"
            }
            for i in range(self.config.test_size)
        ]

        self.train_set = [
            {
                "id": f"humaneval_train_{i}",
                "prompt": f"def function_{i}(x):\n    \"\"\"Docstring\"\"\"",
                "canonical_solution": f"    return x * {i}",
                "test": f"assert function_{i}(2) == {i*2}"
            }
            for i in range(self.config.train_size)
        ]

    def _load_writingprompts(self):
        """Load WritingPrompts dataset"""
        # In a real implementation: load_dataset("writing_prompts")
        print("Note: Using placeholder WritingPrompts data.")

        self.test_set = [
            {
                "id": f"wp_test_{i}",
                "prompt": f"Writing prompt {i} (placeholder)",
                "reference": f"Reference story {i}"
            }
            for i in range(self.config.test_size)
        ]

        self.train_set = [
            {
                "id": f"wp_train_{i}",
                "prompt": f"Writing prompt {i} (placeholder)",
                "reference": f"Reference story {i}"
            }
            for i in range(self.config.train_size)
        ]

    def generate_solution(self, problem: Dict) -> str:
        """Generate a solution for a given problem"""
        if self.client is None:
            # Simulation mode: return dummy solution
            return f"simulated_solution_{hash(problem['id']) % 100}"

        # Construct prompt based on task type
        if self.config.task_id == "gsm8k":
            prompt = self._construct_gsm8k_prompt(problem)
        elif self.config.task_id == "humaneval":
            prompt = self._construct_humaneval_prompt(problem)
        elif self.config.task_id == "writingprompts":
            prompt = self._construct_writingprompts_prompt(problem)
        else:
            raise ValueError(f"Unknown task: {self.config.task_id}")

        # Call API
        try:
            response = self.client.messages.create(
                model=self.config.model_name,
                max_tokens=1024,
                temperature=self.config.temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            print(f"Error generating solution: {e}")
            return ""

    def verify_solution(self, problem: Dict, solution: str) -> float:
        """Verify a solution and return a score [0, 1]"""
        if self.client is None:
            # Simulation mode: return random score
            import random
            return random.random()

        # Construct verification prompt
        prompt = f"""Problem: {problem.get('question', problem.get('prompt', ''))}
Proposed solution: {solution}

Is this solution correct? Rate from 0 (completely wrong) to 1 (completely correct).

Score:"""

        try:
            response = self.client.messages.create(
                model=self.config.model_name,
                max_tokens=100,
                temperature=self.config.verification_temperature,
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse score from response
            text = response.content[0].text
            # Extract first number between 0 and 1
            import re
            match = re.search(r'0\.\d+|[01]\.?\d*', text)
            if match:
                score = float(match.group())
                return max(0.0, min(1.0, score))
            return 0.5  # Default if parsing fails

        except Exception as e:
            print(f"Error verifying solution: {e}")
            return 0.5

    def evaluate_generation(self) -> float:
        """Measure generation accuracy γ_t on test set"""
        print(f"Evaluating generation on {len(self.test_set)} test examples...")

        correct = 0
        for problem in self.test_set:
            solution = self.generate_solution(problem)
            # Check correctness (task-specific)
            if self._is_correct(problem, solution):
                correct += 1

        return correct / len(self.test_set) if self.test_set else 0.0

    def evaluate_verification(self) -> float:
        """Measure verification accuracy ν_t on test set"""
        print(f"Evaluating verification on {len(self.test_set)} test examples...")

        correct = 0
        for problem in self.test_set:
            # Create correct and incorrect solutions
            correct_solution = problem.get('answer', problem.get('canonical_solution', ''))
            incorrect_solution = "wrong answer"

            score_correct = self.verify_solution(problem, correct_solution)
            score_incorrect = self.verify_solution(problem, incorrect_solution)

            # Verification is correct if it ranks correct > incorrect
            if score_correct > score_incorrect:
                correct += 1

        return correct / len(self.test_set) if self.test_set else 0.0

    def run_iteration(self, iteration: int) -> IterationMetrics:
        """Run one iteration of self-training"""
        print(f"\n=== Iteration {iteration} ===")

        # Step 1: Measure γ_t and ν_t
        gamma_t = self.evaluate_generation()
        nu_t = self.evaluate_verification()

        print(f"γ_{iteration} = {gamma_t:.3f}")
        print(f"ν_{iteration} = {nu_t:.3f}")

        # Step 2: Generate solutions for training set
        print(f"Generating solutions for {len(self.train_set)} training examples...")
        generated_solutions = []
        for problem in self.train_set:
            solution = self.generate_solution(problem)
            score = self.verify_solution(problem, solution)
            generated_solutions.append({
                "problem": problem,
                "solution": solution,
                "score": score
            })

        # Step 3: Filter by threshold
        filtered_solutions = [
            sol for sol in generated_solutions
            if sol["score"] >= self.config.filter_threshold
        ]
        print(f"Filtered: {len(filtered_solutions)}/{len(generated_solutions)} examples")

        # Step 4: Update few-shot examples for next iteration
        # Keep top-k examples sorted by score
        self.few_shot_examples = sorted(
            filtered_solutions,
            key=lambda x: x["score"],
            reverse=True
        )[:5]  # Keep top 5 as few-shot examples

        # Compute convergence delta
        convergence_delta = None
        if iteration > 0 and self.results:
            prev_gamma = self.results[-1].gamma_t
            convergence_delta = abs(gamma_t - prev_gamma)
            print(f"Convergence Δ = {convergence_delta:.4f}")

        # Record metrics
        metrics = IterationMetrics(
            iteration=iteration,
            gamma_t=gamma_t,
            nu_t=nu_t,
            num_generated=len(generated_solutions),
            num_filtered=len(filtered_solutions),
            convergence_delta=convergence_delta,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
        )

        return metrics

    def run(self):
        """Run the complete self-training experiment"""
        print(f"\n{'='*60}")
        print(f"Starting experiment: {self.config.task_name}")
        print(f"Mode: {self.config.mode}")
        print(f"Iterations: {self.config.iterations}")
        print(f"{'='*60}\n")

        # Load data
        self.load_data()

        # Run iterations
        for i in range(self.config.iterations):
            metrics = self.run_iteration(i)
            self.results.append(metrics)

            # Check for convergence
            if metrics.convergence_delta is not None and metrics.convergence_delta < 0.02:
                print(f"\nConverged at iteration {i}!")

        # Save results
        self.save_results()

        # Print summary
        self.print_summary()

    def save_results(self):
        """Save experiment results to JSON"""
        output_dir = Path(f"experiments/self-training-validation/results")
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / f"{self.config.task_id}_{self.config.mode}_{int(time.time())}.json"

        data = {
            "config": asdict(self.config),
            "results": [asdict(m) for m in self.results]
        }

        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"\nResults saved to: {output_file}")

    def print_summary(self):
        """Print summary of experimental results"""
        print(f"\n{'='*60}")
        print("EXPERIMENT SUMMARY")
        print(f"{'='*60}")

        if not self.results:
            print("No results to summarize.")
            return

        gamma_0 = self.results[0].gamma_t
        nu_0 = self.results[0].nu_t
        gamma_inf = self.results[-1].gamma_t
        nu_inf = self.results[-1].nu_t

        improvement = (gamma_inf - gamma_0) / gamma_0 if gamma_0 > 0 else 0

        print(f"Task: {self.config.task_name}")
        print(f"Iterations: {len(self.results)}")
        print(f"\nInitial capabilities:")
        print(f"  γ_0 = {gamma_0:.3f}")
        print(f"  ν_0 = {nu_0:.3f}")
        print(f"\nFinal capabilities:")
        print(f"  γ_∞ = {gamma_inf:.3f}")
        print(f"  ν_∞ = {nu_inf:.3f}")
        print(f"\nImprovement:")
        print(f"  Absolute: {gamma_inf - gamma_0:.3f}")
        print(f"  Relative: {improvement:.1%}")
        print(f"\nTheoretical prediction (Theorem 1):")
        print(f"  γ_∞ ≤ ν_0 + ε")
        print(f"  {gamma_inf:.3f} ≤ {nu_0:.3f} + ε")

        if gamma_inf <= nu_0 + 0.2:  # Assuming ε ≈ 0.2
            print(f"  ✓ Prediction holds (ε ≈ {gamma_inf - nu_0:.3f})")
        else:
            print(f"  ✗ Prediction violated (slack = {gamma_inf - nu_0:.3f})")

        print(f"{'='*60}\n")

    def _is_correct(self, problem: Dict, solution: str) -> bool:
        """Check if solution is correct (task-specific)"""
        # Simplified correctness checking for demonstration
        # Real implementation would use proper evaluation
        if self.config.task_id == "gsm8k":
            # Check if solution contains the correct answer
            answer = problem.get('answer', '')
            return answer in solution
        elif self.config.task_id == "humaneval":
            # Would execute tests here
            return "return" in solution
        elif self.config.task_id == "writingprompts":
            # Would use quality metrics here
            return len(solution) > 100
        return False

    def _construct_gsm8k_prompt(self, problem: Dict) -> str:
        """Construct prompt for GSM8K problem"""
        prompt = ""

        # Add few-shot examples if available
        if self.few_shot_examples:
            prompt += "Here are some example solutions:\n\n"
            for ex in self.few_shot_examples[:3]:
                prompt += f"Problem: {ex['problem'].get('question', '')}\n"
                prompt += f"Solution: {ex['solution']}\n\n"

        prompt += f"Now solve this problem:\n{problem['question']}\n\nSolution:"
        return prompt

    def _construct_humaneval_prompt(self, problem: Dict) -> str:
        """Construct prompt for HumanEval problem"""
        prompt = problem['prompt']

        if self.few_shot_examples:
            prompt = "Example solutions:\n\n"
            for ex in self.few_shot_examples[:2]:
                prompt += f"{ex['problem']['prompt']}\n{ex['solution']}\n\n"
            prompt += f"Now complete:\n{problem['prompt']}"

        return prompt

    def _construct_writingprompts_prompt(self, problem: Dict) -> str:
        """Construct prompt for WritingPrompts"""
        prompt = f"Write a story for this prompt:\n{problem['prompt']}\n\nStory:"
        return prompt


def main():
    parser = argparse.ArgumentParser(description="Run self-training convergence experiment")
    parser.add_argument("--task", required=True, choices=["gsm8k", "humaneval", "writingprompts"],
                       help="Task to run experiment on")
    parser.add_argument("--mode", default="canary", choices=["canary", "full"],
                       help="Experiment mode: canary (small) or full")
    parser.add_argument("--model", default="claude-3-5-sonnet-20241022",
                       help="Model to use")
    parser.add_argument("--api-key", help="API key (or set ANTHROPIC_API_KEY env var)")

    args = parser.parse_args()

    # Load experiment spec
    spec_path = Path("experiments/self-training-validation/spec.yaml")
    with open(spec_path) as f:
        spec = yaml.safe_load(f)

    # Find task config
    task_config = next((t for t in spec['design']['tasks'] if t['id'] == args.task), None)
    if not task_config:
        print(f"Error: Task {args.task} not found in spec")
        return

    # Create experiment config
    if args.mode == "canary":
        test_size = spec['canary'].get('instances_per_difficulty', 5) * 3  # 3 difficulties
        train_size = 50
        iterations = 3
    else:
        test_size = task_config['test_size']
        train_size = task_config['train_size']
        iterations = spec['design']['iterations']

    config = ExperimentConfig(
        task_id=args.task,
        task_name=task_config['name'],
        mode=args.mode,
        test_size=test_size,
        train_size=train_size,
        iterations=iterations,
        temperature=spec['design']['temperature'],
        verification_temperature=spec['design']['verification_temperature'],
        filter_threshold=spec['design']['filter_threshold'],
        model_name=args.model
    )

    # Run experiment
    experiment = SelfTrainingExperiment(config, api_key=args.api_key)
    experiment.run()


if __name__ == "__main__":
    main()
