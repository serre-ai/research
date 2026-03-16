# Review Simulation — Predict Acceptance Before Submission

**Status:** Planned
**Priority:** High — reduces rejection risk, prioritizes revision effort
**Estimated effort:** 12-16 hours
**Dependencies:** Paper in submission-ready state, verification layer (recommended but not required)

## Motivation

Peer review is the highest-stakes filter in academic publishing. A NeurIPS submission gets 3-4 reviews, and the outcome depends on which reviewers are assigned. By simulating the review process with calibrated personas, we can:

- Identify weaknesses before real reviewers do
- Estimate acceptance probability to guide submission timing
- Prioritize revision effort on the issues most likely to cause rejection
- Test whether framing changes affect perceived novelty and impact

The reasoning-gaps paper targets NeurIPS 2026. A simulated review panel costs ~$15-25 and takes 10 minutes. A rejection costs 6 months of delay. The expected value calculation is straightforward.

## Reviewer Personas

Five personas calibrated to a typical NeurIPS review panel. Each has distinct expertise, disposition, and blind spots — real panels have this variance.

### `shared/prompts/reviewer-personas.yaml`

```yaml
# Synthetic reviewer personas for peer review simulation.
# Each profile defines expertise, disposition, evaluation focus, and
# common criticism patterns calibrated to NeurIPS/ICML/ACL standards.
#
# Usage: ReviewSimulator selects 3-5 personas per run.
# Default panel: methodologist, empiricist, domain_expert (core 3)
# Extended panel: + theorist, area_chair (5-reviewer run)

reviewer_profiles:
  - id: "methodologist"
    name: "Dr. A (Methodology)"
    expertise:
      - "statistical methodology"
      - "experimental design"
      - "reproducibility"
      - "causal inference"
    disposition: "rigorous"
    description: >
      Cares most about whether the experiments actually support the claims.
      Will check sample sizes, statistical tests, confidence intervals, and
      whether the evaluation protocol has obvious confounds. Unimpressed by
      novelty if the evidence is weak. Writes detailed, structured reviews.
    focus:
      - "Are the experiments well-designed and free of confounds?"
      - "Are statistical claims valid (proper tests, CIs, effect sizes)?"
      - "Can I reproduce this from the paper alone?"
      - "Are baselines appropriate and sufficient?"
      - "Is the evaluation protocol standard or justified if non-standard?"
    common_criticisms:
      - "insufficient baselines"
      - "missing ablations"
      - "p-hacking or multiple comparison concerns"
      - "no confidence intervals"
      - "evaluation protocol not clearly described"
      - "cherry-picked results or examples"
    scoring_tendencies:
      rigor: "strict — demands proper statistical methodology"
      novelty: "lenient — will accept incremental work if rigor is high"
      clarity: "moderate — expects clear methods section above all"

  - id: "theorist"
    name: "Dr. B (Theory)"
    expertise:
      - "computational complexity"
      - "formal methods"
      - "mathematical proofs"
      - "information theory"
      - "learning theory"
    disposition: "skeptical"
    description: >
      Evaluates formal claims with extreme care. Will check every proof step,
      question whether formalisms add real insight or are decorative, and push
      back on overclaimed generality. Respects clean mathematical work but
      has no patience for hand-waving disguised as formalism. Terse reviewer.
    focus:
      - "Are the theoretical claims sound and complete?"
      - "Are proofs correct, or do they have gaps?"
      - "Is the formalism necessary, or would natural language suffice?"
      - "Does the theoretical framework actually predict the empirical results?"
      - "Are the assumptions stated and reasonable?"
    common_criticisms:
      - "proof gaps or unstated assumptions"
      - "overclaimed generality — results hold for a narrow case only"
      - "unnecessary formalism that obscures rather than clarifies"
      - "disconnect between theory and experiments"
      - "missing lower bounds or impossibility results"
    scoring_tendencies:
      rigor: "strict on formal claims — lenient on empirical"
      novelty: "high bar — wants genuine theoretical insight"
      clarity: "expects mathematical precision; tolerates terse exposition"

  - id: "empiricist"
    name: "Dr. C (Empirical ML)"
    expertise:
      - "LLM evaluation"
      - "benchmarking"
      - "scaling laws"
      - "prompt engineering"
      - "model comparison"
    disposition: "constructive"
    description: >
      Has evaluated dozens of LLM papers. Knows all the ways benchmarks can
      mislead. Cares about whether results generalize beyond the specific
      models and tasks tested. Constructive in feedback — will suggest
      specific improvements rather than just listing problems. Values
      practical impact alongside scientific rigor.
    focus:
      - "Are the benchmarks meaningful and not gameable?"
      - "Do results generalize across model families and scales?"
      - "Is the evaluation fair — same prompts, same decoding, same compute?"
      - "Are there enough models to support the claims?"
      - "Would practitioners learn something actionable from this?"
    common_criticisms:
      - "benchmark gaming or overfitting to specific models"
      - "cherry-picked model selection"
      - "missing important model families (e.g., open-source, non-English)"
      - "unfair comparison conditions"
      - "results may not generalize to real-world tasks"
      - "no error analysis or failure case discussion"
    scoring_tendencies:
      rigor: "moderate — wants solid evals but not theorem-level formalism"
      novelty: "moderate — values new benchmarks if well-motivated"
      clarity: "values accessibility; wants clear takeaways"

  - id: "domain_expert"
    name: "Dr. D (Reasoning & Cognition)"
    expertise:
      - "reasoning in LLMs"
      - "cognitive science"
      - "chain-of-thought prompting"
      - "AI alignment"
      - "interpretability"
    disposition: "enthusiastic_but_careful"
    description: >
      Deeply interested in the topic and inclined to support good work in
      this area. But precisely because they care, they hold a high bar for
      claims about reasoning — the field has been burned by hype before.
      Will push on whether results genuinely reveal something about reasoning
      vs. pattern matching. Writes engaged, substantive reviews.
    focus:
      - "Does this advance our understanding of LLM reasoning?"
      - "Are the claims about reasoning well-scoped and defensible?"
      - "Is there a meaningful connection to cognitive science or theory?"
      - "Does the taxonomy or framework add real structure?"
      - "Are the implications for the field discussed honestly?"
    common_criticisms:
      - "overclaimed impact — this is a contribution, not a revolution"
      - "missing related work in cognitive science or philosophy"
      - "weak motivation — why should we care about this specific gap?"
      - "conflates performance with understanding"
      - "taxonomy is ad hoc — not clearly grounded in theory or data"
    scoring_tendencies:
      rigor: "moderate — cares more about insight than formalism"
      novelty: "high bar — wants genuine conceptual advance"
      clarity: "values clear writing and honest framing of limitations"

  - id: "area_chair"
    name: "AC (Area Chair)"
    expertise:
      - "broad ML/AI"
      - "venue standards"
      - "novelty assessment"
      - "meta-review synthesis"
    disposition: "calibrated"
    description: >
      Has seen hundreds of submissions. Evaluates relative to the venue
      standard, not in absolute terms. Asks: would this paper improve the
      conference? Does it contribute something the community needs? Not
      swayed by either flashy results or dense formalism — looks for the
      core contribution and whether it holds up. Reads all other reviews
      and synthesizes.
    focus:
      - "Is this novel enough for a top venue?"
      - "Does it meet the venue's standards for rigor and clarity?"
      - "Will this generate productive discussion at the conference?"
      - "Is the paper positioned correctly in the literature?"
      - "Would acceptance set a good precedent?"
    common_criticisms:
      - "incremental contribution — does not clear the novelty bar"
      - "wrong venue — this belongs at a workshop or a different conference"
      - "unclear positioning — what is the one-sentence contribution?"
      - "writing needs significant revision"
      - "interesting idea but execution is not ready"
    scoring_tendencies:
      rigor: "expects venue-appropriate rigor"
      novelty: "key dimension — will override good rigor if novelty is low"
      clarity: "expects polished writing for a top venue"
```

