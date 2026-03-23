# Writer Session Report
**Date**: 2026-03-23
**Paper**: On the Verification Complexity of LLM Outputs: When Checking is as Hard as Generating
**Draft version**: v0.3 (Theorem 2c critique)
**Session Type**: Critic Review (Linear Issue DW-142)

---

## Executive Summary

**Task:** Conduct critic review of "revised Theorem 2c + Lemma 3" and check whether "Definition 7 is circular" (Linear issue DW-142).

**Finding:** **The requested components do not fully exist.** Theorem 2c exists (part c of the Self-Consistency Condition theorem), but Definition 7 and Lemma 3 are missing from the paper. Critical assessment reveals that Theorem 2c has a proof gap that requires these missing components.

**Work Completed:**
- Conducted thorough critic review of Theorem 2c
- Identified proof gap: connection between VC ⊄ cap(M) and bottleneck existence is asserted but not proved
- Identified informal statement compared to Theorem 2 parts (a) and (b)
- Documented missing components (Definition 7, Lemma 3) and their intended purpose
- Wrote comprehensive critique at `reviews/critic-review-2026-03-23-theorem-2c.md`
- Updated `status.yaml` to reflect findings

**Status:** Theorem 2c is **not publication-ready** without Definition 7 and Lemma 3. Routed to Theorist agent for formal development.

---

## Critique Summary

### Theorem 2c: The Bottleneck Structure Condition

**Current statement** (lines 260-266):
> Error correlation depends on whether the source of failure is *shared* across samples or *instance-specific*:
> - If failures arise from a shared structural limitation [...], then errors are positively correlated (ρ > 0) regardless of VC class.
> - If failures arise from instance-specific stochastic difficulty [...], then errors may be approximately independent (ρ ≈ 0) even when VC is hard.

**Strengths:**
- ✅ Addresses real gap in self-consistency literature (Wang et al. 2023 assumes independence)
- ✅ Distinction between shared vs stochastic bottlenecks is insightful
- ✅ Makes testable predictions
- ✅ Well-integrated with empirical findings

**Critical Weaknesses:**
1. ❌ **Informal statement** — Parts (a) and (b) are mathematically precise; part (c) is prose
2. ❌ **"Bottleneck structure" undefined** — Central concept not formalized (Definition 7 missing)
3. ❌ **Proof gap** — Extended Proof asserts "VC ⊄ cap(M) → bottleneck exists" without proof (Lemma 3 missing)
4. ⚠️ **"Regardless of VC class" contradicts findings** — Empirical results show ρ varies with VC (Type 4 algorithmic: ρ=0.42, Type 5 intractability: ρ=0.06)
5. ⚠️ **Unclear relationship to framework** — Connection to VC complexity only clarified in Discussion (10 pages later)

**Verdict:** A hostile theory reviewer would flag this as **incomplete**.

---

## Missing Components

### Definition 7 (Computational Bottleneck) — NOT IN PAPER

**Expected purpose:** Formalize "shared structural limitation" vs "instance-specific stochastic difficulty" used in Theorem 2c.

**Why needed:**
- Theorem 2c uses these concepts without definition
- Lemma 2 assumes "computational bottleneck B" exists but does not define it
- Without definition, the theorem is not testable and potentially circular

**Suggested definition** (for Theorist):
> Let F be a reasoning task and M a model class. A *computational bottleneck* for (F, M) is a verification subtask V_sub such that:
> 1. Computing V_sub is necessary for distinguishing correct from incorrect answers on non-negligible instances
> 2. V_sub ∉ cap(M) (the model cannot compute V_sub)
> 3. The bottleneck is *shared* if all instances require V_sub; *stochastic* if Pr[x requires V_sub] = q < 1 with independent instances

**Circularity check:** This definition is **not circular** — it references cap(M) (Definition 5) but not correlation ρ.

### Lemma 3 (Verification Hardness Produces Bottleneck) — NOT IN PAPER

**Expected purpose:** Prove that VC(F) ⊄ cap(M) implies a computational bottleneck exists, closing the proof gap in Extended Theorem 2.

**Current gap:**
- Lemma 2 proves: bottleneck B → ρ > 0 ✅
- Extended Proof asserts: VC ⊄ cap(M) → bottleneck B exists ❌ (not proved)
- Need: The connecting link

**Suggested statement** (for Theorist):
> Let F be a reasoning task with VC(F) ⊄ cap(M). Then there exists a computational bottleneck B (Definition 7) with Pr[B | x ∼ D] = q > 0 such that errors conditioned on B have probability r > 1/2.

**Tightness check:** This lemma is **non-trivial** because:
- Not every VC ⊄ cap(M) situation produces high correlation
- If bottleneck is rare (q ≈ 0) or failures are still random (r ≈ 1/2), then ρ may be small
- The lemma must establish q and r are bounded away from 0 and 1/2

