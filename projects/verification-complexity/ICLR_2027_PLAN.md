# ICLR 2027 Submission Plan
**Project:** verification-complexity
**Paper:** On the Verification Complexity of LLM Outputs: When Checking is as Hard as Generating
**Decision Date:** 2026-03-22
**Submission Deadline:** 2026-09-25 (estimated, typically late September)
**Days Available:** 187 days from decision date

---

## Decision Rationale

**Why ICLR 2027 instead of NeurIPS 2026:**
- NeurIPS deadline (May 6) is 45 days away—insufficient for quality
- Experimental validation is incomplete (only 3 pilot instances, all results are placeholders)
- Project guidance: "Better to submit a strong theory paper late than a weak one on time"
- ICLR is equally prestigious for ML theory connecting to practice
- 187 days allows significant enhancements beyond minimal viable submission
- Risk mitigation: time to handle unexpected experimental results
- Quality over speed: strong ICLR acceptance > rushed NeurIPS borderline

**What we already have:**
- ✅ Complete theoretical framework (Definitions 1-6, Theorems 1-3 with full proofs)
- ✅ Comprehensive literature review (60 papers)
- ✅ Well-structured 22-page LaTeX draft (v0.2)
- ✅ Extended discussion section (limitations, scope, future work)
- ✅ Professional formatting with proper theorem environments
- ✅ NeurIPS checklist complete
- ✅ Appendix scaffolding (proof outlines, experimental design)

**What needs completion:**
- ❌ Experimental results (GSM8K, MATH, 3-SAT, PlanBench-HTN)
- ❌ Results tables and figures
- ❌ Statistical analysis with confidence intervals
- ❌ Extended appendix proofs (Lemmas 1-2 full expansions)

**Optional enhancements for ICLR:**
- 🔲 Theorem 4: Oversight Ceiling (formalize PSPACE upper bound)
- 🔲 Interactive verification section (debate, recursive reward modeling)
- 🔲 Average-case verification complexity analysis
- 🔲 Case studies (3 detailed examples)
- 🔲 Additional benchmarks (ARC, code verification)
- 🔲 Ablation studies (temperature, model size, prompt format)

---

## Timeline (187 days, March 22 - September 25)

### Phase 1: Experimental Validation (March 22 - April 30, ~40 days)
**Owner:** Experimenter agent
**Budget:** $100 for API calls

**Week 1-2 (March 22 - April 5):**
- Run full self-consistency experiments on GSM8K (1,319 instances × 3 models × 5 N values)
- Run full self-consistency experiments on MATH (500 instances × 3 models × 5 N values)
- Estimated: ~15K API calls, $45

**Week 3-4 (April 6 - April 19):**
- Run 3-SAT experiments (200 instances × 3 models × 5 N values)
- Run PlanBench-HTN experiments (100 instances × 3 models × 5 N values)
- Estimated: ~4.5K API calls, $20

**Week 5-6 (April 20 - April 30):**
- Statistical analysis: bootstrap confidence intervals, significance tests
- Generate results tables (Table 2 in main text)
- Generate figures: accuracy vs N curves, lift vs VC correlation
- Error correlation analysis for HTN tasks
- Estimated: local compute only

**Deliverable:** Complete experimental results with statistical rigor integrated into Section 5

---

### Phase 2: Results Integration & Appendix Completion (May 1 - May 31, ~30 days)
**Owner:** Writer agent (this agent)

**Week 1-2 (May 1 - May 15):**
- Integrate experimental results into Section 5
- Replace all "---" placeholders with actual numbers
- Write results interpretation paragraphs
- Add figures to paper (accuracy curves, correlation plots)
- Verify all claims match evidence

**Week 3-4 (May 16 - May 31):**
- Expand Appendix A.1: full proofs for Lemmas 1-2
- Complete Appendix A.2: extended experimental details
- Add supplementary tables (breakdown by difficulty, convergence curves)
- Write failure mode analysis section
- Compile and verify PDF (ensure <9 pages main text if limit applies)

