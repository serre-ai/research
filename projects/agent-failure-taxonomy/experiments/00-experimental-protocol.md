# Experimental Protocol: Agent Failure Taxonomy Validation

**Date**: 2026-03-28
**Purpose**: Empirical validation of taxonomy through controlled failure reproduction
**Session**: 8 (First Experimenter session after 7 failed Researcher sessions)

---

## Objective

Reproduce key failure modes across multiple agent architectures to:
1. **Validate taxonomy categories** - Confirm failures cluster into predicted categories
2. **Quantify architecture-failure correlations** - Measure which architectures exhibit which failures
3. **Establish reproducibility** - Document conditions for reliable failure reproduction
4. **Differentiate from concurrent work** - Our empirical edge is cross-architecture comparison

---

## Framework Selection

### Selection Criteria
1. **Architecture diversity**: Cover major architectural patterns (reactive, planning, reflective)
2. **Maturity**: Production-ready with stable APIs
3. **Transparency**: Observable internal state for failure diagnosis
4. **Cost**: Keep within budget constraints

### Selected Frameworks

#### 1. ReAct (via LangChain)
- **Architecture**: Reactive loop (Observation → Reasoning → Action)
- **Why**: Most widely studied, baseline for comparison
- **High-risk failures**: Infinite loops (3.1), context exhaustion (4.3), progress monitoring (3.1)
- **Implementation**: LangChain agent with custom tools

#### 2. Plan-then-Execute (via Custom Implementation)
- **Architecture**: Upfront planning, then sequential execution
- **Why**: Contrasts with reactive approach, tests planning quality
- **High-risk failures**: False completion (5.1), state verification absence (4.1)
- **Implementation**: Two-phase: planner LLM + executor LLM with tool calls

#### 3. Reflexion (via Custom Implementation)
- **Architecture**: Actor-Evaluator-Reflector loop with memory
- **Why**: Tests self-correction capabilities (C7)
- **High-risk failures**: Confirmation bias (5.2), degeneration-of-thought (5.2), complexity plateau
- **Implementation**: Three-model architecture with reflection memory

### Deferred for Phase 2
- **AutoGPT**: High operational overhead, less architectural diversity vs. ReAct
- **Tree-of-Thought**: High cost per evaluation, narrow use case
- **Multi-agent**: MAST taxonomy already covers this space

---

## Priority Failure Selection

### Selection Criteria
1. **High reproducibility** (Easy/High from instances)
2. **Coverage**: At least 1 failure per major category
3. **Theoretical significance**: Maps to fundamental LLM limitations (C1-C8)
4. **Architecture differentiation**: Expected to vary across frameworks

### Selected Failures (Pilot: 6 failures)

#### F1: Tool Fabrication (Category 1.1 - Tool-Use)
- **Instance**: #18 - Tool count scaling causes fabrication
- **LLM Limitation**: C6 (Tool Grounding) + C1 (Factual Grounding)
- **Reproducibility**: Easy
- **Test Design**:
  - Present agent with 10-30 tools
  - Task requires tool not in set
  - Measure: fabrication rate, tool count threshold
- **Expected variance**: All frameworks vulnerable, but threshold may differ
- **Budget**: ~$0.10 per run (3 frameworks × 5 tools counts × 10 instances = 150 runs × 2 models)

#### F2: Infinite Loops (Category 3.1 - Planning)
- **Instance**: #14 - AutoGPT loops on ambiguous tasks
- **LLM Limitation**: C3 (Meta-Cognitive Monitoring)
- **Reproducibility**: Medium
- **Test Design**:
  - Ambiguous task with multiple valid interpretations
  - No clear success criteria
  - Measure: iteration count, action diversity, convergence
- **Expected variance**: ReAct most vulnerable, Plan-then-execute should avoid
- **Budget**: ~$0.20 per run (potential long runs)

#### F3: Context Degradation (Category 4.3 - State Tracking)
- **Instance**: #49 - Performance < 50% at 32k tokens
- **LLM Limitation**: C2 (Long-Range Coherence) - fundamental
- **Reproducibility**: Easy
- **Test Design**:
  - Multi-step task requiring information from step 1 at step 10+
  - Vary context length: 4k, 8k, 16k, 32k tokens
  - Measure: accuracy vs. context length
