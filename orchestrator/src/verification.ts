/**
 * ClaimVerifier — traces paper claims to supporting evidence.
 *
 * Extracts claims from LaTeX (propositions, definitions, numerical assertions),
 * matches them against the knowledge graph and data files, checks internal
 * consistency, and produces structured verification reports.
 */

import { readFile } from "node:fs/promises";
import { join } from "node:path";
import { randomUUID } from "node:crypto";
import type pg from "pg";
import type { KnowledgeGraph, ClaimRow } from "./knowledge-graph.js";

// ============================================================
// Types
// ============================================================

export interface ExtractedClaim {
  id: string;
  text: string;
  claimType: "proposition" | "definition" | "corollary" | "remark" | "numerical" | "prediction";
  section: string;
  label?: string;
  lineNumber: number;
  latexSnippet: string;
  numbers: NumberAssertion[];
  references: string[];
}

export interface NumberAssertion {
  value: number;
  context: string;
  rawText: string;
}

export interface EvidenceLink {
  claimId: string;
  evidenceType: "kg_claim" | "data_file" | "figure" | "cross_reference";
  evidenceId: string;
  strength: number;
  match: string;
  verified: boolean;
  discrepancy?: string;
}

export interface ConsistencyCheck {
  category: "intra_paper" | "paper_vs_data";
  status: "consistent" | "inconsistent" | "unverifiable";
  description: string;
  locations: Array<{ line: number; value: string }>;
  sourceValue?: string;
  paperValue?: string;
}

export interface VerificationReport {
  id: string;
  project: string;
  timestamp: string;
  latexPath: string;
  totalClaims: number;
  verifiedClaims: number;
  unverifiedClaims: number;
  inconsistencies: number;
  missingEvidence: number;
  claims: Array<ExtractedClaim & {
    evidence: EvidenceLink[];
    status: "verified" | "unverified" | "inconsistent" | "no_evidence";
  }>;
  consistencyChecks: ConsistencyCheck[];
  missingFigures: string[];
  brokenReferences: string[];
}

// ============================================================
// Constants
// ============================================================

const ENVIRONMENT_RE = /\\begin\{(proposition|definition|corollary|remark)\}(?:\[([^\]]*)\])?\s*\\label\{([^}]*)\}\s*([\s\S]*?)\\end\{\1\}/g;

const NUMBER_PATTERNS = [
  // Comma-separated integers: 148,068
  { re: /\b(\d{1,3}(?:,\d{3})+)\b/g, context: "count" },
  // Decimal numbers in context: 0.503, +0.340, -0.051
  { re: /[+-]?\d+\.\d{2,}/g, context: "value" },
  // Word-numbers: "twelve models", "five families", "nine tasks"
  { re: /\b(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen)\b\s+(model|famil|task|condition|instance|benchmark|gap|proposition|definition)/gi, context: "word_count" },
];

const WORD_TO_NUM: Record<string, number> = {
  one: 1, two: 2, three: 3, four: 4, five: 5, six: 6,
  seven: 7, eight: 8, nine: 9, ten: 10, eleven: 11,
  twelve: 12, thirteen: 13, fourteen: 14, fifteen: 15,
};

const NUM_TOLERANCE = 0.01;

// ============================================================
// ClaimVerifier
// ============================================================

export class ClaimVerifier {
  private pool: pg.Pool | null;
  private kg: KnowledgeGraph | null;
  private rootDir: string;

  constructor(pool: pg.Pool | null, kg: KnowledgeGraph | null, rootDir: string) {
    this.pool = pool;
    this.kg = kg;
    this.rootDir = rootDir;
  }

  // --------------------------------------------------------
  // Core: verifyAll
  // --------------------------------------------------------