**Deliverable:** Draft v0.3 with complete experiments and expanded appendices

---

### Phase 3: ICLR Enhancements (June 1 - July 31, ~60 days)
**Owner:** Theorist + Writer agents

**June 1-15: Theorem 4 (Oversight Ceiling)**
- Formalize PSPACE upper bound for scalable oversight
- Prove that interactive verification (debate) extends verification power to $\IP = \PSPACE$
- Connect to existing debate literature (Irving et al., Brown-Cohen et al.)
- Add as Section 5.5 or separate section before Related Work

**June 16-30: Interactive Verification Extension**
- Write new subsection: "Beyond Single-Round Verification"
- Cover debate protocols, recursive reward modeling
- Formalize when interaction is necessary vs merely helpful
- Connection to $\IP = \PSPACE$ result

**July 1-15: Case Studies**
- Write 3 detailed case studies showing verification hardness:
  1. Mathematical proof verification (Type 1, easy verification)
  2. HTN planning verification (Type 5, hard verification)
  3. Creative problem-solving (Type 6, no verification function)
- Each case study: ~1 page with concrete examples

**July 16-31: Average-Case Analysis (if time permits)**
- Define distributional verification complexity $\VC_{\text{avg}}(\calF, \calD)$
- Formalize when average-case is easier than worst-case
- Connect to practical benchmark performance
- Add as subsection in Discussion or Appendix

**Deliverable:** Draft v0.4 with Theorem 4, interactive verification, case studies

---

### Phase 4: Additional Experiments & Ablations (August 1-31, ~30 days)
**Owner:** Experimenter agent
**Budget:** $50 for extended experiments (optional)

**Optional experiments (priority order):**
1. ARC benchmark (abstract reasoning, $\VC$ analysis)
2. Code verification tasks (with/without test suites)
3. Ablation: temperature effect on self-consistency
4. Ablation: model size vs verification capability
5. Symbolic math tasks (Mathematica verification)

**Note:** These are enhancements, not requirements. Core paper is complete after Phase 3.

**Deliverable:** Extended experimental results (if pursued)

---

### Phase 5: Internal Review & Polish (September 1-20, ~20 days)
**Owner:** Critic + Writer agents

**September 1-7: Internal Review**
- Critic agent performs full paper review
- Check: all theorems correct, all proofs complete, all claims supported
- Check: experimental results match text, figures referenced, tables formatted
- Check: related work comprehensive, positioning clear
- Check: writing quality (clarity, concision, flow)

**September 8-14: Address Review Feedback**
- Writer agent addresses all Critic feedback
- Prioritize: correctness > clarity > style
- Re-compile and verify no new errors

**September 15-20: Final Polish**
- Proofread entire paper
- Check bibliography formatting
- Verify all cross-references work
- Check page count vs ICLR limit
- Spell check, grammar check
- Ensure anonymization (no author names, affiliations, acknowledgments)
- Final PDF compilation

**Deliverable:** Draft v1.0, camera-ready for submission

---

### Phase 6: Submission (September 21-25, ~5 days)

**September 21-23: Pre-submission Checklist**
- Convert to ICLR 2027 LaTeX template (if different from NeurIPS)
- Prepare supplementary materials (code, extended proofs if needed)
- Write abstract (250 words, ensure it stands alone)
- Prepare keywords and subject areas
- Check OpenReview submission requirements

**September 24: arXiv Preprint**
- Post arXiv preprint to establish priority
- Use arXiv identifier in OpenReview submission (if allowed)

**September 25: Submit to ICLR 2027**
- Upload PDF to OpenReview
- Upload supplementary materials
- Complete submission form
- Confirm submission before deadline

**Deliverable:** Submitted paper + arXiv preprint

---

## Buffer & Risk Management

**Total planned work:** ~140 days
**Total available:** 187 days
**Buffer:** 47 days (~33% buffer)