## New Files

### `orchestrator/src/review-simulator.ts` — ReviewSimulator class

```typescript
import { readFile } from "node:fs/promises";
import { join } from "node:path";
import { parse as parseYaml } from "./yaml.js";
import type pg from "pg";

// ============================================================
// Types
// ============================================================

export interface ReviewerProfile {
  id: string;
  name: string;
  expertise: string[];
  disposition: string;
  description: string;
  focus: string[];
  commonCriticisms: string[];
  scoringTendencies: Record<string, string>;
}

export interface SimulatedReview {
  reviewerId: string;
  reviewerName: string;
  summary: string;
  strengths: string[];
  weaknesses: string[];
  questions: string[];
  suggestions: string[];
  scores: {
    novelty: number;         // 1-10
    rigor: number;           // 1-10
    clarity: number;         // 1-10
    significance: number;    // 1-10
    overall: number;         // 1-10
    confidence: number;      // 1-5 (reviewer self-assessed confidence)
  };
  verdict:
    | "strong_accept"
    | "accept"
    | "weak_accept"
    | "borderline"
    | "weak_reject"
    | "reject"
    | "strong_reject";
  costUsd: number;
  latencyMs: number;
}

export interface AcceptancePrediction {
  probability: number;                    // 0-1
  predictedScore: number;                 // weighted average overall score
  consensus: string;                      // e.g. "split", "unanimous_accept"
  topWeaknesses: string[];                // prioritized revision targets
  improvementPotential: number;           // estimated probability gain
  confidenceInterval: [number, number];   // 95% CI on probability estimate
}

export interface SimulationResult {
  project: string;
  venue: string;
  timestamp: string;
  reviews: SimulatedReview[];
  prediction: AcceptancePrediction;
  revisionPlan: RevisionItem[];
  totalCostUsd: number;
  totalLatencyMs: number;
}

export interface RevisionItem {
  priority: number;                       // 1 = highest
  category: string;                       // "methodology", "writing", "framing", etc.
  description: string;
  sourcedFrom: string[];                  // reviewer IDs that raised this
  estimatedEffort: "small" | "medium" | "large";
  expectedImpact: "low" | "medium" | "high";
}

// ============================================================
// ReviewSimulator
// ============================================================

export class ReviewSimulator {
  private profiles: ReviewerProfile[] = [];

  constructor(
    private pool: pg.Pool,
    private rootDir: string
  ) {}

  /**
   * Load reviewer profiles from YAML.
   */
  async loadProfiles(): Promise<void> { /* ... */ }

  /**
   * Run a simulated review panel.
   *
   * @param paperPath - Path to paper directory containing .tex files
   * @param venue - Target venue (e.g. "neurips2026", "acl2027")
   * @param numReviewers - Number of reviewers (default: 3, max: 5)
   * @returns Full simulation result with reviews, prediction, and revision plan
   *
   * Process:
   * 1. Load and compile the paper (all .tex files, figures, tables)
   * 2. Select reviewer panel (core 3 or extended 5)
   * 3. Run each review in parallel (independent API calls)
   * 4. Aggregate scores and compute acceptance prediction
   * 5. Generate prioritized revision plan from weaknesses
   * 6. Persist results to DB
   */
  async simulate(
    paperPath: string,
    venue: string,
    numReviewers: number = 3
  ): Promise<SimulationResult> { /* ... */ }

  /**
   * Aggregate individual reviews into an acceptance prediction.
   *
   * Scoring model:
   * - Weighted average of overall scores (weight = reviewer confidence)
   * - Map average score to acceptance probability using venue-calibrated curve
   * - Detect consensus vs. split (high variance in scores)
   * - Estimate improvement potential from weakness severity distribution
   */
  aggregate(reviews: SimulatedReview[], venue: string): AcceptancePrediction { /* ... */ }

  /**
   * Extract and prioritize revision items from all reviews.
   *
   * Deduplication: Weaknesses mentioned by multiple reviewers are merged.
   * Prioritization: Items raised by more reviewers rank higher.
   * Effort estimation: Based on weakness category (writing = small,
   *   new experiments = large).
   * Impact estimation: Items affecting rigor/novelty scores rank higher
   *   than clarity-only items.
   */
  prioritizeRevisions(reviews: SimulatedReview[]): RevisionItem[] { /* ... */ }
}
```

