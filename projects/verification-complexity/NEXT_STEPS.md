# Verification-Complexity: Next Steps
**Updated**: 2026-03-24
**Project Health**: EXCELLENT (see META_REVIEW_2026-03-24.md)
**Timeline**: 185 days to ICLR 2027 submission (September 25, 2026)

---

## Work Streams

Two parallel, independent work streams:

### Stream 1: Theory Completion (Theorist)
**Blocks**: Paper completeness (Theorem 2c incomplete)
**Priority**: HIGH
**Owner**: Theorist agent
**Duration**: 1-2 weeks calendar time (2-3 focused sessions)

### Stream 2: Experiment Execution (Critic → Experimenter → Writer)
**Blocks**: Section 5 experimental results
**Priority**: HIGH
**Owner**: Critic (approval), then Experimenter (execution), then Writer (integration)
**Duration**: Critic 2h, Experimenter 12h runtime, Writer 2h

---

## Stream 1: Theory Completion (THEORIST)

### Context
Theorem 2c (Self-Consistency Condition, part c) has a proof gap identified in critic review 2026-03-23:
- Statement is informal compared to parts (a) and (b)
- Key term "bottleneck structure" is undefined
- Proof asserts "VC ⊄ cap(M) → bottleneck exists" without proving it
- Missing: Definition 7 and Lemma 3

### Task 1.1: Write Definition 7 (Computational Bottleneck)

**Input**:
- reviews/critic-review-2026-03-23-theorem-2c.md (lines 130-150)
- paper/main.tex (Theorem 2c at lines 260-266)

**Requirements**:
1. Formalize "shared structural limitation" vs "instance-specific stochastic difficulty"
2. Define conditions for when a verification subtask qualifies as a bottleneck
3. Distinguish "shared" bottleneck (all instances require it) from "stochastic" bottleneck (Pr[required]=q<1)
4. Ensure definition is NOT circular (does not reference correlation ρ)
5. Ensure definition is upstream of Theorem 2c (can be used in proof)

**Suggested structure** (from critic review):
```
Definition 7 (Computational Bottleneck)
Let F be a reasoning task and M a model class. A computational bottleneck
for (F, M) is a verification subtask V_sub: X × Y → {0,1} such that:
1. Computing V_sub is necessary for distinguishing correct from incorrect
   answers on a non-negligible fraction of inputs
2. V_sub ∉ cap(M) (the model cannot compute V_sub)
3. The bottleneck is:
   - *shared* if all instances x ∼ D require V_sub
   - *stochastic* if Pr[x requires V_sub] = q < 1 and instances are independent
```

**Deliverable**: Formal definition ready for paper integration

---

### Task 1.2: Prove Lemma 3 (Verification Hardness Produces Bottleneck)

**Input**:
- reviews/critic-review-2026-03-23-theorem-2c.md (lines 151-179)
- Definition 7 (from Task 1.1)
- paper/main.tex (Extended Proof at lines 823-869)

**Requirements**:
1. Prove: If VC(F) ⊄ cap(M), then there exists a computational bottleneck B (Definition 7) with Pr[B | x ∼ D] = q > 0
2. Establish: Errors conditioned on B have probability r > 1/2
3. Show this is **non-trivial** (not automatic from VC hardness)
4. Connect worst-case VC hardness to average-case error correlation

**Suggested statement** (from critic review):
```
Lemma 3 (Verification Hardness Produces Bottleneck)
Let F be a reasoning task with VC(F) ⊄ cap(M). Then there exists a
computational bottleneck B (Definition 7) occurring with probability
Pr[B | x ∼ D] = q > 0 such that samples conditioned on B have error
probability r > 1/2.
```

**Proof sketch**:
- Since VC(F) ⊄ cap(M), there exists a verification computation V that M cannot perform
- For instances x where V is required, M cannot verify its output
- This produces systematic errors: M fails on same instances regardless of sampling
- These instances constitute bottleneck B with Pr[B] = q > 0

**Deliverable**: Complete formal proof with all steps justified

---

### Task 1.3: Revise Theorem 2c Statement

**Input**:
- Definition 7 (from Task 1.1)
- Lemma 3 (from Task 1.2)
- reviews/critic-review-2026-03-23-theorem-2c.md (lines 47-93)

**Requirements**:
1. Match formality of Theorem 2 parts (a) and (b)
2. Reference Definition 7 explicitly
3. Clarify relationship to VC complexity (not "regardless of" but "not monotonic in")
4. Replace prose with precise mathematical conditions

**Current statement** (informal):
> (c) (Bottleneck structure) Error correlation depends on whether the source
> of failure is shared across samples or instance-specific: [prose continues...]

**Suggested revision** (formal):
> (c) (Bottleneck structure) Let B be a computational bottleneck (Definition 7)
> for (F, M). If B is shared with Pr[B | x ∼ D] = q > 0, then by Lemma 3,
> error correlation ρ ≥ q²(r - 1/2)² > 0 where r is the error probability
> conditioned on B. For within-model sampling at fixed temperature, shared
> bottlenecks dominate (q ≈ 1), producing ρ > 0 independent of stochastic
> instance difficulty.

**Deliverable**: Revised theorem statement ready for paper integration

---

### Task 1.4: Update Extended Proof

**Input**:
- Lemma 3 (from Task 1.2)
- paper/main.tex (Extended Proof at lines 823-869)

**Requirements**:
1. Replace assertion "VC ⊄ cap(M) → bottleneck exists" with "by Lemma 3"
2. Connect all proof steps explicitly (no gaps)
3. Ensure proof flows: VC hardness → Lemma 3 → bottleneck exists → Lemma 2 → ρ > 0

**Deliverable**: Updated proof ready for Writer integration

---

### Success Criteria for Stream 1

- [ ] Definition 7 is formal, non-circular, and usable in proofs
- [ ] Lemma 3 has a complete proof with all steps justified
- [ ] Theorem 2c statement matches formality of parts (a) and (b)
- [ ] Extended Proof has no gaps (all connections proved)
- [ ] A hostile theory reviewer would accept the revised theorem

**When complete**: Flag Writer agent to integrate Definition 7 + Lemma 3 into paper

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

| Milestone | Owner | Duration | Deadline |
|-----------|-------|----------|----------|
| Definition 7 + Lemma 3 | Theorist | 1-2 weeks | April 14 |
| Critic review spec | Critic | 2 hours | April 1 |
| Execute experiment | Experimenter | 12h runtime | April 7 |
| Analyze + figures | Experimenter | 2 hours | April 8 |
| Integrate results | Writer | 2 hours | April 9 |
| Integrate theory | Writer | 4 hours | April 16 |
| Internal review | Critic | 1 day | May 1 |
| Final polish | Writer | 1 week | June 1 |
| **Paper complete** | — | — | **June 1, 2026** |
| arXiv preprint | — | — | August 15, 2026 |
| **ICLR submission** | — | — | **September 25, 2026** |

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