- **Expected variance**: All frameworks degrade similarly (fundamental limit)
- **Budget**: ~$0.30 per run (long contexts expensive)

#### F4: Self-Correction Failure (Category 5.2 - Self-Correction)
- **Instance**: #43 - Reflexion degeneration-of-thought
- **LLM Limitation**: C7 (Self-Correction Capability) - fundamental
- **Reproducibility**: Easy
- **Test Design**:
  - Task with common misconception (e.g., Monty Hall problem)
  - Allow up to 5 reflection cycles
  - Measure: error persistence, correction rate, degeneration
- **Expected variance**: Reflexion specifically vulnerable, others may not implement reflection
- **Budget**: ~$0.15 per run (multiple reflection cycles)

#### F5: False Completion (Category 5.1 - Self-Correction)
- **Instance**: #19 - Reports task complete when incomplete
- **LLM Limitation**: C3 (Meta-Cognitive Monitoring) + C7 (Self-Correction)
- **Reproducibility**: Medium
- **Test Design**:
  - Multi-step task with partial completion trap
  - Measure: self-reported completion vs. objective completion
  - Track: which steps completed before claiming done
- **Expected variance**: Plan-then-execute may be more vulnerable (upfront plan creates illusion)
- **Budget**: ~$0.10 per run

#### F6: State Divergence (Category 4.1 - State Tracking)
- **Instance**: #25 - Reports data deleted when still exists
- **LLM Limitation**: C5 (State Tracking)
- **Reproducibility**: High
- **Test Design**:
  - Simulated file system, track agent's state model vs. actual state
  - Actions: create, delete, move files
  - Measure: state divergence after N steps
- **Expected variance**: All frameworks vulnerable unless external verification
- **Budget**: ~$0.08 per run

---

## Pilot Experiment Scope

### Phase 1: Infrastructure + Single Failure (This session goal)
- **Scope**: Build framework wrappers, implement F1 (Tool Fabrication) for ReAct only
- **Output**: Proof-of-concept, validate infrastructure works
- **Budget**: < $2 (under pre-registration threshold)
- **Success criteria**:
  - Successfully run 10 instances of tool fabrication test
  - Measure fabrication rate
  - Log all API calls with costs
  - Checkpoint system works

### Phase 2: Pilot Reproduction (Next session)
- **Scope**: F1 + F5 across 3 frameworks
- **Instances**: 20 per framework per failure = 120 total
- **Budget**: ~$20-30 (requires pre-registration spec)
- **Success criteria**:
  - Both failures reproduce reliably
  - Clear architectural differences emerge
  - Data validates taxonomy categories

### Phase 3: Full Validation (Future sessions)
- **Scope**: All 6 failures across 3 frameworks
- **Instances**: 30-50 per combination
- **Budget**: ~$100-150 (requires pre-registration spec)
- **Output**: Paper-ready frequency tables, correlation matrices

---

## Experimental Design Standards

### Control Variables
- **Model**: Claude Sonnet 3.5 (same across all frameworks for fair comparison)
- **Temperature**: 0.0 (deterministic sampling)
- **System prompt**: Standardized across frameworks where applicable
- **Tool set**: Identical tools available to all frameworks
- **Evaluation**: Automated extraction + manual spot-checks (10% sample)

### Dependent Variables
- **Primary**: Failure occurrence (binary: yes/no)
- **Secondary**: Failure severity (qualitative: minor/moderate/critical)
- **Tertiary**: Recovery attempts, iteration count, cost per instance

### Confounds to Control
- **Model variance**: Use same model, same temperature
- **Tool implementation**: Same underlying tool code across frameworks
- **Task complexity**: Normalize difficulty across failure types
- **Prompt engineering**: Minimal, fair prompts for each framework

---

## Success Criteria

### Infrastructure Level
- ✅ All 3 frameworks can be instantiated and run programmatically
- ✅ Checkpoint/resume works (no lost work on crashes)
- ✅ API costs logged per call with attribution
- ✅ All outputs stored in structured format (JSON)