### Prompt Engineering Strategy

Each reviewer gets a carefully constructed system prompt containing:

1. **Persona definition**: Full profile from YAML including disposition, expertise, focus areas
2. **Venue calibration**: Specific acceptance rate and standards for the target venue
3. **Review format**: Structured template matching real review formats (summary, strengths, weaknesses, questions, scores)
4. **Anti-sycophancy instructions**: Explicit instruction to find weaknesses, not just praise. "You are evaluating this paper for rejection. What would make you reject it?"
5. **Scoring rubric**: Detailed rubric for each score dimension, calibrated to venue

**Model selection**: Opus 4.6 for all reviews. Cheaper models produce reviews that are too superficial and miss subtle issues. The cost per review (~$3-5 with a 20-page paper) is justified by quality.

**Context window**: Full paper content fits within the context window. Include:
- All `.tex` files concatenated with section markers
- Figure captions (not image data — describe figures textually)
- Table data (LaTeX source, which is readable)
- Verification report if available (so reviewers know which claims are backed by data)

### Score-to-Probability Calibration

Map aggregate review scores to acceptance probability using venue-specific curves:

```
NeurIPS calibration (historical approximation):
  avg_score >= 7.5  →  p(accept) = 0.90
  avg_score >= 6.5  →  p(accept) = 0.65
  avg_score >= 5.5  →  p(accept) = 0.35
  avg_score >= 4.5  →  p(accept) = 0.10
  avg_score < 4.5   →  p(accept) = 0.02

Adjustments:
  - High variance (std > 1.5): -0.10 (split panel is risky)
  - Low variance (std < 0.5): +0.05 (consensus is favorable)
  - Any "strong_reject": -0.15 (champion problem)
  - Any "strong_accept" with confidence >= 4: +0.10
```

