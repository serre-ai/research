#!/usr/bin/env python3
"""Real-time cost and progress monitor for ReasonGap evaluations.

Shows live costs from provider APIs + checkpoint progress.

Usage:
    python cost_monitor.py              # one-shot status
    python cost_monitor.py --watch 30   # refresh every 30 seconds
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path


CHECKPOINT_DIR = Path(__file__).resolve().parent / "results" / "checkpoints"


# ---------------------------------------------------------------------------
# Provider cost APIs
# ---------------------------------------------------------------------------

def get_openrouter_cost() -> dict | None:
    """Query OpenRouter /auth/key for real-time usage."""
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        return None
    try:
        import urllib.request
        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/auth/key",
            headers={"Authorization": f"Bearer {key}"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())["data"]
        return {
            "provider": "OpenRouter",
            "total": data.get("usage", 0),
            "daily": data.get("usage_daily", 0),
            "limit": data.get("limit"),
            "remaining": data.get("limit_remaining"),
        }
    except Exception as e:
        return {"provider": "OpenRouter", "error": str(e)}


def get_openai_cost() -> dict | None:
    """Check OpenAI — no real-time API, return note."""
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        return None
    return {
        "provider": "OpenAI",
        "note": "Check platform.openai.com/usage (no real-time API)",
    }


def get_anthropic_cost() -> dict | None:
    """Check Anthropic — no real-time API, return note."""
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return None
    return {
        "provider": "Anthropic",
        "note": "Check console.anthropic.com/settings/billing (no real-time API)",
    }


# ---------------------------------------------------------------------------
# Checkpoint progress
# ---------------------------------------------------------------------------

def get_checkpoint_progress() -> list[dict]:
    """Scan checkpoint dir for progress across all models/tasks/conditions."""
    if not CHECKPOINT_DIR.exists():
        return []

    results = []
    for f in sorted(CHECKPOINT_DIR.iterdir()):
        if not f.suffix == ".jsonl":
            continue
        correct = total = 0
        try:
            with open(f) as fh:
                for line in fh:
                    d = json.loads(line)
                    total += 1
                    if d.get("correct"):
                        correct += 1
        except (json.JSONDecodeError, OSError):
            continue

        name = f.stem
        pct = correct / total * 100 if total else 0
        done = total >= 500
        results.append({
            "name": name,
            "correct": correct,
            "total": total,
            "accuracy": pct,
            "done": done,
        })
    return results


def categorize_checkpoints(checkpoints: list[dict]) -> dict[str, list[dict]]:
    """Group checkpoints by provider/model family."""
    groups: dict[str, list[dict]] = {}
    for cp in checkpoints:
        name = cp["name"]
        if name.startswith("claude-haiku"):
            group = "Haiku 4.5"
        elif name.startswith("gpt-4o-mini"):
            group = "GPT-4o-mini"
        elif name.startswith("gpt-4o_"):
            group = "GPT-4o"
        elif "llama-3.1-8b" in name:
            group = "Llama 3.1 8B"
        elif "llama-3.1-70b" in name:
            group = "Llama 3.1 70B"
        elif "ministral-8b" in name:
            group = "Ministral 8B"
        elif "mistral-small" in name:
            group = "Mistral Small 24B"
        elif "qwen-2.5-7b" in name or "qwen_2.5-7b" in name:
            group = "Qwen 2.5 7B"
        elif "qwen-2.5-72b" in name or "qwen_2.5-72b" in name:
            group = "Qwen 2.5 72B"
        else:
            group = "Other"
        groups.setdefault(group, []).append(cp)
    return groups


# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------

def print_status():
    """Print full status report."""
    now = time.strftime("%H:%M:%S")
    print(f"\n{'=' * 70}")
    print(f"  ReasonGap Evaluation Monitor — {now}")
    print(f"{'=' * 70}")

    # Costs
    print(f"\n  COSTS")
    print(f"  {'-' * 66}")
    for fn in [get_openrouter_cost, get_openai_cost, get_anthropic_cost]:
        info = fn()
        if not info:
            continue
        provider = info["provider"]
        if "error" in info:
            print(f"  {provider:15s}  ERROR: {info['error']}")
        elif "note" in info:
            print(f"  {provider:15s}  {info['note']}")
        else:
            total = info.get("total", 0)
            daily = info.get("daily", 0)
            limit = info.get("limit")
            remaining = info.get("remaining")
            line = f"  {provider:15s}  Total: ${total:.4f}  |  Today: ${daily:.4f}"
            if limit is not None:
                line += f"  |  Limit: ${limit:.2f}"
            if remaining is not None:
                line += f"  |  Remaining: ${remaining:.2f}"
            print(line)

    # Progress
    checkpoints = get_checkpoint_progress()
    if not checkpoints:
        print("\n  No checkpoint data found.")
        return

    groups = categorize_checkpoints(checkpoints)

    print(f"\n  PROGRESS BY MODEL")
    print(f"  {'-' * 66}")

    for model, cps in groups.items():
        done_count = sum(1 for c in cps if c["done"])
        total_combos = len(cps)
        total_instances = sum(c["total"] for c in cps)
        total_correct = sum(c["correct"] for c in cps)
        avg_acc = total_correct / total_instances * 100 if total_instances else 0

        status = "DONE" if done_count == total_combos else f"{done_count}/{total_combos}"
        print(f"  {model:22s}  {status:>8s} combos  |  {total_instances:>6d} inst  |  Avg acc: {avg_acc:5.1f}%")

    # Summary
    all_done = sum(1 for c in checkpoints if c["done"])
    all_partial = sum(1 for c in checkpoints if not c["done"])
    all_instances = sum(c["total"] for c in checkpoints)
    print(f"\n  TOTALS: {all_done} complete, {all_partial} in progress, {all_instances:,} instances evaluated")
    print(f"{'=' * 70}\n")


def main():
    parser = argparse.ArgumentParser(description="Monitor ReasonGap evaluation costs and progress.")
    parser.add_argument("--watch", "-w", type=int, default=None,
                        help="Refresh interval in seconds (default: one-shot)")
    args = parser.parse_args()

    # Load env
    env_path = Path(__file__).resolve().parent.parent.parent.parent / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, val = line.partition("=")
                    os.environ.setdefault(key.strip(), val.strip())

    if args.watch:
        try:
            while True:
                print("\033[2J\033[H", end="")  # clear screen
                print_status()
                time.sleep(args.watch)
        except KeyboardInterrupt:
            print("\nStopped.")
    else:
        print_status()


if __name__ == "__main__":
    main()
