#!/usr/bin/env python3
"""Ingest eval result JSON files into PostgreSQL.

Reads all *.json files from the results/ directory (excluding progress.json
and the analysis/ subdirectory), inserts instance-level data into eval_results
and run-level summaries into eval_runs, then refreshes the checkpoints
materialized view.

Usage:
    python ingest_results.py [--results-dir PATH] [--dry-run]

Environment:
    DATABASE_URL  PostgreSQL connection string
                  Default: postgresql://deepwork:3db364c531740cb97cb02577dc2d40df@localhost:5432/deepwork
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import psycopg2
import psycopg2.extras

DEFAULT_DATABASE_URL = (
    "postgresql://deepwork:3db364c531740cb97cb02577dc2d40df@localhost:5432/deepwork"
)

RESULTS_DIR = Path(__file__).resolve().parent / "results"

# Files to skip in the results directory
SKIP_FILES = {"progress.json"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest eval results into PostgreSQL")
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=RESULTS_DIR,
        help="Path to the results directory (default: ./results/)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and validate files without writing to the database",
    )
    return parser.parse_args()


def load_result_file(path: Path) -> dict | None:
    """Load and validate a single result JSON file.

    Returns the parsed dict or None if the file should be skipped.
    """
    try:
        with open(path) as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"  WARN: Skipping {path.name} — invalid JSON: {e}")
        return None
    except OSError as e:
        print(f"  WARN: Skipping {path.name} — read error: {e}")
        return None

    if not isinstance(data, dict):
        print(f"  WARN: Skipping {path.name} — top-level value is not an object")
        return None

    summary = data.get("summary")
    if not summary or not isinstance(summary, dict):
        print(f"  WARN: Skipping {path.name} — missing or invalid 'summary'")
        return None

    # Require essential summary fields
    for field in ("task", "model", "condition"):
        if not summary.get(field):
            print(
                f"  WARN: Skipping {path.name} — summary missing or empty '{field}'"
            )
            return None

    results = data.get("results")
    if results is None:
        print(f"  WARN: Skipping {path.name} — missing 'results' array")
        return None

    if not isinstance(results, list):
        print(f"  WARN: Skipping {path.name} — 'results' is not an array")
        return None

    return data


def build_run_row(summary: dict, instance_count: int) -> dict:
    """Build an eval_runs row dict from a summary block."""
    model = summary["model"]
    task = summary["task"]
    condition = summary["condition"]
    run_id = f"{model}_{task}_{condition}"

    accuracy = summary.get("accuracy")
    total_expected = summary.get("total_instances")
    mean_latency = summary.get("mean_latency_ms")
    accuracy_by_difficulty = summary.get("accuracy_by_difficulty")

    metadata = {}
    if mean_latency is not None:
        metadata["avg_latency_ms"] = mean_latency
    if accuracy_by_difficulty is not None:
        metadata["accuracy_by_difficulty"] = accuracy_by_difficulty

    return {
        "run_id": run_id,
        "model": model,
        "task": task,
        "condition": condition,
        "status": "completed",
        "accuracy": accuracy,
        "instance_count": instance_count,
        "total_expected": total_expected,
        "metadata": json.dumps(metadata),
    }


def build_result_rows(results: list[dict]) -> list[dict]:
    """Build eval_results row dicts from the results array.

    Skips individual instances that are missing required fields.
    """
    rows = []
    for item in results:
        if not isinstance(item, dict):
            continue

        instance_id = item.get("instance_id")
        model = item.get("model")
        task = item.get("task")
        condition = item.get("condition")
        difficulty = item.get("difficulty")
        correct = item.get("correct")
        ground_truth = item.get("ground_truth")

        # All required fields must be present
        if instance_id is None or model is None or task is None or condition is None:
            continue
        if difficulty is None or correct is None or ground_truth is None:
            continue
        if not model:  # empty string model
            continue

        # Build the row
        metadata = item.get("metadata") or {}
        # Store prompt_sent in metadata rather than losing it
        prompt_sent = item.get("prompt_sent")
        if prompt_sent:
            metadata["prompt_sent"] = prompt_sent

        rows.append(
            {
                "instance_id": str(instance_id),
                "model": str(model),
                "task": str(task),
                "condition": str(condition),
                "difficulty": int(difficulty),
                "correct": bool(correct),
                "extracted_answer": item.get("extracted_answer"),
                "ground_truth": str(ground_truth),
                "latency_ms": item.get("latency_ms"),
                "response": item.get("model_response"),
                "metadata": json.dumps(metadata),
            }
        )

    return rows


def ingest(args: argparse.Namespace) -> None:
    results_dir = args.results_dir.resolve()
    if not results_dir.is_dir():
        print(f"ERROR: Results directory not found: {results_dir}")
        sys.exit(1)

    # Collect JSON files (skip known non-result files, skip subdirectories)
    json_files = sorted(
        p
        for p in results_dir.iterdir()
        if p.is_file() and p.suffix == ".json" and p.name not in SKIP_FILES
    )

    if not json_files:
        print("No result JSON files found.")
        sys.exit(0)

    print(f"Found {len(json_files)} JSON files in {results_dir}")

    # Parse all files first
    all_result_rows: list[dict] = []
    all_run_rows: list[dict] = []
    skipped = 0
    empty = 0

    for path in json_files:
        data = load_result_file(path)
        if data is None:
            skipped += 1
            continue

        summary = data["summary"]
        results = data["results"]

        if len(results) == 0:
            empty += 1
            # Still create the run row (with 0 instances) so we track it
            run_row = build_run_row(summary, instance_count=0)
            all_run_rows.append(run_row)
            continue

        result_rows = build_result_rows(results)
        run_row = build_run_row(summary, instance_count=len(result_rows))

        all_result_rows.extend(result_rows)
        all_run_rows.append(run_row)

    print(
        f"Parsed: {len(all_run_rows)} runs, {len(all_result_rows)} instances "
        f"({skipped} files skipped, {empty} files with 0 instances)"
    )

    if args.dry_run:
        print("Dry run — no database writes.")
        # Show a summary of what would be inserted
        models = sorted(set(r["model"] for r in all_run_rows if r["model"]))
        tasks = sorted(set(r["task"] for r in all_run_rows))
        conditions = sorted(set(r["condition"] for r in all_run_rows))
        print(f"  Models ({len(models)}): {', '.join(models)}")
        print(f"  Tasks ({len(tasks)}): {', '.join(tasks)}")
        print(f"  Conditions ({len(conditions)}): {', '.join(conditions)}")
        return

    # Connect to PostgreSQL
    database_url = os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)
    print(f"Connecting to database...")

    try:
        conn = psycopg2.connect(database_url)
    except psycopg2.Error as e:
        print(f"ERROR: Failed to connect to database: {e}")
        sys.exit(1)

    try:
        cur = conn.cursor()

        # Insert eval_results in batches using execute_values for performance
        if all_result_rows:
            print(f"Inserting {len(all_result_rows)} eval_results...")
            t0 = time.monotonic()

            insert_results_sql = """
                INSERT INTO eval_results
                    (instance_id, model, task, condition, difficulty, correct,
                     extracted_answer, ground_truth, latency_ms, response, metadata)
                VALUES %s
                ON CONFLICT (instance_id, model, condition) DO NOTHING
            """

            # Build tuples for execute_values
            result_tuples = [
                (
                    r["instance_id"],
                    r["model"],
                    r["task"],
                    r["condition"],
                    r["difficulty"],
                    r["correct"],
                    r["extracted_answer"],
                    r["ground_truth"],
                    r["latency_ms"],
                    r["response"],
                    r["metadata"],
                )
                for r in all_result_rows
            ]

            psycopg2.extras.execute_values(
                cur,
                insert_results_sql,
                result_tuples,
                page_size=1000,
            )

            inserted_results = cur.rowcount
            elapsed = time.monotonic() - t0
            print(
                f"  eval_results: {inserted_results} new rows inserted "
                f"({len(all_result_rows) - inserted_results} duplicates skipped) "
                f"in {elapsed:.1f}s"
            )

        # Insert/update eval_runs
        if all_run_rows:
            print(f"Upserting {len(all_run_rows)} eval_runs...")
            t0 = time.monotonic()

            upsert_runs_sql = """
                INSERT INTO eval_runs
                    (run_id, model, task, condition, status,
                     completed_at, accuracy, instance_count, total_expected, metadata)
                VALUES (%s, %s, %s, %s, %s, NOW(), %s, %s, %s, %s)
                ON CONFLICT (run_id) DO UPDATE SET
                    status = EXCLUDED.status,
                    completed_at = EXCLUDED.completed_at,
                    accuracy = EXCLUDED.accuracy,
                    instance_count = EXCLUDED.instance_count,
                    total_expected = EXCLUDED.total_expected,
                    metadata = EXCLUDED.metadata
            """

            for r in all_run_rows:
                cur.execute(
                    upsert_runs_sql,
                    (
                        r["run_id"],
                        r["model"],
                        r["task"],
                        r["condition"],
                        r["status"],
                        r["accuracy"],
                        r["instance_count"],
                        r["total_expected"],
                        r["metadata"],
                    ),
                )

            elapsed = time.monotonic() - t0
            print(f"  eval_runs: {len(all_run_rows)} rows upserted in {elapsed:.1f}s")

        # Refresh materialized view
        print("Refreshing checkpoints materialized view...")
        t0 = time.monotonic()
        cur.execute("SELECT refresh_checkpoints()")
        elapsed = time.monotonic() - t0
        print(f"  Refreshed in {elapsed:.1f}s")

        conn.commit()
        print("Done. All changes committed.")

    except psycopg2.Error as e:
        conn.rollback()
        print(f"ERROR: Database operation failed: {e}")
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    ingest(parse_args())