These calibrations are initial estimates and should be refined as we collect data on simulated vs. actual outcomes.

### Consensus Detection

```
unanimous_accept:    all verdicts in {strong_accept, accept}
majority_accept:     >50% accept-side, no strong_reject
split:               accept-side and reject-side both >= 30%
majority_reject:     >50% reject-side
unanimous_reject:    all verdicts in {reject, strong_reject}
```

### `orchestrator/src/routes/review.ts` — API routes

```typescript
import { Router, type Request, type Response } from "express";
import type pg from "pg";
import { ReviewSimulator } from "../review-simulator.js";

export function reviewRoutes(pool: pg.Pool, rootDir: string): Router {
  const router = Router();
  const simulator = new ReviewSimulator(pool, rootDir);

  // POST /api/projects/:id/review-simulate
  // Trigger a review simulation.
  // Body: { venue: "neurips2026", numReviewers?: 3 | 5 }
  // Returns: SimulationResult
  router.post("/projects/:id/review-simulate", async (req: Request, res: Response) => {
    /* ... */
  });

  // GET /api/projects/:id/review-simulations
  // List all past simulation results for a project.
  // Query params: ?limit=10&offset=0
  router.get("/projects/:id/review-simulations", async (req: Request, res: Response) => {
    /* ... */
  });

  // GET /api/projects/:id/review-simulations/:runId
  // Get a specific simulation result with full reviews.
  router.get("/projects/:id/review-simulations/:runId", async (req: Request, res: Response) => {
    /* ... */
  });

  // GET /api/projects/:id/revision-plan
  // Get the latest prioritized revision plan.
  router.get("/projects/:id/revision-plan", async (req: Request, res: Response) => {
    /* ... */
  });

  return router;
}
```

### Schema additions

New migration file: `orchestrator/sql/006_review_simulation.sql`