  async verifyAll(project: string): Promise<VerificationReport> {
    const latexPath = join(this.rootDir, "projects", project, "paper", "main.tex");
    let latex: string;
    try {
      latex = await readFile(latexPath, "utf-8");
    } catch {
      throw new Error(`Paper not found at ${latexPath}`);
    }

    const reportId = randomUUID();
    const extracted = this.extractClaims(latex);
    const summaryData = await this.loadSummaryData(project);
    const consistencyChecks = this.checkConsistency(latex, summaryData);

    // Link evidence for each claim
    const claims: VerificationReport["claims"] = [];
    for (const claim of extracted) {
      const evidence = await this.linkEvidence(claim, project, summaryData);
      const hasEvidence = evidence.length > 0;
      const hasInconsistency = evidence.some((e) => !e.verified);
      const status = hasInconsistency ? "inconsistent" as const
        : hasEvidence ? "verified" as const
        : claim.claimType === "definition" ? "verified" as const // definitions are self-evident
        : "no_evidence" as const;

      claims.push({ ...claim, evidence, status });
    }

    // Check figure references
    const missingFigures = await this.checkFigures(latex, project);
    const brokenReferences = this.checkReferences(latex);

    // Update KG confidence for matched claims
    await this.updateKGConfidence(claims);

    const report: VerificationReport = {
      id: reportId,
      project,
      timestamp: new Date().toISOString(),
      latexPath: `projects/${project}/paper/main.tex`,
      totalClaims: claims.length,
      verifiedClaims: claims.filter((c) => c.status === "verified").length,
      unverifiedClaims: claims.filter((c) => c.status === "no_evidence").length,
      inconsistencies: claims.filter((c) => c.status === "inconsistent").length
        + consistencyChecks.filter((c) => c.status === "inconsistent").length,
      missingEvidence: claims.filter((c) => c.status === "no_evidence").length,
      claims,
      consistencyChecks,
      missingFigures,
      brokenReferences,
    };

    // Persist report
    await this.persistReport(report);

    return report;
  }

  // --------------------------------------------------------
  // Claim extraction
  // --------------------------------------------------------

  extractClaims(latex: string): ExtractedClaim[] {
    const claims: ExtractedClaim[] = [];
    const lines = latex.split("\n");

    // Track current section
    let currentSection = "preamble";
    const sectionMap = new Map<number, string>();
    for (let i = 0; i < lines.length; i++) {
      const secMatch = lines[i].match(/\\(?:section|subsection)\{.*?\}\s*(?:\\label\{([^}]+)\})?/);
      if (secMatch) {
        currentSection = secMatch[1] ?? lines[i].replace(/\\(?:sub)?section\{/, "").replace(/\}.*/, "").trim();
        sectionMap.set(i, currentSection);
      }
    }

    // 1. Formal environments
    let match: RegExpExecArray | null;
    ENVIRONMENT_RE.lastIndex = 0;
    while ((match = ENVIRONMENT_RE.exec(latex)) !== null) {
      const envType = match[1] as ExtractedClaim["claimType"];
      const title = match[2] ?? "";
      const label = match[3];
      const body = match[4].trim();
      const lineNum = latex.substring(0, match.index).split("\n").length;

      // Find section for this line
      let section = "unknown";
      for (const [line, sec] of sectionMap) {
        if (line <= lineNum) section = sec;
      }

      const plainText = this.stripLatex(body);
      claims.push({
        id: `env-${label}`,
        text: title ? `${envType} (${title}): ${plainText.slice(0, 300)}` : `${envType}: ${plainText.slice(0, 300)}`,
        claimType: envType,
        section,
        label,
        lineNumber: lineNum,
        latexSnippet: match[0].slice(0, 200),
        numbers: this.extractNumbers(plainText),
        references: this.extractRefs(match[0]),
      });
    }

    // 2. Numerical assertions from abstract and experiments sections
    const abstractMatch = latex.match(/\\begin\{abstract\}([\s\S]*?)\\end\{abstract\}/);
    if (abstractMatch) {
      const abstractLine = latex.substring(0, latex.indexOf("\\begin{abstract}")).split("\n").length;
      const nums = this.extractNumbers(abstractMatch[1]);
      if (nums.length > 0) {
        claims.push({
          id: "num-abstract",
          text: `Abstract numerical assertions: ${nums.map((n) => n.rawText).join(", ")}`,
          claimType: "numerical",
          section: "abstract",
          lineNumber: abstractLine,
          latexSnippet: abstractMatch[1].slice(0, 200),
          numbers: nums,
          references: this.extractRefs(abstractMatch[1]),
        });
      }
    }