### Reproduction Level
- ✅ At least 4 of 6 failures reproduce reliably (>60% occurrence)
- ✅ Failure rates differ meaningfully across architectures (>20% delta)
- ✅ Instances match taxonomy categories (inter-rater agreement >0.8)

### Validation Level
- ✅ Taxonomy categories confirmed as distinct and separable
- ✅ Architecture-failure correlation matrix populated with empirical data
- ✅ At least 2 failure types show clear LLM limitation (C1-C8) signatures
- ✅ Results differentiate from Shah et al. taxonomy (show cognitive vs. implementation split)

---

## Risk Mitigation

### Risk 1: Failures don't reproduce reliably
- **Likelihood**: Medium (production systems may have mitigations)
- **Mitigation**: Start with highest reproducibility instances (#18, #43, #49)
- **Fallback**: Document non-reproduction as finding (some "failures" may be fixed)

### Risk 2: Budget overrun
- **Likelihood**: Medium (long-context and iterative failures expensive)
- **Mitigation**: Canary runs mandatory, strict per-instance cost limits
- **Fallback**: Reduce instance counts, focus on 3-4 failures instead of 6

### Risk 3: Framework integration complexity
- **Likelihood**: Low-Medium (LangChain well-documented, others custom)
- **Mitigation**: Start with LangChain (mature), build others incrementally
- **Fallback**: Reduce to 2 frameworks (ReAct + Plan-then-execute)

### Risk 4: Taxonomy validation fails (categories not distinct)
- **Likelihood**: Low (grounded theory methodology produced categories)
- **Mitigation**: Pre-registered category definitions, blind coding subset
- **Fallback**: Refine categories based on empirical data (expected in research)

---

## Timeline and Resource Allocation

### Session 8 (Current): Infrastructure + Pilot (< $2)
- Design protocol ✅
- Build ReAct wrapper with LangChain
- Implement F1 (Tool Fabrication) test
- Run 10 pilot instances
- Validate infrastructure

### Session 9: Pilot Reproduction (~ $20-30, requires spec)
- Create pre-registration spec for F1 + F5 across 3 frameworks
- Implement Plan-then-execute framework
- Run F1 + F5 pilot (20 instances each)
- Initial analysis

### Session 10: Reflexion + Expansion (~ $30-40, requires spec)
- Implement Reflexion framework
- Add F2, F4 to evaluation
- Run expanded pilot (30 instances per combination)
- Preliminary results

### Session 11+: Full Validation (~ $50-100, requires spec)
- Add remaining failures (F3, F6)
- Scale to 50 instances per combination
- Complete statistical analysis
- Generate publication figures

**Total estimated cost**: $150-200 (well within $645 available budget)

---

## Deliverables

### Immediate (This session)
- [x] Experimental protocol document
- [ ] ReAct framework wrapper (src/frameworks/react_agent.py)
- [ ] Tool fabrication test (src/tests/tool_fabrication.py)
- [ ] Pilot run (10 instances)
- [ ] Infrastructure validation report

### Short-term (Next 2 sessions)
- [ ] Pre-registration spec for pilot reproduction
- [ ] All 3 framework implementations
- [ ] F1 + F5 reproduction across frameworks
- [ ] Initial correlation matrix

### Medium-term (Sessions 11-13)
- [ ] Full 6-failure validation
- [ ] Statistical analysis with confidence intervals
- [ ] Publication-ready figures (3-4 figures)
- [ ] Architecture selection guidance table

---

## Integration with Paper

### Methodology Section
- Controlled reproduction protocol
- Framework descriptions
- Failure selection criteria
- Evaluation metrics

### Results Section
- Failure reproduction rates (Table: Framework × Failure)
- Architecture-failure correlation matrix (Table)
- Statistical significance tests
- Figures: failure distribution, architecture risk profiles

### Discussion Section
- Validation of taxonomy categories
- Architectural guidance for practitioners
- Comparison to Shah et al. (cognitive vs. implementation)
- Fundamental vs. correctable distinction empirically validated

---

## Document Status

**Status**: Complete - ready to implement
**Next action**: Build infrastructure (src/ directory structure)
**Session budget remaining**: ~$4 for pilot implementation
**Confidence**: High (0.85) - protocol is feasible, well-scoped, and theory-grounded
