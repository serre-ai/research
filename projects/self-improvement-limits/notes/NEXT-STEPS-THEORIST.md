# Next Steps for Theorist Agent

## Project Context
This project aims to prove formal impossibility results for unsupervised self-improvement in language models. The core claim is that self-improvement without external verification converges to a fixed point bounded by the model's initial verification capability.

**Current status**: Project initialized (2026-03-22)
**Your role**: Develop the formal framework and prove the core theorems

## Immediate Tasks

### Task 1: Read Background Material
Before starting formalization, understand the landscape:

1. **Read project files**:
   - `BRIEF.md` - Project goals and contribution claims
   - `status.yaml` - Current state
   - `CLAUDE.md` - Agent-specific instructions

2. **Review backlog description**: `docs/ideas/backlog.yaml` lines 61-87 for original conception

3. **Wait for literature survey** (optional but recommended): The Researcher agent should conduct a literature survey first. You can proceed without it, but knowing existing impossibility results helps position our contributions.

### Task 2: Formalize Self-Improvement Processes
**Deliverable**: `notes/formal-framework.md`

You need to formalize three types of self-improvement:

#### 2.1: Self-Training
Formalize the iterative process where a model trains on its own generated outputs:
- Model \(\M_t\) generates data \(\D_t\)
- Model evaluates/filters data using verification capability
- Model trains on filtered data to produce \(\M_{t+1}\)

**Questions to answer**:
- How to formalize "verification capability"? Options:
  - Information-theoretic: \(\Ver(\M)\) as mutual information about ground truth
  - Computational: \(\Ver(\M)\) as accuracy on verification tasks
  - Game-theoretic: \(\Ver(\M)\) as Nash equilibrium in verification game
- How to define "generation capability"?
  - \(\Gen(\M)\) as expected quality of generated outputs
  - Connection to \(\Ver\): generation is "easier" than verification for many tasks
- What assumptions are minimal?
  - Stochastic models? Deterministic?
  - Fixed computational budget? Arbitrary?

**Suggested approach**:
Start with simple formalization (e.g., discrete task space, binary verification), prove results, then generalize if needed.

#### 2.2: Self-Refinement
Formalize iterative refinement where model improves own outputs:
- Model generates initial output
- Model critiques and refines
- Iterate until convergence

This differs from self-training - same model refines rather than training new model on data.

**Key question**: Is self-refinement a special case of self-training, or does it need separate formalization?

#### 2.3: Self-Play
Formalize game-based self-improvement:
- Two copies of model play a game
- Outcomes determine training signal
- No external evaluator

**Key insight to formalize**: Self-play can work when game provides implicit verification (e.g., chess - outcomes are objective).

### Task 3: Define Verification-Generation Gap
**Deliverable**: Section in `notes/formal-framework.md`

Formalize the gap between verification difficulty and generation difficulty:
- For task \(x\), define \(\Ver(x)\) = difficulty of verifying solution
- For task \(x\), define \(\Gen(x)\) = difficulty of generating solution
- Gap: \(\Gen(x) - \Ver(x)\)

**Key property**: For many tasks, verification is easier than generation (e.g., checking a proof vs finding a proof).

**Questions**:
- How to measure difficulty? Computational complexity? Sample complexity?
- How does gap evolve during self-improvement?
- Can self-improvement reduce the gap, or is it invariant?

### Task 4: Prove Core Theorems
**Deliverable**: `notes/proofs.md`

After formalizing the framework, prove these results:

#### Theorem 1: Fixed-Point Convergence
**Claim**: Self-training without external verification converges to a fixed point.

