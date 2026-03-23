#!/usr/bin/env python3
"""Export evaluation results from PostgreSQL to JSON files.

Reads all eval results from the database and writes them as JSON files
in the format expected by the analysis pipeline (loader.py).

Each file is named: {model_safe}_{task}_{condition}.json
with a structure of {"summary": {...}, "results": [...]}.

Usage:
    python export_results.py --output-dir results/
    python export_results.py --output-dir results/ --dry-run

Environment:
    DATABASE_URL  PostgreSQL connection string (required)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import psycopg2
import psycopg2.extras

from io_utils import atomic_json_write

DEFAULT_DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://deepwork:deepwork@localhost:5432/deepwork",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export eval results from PostgreSQL to JSON")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "results",
        help="Directory to write JSON files (default: ./results/)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Query counts only, don't write files",
    )
    return parser.parse_args()


def safe_model_name(model: str) -> str:
    """Convert model name to filesystem-safe string."""
    return model.replace(":", "_").replace("/", "_")


def export(args: argparse.Namespace) -> None:
    database_url = os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)
    output_dir = args.output_dir.resolve()

    print(f"Connecting to database...")
    try:
        conn = psycopg2.connect(database_url)
    except psycopg2.Error as e:
        print(f"ERROR: Failed to connect: {e}")
        sys.exit(1)

    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Get all distinct (model, task, condition) combinations
        cur.execute("""
            SELECT DISTINCT model, task, condition, COUNT(*) as cnt
            FROM eval_results
            GROUP BY model, task, condition
            ORDER BY model, task, condition
        """)
        combos = cur.fetchall()

        print(f"Found {len(combos)} (model, task, condition) combinations")

        if args.dry_run:
            total = 0
            for row in combos:
                print(f"  {row['model']} / {row['task']} / {row['condition']}: {row['cnt']} instances")
                total += row['cnt']
            print(f"\nTotal: {total} instances")
            return

        output_dir.mkdir(parents=True, exist_ok=True)
        files_written = 0
        total_instances = 0

        for combo in combos:
            model = combo["model"]
            task = combo["task"]
            condition = combo["condition"]
            count = combo["cnt"]

            # Fetch all results for this combination
            cur.execute("""
                SELECT instance_id, model, task, condition, difficulty,
                       correct, extracted_answer, ground_truth, latency_ms,
                       metadata
                FROM eval_results
                WHERE model = %s AND task = %s AND condition = %s
                ORDER BY difficulty, instance_id
            """, (model, task, condition))

            results = []
            for row in cur.fetchall():
                record = {
                    "instance_id": row["instance_id"],
                    "model": row["model"],
                    "task": row["task"],
                    "condition": row["condition"],
                    "difficulty": row["difficulty"],
                    "correct": row["correct"],
                    "extracted_answer": row["extracted_answer"],
                    "ground_truth": row["ground_truth"],
                    "latency_ms": float(row["latency_ms"]) if row["latency_ms"] is not None else 0.0,
                }
                # Merge metadata if present
                if row["metadata"]:
                    meta = row["metadata"] if isinstance(row["metadata"], dict) else json.loads(row["metadata"])
                    record["metadata"] = meta
                results.append(record)

            # Compute summary
            n_correct = sum(1 for r in results if r["correct"])
            accuracy = n_correct / len(results) if results else 0.0

            # Accuracy by difficulty
            diff_groups: dict[int, list[bool]] = {}
            for r in results:
                d = r["difficulty"]
                diff_groups.setdefault(d, []).append(r["correct"])
            accuracy_by_difficulty = {
                str(d): sum(v) / len(v) for d, v in sorted(diff_groups.items())
            }

            summary = {
                "model": model,
                "task": task,
                "condition": condition,
                "accuracy": accuracy,
                "total_instances": len(results),
                "accuracy_by_difficulty": accuracy_by_difficulty,
            }

            data = {"summary": summary, "results": results}

            # Write file
            model_safe = safe_model_name(model)
            filename = f"{model_safe}_{task}_{condition}.json"
            filepath = output_dir / filename

            atomic_json_write(filepath, data)

            files_written += 1
            total_instances += len(results)
            print(f"  {filename} ({len(results)} instances, {accuracy:.1%} accuracy)")

        print(f"\nExported {files_written} files, {total_instances} total instances to {output_dir}")

    except psycopg2.Error as e:
        print(f"ERROR: Database query failed: {e}")
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    export(parse_args())
