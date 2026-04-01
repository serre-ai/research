#!/usr/bin/env node
/**
 * Backfill embeddings for lit_papers that have abstracts but no embedding vector.
 *
 * Usage:
 *   npm run build --workspace=orchestrator
 *   npm run backfill-embeddings --workspace=orchestrator
 *
 * Requires DATABASE_URL and VOYAGE_API_KEY (or OPENAI_API_KEY) in .env or environment.
 */

import pg from "pg";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { createEmbedFn } from "./embeddings.js";

// ---------- env loading (same pattern as migrate.ts) ----------

function loadEnv(): void {
  try {
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
    // .env not found, continue with existing env
  }
}

// ---------- main ----------

async function main(): Promise<void> {
  loadEnv();

  const databaseUrl = process.env.DATABASE_URL;
  if (!databaseUrl) {
    console.error("[backfill] DATABASE_URL not set");
    process.exit(1);
  }

  const embedFn = createEmbedFn();
  if (!embedFn) {
    console.error("[backfill] No embedding API key found (set VOYAGE_API_KEY or OPENAI_API_KEY)");
    process.exit(1);
  }

  const { Pool } = pg;
  const pool = new Pool({ connectionString: databaseUrl, max: 2 });

  try {
    // Query papers with abstracts but no embeddings
    const { rows } = await pool.query<{ id: string; title: string; abstract: string }>(
      `SELECT id, title, abstract FROM lit_papers
       WHERE abstract IS NOT NULL AND embedding IS NULL
       ORDER BY discovered_at DESC`,
    );

    if (rows.length === 0) {
      console.log("[backfill] All papers already have embeddings. Nothing to do.");
      return;
    }

    console.log(`[backfill] Found ${rows.length} papers missing embeddings.\n`);

    let succeeded = 0;
    let failed = 0;

    for (let i = 0; i < rows.length; i++) {
      const paper = rows[i];
      const label = paper.title.length > 70 ? paper.title.slice(0, 67) + "..." : paper.title;
      process.stdout.write(`Embedding ${i + 1}/${rows.length}: ${label}...`);

      try {
        // Same embedding text format as LiteratureMonitor.embedPapers()
        const text = `${paper.title}. ${paper.abstract}`;
        const embedding = await embedFn(text);
        const vecStr = `[${embedding.join(",")}]`;

        await pool.query("UPDATE lit_papers SET embedding = $1 WHERE id = $2", [vecStr, paper.id]);
        console.log(" done");
        succeeded++;
      } catch (err) {
        const msg = err instanceof Error ? err.message : String(err);
        console.log(` FAILED: ${msg}`);
        failed++;
      }

      // Rate limit: 200ms between calls (matches batchEmbed pattern)
      if (i < rows.length - 1) {
        await new Promise((r) => setTimeout(r, 200));
      }
    }

    console.log(`\n[backfill] Complete. ${succeeded} succeeded, ${failed} failed.`);
  } finally {
    await pool.end();
  }
}

main().catch((err) => {
  console.error("[backfill] Fatal error:", err);
  process.exit(1);
});