**Formal statement** (sketch, you'll refine):
> Let \(\M_0\) be the initial model, and \(\M_{t+1} = \T(\M_t, \D_{\M_t})\) where \(\D_{\M_t}\) is generated and filtered by \(\M_t\). Then \(\exists t^*\) such that \(\M_{t^*} = \M_{t^*+1}\) (or \(\|\M_{t^*} - \M_{t^*+1}\| < \epsilon\)).

**What to prove**:
- Existence of fixed point
- Convergence to fixed point (under what assumptions?)
- Uniqueness? (May not hold - could have multiple fixed points)

**Proof approach ideas**:
- Banach fixed-point theorem (need contraction mapping)
- Monotone convergence (need partial order on models)
- Lyapunov function (need some notion of "energy" that decreases)

#### Theorem 2: Verification Bounds Capability Gain
**Claim**: The fixed point is bounded by initial verification capability.

**Formal statement** (sketch):
> Let \(\M_0\) be the initial model with verification capability \(\Ver(\M_0)\). Let \(\M_\infty\) be the fixed point of self-training. Then \(\Gen(\M_\infty) \leq \Ver(\M_0) + \epsilon\) for some \(\epsilon\) depending on training procedure.

**What to prove**:
- Upper bound on \(\Gen(\M_\infty)\) in terms of \(\Ver(\M_0)\)
- Characterize \(\epsilon\) - when is it small? When large?
- Is bound tight? (Construct example achieving bound)

**Key insight**: Model cannot learn to generate things it cannot verify, because it cannot select better training data than it can verify.

**Proof approach ideas**:
- Information-theoretic: Training data has limited mutual information with ground truth, bounded by \(\Ver(\M_0)\)
- Computational: Verification is the bottleneck in feedback loop
- Inductive: If \(\Gen(\M_t) > \Ver(\M_t)\), then filtering introduces errors, degrading \(\Gen(\M_{t+1})\)

#### Theorem 3: Gap Determines Ceiling
**Claim**: The verification-generation gap determines maximum achievable improvement.

**Formal statement** (sketch):
> For task distribution with gap \(g = \E[\Gen(x) - \Ver(x)]\), self-improvement is limited: \(\Gen(\M_\infty) - \Gen(\M_0) \leq f(g, \Ver(\M_0))\) for some function \(f\).

**What to prove**:
- Express ceiling on improvement as function of gap
- Characterize \(f\) - how does improvement scale with gap?
- When is gap bridgeable vs unbridgeable?

#### Theorem 4: Self-Play Requires Implicit Verification
**Claim**: Self-play exceeds self-training bounds only when game provides verification.

**Formal statement** (sketch):
> Let \(G\) be a game, \(\M_0\) the initial model, \(\M_\infty\) the limit of self-play. If \(\Gen(\M_\infty) > \Ver(\M_0) + \epsilon\), then \(G\) has property \(P\) (objective outcomes that provide verification signal).

**What to prove**:
- Characterize property \(P\) - what game structures provide verification?
- Show games without \(P\) reduce to self-training (same bounds)
- Show games with \(P\) can exceed bounds (constructive example)

**Examples to formalize**:
- Chess: Has \(P\) (win/loss is objective)
- Creative writing: Lacks \(P\) (quality is subjective, requires verification capability)
- Theorem proving: Has \(P\) (proof checking is easier than proof finding)

### Task 5: Write Proof Sketches
**Deliverable**: Sections in `notes/proofs.md`

For each theorem:
1. **Intuition**: 2-3 paragraphs explaining the key idea in plain language
2. **Formal statement**: Precise theorem statement with all assumptions explicit
3. **Proof sketch**: Main proof steps, key lemmas, overall strategy
4. **Full proof**: Complete rigorous proof (this will go in paper appendix)

**Quality bar**:
- Every assumption must be stated explicitly
- Every step must be justified
- Proof should be verifiable by expert reader
- If you're not sure a step is correct, mark it with "TODO: verify"

## Recommended Approach

### Phase 1: Simple Case (2-3 sessions)
Start with the simplest possible formalization:
- Binary classification tasks (correct/incorrect)
- Deterministic models
- Perfect verification on training distribution
- Finite task space

Prove Theorems 1-2 in this simple case first. This builds intuition and tests whether proof techniques work.

### Phase 2: Generalization (3-5 sessions)
Extend to more realistic settings:
- Continuous quality scores
- Stochastic models
- Imperfect verification
- Infinite task spaces

Prove that results from Phase 1 still hold (possibly with modified bounds).

### Phase 3: Self-Play (2-3 sessions)
Add game-theoretic formalization for self-play (Theorem 4). This may require different proof techniques (Nash equilibrium, game theory).

### Phase 4: Gap Characterization (2-3 sessions)
Characterize verification-generation gap (Theorem 3) and prove how it determines ceiling.

## Expected Challenges

1. **Defining verification capability formally**: This is not standard in ML theory. You may need to develop new definitions.

2. **Proving convergence**: Fixed-point theorems often require strong assumptions (contraction mapping, compactness). Can we prove convergence with realistic assumptions?

3. **Tightness of bounds**: Proving upper bounds is often easier than proving they're tight. You may need to construct adversarial examples.

4. **Self-play is different**: Game-theoretic analysis may require different techniques than supervised learning analysis.

5. **Connection to practice**: Theorems should connect to real self-improvement methods (STaR, ReST), not just abstract processes.

## Deliverables Checklist

- [ ] `notes/formal-framework.md` - Complete formalization
- [ ] `notes/proofs.md` - All theorem statements and proofs
- [ ] `notes/notation.md` - Notation table (what each symbol means)
- [ ] `notes/assumptions.md` - Discussion of assumptions and when they hold
- [ ] `notes/examples.md` - Worked examples illustrating theorems
- [ ] Update `status.yaml` - Mark theoretical framework complete
- [ ] Update `paper/main.tex` - Add notation commands for new symbols

## Questions to Resolve

These are research questions you'll need to answer:

1. **Information-theoretic vs computational**: Should impossibility results be based on information theory (Shannon entropy, mutual information) or computational complexity (P vs NP style)? Or both?

2. **Distributional assumptions**: Do we assume IID data? Adversarial distribution? Does it matter?

3. **Model class**: Should we prove results for all models, or specific classes (linear, neural networks)? Broader is better, but may be harder to prove.

4. **Verification oracle**: In practice, models have imperfect verification. Should we assume perfect verification and prove impossibility even in that idealized case? Or model imperfect verification?

5. **Positive results**: Should we include constructive results showing when self-improvement IS possible (e.g., with verification oracle, or for specific task distributions)?

## Resources

### Related ML theory
- PAC learning: Valiant (1984), VC dimension, sample complexity
- No-free-lunch: Wolpert & Macready (1997)
- Online learning regret bounds: Cesa-Bianchi & Lugosi
- Impossibility in active learning: Dasgupta (2005)

### Game theory for self-play
- Fictitious play convergence: Robinson (1951), Fudenberg & Levine
- Nash equilibrium existence: Nash (1950)
- Repeated games: Folk theorem

### Fixed-point theory
- Banach fixed-point theorem
- Brouwer/Kakutani fixed-point theorems
- Tarski's fixed-point theorem (for lattices)

### Verification complexity
- Proof complexity: Cook-Reckhow (1979)
- TFNP complexity class
- Verification vs generation in cryptography

## Communication

After completing each phase:
1. Update `status.yaml` with progress
2. Create git commits: `research(self-improvement-limits): completed [phase]`
3. If you discover issues with project direction, document in `notes/concerns.md`
4. If you need literature survey, flag in `status.yaml` blockers

## Timeline

Estimated timeline for theory development:
- Phase 1 (simple case): 2-3 sessions
- Phase 2 (generalization): 3-5 sessions
- Phase 3 (self-play): 2-3 sessions
- Phase 4 (gap characterization): 2-3 sessions
- **Total**: 10-15 sessions

After theory is complete, Writer agent can draft the paper (~5-8 sessions).

---

**You are now unblocked to begin work. Start with reading the project files, then begin Phase 1 formalization.**