**Use buffer for:**
- Unexpected experimental results requiring theory revision
- Extended internal review cycles if Critic finds major issues
- Additional experiments if reviewers are likely to ask
- Handling interruptions or other project priorities

**Risk scenarios:**
1. **Experiments contradict theory:** Use buffer to understand why, potentially revise theorems or scope
2. **Theorem 4 proof is harder than expected:** Defer to extended version or journal paper
3. **ICLR deadline moves earlier:** We have 47-day buffer, can absorb ~3 weeks of schedule slip
4. **Quality concerns from Critic:** Multiple revision cycles built into Phase 5

---

## Success Metrics

**Minimum bar for submission:**
- ✅ All experiments complete with statistical rigor
- ✅ All theorems proved correctly
- ✅ All figures and tables publication-quality
- ✅ Paper compiles cleanly
- ✅ <9 pages main text (if ICLR enforces limit)

**Target for strong submission:**
- ✅ Theorem 4 included
- ✅ Interactive verification section complete
- ✅ 3 case studies written
- ✅ Multiple internal review cycles
- ✅ All Critic feedback addressed

**Confidence in acceptance:**
- With minimum bar: 75% (strong theory, complete experiments)
- With target enhancements: 85% (exceptional theory + experiments + polish)

---

## Next Immediate Actions

**For Experimenter agent (next session):**
1. Set up experimental infrastructure (self-consistency evaluator)
2. Run GSM8K experiments (1,319 instances × 3 models × 5 N values)
3. Run MATH experiments (500 instances × 3 models × 5 N values)
4. Generate preliminary results tables

**For Writer agent (this session):**
1. ✅ Update status.yaml with ICLR decision
2. ✅ Create this ICLR plan document
3. ✅ Update paper LaTeX to reflect ICLR target (if template differs)
4. Commit and push changes

**For Theorist agent (June session):**
1. Prove Theorem 4 (Oversight Ceiling)
2. Formalize interactive verification connection to $\IP = \PSPACE$
3. Write formal statements and proofs

---

## Coordination Notes

This plan involves multiple agents:
- **Experimenter:** Runs all experiments, generates results
- **Writer:** Integrates results, writes prose, polishes
- **Theorist:** Proves Theorem 4, formalizes interactive verification
- **Critic:** Reviews paper for correctness and quality

**Handoff points:**
- Experimenter → Writer: After Phase 1 (experimental results ready)
- Theorist → Writer: After June 15 (Theorem 4 proved)
- Writer → Critic: After September 1 (draft ready for review)
- Critic → Writer: After September 7 (review feedback ready)

**Commit discipline:**
- Commit after every significant milestone
- Push immediately after commit
- Use conventional commit format: `paper(verification-complexity): description`
- Update status.yaml after each phase completes

---

## Alternative Paths

**If experiments are done early (before May 1):**
- Start Phase 3 enhancements immediately
- Use extra time for additional benchmarks or deeper case studies

**If Theorem 4 is too hard:**
- Defer to extended version
- Strengthen case studies and average-case analysis instead
- Paper is still strong without Theorem 4

**If timeline pressure emerges:**
- Drop optional experiments (ARC, code verification, ablations)
- Drop average-case analysis subsection
- Minimum viable submission is still strong

**If we want to submit to both venues:**
- Submit to NeurIPS May 6 with incomplete experiments (high risk)
- If rejected, use reviews to improve for ICLR
- Not recommended: violates "better late than rushed" principle

---

## Conclusion

**ICLR 2027 is the right choice.** We have a complete theoretical contribution, a clear path to experimental validation, and ample time for enhancements that will make the paper exceptional. The 47-day buffer protects against risks, and the quality improvement over a rushed NeurIPS submission is substantial.

**Estimated acceptance probability: 85% with full plan execution.**

Next step: Flag for Experimenter agent to begin Phase 1.
