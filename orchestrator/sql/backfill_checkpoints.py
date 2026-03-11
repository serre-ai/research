#!/usr/bin/env python3
"""
Backfill eval_results and eval_runs from JSONL checkpoint files.

Usage:
    python backfill_checkpoints.py [--dir <checkpoints_dir>] [--db <dsn>] [--dry-run]

Reads all *.jsonl files from the checkpoints directory, inserts into
eval_results (ON CONFLICT DO NOTHING for idempotency), computes
eval_runs aggregates, and refreshes the checkpoints materialized view.
"""

import argparse
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

import psycopg2
from psycopg2.extras import execute_values


DEFAULT_CHECKPOINT_DIR = os.path.join(
    os.path.dirname(__file__),
    "..",
    "..",
    "projects",
    "reasoning-gaps",
    "benchmarks",
    "results",
    "checkpoints",
)

DEFAULT_DSN = os.environ.get(
    "DATABASE_URL",
    "postgresql://deepwork:deepwork@localhost:5432/deepwork",
)


def parse_args():
    parser = argparse.ArgumentParser(description="Backfill eval results from JSONL checkpoints")
    parser.add_argument(
        "--dir",
        default=DEFAULT_CHECKPOINT_DIR,
        help="Path to checkpoints directory containing *.jsonl files",
    )
    parser.add_argument(
        "--db",
        default=DEFAULT_DSN,
        help="PostgreSQL connection string (default: $DATABASE_URL or local)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse files and report stats without writing to database",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=500,
        help="Number of rows per INSERT batch (default: 500)",
    )
    return parser.parse_args()


def read_checkpoint_files(checkpoint_dir: str) -> list[dict]:
    """Read all JSONL files and return list of result dicts."""
    results = []
    checkpoint_path = Path(checkpoint_dir)

    if not checkpoint_path.exists():
        print(f"Error: checkpoint directory not found: {checkpoint_dir}", file=sys.stderr)
        sys.exit(1)

    jsonl_files = sorted(checkpoint_path.glob("*.jsonl"))
    if not jsonl_files:
        print(f"Warning: no .jsonl files found in {checkpoint_dir}", file=sys.stderr)
        return results

    print(f"Found {len(jsonl_files)} checkpoint files")

    for filepath in jsonl_files:
        line_count = 0
        with open(filepath, "r") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    results.append(record)
                    line_count += 1
                except json.JSONDecodeError as e:
                    print(f"  Warning: {filepath.name}:{line_num} — invalid JSON: {e}", file=sys.stderr)

        print(f"  {filepath.name}: {line_count} records")

    return results


def insert_eval_results(conn, results: list[dict], batch_size: int) -> int:
    """Insert eval results with ON CONFLICT DO NOTHING. Returns inserted count."""
    if not results:
        return 0

    rows = []
    for r in results:
        metadata = r.get("metadata", {})
        # Include prompt_sent in metadata if present
        if "prompt_sent" in r:
            metadata["prompt_sent"] = r["prompt_sent"]

        rows.append((
            r["instance_id"],
            r["model"],
            r["task"],
            r["condition"],
            r.get("difficulty", 0),
            r["correct"],
            r.get("extracted_answer"),
            r["ground_truth"],
            r.get("latency_ms"),
            r.get("model_response"),
            json.dumps(metadata),
        ))

    inserted = 0
    cur = conn.cursor()

    for i in range(0, len(rows), batch_size):
        batch = rows[i : i + batch_size]
        execute_values(
            cur,
            """
            INSERT INTO eval_results (
                instance_id, model, task, condition, difficulty,
                correct, extracted_answer, ground_truth, latency_ms,
                response, metadata
            )
            VALUES %s
            ON CONFLICT (instance_id, model, condition) DO NOTHING
            """,
            batch,
            template="(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)",
        )
        inserted += cur.rowcount

    conn.commit()
    cur.close()
    return inserted


