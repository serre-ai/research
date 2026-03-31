# Verification-Complexity: Next Steps
**Updated**: 2026-03-30
**Project Health**: EXCELLENT
**Timeline**: 179 days to ICLR 2027 submission (September 25, 2026)

---

## Work Streams

### Stream 1: Theory Completion -- COMPLETE (2026-03-30)
**Status**: DONE
**Deliverables**: All integrated into `paper/main.tex`
- Definition 7 (Computational Bottleneck) -- formal, non-circular, shared/stochastic distinction
- Assumption (Distributional Verification Hardness) -- bridges worst-case to average-case
- Lemma 3 (Verification Hardness Produces Bottleneck) -- complete 5-step proof
- Theorem 2c revised -- three sub-parts (c.i/c.ii/c.iii) matching formality of parts (a)/(b)
- Extended Proof updated -- explicit logical chain with no gaps
- Remark on VC-correlation non-monotonicity -- connects theory to empirical findings
- Lemma 2 reworded -- references Definition 7 formally
- Discussion paragraph updated -- references Remark and Definition 7

All five critic review weaknesses (W1-W5) addressed. Theory is publication-ready.

### Stream 2: Experiment Execution (Critic -> Experimenter -> Writer)
**Blocks**: Section 5 experimental results
**Priority**: HIGH (now the ONLY remaining blocker)
**Owner**: Critic (approval), then Experimenter (execution), then Writer (integration)
**Duration**: Critic 2h, Experimenter 12h runtime, Writer 2h

---

## Stream 2: Experiment Execution (CRITIC → EXPERIMENTER → WRITER)

### Task 2.1: Critic Review of Experiment Spec (CRITIC)

**Input**: experiments/cross-model-verification/spec.yaml (status=draft)

**Requirements**:
Review against 6 criteria (from spec.yaml):
1. ✅ Predictions are specific and falsifiable (checked in spec)
2. ✅ Design conditions match theoretical framework (Table 1) (checked in spec)
3. ✅ Sample size sufficient for statistical power (n=50 per task, 9 tasks) (checked in spec)
4. ✅ Pre-registered analyses prevent p-hacking (6 analyses listed) (checked in spec)
5. ✅ Budget is reasonable ($38, validated by canary $0.10/50 = $0.002/call) (checked in spec)
6. ✅ Canary diagnostics passed (B4=100%, B7=64%, 36pp gap, p<0.001) (checked in spec)

**Action**:
- If all criteria pass: Update spec.yaml with `review.status: approved` and `review.date: YYYY-MM-DD`
- If issues found: Update spec.yaml with `review.status: rejected` and `review.notes: [issues]`

**Deliverable**: spec.yaml with updated review.status

**Duration**: 1-2 hours

---

### Task 2.2: Execute Full Experiment (EXPERIMENTER, after approval)

**Input**:
- experiments/cross-model-verification/spec.yaml (status=approved)
- experiments/cross_model_verification.py

**Budget**: $38 (4,050 verifications at $0.002 each, validated by canary)

**Command**:
```bash
cd projects/verification-complexity/experiments

# Dry run to verify cost estimate
python cross_model_verification.py --dry-run

# Full run with resume support
python cross_model_verification.py \
  --generators haiku,gpt4o,llama70b \
  --verifiers haiku,sonnet,gpt4o-mini \
  --tasks B1,B2,B3,B4,B5,B6,B7,B8,B9 \
  --instances-per-difficulty 10 \
  --prompt-variant answer_only \
  --resume
```

**Monitoring**:
- Cost tracking: log cumulative cost every 100 calls
- Progress: log completion % every 500 calls
- Errors: retry transient failures, log persistent failures
- Checkpointing: atomic append to JSONL, resumable from any point

**Output**:
- 9 JSONL files: experiments/results/verify_{gen}_by_{ver}_answer_only.jsonl
- Total: 4,050 verification records

**Duration**: ~12 hours runtime (can run in background)

---

### Task 2.3: Analyze Results and Generate Figures (EXPERIMENTER)

**Input**: experiments/results/verify_*.jsonl (from Task 2.2)

**Commands**:
```bash
# Run full analysis (implements all 6 pre-registered analyses)
python analyze_verification_results.py \
  --results experiments/results/verify_*.jsonl \
  --output experiments/results/full_analysis.json

# Generate publication-ready figures
python generate_figures.py \
  --analysis experiments/results/full_analysis.json \
  --output experiments/results/figures/
```

**Pre-registered analyses** (from spec.yaml):
1. Verification accuracy by VC class (ANOVA)
2. Cross-model consistency within VC class (ICC)
3. Error type breakdown (false pos vs neg)
4. Difficulty scaling (linear regression)
5. Latency by VC class (Kruskal-Wallis)
6. Generator-verifier interaction (two-way ANOVA)