    // 3. Numerical claims from experiments section
    const expStart = latex.indexOf("\\section{Experiments}");
    const expEnd = latex.indexOf("\\section{Discussion}");
    if (expStart >= 0 && expEnd >= 0) {
      const expSection = latex.substring(expStart, expEnd);
      const expLine = latex.substring(0, expStart).split("\n").length;

      // Find sentences with decimal numbers (accuracy values, lifts)
      const sentences = expSection.split(/(?<=[.!?])\s+/);
      for (let i = 0; i < sentences.length; i++) {
        const nums = this.extractNumbers(sentences[i]);
        const significantNums = nums.filter((n) =>
          n.context === "value" || n.context === "count",
        );
        if (significantNums.length >= 2) {
          claims.push({
            id: `num-exp-${i}`,
            text: this.stripLatex(sentences[i]).slice(0, 300),
            claimType: "numerical",
            section: "sec:experiments",
            lineNumber: expLine + i,
            latexSnippet: sentences[i].slice(0, 200),
            numbers: significantNums,
            references: this.extractRefs(sentences[i]),
          });
        }
      }
    }

    return claims;
  }

  // --------------------------------------------------------
  // Evidence linking
  // --------------------------------------------------------

  private async linkEvidence(
    claim: ExtractedClaim,
    project: string,
    summaryData: Map<string, string>,
  ): Promise<EvidenceLink[]> {
    const links: EvidenceLink[] = [];

    // 1. KG semantic matching
    if (this.kg && (claim.claimType === "proposition" || claim.claimType === "corollary")) {
      try {
        const kgMatches = await this.kg.query(claim.text, {
          project,
          limit: 3,
          threshold: 0.25,
        });
        for (const kgClaim of kgMatches) {
          links.push({
            claimId: claim.id,
            evidenceType: "kg_claim",
            evidenceId: kgClaim.id,
            strength: kgClaim.distance ? 1 - kgClaim.distance : 0.5,
            match: `KG claim: "${kgClaim.statement.slice(0, 100)}" (confidence: ${kgClaim.confidence})`,
            verified: kgClaim.confidence >= 0.5,
          });
        }
      } catch {
        // KG unavailable
      }
    }

    // 2. Numerical verification against summary data
    for (const num of claim.numbers) {
      const dataMatch = this.matchNumberAgainstData(num, summaryData);
      if (dataMatch) {
        links.push(dataMatch);
      }
    }

    return links;
  }

  private matchNumberAgainstData(
    num: NumberAssertion,
    summaryData: Map<string, string>,
  ): EvidenceLink | null {
    // Match comma-separated counts (e.g., "159,162" against "Instances: 309,501")
    if (num.context === "count") {
      const paperValue = parseInt(num.rawText.replace(/,/g, ""));
      const dataInstances = summaryData.get("instances");
      if (dataInstances) {
        const dataValue = parseInt(dataInstances.replace(/,/g, ""));
        const match = paperValue === dataValue;
        return {
          claimId: "",
          evidenceType: "data_file",
          evidenceId: "summary.md:instances",
          strength: match ? 1.0 : 0.3,
          match: `Paper: ${num.rawText}, Data: ${dataInstances}`,
          verified: match,
          discrepancy: match ? undefined : `Paper says ${num.rawText} but data has ${dataInstances}`,
        };
      }
    }

    // Match word-counts (e.g., "twelve models")
    if (num.context === "word_count") {
      const dataModels = summaryData.get("models");
      if (dataModels && num.rawText.toLowerCase().includes("model")) {
        const match = num.value === parseInt(dataModels);
        return {
          claimId: "",
          evidenceType: "data_file",
          evidenceId: "summary.md:models",
          strength: match ? 1.0 : 0.3,
          match: `Paper: ${num.value} models, Data: ${dataModels} models`,
          verified: match,
          discrepancy: match ? undefined : `Paper says ${num.value} models but data has ${dataModels}`,
        };
      }
    }

    // Match decimal accuracy/lift values
    if (num.context === "value" && Math.abs(num.value) < 2) {
      // Check against accuracy values in summary
      for (const [key, val] of summaryData) {
        if (!key.startsWith("acc:") && !key.startsWith("lift:")) continue;
        const dataValue = parseFloat(val);
        if (isNaN(dataValue)) continue;

        if (Math.abs(num.value - dataValue) < NUM_TOLERANCE) {
          return {
            claimId: "",
            evidenceType: "data_file",
            evidenceId: `summary.md:${key}`,
            strength: 0.9,
            match: `Paper: ${num.rawText}, Data: ${val} (${key})`,
            verified: true,
          };
        }
      }
    }

    return null;
  }

  // --------------------------------------------------------
  // Consistency checking
  // --------------------------------------------------------

  checkConsistency(
    latex: string,
    summaryData: Map<string, string>,
  ): ConsistencyCheck[] {
    const checks: ConsistencyCheck[] = [];
    const lines = latex.split("\n");

    // 1. Intra-paper: find repeated numbers and check they match
    const numberMap = new Map<string, Array<{ line: number; value: string }>>();
    for (let i = 0; i < lines.length; i++) {
      // Large integers
      const bigNums = lines[i].matchAll(/\b(\d{1,3}(?:,\d{3})+)\b/g);
      for (const m of bigNums) {
        const normalized = m[1].replace(/,/g, "");
        const locs = numberMap.get(normalized) ?? [];
        locs.push({ line: i + 1, value: m[1] });
        numberMap.set(normalized, locs);
      }
    }

    // Numbers appearing more than once should be consistent (they are, by identity)
    // But check if DIFFERENT large numbers appear in similar contexts
    const instanceCounts = new Set<string>();
    for (const [normalized, locs] of numberMap) {
      if (parseInt(normalized) > 10000) {
        instanceCounts.add(normalized);
        if (locs.length > 1) {
          checks.push({
            category: "intra_paper",
            status: "consistent",
            description: `Instance count ${locs[0].value} appears ${locs.length} times consistently`,
            locations: locs,
          });
        }
      }
    }

    // 2. Paper vs data: key figures from summary
    const paperInstances = this.findFirstMatch(latex, /(\d{1,3}(?:,\d{3})+)\s*(?:evaluated\s+)?instances/i);
    const dataInstances = summaryData.get("instances");
    if (paperInstances && dataInstances) {
      const pVal = paperInstances.replace(/,/g, "");
      const dVal = dataInstances.replace(/,/g, "");
      const match = pVal === dVal;
      checks.push({
        category: "paper_vs_data",
        status: match ? "consistent" : "inconsistent",
        description: match
          ? `Instance count matches: ${paperInstances}`
          : `Instance count mismatch: paper says ${paperInstances}, data has ${dataInstances}`,
        locations: [],
        paperValue: paperInstances,
        sourceValue: dataInstances,
      });
    }

    // Check model count
    const paperModels = summaryData.get("models");
    const modelWordMatch = latex.match(/\b(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen)\b\s+models?/i);
    if (modelWordMatch && paperModels) {
      const paperCount = WORD_TO_NUM[modelWordMatch[1].toLowerCase()];
      const dataCount = parseInt(paperModels);
      const match = paperCount === dataCount;
      checks.push({
        category: "paper_vs_data",
        status: match ? "consistent" : "inconsistent",
        description: match
          ? `Model count matches: ${paperCount}`
          : `Model count mismatch: paper says ${modelWordMatch[1]} (${paperCount}), data has ${dataCount}`,
        locations: [],
        paperValue: String(paperCount),
        sourceValue: paperModels,
      });
    }

    // Check overall accuracy values
    for (const condition of ["direct", "short_cot", "budget_cot"]) {
      const dataAcc = summaryData.get(`acc:${condition}`);
      if (!dataAcc) continue;
      const dataVal = parseFloat(dataAcc);

      // Find this value in the paper
      const paperMatch = this.findAccuracyInPaper(latex, condition, dataVal);
      if (paperMatch) {
        checks.push({
          category: "paper_vs_data",
          status: paperMatch.match ? "consistent" : "inconsistent",
          description: paperMatch.match
            ? `${condition} accuracy matches: ${dataAcc}`
            : `${condition} accuracy mismatch: paper=${paperMatch.paperValue}, data=${dataAcc}`,
          locations: [],
          paperValue: paperMatch.paperValue,
          sourceValue: dataAcc,
        });
      }
    }

    return checks;
  }

  // --------------------------------------------------------
  // Figure and reference checks
  // --------------------------------------------------------

  private async checkFigures(latex: string, project: string): Promise<string[]> {
    const missing: string[] = [];
    const figRefs = latex.matchAll(/\\includegraphics(?:\[.*?\])?\{([^}]+)\}/g);
    for (const m of figRefs) {
      const figPath = m[1];
      const fullPath = join(this.rootDir, "projects", project, "paper", figPath);
      try {
        await readFile(fullPath);
      } catch {
        // Try with common extensions
        let found = false;
        for (const ext of [".pdf", ".png", ".jpg"]) {
          try {
            await readFile(fullPath + ext);
            found = true;
            break;
          } catch { /* continue */ }
        }
        if (!found) missing.push(figPath);
      }
    }
    return missing;
  }

  private checkReferences(latex: string): string[] {
    const broken: string[] = [];
    // Find all \label{...} definitions
    const labels = new Set<string>();
    for (const m of latex.matchAll(/\\label\{([^}]+)\}/g)) {
      labels.add(m[1]);
    }
    // Find all \Cref{...} and \cref{...} references
    for (const m of latex.matchAll(/\\[Cc]ref\{([^}]+)\}/g)) {
      const refs = m[1].split(",").map((r) => r.trim());
      for (const ref of refs) {
        if (!labels.has(ref)) {
          broken.push(ref);
        }
      }
    }
    return [...new Set(broken)];
  }

  // --------------------------------------------------------
  // KG confidence updates
  // --------------------------------------------------------

  private async updateKGConfidence(
    claims: VerificationReport["claims"],
  ): Promise<void> {
    if (!this.kg) return;

    for (const claim of claims) {
      for (const ev of claim.evidence) {
        if (ev.evidenceType !== "kg_claim") continue;
        try {
          const kgClaim = await this.kg.getClaim(ev.evidenceId);
          if (!kgClaim) continue;

          if (ev.verified && kgClaim.confidence < 0.9) {
            await this.kg.updateConfidence(
              ev.evidenceId,
              Math.min(kgClaim.confidence + 0.1, 1.0),
              "Verified by paper verification layer",
              "verifier",
            );
          } else if (!ev.verified && kgClaim.confidence > 0.2) {
            await this.kg.updateConfidence(
              ev.evidenceId,
              Math.max(kgClaim.confidence - 0.15, 0.1),
              `Inconsistency: ${ev.discrepancy}`,
              "verifier",
            );
          }
        } catch {
          // Non-fatal
        }
      }
    }
  }

  // --------------------------------------------------------
  // Data loading
  // --------------------------------------------------------

  private async loadSummaryData(project: string): Promise<Map<string, string>> {
    const data = new Map<string, string>();
    const summaryPath = join(this.rootDir, "projects", project, "benchmarks", "results", "analysis", "summary.md");

    try {
      const content = await readFile(summaryPath, "utf-8");

      // Parse key metrics from summary.md
      const instancesMatch = content.match(/\*\*Instances\*\*:\s*([\d,]+)/);
      if (instancesMatch) data.set("instances", instancesMatch[1]);

      const modelsMatch = content.match(/\*\*Models\*\*:\s*(\d+)/);
      if (modelsMatch) data.set("models", modelsMatch[1]);

      const tasksMatch = content.match(/\*\*Tasks\*\*:\s*(\d+)/);
      if (tasksMatch) data.set("tasks", tasksMatch[1]);

      // Parse accuracy by condition
      const conditionRe = /\*\*(\w+)\*\*:\s*([\d.]+)/g;
      let condMatch;
      while ((condMatch = conditionRe.exec(content)) !== null) {
        const key = condMatch[1].toLowerCase();
        if (["direct", "short_cot", "budget_cot"].includes(key)) {
          data.set(`acc:${key}`, condMatch[2]);
        }
      }

      // Parse CoT lift values
      const liftRe = /CoT lift \((\w+)\):\s*([+-]?[\d.]+)/g;
      let liftMatch;
      while ((liftMatch = liftRe.exec(content)) !== null) {
        const condition = liftMatch[1].toLowerCase();
        const section = content.substring(Math.max(0, content.lastIndexOf("###", liftRe.lastIndex)), liftRe.lastIndex);
        const typeMatch = section.match(/Type (\d+)/);
        if (typeMatch) {
          data.set(`lift:type${typeMatch[1]}_${condition}`, liftMatch[2]);
        }
      }

      // Parse aggregate predictions
      const predRe = /Types? ([\d,]+).*?CoT lift = ([+-]?[\d.]+)/g;
      let predMatch;
      while ((predMatch = predRe.exec(content)) !== null) {
        data.set(`lift:types_${predMatch[1].replace(",", "_")}`, predMatch[2]);
      }
    } catch {
      // Summary not available
    }

    return data;
  }

  // --------------------------------------------------------
  // Persistence
  // --------------------------------------------------------

  private async persistReport(report: VerificationReport): Promise<void> {
    if (!this.pool) return;
    try {
      await this.pool.query(
        `INSERT INTO verification_reports
         (id, project, latex_path, total_claims, verified_claims, unverified_claims,
          inconsistencies, missing_evidence, report, triggered_by)
         VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)`,
        [
          report.id, report.project, report.latexPath,
          report.totalClaims, report.verifiedClaims, report.unverifiedClaims,
          report.inconsistencies, report.missingEvidence,
          JSON.stringify(report), "manual",
        ],
      );
    } catch (err) {
      console.error("[Verifier] Failed to persist report:", err);
    }
  }

  // --------------------------------------------------------
  // API accessors
  // --------------------------------------------------------

  async getLatestReport(project: string): Promise<VerificationReport | null> {
    if (!this.pool) return null;
    try {
      const { rows } = await this.pool.query(
        `SELECT report FROM verification_reports
         WHERE project = $1 ORDER BY created_at DESC LIMIT 1`,
        [project],
      );
      return rows.length > 0 ? rows[0].report as VerificationReport : null;
    } catch {
      return null;
    }
  }

  async getReportHistory(project: string, limit = 10): Promise<Array<{
    id: string;
    timestamp: string;
    totalClaims: number;
    verified: number;
    inconsistencies: number;
  }>> {
    if (!this.pool) return [];
    try {
      const { rows } = await this.pool.query(
        `SELECT id, created_at, total_claims, verified_claims, inconsistencies
         FROM verification_reports WHERE project = $1
         ORDER BY created_at DESC LIMIT $2`,
        [project, limit],
      );
      return rows.map((r: Record<string, unknown>) => ({
        id: r.id as string,
        timestamp: (r.created_at as Date).toISOString(),
        totalClaims: r.total_claims as number,
        verified: r.verified_claims as number,
        inconsistencies: r.inconsistencies as number,
      }));
    } catch {
      return [];
    }
  }

  // --------------------------------------------------------
  // Helpers
  // --------------------------------------------------------

  private stripLatex(text: string): string {
    return text
      .replace(/\\[a-zA-Z]+\{([^}]*)\}/g, "$1")  // \cmd{arg} → arg
      .replace(/\\[a-zA-Z]+/g, "")                 // \cmd → ""
      .replace(/\$[^$]*\$/g, "[math]")              // $..$ → [math]
      .replace(/\{|\}/g, "")                         // braces
      .replace(/\s+/g, " ")                           // whitespace
      .trim();
  }

  private extractNumbers(text: string): NumberAssertion[] {
    const nums: NumberAssertion[] = [];
    for (const pattern of NUMBER_PATTERNS) {
      const re = new RegExp(pattern.re.source, pattern.re.flags);
      let m;
      while ((m = re.exec(text)) !== null) {
        if (pattern.context === "word_count") {
          const word = m[1].toLowerCase();
          const value = WORD_TO_NUM[word];
          if (value !== undefined) {
            nums.push({ value, context: "word_count", rawText: m[0] });
          }
        } else if (pattern.context === "count") {
          nums.push({
            value: parseInt(m[0].replace(/,/g, "")),
            context: "count",
            rawText: m[0],
          });
        } else {
          const val = parseFloat(m[0]);
          if (!isNaN(val)) {
            nums.push({ value: val, context: "value", rawText: m[0] });
          }
        }
      }
    }
    return nums;
  }

  private extractRefs(text: string): string[] {
    const refs: string[] = [];
    for (const m of text.matchAll(/\\[Cc]ref\{([^}]+)\}/g)) {
      refs.push(...m[1].split(",").map((r) => r.trim()));
    }
    for (const m of text.matchAll(/\\citep?\{([^}]+)\}/g)) {
      refs.push(...m[1].split(",").map((r) => r.trim()));
    }
    return refs;
  }

  private findFirstMatch(text: string, re: RegExp): string | null {
    const m = text.match(re);
    return m ? m[1] : null;
  }

  private findAccuracyInPaper(
    latex: string,
    condition: string,
    dataValue: number,
  ): { match: boolean; paperValue: string } | null {
    // Look for patterns like "0.503 for direct" or "direct.*0.503"
    const condLabel = condition.replace(/_/g, "[_ ]?");
    const re1 = new RegExp(`(\\d+\\.\\d+)\\s+(?:for\\s+)?${condLabel}`, "i");
    const re2 = new RegExp(`${condLabel}[^.]*?(\\d+\\.\\d+)`, "i");

    for (const re of [re1, re2]) {
      const m = latex.match(re);
      if (m) {
        const paperVal = parseFloat(m[1]);
        return {
          match: Math.abs(paperVal - dataValue) < NUM_TOLERANCE,
          paperValue: m[1],
        };
      }
    }
    return null;
  }
}