def compute_and_insert_runs(conn, results: list[dict]) -> int:
    """Compute run-level aggregates and upsert into eval_runs. Returns upserted count."""
    if not results:
        return 0

    # Group by (model, task, condition) — each group is one "run"
    runs = defaultdict(list)
    for r in results:
        key = (r["model"], r["task"], r["condition"])
        runs[key].append(r)

    rows = []
    for (model, task, condition), instances in runs.items():
        run_id = f"{model}_{task}_{condition}"
        correct_count = sum(1 for i in instances if i["correct"])
        total = len(instances)
        accuracy = correct_count / total if total > 0 else 0.0
        avg_latency = (
            sum(i.get("latency_ms", 0) for i in instances) / total if total > 0 else 0.0
        )

        rows.append((
            run_id,
            model,
            task,
            condition,
            "completed",
            total,
            round(accuracy, 4),
            json.dumps({"avg_latency_ms": round(avg_latency, 1), "correct_count": correct_count}),
        ))

    cur = conn.cursor()
    execute_values(
        cur,
        """
        INSERT INTO eval_runs (
            run_id, model, task, condition, status,
            instance_count, accuracy, metadata
        )
        VALUES %s
        ON CONFLICT (run_id) DO UPDATE SET
            status = EXCLUDED.status,
            instance_count = EXCLUDED.instance_count,
            accuracy = EXCLUDED.accuracy,
            metadata = EXCLUDED.metadata,
            completed_at = NOW()
        """,
        rows,
        template="(%s, %s, %s, %s, %s, %s, %s, %s::jsonb)",
    )
    upserted = cur.rowcount
    conn.commit()
    cur.close()
    return upserted


def refresh_materialized_view(conn):
    """Refresh the checkpoints materialized view."""
    cur = conn.cursor()
    cur.execute("REFRESH MATERIALIZED VIEW CONCURRENTLY checkpoints")
    conn.commit()
    cur.close()


def print_summary(results: list[dict]):
    """Print a dry-run summary of what would be inserted."""
    runs = defaultdict(list)
    for r in results:
        key = (r["model"], r["task"], r["condition"])
        runs[key].append(r)

    models = sorted(set(r["model"] for r in results))
    tasks = sorted(set(r["task"] for r in results))
    conditions = sorted(set(r["condition"] for r in results))

    print(f"\nSummary:")
    print(f"  Total instances: {len(results)}")
    print(f"  Unique runs: {len(runs)}")
    print(f"  Models ({len(models)}): {', '.join(models)}")
    print(f"  Tasks ({len(tasks)}): {', '.join(tasks)}")
    print(f"  Conditions ({len(conditions)}): {', '.join(conditions)}")

    print(f"\nAccuracy by run:")
    for (model, task, condition), instances in sorted(runs.items()):
        total = len(instances)
        correct = sum(1 for i in instances if i["correct"])
        acc = correct / total if total > 0 else 0
        print(f"  {model} / {task} / {condition}: {correct}/{total} ({acc:.1%})")


def main():
    args = parse_args()

    print(f"Checkpoint dir: {os.path.abspath(args.dir)}")
    print(f"Database: {args.db.split('@')[-1] if '@' in args.db else args.db}")
    print(f"Dry run: {args.dry_run}")
    print()

    # Read all checkpoint files
    results = read_checkpoint_files(args.dir)
    if not results:
        print("No results to process.")
        return

    print_summary(results)

    if args.dry_run:
        print("\nDry run — no database changes made.")
        return

    # Connect to database
    print(f"\nConnecting to database...")
    try:
        conn = psycopg2.connect(args.db)
    except psycopg2.Error as e:
        print(f"Error connecting to database: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        # Insert eval results
        print("Inserting eval_results...")
        inserted = insert_eval_results(conn, results, args.batch_size)
        print(f"  Inserted {inserted} new rows ({len(results) - inserted} duplicates skipped)")

        # Compute and insert run aggregates
        print("Computing eval_runs aggregates...")
        upserted = compute_and_insert_runs(conn, results)
        print(f"  Upserted {upserted} run records")

        # Refresh materialized view
        print("Refreshing checkpoints materialized view...")
        try:
            refresh_materialized_view(conn)
            print("  Done")
        except psycopg2.Error as e:
            # CONCURRENTLY requires a unique index and the view to be populated first
            # Fall back to non-concurrent refresh
            conn.rollback()
            cur = conn.cursor()
            cur.execute("REFRESH MATERIALIZED VIEW checkpoints")
            conn.commit()
            cur.close()
            print("  Done (non-concurrent refresh)")

        print("\nBackfill complete.")

    except Exception as e:
        conn.rollback()
        print(f"Error during backfill: {e}", file=sys.stderr)
        sys.exit(1)

    finally:
        conn.close()


if __name__ == "__main__":
    main()