```sql
BEGIN;

-- ============================================================
-- Review Simulation Runs
-- ============================================================
CREATE TABLE review_simulations (
    id              SERIAL PRIMARY KEY,
    project         TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    venue           TEXT NOT NULL,
    num_reviewers   INTEGER NOT NULL,
    predicted_score REAL,
    acceptance_prob REAL,
    consensus       TEXT,
    top_weaknesses  JSONB NOT NULL DEFAULT '[]',
    revision_plan   JSONB NOT NULL DEFAULT '[]',
    total_cost_usd  REAL NOT NULL DEFAULT 0,
    total_latency_ms REAL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_review_sims_project ON review_simulations (project);
CREATE INDEX idx_review_sims_created ON review_simulations (created_at);

-- ============================================================
-- Individual Simulated Reviews
-- ============================================================
CREATE TABLE simulated_reviews (
    id              SERIAL PRIMARY KEY,
    simulation_id   INTEGER NOT NULL REFERENCES review_simulations(id) ON DELETE CASCADE,
    reviewer_id     TEXT NOT NULL,           -- persona ID from YAML
    summary         TEXT NOT NULL,
    strengths       JSONB NOT NULL DEFAULT '[]',
    weaknesses      JSONB NOT NULL DEFAULT '[]',
    questions       JSONB NOT NULL DEFAULT '[]',
    suggestions     JSONB NOT NULL DEFAULT '[]',
    scores          JSONB NOT NULL,
        -- { "novelty": 7, "rigor": 8, "clarity": 6, "significance": 7,
        --   "overall": 7, "confidence": 4 }
    verdict         TEXT NOT NULL
                    CHECK (verdict IN (
                        'strong_accept', 'accept', 'weak_accept', 'borderline',
                        'weak_reject', 'reject', 'strong_reject'
                    )),
    cost_usd        REAL NOT NULL DEFAULT 0,
    latency_ms      REAL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_sim_reviews_simulation ON simulated_reviews (simulation_id);
CREATE INDEX idx_sim_reviews_reviewer   ON simulated_reviews (reviewer_id);
CREATE INDEX idx_sim_reviews_verdict    ON simulated_reviews (verdict);

-- ============================================================
-- View: acceptance probability trend
-- ============================================================
CREATE VIEW v_acceptance_trend AS
SELECT
    project,
    venue,
    created_at,
    acceptance_prob,
    predicted_score,
    consensus,
    (SELECT COUNT(*) FROM simulated_reviews sr
     WHERE sr.simulation_id = rs.id
     AND sr.verdict IN ('strong_accept', 'accept', 'weak_accept')) AS accept_votes,
    (SELECT COUNT(*) FROM simulated_reviews sr
     WHERE sr.simulation_id = rs.id
     AND sr.verdict IN ('weak_reject', 'reject', 'strong_reject')) AS reject_votes
FROM review_simulations rs
ORDER BY project, created_at;

COMMIT;
```

### OpenClaw skill: `review-simulate`

Add to agent skill set. Primarily used by the strategist and editor agents.

```
/review-simulate <project> [--venue <venue>] [--reviewers <3|5>]
  Simulate a peer review panel for the paper. Returns individual reviews
  with scores, an aggregated acceptance prediction, and a prioritized
  revision plan. Default: 3 reviewers, NeurIPS venue.

  Cost: ~$10-15 for 3 reviewers, ~$15-25 for 5 reviewers (Opus 4.6).

  Use after major revisions to track whether changes improved the paper.
  Use with 5 reviewers before submission deadline for highest fidelity.
```

## Integration with Existing Systems

### Strategist agent workflow

The strategist agent (`.claude/agents/strategist.md`) uses review simulation to make submission decisions:

```
When the paper approaches submission readiness:
1. Run /review-simulate with 3 reviewers
2. If acceptance_prob < 0.40: prioritize revision plan, defer submission
3. If acceptance_prob 0.40-0.65: run with 5 reviewers for higher confidence
4. If acceptance_prob > 0.65: consider submission; run final 5-reviewer panel
5. Log prediction in predictions table for calibration tracking
```

### Revision plan to backlog

The prioritized revision plan feeds directly into the backlog manager (`orchestrator/src/backlog.ts`):

```typescript
// After simulation completes:
for (const item of result.revisionPlan) {
  await backlog.add({
    project: config.projectName,
    title: item.description,
    priority: item.priority,
    category: item.category,
    source: `review-simulation-${simulationId}`,
    estimatedEffort: item.estimatedEffort,
  });
}
```

### Dashboard integration

The Astro dashboard at `site/` should display:
- Acceptance probability gauge (0-100%) with trend sparkline
- Latest review verdicts as colored badges
- Top 3 weaknesses as actionable cards
- Revision plan as a prioritized checklist
- Cost tracking for simulation runs

### Prediction calibration

Every simulation produces an acceptance prediction. When the paper is eventually submitted and reviewed:
1. Record the actual outcome (accept/reject, actual reviewer scores)
2. Compare against simulated prediction
3. Update calibration curves in the prediction table
4. Over time, this creates a calibrated acceptance predictor

This feeds into the predictions system already in the collective schema (`predictions` table). The strategist agent logs each simulation's predicted probability as a formal prediction, which gets resolved when the actual venue decision arrives.

## Task Breakdown

| # | Task | Est. hours | Dependencies |
|---|------|-----------|--------------|
| 1 | Reviewer personas YAML file | 1.0 | None |
| 2 | ReviewSimulator class — structure, types, profile loading | 1.0 | Task 1 |
| 3 | Individual review prompt engineering and generation | 3.5 | Task 2 |
| 4 | Score aggregation and acceptance prediction logic | 2.0 | Task 3 |
| 5 | Revision prioritization and deduplication | 1.5 | Task 3 |
| 6 | Schema migration (`006_review_simulation.sql`) | 0.5 | None |
| 7 | API routes (`routes/review.ts`) | 1.5 | Tasks 4, 5, 6 |
| 8 | OpenClaw `review-simulate` skill | 1.0 | Task 7 |
| 9 | Backlog integration for revision items | 0.5 | Task 5 |
| 10 | Test with reasoning-gaps paper | 2.0 | Tasks 1-8 |
| **Total** | | **~14.5 hours** | |