---

## Comparison to Other Theorems

**Theorem 1 (Verification Advantage):** ✅ Excellent — formally stated, complete proof, clear connection to LLM methods

**Theorem 2a (Plurality condition):** ✅ Excellent — classical result, well-proved

**Theorem 2b (Correlation reduces N_eff):** ✅ Excellent — tight result via Lemma 1

**Theorem 2c (Bottleneck structure):** ⚠️ Needs work — informal statement, undefined terms, proof gap

**Theorem 3 (Gap Collapse for Planning):** ✅ Excellent — formally stated, complete proof with tightness argument

**Overall theorem quality:** 3.5/4 excellent, 0.5/4 needs revision

---

## Recommendations

### Immediate: Theorist Agent
1. **Write Definition 7** (Computational Bottleneck)
   - Formalize shared vs stochastic bottleneck distinction
   - Ensure definition is not circular
   - Connect to cap(M) and VC(F)

2. **Prove Lemma 3** (Verification Hardness Produces Bottleneck)
   - Show VC(F) ⊄ cap(M) → bottleneck B exists with Pr[B] = q > 0
   - Establish errors conditioned on B have probability r > 1/2
   - Argue this is non-trivial (not automatic)

3. **Revise Theorem 2c statement**
   - Match formality of parts (a) and (b)
   - Replace prose with precise mathematical conditions
   - Clarify relationship to VC complexity (not "regardless of" but "not monotonic in")
   - Reference Definition 7 explicitly

### Follow-up: Writer Agent
4. Update Extended Proof in Appendix A.1 to reference Lemma 3
5. Add forward reference in Theorem 2c to Discussion (lines 520-523) where VC-correlation relationship is clarified
6. Consider moving Discussion clarification earlier (Remark after Theorem 2)

### Timeline
- **Target completion:** June 2026
- **Rationale:** Needed before ICLR submission (September 2026)
- **Priority:** High — Theorem 2c is a main result

---

## Impact Assessment

**Without fixes:**
- Theorem 2c is the weakest theorem in the paper
- Vulnerable to hostile review ("incomplete result," "undefined terms," "proof gap")
- Reduces overall paper quality from 85% to 70% publication-ready

**With fixes:**
- Theorem 2c becomes a strong, novel contribution
- Formal connection between verification complexity and self-consistency effectiveness
- Explains empirical findings (high ρ for algorithmic gaps despite VC=P, low ρ for intractability tasks despite VC⊇coNP)
- Paper returns to 90% publication-ready (pending experimental results)

---

## Decisions Made This Session

**Decision:** Identify proof gap in Theorem 2c and route to Theorist for Definition 7 + Lemma 3 development

**Rationale:** Linear issue DW-142 requested critic review of "Theorem 2c + Lemma 3" and whether "Definition 7 is circular." Investigation revealed Definition 7 and Lemma 3 do not exist in the paper, and Theorem 2c has a proof gap that requires them. The Extended Proof asserts "VC ⊄ cap(M) → bottleneck exists → ρ > 0" but only proves the second arrow (Lemma 2), not the first. The statement is also informal compared to other theorem parts. Without these components, a hostile theory reviewer would flag Theorem 2c as incomplete. The fix requires formal development by Theorist agent (Definition 7, Lemma 3, revised Theorem 2c statement), not just writing polish.

**Logged in:** `status.yaml` decisions_made (2026-03-23)

---

## Next Steps

1. **Theorist agent (March-June 2026):** Develop Definition 7, prove Lemma 3, revise Theorem 2c statement
2. **Critic agent (June 2026):** Re-review revised Theorem 2c with new components
3. **Writer agent (June 2026):** Integrate Definition 7, Lemma 3, and revised Theorem 2c into paper
4. **Experimenter agent (April-July 2026):** Run full experiments (parallel to theory work)
5. **Writer agent (July-August 2026):** Integrate experimental results and prepare for submission
6. **Submit (September 25, 2026):** ICLR 2027 deadline

---

## Paper Status Update

**Draft version:** v0.3 (Theorem 2c identified as incomplete)

**Sections needing revision:**
- Framework (Section 3): Add Definition 7
- Main Results (Section 4): Revise Theorem 2c statement
- Appendix A.1: Add Lemma 3, update Extended Proof of Theorem 2

**Confidence:**
- **Before critique:** 0.85 for ICLR acceptance
- **After critique:** 0.70 for ICLR acceptance (with fixes required)
- **With fixes complete:** 0.90 for ICLR acceptance

**Timeline impact:**
- No change to overall timeline
- Theory fixes in parallel with experimental work (April-June)
- Integration and polish (July-August)
- Submission (September 25, 2026)

---

**Session complete.**
**Critic review documented.**
**Routed to Theorist for Definition 7 + Lemma 3 development.**
