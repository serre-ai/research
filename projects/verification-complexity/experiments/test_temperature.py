#!/usr/bin/env python3
"""Test temperature effect on self-consistency sample diversity.

Quick test: B4 d4 + B7 d4 with T=1.0, N=9, 20 instances each.
Compare agreement rates against T=0.7 baseline.
"""

import json
import logging
import os
import sys
import time
from collections import Counter
from pathlib import Path

# Add reasoning-gaps benchmarks to path
BENCHMARKS_DIR = Path(__file__).resolve().parents[2] / "reasoning-gaps" / "benchmarks"
sys.path.insert(0, str(BENCHMARKS_DIR))
sys.path.insert(0, str(BENCHMARKS_DIR / "clients"))
sys.path.insert(0, str(BENCHMARKS_DIR / "tasks"))

from anthropic_client import AnthropicClient
from answer_extraction import extract_answer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("temp_test")


def create_haiku_client(temperature: float):
    """Create Haiku client with specified temperature."""
    import anthropic

    client = AnthropicClient("claude-haiku-4-5-20251001")

    def query_with_temp(prompt, system_prompt="", max_tokens=512):
        messages = [{"role": "user", "content": prompt}]
        kwargs = {
            "model": "claude-haiku-4-5-20251001",
            "max_tokens": max_tokens,
            "messages": messages,
            "temperature": temperature,
        }
        if system_prompt:
            kwargs["system"] = system_prompt

        start = time.perf_counter()
        response = client._client.messages.create(**kwargs)
        latency_ms = (time.perf_counter() - start) * 1000

        text_parts = []
        for block in response.content:
            if hasattr(block, "text"):
                text_parts.append(block.text)
        return "\n".join(text_parts), latency_ms

    client.query = query_with_temp
    return client


def generate_b4_instance(difficulty: int, seed: int):
    """Generate a B4 state machine instance."""
    import b4_state_machine
    instances = b4_state_machine.generate(1, difficulty, seed)
    return instances[0]


def generate_b7_instance(difficulty: int, seed: int):
    """Generate a B7 3-SAT instance."""
    import b7_3sat
    instances = b7_3sat.generate(1, difficulty, seed)
    return instances[0]


def evaluate_instance(instance, client, condition="short_cot"):
    """Evaluate one instance."""
    # Build prompt
    question = instance["prompt"]
    if condition == "short_cot":
        prompt = "Think step by step, then provide your final answer on the last line.\n\n" + question
    else:
        prompt = question

    # Query model
    response, latency_ms = client.query(prompt, max_tokens=1024)

    # Extract answer
    extracted = extract_answer(response, instance["task"])

    # Check correctness
    ground_truth = str(instance["answer"])
    correct = extracted.strip().lower() == ground_truth.strip().lower()

    return {
        "response": response,
        "extracted": extracted,
        "ground_truth": ground_truth,
        "correct": correct,
        "latency_ms": latency_ms,
    }