### Suggested implementation order

**Phase 1 — Personas and core simulation (Tasks 1-3, ~5.5 hours)**
Define personas, build the simulator, get individual reviews working. This is the highest-value piece — even without aggregation, individual simulated reviews are useful.

**Phase 2 — Prediction and prioritization (Tasks 4-6, ~4 hours)**
Aggregate reviews into actionable intelligence. Schema for persistence.

**Phase 3 — Integration and testing (Tasks 7-10, ~5 hours)**
API exposure, agent skills, and end-to-end testing with the reasoning-gaps paper.

## Success Criteria

1. **Simulated reviews identify at least 80% of weaknesses that real reviewers would find.** Measured by comparing simulated reviews against actual reviews after submission. This is a long-term calibration goal.

2. **Predicted acceptance probability is within 15% of actual outcome.** Over multiple submissions, the calibration curve should converge. Initial estimate: within 20% on first use, improving with each data point.

3. **Prioritized revision list is actionable.** Each item should be specific enough that a single agent session can address it. Test: can the writer agent take the top revision item and produce a meaningful edit in one session?

4. **Cost per simulation is predictable.** Target: $10-15 for 3-reviewer panel, $15-25 for 5-reviewer panel. Track actual costs and flag if they exceed 150% of target.

5. **Simulation latency under 5 minutes for a full 5-reviewer panel.** Reviews run in parallel; bottleneck is the slowest individual review.

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| LLM reviewers are too positive (sycophancy) | False confidence in paper quality | Anti-sycophancy prompting ("find reasons to reject"); score calibration against real reviews; require at least one weakness per review |
| Reviewers miss subtle flaws | Same as above | Use Opus 4.6 (highest capability); include verification report in reviewer context; test against papers with known weaknesses |
| Persona diversity insufficient | All reviews converge on same points | Ensure personas have genuinely different dispositions and expertise; vary temperature across reviewers |
| Cost overruns on long papers | Budget impact | Cap context to 30k tokens per review; summarize figures instead of including images; track and alert on cost |
| Over-optimization for simulated reviewers | Paper optimized for fake review but not real | Rotate persona definitions periodically; add noise to scoring; never reveal exact persona prompts to writing agents |

## Open Questions

1. **Should reviews be shown to the writer agent verbatim?** Risk: writer optimizes for simulated reviewer language. Alternative: only show the revision plan, not raw reviews. Current plan: show full reviews to the critic agent, only revision plan to the writer.

2. **How many simulation runs per paper?** Budget consideration. Proposal: 1 run after each major revision phase (3-5 runs total per paper), plus 1 final run before submission. At ~$15-25 per run, total cost is $60-125 per paper.

3. **Should we simulate the rebuttal?** After getting simulated reviews, simulate a rebuttal process where the author addresses concerns and reviewers update scores. This would better predict post-rebuttal outcomes. Current plan: out of scope for v1, add in v2 if the base system proves useful.

4. **Venue-specific calibration data?** The score-to-probability mapping is currently estimated. To calibrate properly, we need actual submission outcomes. Plan: start with estimates, log predictions as formal predictions in the `predictions` table, and update calibration as outcomes arrive.

## Future Extensions

- **Rebuttal simulation**: After initial reviews, generate an author response and have reviewers update their scores. Predicts post-rebuttal outcome.
- **Meta-review synthesis**: The area_chair persona synthesizes all reviews into a meta-review with an accept/reject recommendation, mimicking the actual AC workflow.
- **Reviewer assignment prediction**: Given the paper's topic and keyword profile, predict which reviewer types are most likely to be assigned. Weight the simulation accordingly.
- **A/B testing framing**: Run the same paper with different abstracts, introductions, or framings to see which version gets higher simulated scores. Guides revision decisions.
- **Multi-venue comparison**: Simulate reviews for multiple venues (NeurIPS, ICML, ACL) to find the best fit for the paper.
