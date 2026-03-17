/**
 * Backfill the knowledge graph from existing reasoning-gaps project data.
 *
 * Sources:
 * 1. Eval results from PostgreSQL (checkpoints materialized view)
 * 2. Decisions from status.yaml
 * 3. Key findings from analysis/summary.md
 * 4. Key references from status.yaml
 *
 * Usage: npx tsx orchestrator/scripts/backfill-knowledge.ts
 *
 * Requires: DATABASE_URL environment variable (or PGHOST/PGDATABASE/etc.)
 *           VOYAGE_API_KEY or OPENAI_API_KEY for embeddings
 */

import pg from "pg";
import { readFile } from "node:fs/promises";
import { join } from "node:path";
import { KnowledgeGraph, type ClaimRow } from "../src/knowledge-graph.js";
import { createEmbedFn } from "../src/embeddings.js";

const PROJECT = "reasoning-gaps";
const ROOT_DIR = join(import.meta.dirname, "../..");

interface BackfillStats {
  evalResults: number;
  decisions: number;
  findings: number;
  citations: number;
  relations: number;
  skippedDuplicates: number;
}

async function main(): Promise<void> {
  const pool = new pg.Pool({
    connectionString: process.env.DATABASE_URL,
    max: 5,
  });

  const embedFn = createEmbedFn();
  if (!embedFn) {
    console.warn("⚠ No embedding API key found (VOYAGE_API_KEY or OPENAI_API_KEY).");
    console.warn("  Claims will be inserted without embeddings. Semantic search will use FTS fallback.");
  }

  const kg = new KnowledgeGraph(pool, embedFn);
  const stats: BackfillStats = {
    evalResults: 0,
    decisions: 0,
    findings: 0,
    citations: 0,
    relations: 0,
    skippedDuplicates: 0,
  };

  console.log("=== Knowledge Graph Backfill ===");
  console.log(`Project: ${PROJECT}`);
  console.log();

  // 1. Eval results from PostgreSQL
  console.log("--- Source 1: Eval Results ---");
  await backfillEvalResults(pool, kg, stats);

  // 2. Decisions from status.yaml
  console.log("\n--- Source 2: Decisions (status.yaml) ---");
  await backfillDecisions(kg, stats);

  // 3. Key findings from analysis summary
  console.log("\n--- Source 3: Analysis Findings ---");
  await backfillAnalysisFindings(kg, stats);

  // 4. Citations from status.yaml key_references
  console.log("\n--- Source 4: Key References ---");
  await backfillCitations(kg, stats);

  // Create initial snapshot
  console.log("\n--- Creating snapshot ---");
  await kg.createSnapshot(PROJECT);

  // Print summary
  console.log("\n=== Backfill Complete ===");
  console.log(`  Eval results:       ${stats.evalResults}`);
  console.log(`  Decisions:          ${stats.decisions}`);
  console.log(`  Findings:           ${stats.findings}`);
  console.log(`  Citations:          ${stats.citations}`);
  console.log(`  Relations created:  ${stats.relations}`);
  console.log(`  Skipped duplicates: ${stats.skippedDuplicates}`);
  console.log(`  Total claims:       ${stats.evalResults + stats.decisions + stats.findings + stats.citations}`);

  const kgStats = await kg.getStats();
  console.log(`\n  KG totals: ${kgStats.total_claims} claims, ${kgStats.total_relations} relations, ${kgStats.embedded_claims} with embeddings`);

  await pool.end();
}

// ============================================================
// Source 1: Eval Results
// ============================================================

async function backfillEvalResults(pool: pg.Pool, kg: KnowledgeGraph, stats: BackfillStats): Promise<void> {
  // Aggregate eval results by model/task/condition
  const { rows } = await pool.query(`
    SELECT
      model, task, condition,
      COUNT(*) AS n,
      ROUND(AVG(correct::int)::numeric, 4) AS accuracy
    FROM eval_results
    GROUP BY model, task, condition
    ORDER BY model, task, condition
  `);

  console.log(`  Found ${rows.length} model/task/condition combinations`);

  for (const row of rows) {
    const statement = `${shortModel(row.model)} achieves ${row.accuracy} accuracy on ${row.task} under ${row.condition} condition (n=${row.n})`;

    try {
      await kg.addClaim({
        project: PROJECT,
        claimType: "result",
        statement,
        confidence: 0.95, // empirical results are high-confidence
        source: `eval_results/${row.model}/${row.task}/${row.condition}`,
        sourceType: "eval",
        metadata: {
          model: row.model,
          task: row.task,
          condition: row.condition,
          accuracy: parseFloat(row.accuracy),
          n: parseInt(row.n),
        },
      });
      stats.evalResults++;
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      if (msg.includes("duplicate") || msg.includes("unique")) {
        stats.skippedDuplicates++;
      } else {
        console.error(`  ERROR inserting eval result: ${msg}`);
        stats.skippedDuplicates++; // count but log the error
      }
    }

    // Rate limit embedding API calls
    if (stats.evalResults % 50 === 0 && stats.evalResults > 0) {
      console.log(`  ... ${stats.evalResults} eval results processed`);
      await sleep(500);
    }
  }

  console.log(`  Inserted ${stats.evalResults} eval result claims`);
}

