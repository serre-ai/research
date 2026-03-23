/**
 * Database migration runner.
 *
 * Discovers NNN_*.sql files in orchestrator/sql/, tracks applied versions
 * in a schema_migrations table, and applies pending migrations in order.
 *
 * Each migration runs in a transaction (existing BEGIN/COMMIT stripped,
 * runner wraps its own). An advisory lock prevents concurrent runs.
 *
 * Usage:
 *   Programmatic:  await runMigrations(pool)
 *   CLI:           node dist/migrate.js
 *   Baseline:      node dist/migrate.js --baseline 12
 */

import { readdir, readFile } from "node:fs/promises";
import { join, dirname } from "node:path";
import { createHash } from "node:crypto";
import { fileURLToPath } from "node:url";
import pg from "pg";

const LOCK_ID = 8675309; // advisory lock ID for migration exclusivity

interface MigrationFile {
  version: number;
  filename: string;
  path: string;
}

const CREATE_TRACKING_TABLE = `
CREATE TABLE IF NOT EXISTS schema_migrations (
  version    INTEGER PRIMARY KEY,
  filename   TEXT NOT NULL,
  applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  checksum   TEXT
);
`;

function stripTransactionWrapper(sql: string): string {
  return sql
    .replace(/^\s*BEGIN\s*;\s*$/gim, "")
    .replace(/^\s*COMMIT\s*;\s*$/gim, "");
}

function checksum(content: string): string {
  return createHash("sha256").update(content).digest("hex").slice(0, 16);
}

async function discoverMigrations(): Promise<MigrationFile[]> {
  const thisDir = dirname(fileURLToPath(import.meta.url));
  const sqlDir = join(thisDir, "..", "sql");
  const entries = await readdir(sqlDir);
  const migrations: MigrationFile[] = [];

  for (const entry of entries) {
    const match = entry.match(/^(\d{3})_.*\.sql$/);
    if (match) {
      migrations.push({
        version: parseInt(match[1], 10),
        filename: entry,
        path: join(sqlDir, entry),
      });
    }
  }

  return migrations.sort((a, b) => a.version - b.version);
}

export async function runMigrations(
  pool: pg.Pool,
  options?: { baseline?: number },
): Promise<void> {
  const client = await pool.connect();
  try {
    // Advisory lock prevents concurrent migration runs
    await client.query(`SELECT pg_advisory_lock(${LOCK_ID})`);

    // Ensure tracking table exists
    await client.query(CREATE_TRACKING_TABLE);

    const files = await discoverMigrations();

    // Baseline mode: seed versions 1..N as already applied
    if (options?.baseline) {
      for (const file of files) {
        if (file.version <= options.baseline) {
          const sql = await readFile(file.path, "utf-8");
          await client.query(
            `INSERT INTO schema_migrations (version, filename, checksum)
             VALUES ($1, $2, $3) ON CONFLICT DO NOTHING`,
            [file.version, file.filename, checksum(sql)],
          );
        }
      }
      console.log(`[migrate] Baseline set: versions 1..${options.baseline} marked as applied`);
      return;
    }

    // Get already-applied versions
    const { rows } = await client.query<{ version: number }>(
      "SELECT version FROM schema_migrations ORDER BY version",
    );
    const applied = new Set(rows.map((r) => r.version));

    // Find pending migrations
    const pending = files.filter((f) => !applied.has(f.version));

    if (pending.length === 0) {
      console.log("[migrate] Database is up to date");
      return;
    }

    console.log(`[migrate] ${pending.length} pending migration(s)`);

    for (const migration of pending) {
      console.log(`[migrate] Applying ${migration.filename}...`);
      const sql = await readFile(migration.path, "utf-8");
      const cleanedSql = stripTransactionWrapper(sql);

      try {
        await client.query("BEGIN");
        await client.query(cleanedSql);
        await client.query(
          "INSERT INTO schema_migrations (version, filename, checksum) VALUES ($1, $2, $3)",
          [migration.version, migration.filename, checksum(sql)],
        );
        await client.query("COMMIT");
        console.log(`[migrate] Applied ${migration.filename}`);
      } catch (err) {
        await client.query("ROLLBACK");
        const msg = err instanceof Error ? err.message : String(err);
        console.error(`[migrate] FAILED ${migration.filename}: ${msg}`);
        throw err;
      }
    }

    console.log("[migrate] All migrations applied successfully");
  } finally {
    await client.query(`SELECT pg_advisory_unlock(${LOCK_ID})`).catch(() => {});
    client.release();
  }
}

// ── CLI entry point ──────────────────────────────────────────

const isMainModule =
  import.meta.url === `file://${process.argv[1]}` ||
  process.argv[1]?.endsWith("migrate.js");

if (isMainModule) {
  // Load .env (same pattern as index.ts)
  try {
    const { readFileSync } = await import("node:fs");
    const envPath = join(process.cwd(), ".env");
    const content = readFileSync(envPath, "utf-8");
    for (const line of content.split("\n")) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith("#")) continue;
      const eqIdx = trimmed.indexOf("=");
      if (eqIdx === -1) continue;
      const key = trimmed.slice(0, eqIdx).trim();
      const value = trimmed.slice(eqIdx + 1).trim();
      if (!process.env[key]) {
        process.env[key] = value;
      }
    }
  } catch {
    // .env not found
  }

  const databaseUrl = process.env.DATABASE_URL;
  if (!databaseUrl) {
    console.error("[migrate] DATABASE_URL not set");
    process.exit(1);
  }

  // Parse --baseline N
  let baseline: number | undefined;
  const baselineIdx = process.argv.indexOf("--baseline");
  if (baselineIdx !== -1) {
    baseline = parseInt(process.argv[baselineIdx + 1], 10);
    if (isNaN(baseline) || baseline < 1) {
      console.error("[migrate] Usage: node migrate.js --baseline <N>");
      process.exit(1);
    }
  }

  const { Pool } = pg;
  const pool = new Pool({ connectionString: databaseUrl, max: 2 });
  try {
    await runMigrations(pool, baseline ? { baseline } : undefined);
  } catch {
    process.exit(1);
  } finally {
    await pool.end();
  }
}
