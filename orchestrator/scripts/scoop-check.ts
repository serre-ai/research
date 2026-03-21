/**
 * Scoop check: scan arXiv and Semantic Scholar for potentially competing
 * papers related to the reasoning-gaps project (NeurIPS 2026).
 *
 * Usage: npx tsx orchestrator/scripts/scoop-check.ts
 */

import { ArxivClient, type ArxivPaper } from "../src/arxiv.js";
import { SemanticScholarClient, type S2Paper, type S2Citation } from "../src/semantic-scholar.js";

const CUTOFF_DATE = "2026-03-13";

// ============================================================
// Helpers
// ============================================================

function isAfterCutoff(dateStr: string | null | undefined): boolean {
  if (!dateStr) return false;
  return dateStr.slice(0, 10) >= CUTOFF_DATE;
}

function formatArxivPaper(p: ArxivPaper): string {
  return [
    `  [arXiv:${p.id}] ${p.title}`,
    `    Authors:    ${p.authors.slice(0, 5).join(", ")}${p.authors.length > 5 ? " et al." : ""}`,
    `    Published:  ${p.published.slice(0, 10)}`,
    `    Categories: ${p.categories.join(", ")}`,
    `    PDF:        ${p.pdfUrl}`,
    `    Abstract:   ${p.abstract.slice(0, 300)}${p.abstract.length > 300 ? "..." : ""}`,
  ].join("\n");
}

function formatS2Paper(p: S2Paper): string {
  return [
    `  [S2:${p.paperId?.slice(0, 12)}] ${p.title}`,
    `    Authors:    ${p.authors?.slice(0, 5).map((a) => a.name).join(", ")}${(p.authors?.length ?? 0) > 5 ? " et al." : ""}`,
    `    Year:       ${p.year ?? "?"}  Published: ${p.publicationDate ?? "?"}`,
    `    Venue:      ${p.venue || "—"}`,
    `    Citations:  ${p.citationCount ?? 0}`,
    `    URL:        ${p.url}`,
    `    Abstract:   ${(p.abstract ?? "").slice(0, 300)}${(p.abstract ?? "").length > 300 ? "..." : ""}`,
  ].join("\n");
}

async function sleep(ms: number): Promise<void> {
  return new Promise((r) => setTimeout(r, ms));
}

// ============================================================
// Main
// ============================================================