**Output**:
- experiments/results/full_analysis.json (statistical results)
- experiments/results/figures/fig1_accuracy_by_vc_class.pdf
- experiments/results/figures/fig2_accuracy_heatmap.pdf

**Duration**: ~2 hours

---

### Task 2.4: Integrate Results into Paper (WRITER)

**Input**:
- experiments/results/full_analysis.json
- experiments/results/figures/*.pdf
- paper/main.tex (Section 5 at lines 350-420)

**Requirements**:
1. Fill Table 2 (verification accuracy by task × model) with actual results
2. Add Figure 1 (accuracy by VC class) to paper
3. Add Figure 2 (accuracy heatmap) to paper
4. Write results prose in Section 5 (2-3 paragraphs)
5. Update Discussion section with any unexpected findings
6. Update Appendix A.2 with supplementary tables

**Deliverable**: Paper Section 5 complete with experimental results

**Duration**: ~2 hours

---

### Success Criteria for Stream 2

- [ ] Critic has approved experiment spec (spec.yaml status=approved)
- [ ] Full experiment executed successfully (4,050 verifications, $38 spent)
- [ ] Statistical analysis complete (full_analysis.json generated)
- [ ] Figures 1-2 generated in publication-ready format
- [ ] Paper Section 5 complete with results
- [ ] Results support theoretical predictions (or discrepancies explained)

**When complete**: Paper is 95% complete (pending Theory Stream 1 and final polish)

---

## Post-Completion: Integration and Polish (MAY-JUNE 2026)

Once both streams complete:

1. **Writer**: Integrate Definition 7 + Lemma 3 from Stream 1
2. **Writer**: Ensure coherence between theory (Section 4) and experiments (Section 5)
3. **Critic**: Full paper review (all sections, coherence, polish)
4. **Writer**: Address critic feedback
5. **Writer**: Final polish (figures, bibliography, formatting)

**Target completion**: Mid-June 2026 (3 months before ICLR submission)

---

## Timeline

| Milestone | Owner | Duration | Deadline | Status |
|-----------|-------|----------|----------|--------|
| Definition 7 + Lemma 3 | Theorist | 1 session | March 30 | DONE |
| Critic review spec | Critic | 2 hours | April 7 | PENDING |
| Execute experiment | Experimenter | 12h runtime | April 14 | PENDING |
| Analyze + figures | Experimenter | 2 hours | April 15 | PENDING |
| Integrate results | Writer | 2 hours | April 16 | PENDING |
| Internal review | Critic | 1 day | May 1 | PENDING |
| Final polish | Writer | 1 week | June 1 | PENDING |
| **Paper complete** | -- | -- | **June 1, 2026** | |
| arXiv preprint | -- | -- | August 15, 2026 | |
| **ICLR submission** | -- | -- | **September 25, 2026** | |

**Buffer**: 3.5 months between completion and submission (comfortable)

---

## Orchestrator Instructions

### Trigger Theorist Session
**Condition**: Stream 1 blocking Theorem 2c completeness
**Input**: reviews/critic-review-2026-03-23-theorem-2c.md
**Objective**: Write Definition 7 + prove Lemma 3 + revise Theorem 2c
**Duration**: 2-3 sessions
**Priority**: HIGH

### Trigger Critic Session
**Condition**: experiments/cross-model-verification/spec.yaml status=draft
**Input**: spec.yaml
**Objective**: Review and approve/reject experiment spec
**Duration**: 2 hours
**Priority**: HIGH

### Trigger Experimenter Session (after approval)
**Condition**: spec.yaml status=approved
**Budget**: $38
**Objective**: Execute full cross-model verification + analyze + generate figures
**Duration**: ~14 hours (can run in background)
**Priority**: HIGH

### Trigger Writer Session (after both streams)
**Condition**: Theory fixes complete AND experimental results available
**Input**: Definition 7, Lemma 3, full_analysis.json, figures
**Objective**: Integrate all components into paper
**Duration**: 6 hours
**Priority**: HIGH

---

## Contact Points

- **Questions about theory**: Read reviews/critic-review-2026-03-23-theorem-2c.md (comprehensive)
- **Questions about experiments**: Read experiments/EXPERIMENT_STATUS.md (complete guide)
- **Questions about project health**: Read META_REVIEW_2026-03-24.md (detailed analysis)
- **Questions about paper**: Read paper/main.tex + status.yaml paper_status section

---

**Document maintained by**: Researcher agent
**Last updated**: 2026-03-24
**Next review**: After completion of Stream 1 or Stream 2