def run_test(task_name: str, difficulty: int, num_instances: int, num_samples: int, temperature: float):
    """Run self-consistency test on one task."""
    logger.info(f"\n{'='*60}")
    logger.info(f"Task: {task_name}, Difficulty: {difficulty}, T={temperature}")
    logger.info(f"Instances: {num_instances}, Samples per instance: {num_samples}")
    logger.info(f"{'='*60}")

    client = create_haiku_client(temperature)

    # Generate function
    if task_name == "B4":
        generate = generate_b4_instance
    elif task_name == "B7":
        generate = generate_b7_instance
    else:
        raise ValueError(f"Unknown task: {task_name}")

    results = []

    for i in range(num_instances):
        instance = generate(difficulty, seed=1000 + i)

        # Collect N samples
        answers = []
        correct_flags = []

        for _ in range(num_samples):
            result = evaluate_instance(instance, client)
            answers.append(result["extracted"])
            correct_flags.append(result["correct"])

        # Compute majority vote
        valid_answers = [a for a in answers if a != ""]
        extraction_failures = len(answers) - len(valid_answers)

        if valid_answers:
            vote_counts = Counter(valid_answers)
            majority_answer = vote_counts.most_common(1)[0][0]
            majority_correct = majority_answer.strip().lower() == instance["answer"].strip().lower()
            agreement = vote_counts[majority_answer] / len(valid_answers)
        else:
            majority_answer = ""
            majority_correct = False
            agreement = 0.0

        results.append({
            "instance_id": instance["id"],
            "task": task_name,
            "difficulty": difficulty,
            "temperature": temperature,
            "num_samples": num_samples,
            "answers": answers,
            "correct_flags": correct_flags,
            "majority_answer": majority_answer,
            "majority_correct": majority_correct,
            "agreement": agreement,
            "ground_truth": str(instance["answer"]),
            "extraction_failures": extraction_failures,
            "single_correct": correct_flags[0],
        })

        # Log progress
        status = "✓" if majority_correct else "✗"
        logger.info(
            f"  [{i+1}/{num_instances}] {status} "
            f"agree={agreement:.1%} "
            f"single={'✓' if correct_flags[0] else '✗'}"
        )

    # Compute summary statistics
    avg_agreement = sum(r["agreement"] for r in results) / len(results)
    majority_accuracy = sum(r["majority_correct"] for r in results) / len(results)
    single_accuracy = sum(r["single_correct"] for r in results) / len(results)

    logger.info(f"\n{task_name} d{difficulty} T={temperature} Summary:")
    logger.info(f"  Average agreement: {avg_agreement:.1%}")
    logger.info(f"  Single-sample accuracy: {single_accuracy:.1%}")
    logger.info(f"  Majority-vote accuracy: {majority_accuracy:.1%}")

    return results, {
        "avg_agreement": avg_agreement,
        "majority_accuracy": majority_accuracy,
        "single_accuracy": single_accuracy,
    }


def main():
    """Run T=1.0 test on B4 d4 and B7 d4."""
    OUTPUT_DIR = Path(__file__).parent / "results"
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Configuration
    TEMPERATURE = 1.0
    NUM_SAMPLES = 9
    NUM_INSTANCES = 20
    DIFFICULTY = 4

    logger.info("="*60)
    logger.info("Temperature Diversity Test: T=1.0")
    logger.info(f"Total estimated cost: ~${2 * NUM_INSTANCES * NUM_SAMPLES * 0.002:.2f}")
    logger.info("="*60)

    all_results = {}

    # Test B4
    b4_results, b4_summary = run_test("B4", DIFFICULTY, NUM_INSTANCES, NUM_SAMPLES, TEMPERATURE)
    all_results["B4"] = {"results": b4_results, "summary": b4_summary}

    # Test B7
    b7_results, b7_summary = run_test("B7", DIFFICULTY, NUM_INSTANCES, NUM_SAMPLES, TEMPERATURE)
    all_results["B7"] = {"results": b7_results, "summary": b7_summary}

    # Save results
    output_file = OUTPUT_DIR / f"temp_test_t{TEMPERATURE}_n{NUM_SAMPLES}_d{DIFFICULTY}.json"
    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=2)

    logger.info(f"\nResults saved to: {output_file}")

    # Final summary
    logger.info("\n" + "="*60)
    logger.info("FINAL SUMMARY")
    logger.info("="*60)
    logger.info(f"B4 d{DIFFICULTY}: avg agreement = {b4_summary['avg_agreement']:.1%}")
    logger.info(f"B7 d{DIFFICULTY}: avg agreement = {b7_summary['avg_agreement']:.1%}")

    if b4_summary["avg_agreement"] < 0.85 or b7_summary["avg_agreement"] < 0.85:
        logger.info("\n✓ DIVERSITY GATE PASSED: T=1.0 provides sufficient diversity (<85% agreement)")
        logger.info("  → Proceed with full $92 run at T=1.0")
    else:
        logger.info("\n✗ DIVERSITY GATE FAILED: Agreement still >95%")
        logger.info("  → Need alternative approach (different models as samples, not temperature)")


if __name__ == "__main__":
    main()