async function main() {
  const arxiv = new ArxivClient();
  const s2 = new SemanticScholarClient();

  console.log("=".repeat(72));
  console.log("SCOOP CHECK — reasoning-gaps project");
  console.log(`Cutoff date: ${CUTOFF_DATE}`);
  console.log(`Run at: ${new Date().toISOString()}`);
  console.log("=".repeat(72));

  // ----------------------------------------------------------
  // 1. arXiv searches
  // ----------------------------------------------------------

  const arxivQueries = [
    { label: 'all:"reasoning gaps" AND cat:cs.CL', query: 'all:"reasoning gaps" AND cat:cs.CL' },
    { label: 'all:"chain of thought" AND all:"complexity" AND cat:cs.CL', query: 'all:"chain of thought" AND all:"complexity" AND cat:cs.CL' },
    { label: 'all:"transformer expressiveness" AND all:"circuit complexity"', query: 'all:"transformer expressiveness" AND all:"circuit complexity"' },
    { label: 'ti:"reasoning" AND ti:"benchmark" AND cat:cs.CL', query: 'ti:"reasoning" AND ti:"benchmark" AND cat:cs.CL' },
  ];

  const allArxivRecent: ArxivPaper[] = [];

  for (const { label, query } of arxivQueries) {
    console.log(`\n${"─".repeat(60)}`);
    console.log(`arXiv search: ${label}`);
    console.log("─".repeat(60));
    try {
      const results = await arxiv.search(query, {
        maxResults: 30,
        sortBy: "submittedDate",
        sortOrder: "descending",
      });
      console.log(`  Total results: ${results.length}`);

      const recent = results.filter((p) => isAfterCutoff(p.published));
      console.log(`  After cutoff (${CUTOFF_DATE}): ${recent.length}`);

      if (recent.length > 0) {
        for (const p of recent) {
          console.log(formatArxivPaper(p));
          console.log();
        }
        allArxivRecent.push(...recent);
      } else {
        // Show the most recent 3 anyway for context
        console.log("  (No results after cutoff. Most recent 3:)");
        for (const p of results.slice(0, 3)) {
          console.log(`    [${p.published.slice(0, 10)}] ${p.title}`);
        }
      }
    } catch (err) {
      console.error(`  ERROR: ${err}`);
    }
  }

  // ----------------------------------------------------------
  // 2. Semantic Scholar searches
  // ----------------------------------------------------------

  const s2Queries = [
    { label: '"reasoning gaps" chain of thought', query: "reasoning gaps chain of thought", year: "2026-" },
    { label: '"CoT" "complexity class" transformer', query: "CoT complexity class transformer", year: "2026-" },
    { label: '"chain of thought" benchmark evaluation', query: "chain of thought benchmark evaluation", year: "2025-2026" },
  ];

  const allS2Recent: S2Paper[] = [];

  for (const { label, query, year } of s2Queries) {
    console.log(`\n${"─".repeat(60)}`);
    console.log(`S2 search: ${label}  (year: ${year})`);
    console.log("─".repeat(60));
    try {
      const results = await s2.search(query, {
        limit: 20,
        year,
        fieldsOfStudy: "Computer Science",
      });
      console.log(`  Total results: ${results.length}`);

      const recent = results.filter((p) => isAfterCutoff(p.publicationDate));
      console.log(`  After cutoff (${CUTOFF_DATE}): ${recent.length}`);

      if (recent.length > 0) {
        for (const p of recent) {
          console.log(formatS2Paper(p));
          console.log();
        }
        allS2Recent.push(...recent);
      } else {
        // Show the most recent 3 for context
        console.log("  (No results after cutoff. Most recent 3:)");
        for (const p of results.slice(0, 3)) {
          console.log(`    [${p.publicationDate ?? p.year ?? "?"}] ${p.title}`);
        }
      }
    } catch (err) {
      console.error(`  ERROR: ${err}`);
    }
  }

  // ----------------------------------------------------------
  // 3. Citation tracking of key papers
  // ----------------------------------------------------------

  const keyPapers = [
    { id: "ArXiv:2201.11903", label: "Wei et al. 2022 — CoT prompting" },
    { id: "ArXiv:2405.04776", label: "Feng et al. 2024 — CoT limitations" },
    { id: "ArXiv:2310.07923", label: "Merrill & Sabharwal 2023 — Expressiveness bounds" },
  ];

  const allCitingRecent: S2Paper[] = [];

  for (const { id, label } of keyPapers) {
    console.log(`\n${"─".repeat(60)}`);
    console.log(`Citation check: ${label} (${id})`);
    console.log("─".repeat(60));
    try {
      const citations = await s2.getCitations(id, 100);
      console.log(`  Total recent citations returned: ${citations.length}`);

      // Filter to papers after cutoff with relevant topics
      const recent = citations.filter((c) => {
        const p = c.citingPaper;
        if (!p || !p.title) return false;
        if (!isAfterCutoff(p.publicationDate)) return false;
        return true;
      });

      console.log(`  After cutoff (${CUTOFF_DATE}): ${recent.length}`);

      // Further filter for relevance keywords
      const relevant = recent.filter((c) => {
        const p = c.citingPaper;
        const text = `${p.title} ${p.abstract ?? ""}`.toLowerCase();
        return (
          text.includes("reasoning") ||
          text.includes("chain of thought") ||
          text.includes("cot") ||
          text.includes("complexity") ||
          text.includes("transformer") ||
          text.includes("expressiveness") ||
          text.includes("benchmark") ||
          text.includes("gap")
        );
      });

      console.log(`  Relevant (keyword-filtered): ${relevant.length}`);

      if (relevant.length > 0) {
        for (const c of relevant.slice(0, 10)) {
          console.log(formatS2Paper(c.citingPaper));
          console.log();
        }
        allCitingRecent.push(...relevant.map((c) => c.citingPaper));
      } else if (recent.length > 0) {
        console.log("  (Recent citations exist but none match relevance filter.)");
        for (const c of recent.slice(0, 3)) {
          console.log(`    [${c.citingPaper.publicationDate ?? "?"}] ${c.citingPaper.title}`);
        }
      } else {
        console.log("  (No citations after cutoff date.)");
      }
    } catch (err) {
      console.error(`  ERROR: ${err}`);
    }
  }

  // ----------------------------------------------------------
  // 4. Summary / Threat Assessment
  // ----------------------------------------------------------

  console.log("\n" + "=".repeat(72));
  console.log("SUMMARY — SCOOP THREAT ASSESSMENT");
  console.log("=".repeat(72));

  // Deduplicate across sources
  const seenTitles = new Set<string>();
  const allRecent: Array<{ title: string; date: string; source: string; abstract: string }> = [];

  for (const p of allArxivRecent) {
    const key = p.title.toLowerCase().trim();
    if (!seenTitles.has(key)) {
      seenTitles.add(key);
      allRecent.push({ title: p.title, date: p.published.slice(0, 10), source: `arXiv:${p.id}`, abstract: p.abstract });
    }
  }
  for (const p of [...allS2Recent, ...allCitingRecent]) {
    const key = p.title.toLowerCase().trim();
    if (!seenTitles.has(key)) {
      seenTitles.add(key);
      allRecent.push({ title: p.title, date: p.publicationDate ?? String(p.year ?? "?"), source: p.url, abstract: p.abstract ?? "" });
    }
  }

  console.log(`\nTotal unique papers found after ${CUTOFF_DATE}: ${allRecent.length}`);

  if (allRecent.length === 0) {
    console.log("\n>>> NO SCOOP THREAT DETECTED <<<");
    console.log("No competing papers found since the cutoff date.");
    console.log("The reasoning-gaps research area appears clear for NeurIPS 2026 submission.");
  } else {
    // Assess each paper for threat level
    console.log("\nPapers requiring review:\n");
    for (const p of allRecent) {
      const text = `${p.title} ${p.abstract}`.toLowerCase();
      let threatLevel = "LOW";

      // Check for high-threat keywords
      const highThreatTerms = ["reasoning gap", "reasoning gaps", "cot complexity", "chain-of-thought complexity"];
      const medThreatTerms = [
        "transformer expressiveness", "circuit complexity", "cot limitation",
        "chain of thought limitation", "reasoning benchmark", "complexity class",
      ];

      if (highThreatTerms.some((t) => text.includes(t))) {
        threatLevel = "HIGH";
      } else if (medThreatTerms.some((t) => text.includes(t))) {
        threatLevel = "MEDIUM";
      }

      console.log(`  [${threatLevel}] ${p.title}`);
      console.log(`    Date: ${p.date}  Source: ${p.source}`);
      console.log(`    Abstract: ${p.abstract.slice(0, 200)}${p.abstract.length > 200 ? "..." : ""}`);
      console.log();
    }
  }

  console.log("\n" + "=".repeat(72));
  console.log("Scoop check complete.");
  console.log("=".repeat(72));
}

main().catch((err) => {
  console.error("Fatal error:", err);
  process.exit(1);
});