// ============================================================
// Source 2: Decisions from status.yaml
// ============================================================

async function backfillDecisions(kg: KnowledgeGraph, stats: BackfillStats): Promise<void> {
  const statusPath = join(ROOT_DIR, "projects", PROJECT, "status.yaml");
  const statusContent = await readFile(statusPath, "utf-8");

  // Parse decisions_made from YAML (simple regex — avoid adding yaml dep)
  const decisions = parseDecisions(statusContent);
  console.log(`  Found ${decisions.length} decisions`);

  for (const dec of decisions) {
    try {
      await kg.addClaim({
        project: PROJECT,
        claimType: "decision",
        statement: dec.decision,
        confidence: 0.9,
        source: "status.yaml",
        sourceType: "status_yaml",
        metadata: { date: dec.date, rationale: dec.rationale },
      });
      stats.decisions++;
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      if (!msg.includes("duplicate") && !msg.includes("unique") && !msg.includes("Near-duplicate")) {
        console.error(`  ERROR: ${msg}`);
      }
      stats.skippedDuplicates++;
    }
    await sleep(200);
  }

  console.log(`  Inserted ${stats.decisions} decision claims`);
}

interface Decision {
  date: string;
  decision: string;
  rationale: string;
}

function parseDecisions(yaml: string): Decision[] {
  const decisions: Decision[] = [];
  const decisionSection = yaml.split("decisions_made:")[1];
  if (!decisionSection) return decisions;

  // Split on "  - date:" to get individual entries
  const entries = decisionSection.split(/\n  - date:/);
  for (const entry of entries) {
    if (!entry.trim()) continue;
    const dateMatch = entry.match(/^\s*["']?(\d{4}-\d{2}-\d{2})["']?/);
    const decisionMatch = entry.match(/decision:\s*["'](.+?)["']\s*$/m);
    const rationaleMatch = entry.match(/rationale:\s*["'](.+?)["']\s*$/m);
    if (dateMatch && decisionMatch) {
      decisions.push({
        date: dateMatch[1],
        decision: decisionMatch[1],
        rationale: rationaleMatch?.[1] ?? "",
      });
    }
  }
  return decisions;
}

// ============================================================
// Source 3: Analysis Summary Findings
// ============================================================

async function backfillAnalysisFindings(kg: KnowledgeGraph, stats: BackfillStats): Promise<void> {
  const summaryPath = join(ROOT_DIR, "projects", PROJECT, "benchmarks", "results", "analysis", "summary.md");
  let summary: string;
  try {
    summary = await readFile(summaryPath, "utf-8");
  } catch {
    console.log("  Analysis summary not found, skipping");
    return;
  }

  // Extract structured findings
  const findings: Array<{ statement: string; confidence: number; source: string }> = [];

  // Overall accuracy by condition
  const overallMatches = summary.matchAll(/\*\*(\w+)\*\*:\s*([\d.]+)/g);
  for (const m of overallMatches) {
    if (["budget_cot", "direct", "short_cot"].includes(m[1])) {
      findings.push({
        statement: `Overall accuracy under ${m[1]} condition is ${m[2]} across all models and tasks`,
        confidence: 0.95,
        source: "analysis/summary.md",
      });
    }
  }

  // Per-type findings
  const typeBlocks = summary.matchAll(/### (Type \d+: \w+)\n\n([\s\S]*?)(?=###|\n## |$)/g);
  for (const block of typeBlocks) {
    const typeName = block[1];
    const content = block[2];

    // Extract CoT lift
    const cotLiftMatch = content.match(/CoT lift \(short_cot\):\s*([+-][\d.]+)/);
    if (cotLiftMatch) {
      findings.push({
        statement: `${typeName}: short_cot CoT lift is ${cotLiftMatch[1]}`,
        confidence: 0.95,
        source: "analysis/summary.md",
      });
    }
  }

  // Key predictions check
  const predCheck = summary.match(/Types 2,3.*?CoT lift = ([+-][\d.]+)/);
  const predCheck2 = summary.match(/Types 5,6.*?CoT lift = ([+-][\d.]+)/);
  if (predCheck && predCheck2) {
    findings.push({
      statement: `Framework predictions confirmed: Types 2,3 (depth/serial) CoT lift = ${predCheck[1]} vs Types 5,6 (intractability/architectural) CoT lift = ${predCheck2[1]}`,
      confidence: 0.95,
      source: "analysis/summary.md",
    });
  }

  // Dataset overview as an observation
  const instanceMatch = summary.match(/\*\*Instances\*\*:\s*([\d,]+)/);
  const modelMatch = summary.match(/\*\*Models\*\*:\s*(\d+)/);
  if (instanceMatch && modelMatch) {
    findings.push({
      statement: `ReasonGap evaluation dataset contains ${instanceMatch[1]} instances across ${modelMatch[1]} models, 9 tasks, 3 conditions`,
      confidence: 1.0,
      source: "analysis/summary.md",
    });
  }

  console.log(`  Extracted ${findings.length} findings`);

  // Track the prediction confirmation claim for relations later
  let predictionClaimId: string | undefined;

  for (const f of findings) {
    try {
      const claim = await kg.addClaim({
        project: PROJECT,
        claimType: "finding",
        statement: f.statement,
        confidence: f.confidence,
        source: f.source,
        sourceType: "eval",
      });
      stats.findings++;

      if (f.statement.includes("Framework predictions confirmed")) {
        predictionClaimId = claim.id;
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      if (!msg.includes("duplicate") && !msg.includes("unique") && !msg.includes("Near-duplicate")) {
        console.error(`  ERROR: ${msg}`);
      }
      stats.skippedDuplicates++;
    }
    await sleep(200);
  }

  // Create supports relations: type-specific findings support the prediction confirmation
  if (predictionClaimId) {
    const allClaims = await kg.getProjectClaims(PROJECT, "finding");
    for (const claim of allClaims) {
      if (claim.id !== predictionClaimId && claim.statement.includes("CoT lift")) {
        try {
          await kg.addRelation({
            sourceId: claim.id,
            targetId: predictionClaimId,
            relation: "supports",
            strength: 0.9,
            evidence: "Per-type CoT lift data supports overall prediction confirmation",
          });
          stats.relations++;
        } catch {
          // Relation already exists
        }
      }
    }
  }

  console.log(`  Inserted ${stats.findings} finding claims, ${stats.relations} relations`);
}

// ============================================================
// Source 4: Key References
// ============================================================

async function backfillCitations(kg: KnowledgeGraph, stats: BackfillStats): Promise<void> {
  const statusPath = join(ROOT_DIR, "projects", PROJECT, "status.yaml");
  const statusContent = await readFile(statusPath, "utf-8");

  // Parse key_references from YAML
  const refSection = statusContent.split("key_references:")[1];
  if (!refSection) {
    console.log("  No key_references found, skipping");
    return;
  }

  const refs: string[] = [];
  const lines = refSection.split("\n");
  for (const line of lines) {
    const match = line.match(/^\s*-\s*["'](.+?)["']\s*$/);
    if (match) {
      refs.push(match[1]);
    } else if (line.match(/^\w/) && refs.length > 0) {
      // Hit next top-level key
      break;
    }
  }

  console.log(`  Found ${refs.length} key references`);

  for (const ref of refs) {
    try {
      await kg.addClaim({
        project: PROJECT,
        claimType: "citation",
        statement: ref,
        confidence: 1.0,
        source: "status.yaml",
        sourceType: "status_yaml",
        metadata: { type: "key_reference" },
      });
      stats.citations++;
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      if (!msg.includes("duplicate") && !msg.includes("unique") && !msg.includes("Near-duplicate")) {
        console.error(`  ERROR: ${msg}`);
      }
      stats.skippedDuplicates++;
    }
    await sleep(200);
  }

  console.log(`  Inserted ${stats.citations} citation claims`);
}

// ============================================================
// Helpers
// ============================================================

function shortModel(model: string): string {
  // Shorten model names for readable claim statements
  const map: Record<string, string> = {
    "claude-haiku-4-5-20251001": "Claude Haiku 4.5",
    "claude-sonnet-4-20250514": "Claude Sonnet 4.6",
    "gpt-4o": "GPT-4o",
    "gpt-4o-mini": "GPT-4o Mini",
    "o3": "o3",
    "meta-llama/llama-3.1-8b-instruct": "Llama 3.1 8B",
    "meta-llama/llama-3.1-70b-instruct": "Llama 3.1 70B",
    "mistralai/ministral-8b-2512": "Ministral 8B",
    "mistralai/mistral-small-24b-instruct-2501": "Mistral Small 24B",
    "qwen/qwen-2.5-7b-instruct": "Qwen 2.5 7B",
    "qwen/qwen-2.5-72b-instruct": "Qwen 2.5 72B",
  };
  return map[model] ?? model;
}

function sleep(ms: number): Promise<void> {
  return new Promise((r) => setTimeout(r, ms));
}

main().catch((err) => {
  console.error("Backfill failed:", err);
  process.exit(1);
});
