# Pilot Failure Reproduction Experiment

**Status**: Infrastructure complete, ready for framework implementation
**Created**: 2026-03-29
**Budget**: $8 estimated, $12 max

---

## Objective

Validate taxonomy categories 1.1, 3.1, and 5.2 through controlled reproduction of failures across agent frameworks.

---

## What's Been Completed

### ✅ Experimental Design (2026-03-29)
- **spec.yaml**: Complete experimental specification
  - 3 scenarios (tool fabrication, infinite loops, reflection errors)
  - 4 frameworks (ReAct, AutoGPT, Reflexion, Plan-Execute)
  - 2 models (GPT-4o, Claude 3.5 Sonnet)
  - 30 instances total, canary config defined
  - Budget estimates and diagnostic checks

- **tasks.md**: Detailed task specifications
  - 10 instances per scenario with ground truth
  - Clear success/failure criteria
  - Failure signal definitions
  - Expected results and acceptance criteria

### ✅ Infrastructure Foundation (2026-03-29)
- **Base type system** (src/base_types.py)
  - Task, AgentTrace, FailureSignals dataclasses
  - Abstract AgentFramework interface
  - Checkpoint system for crash recovery
  - ExperimentSpec loader

- **Task generators** (src/tasks/)
  - Tool fabrication: 10 instances, 15-20 tools each
  - Mix of real and decoy tools
  - Deterministic ground truth

- **Failure extractors** (src/evaluation/)
  - Tool fabrication detector (checks tool existence)
  - Loop detector (iteration count, stagnation patterns)
  - Reflection error detector (answer persistence, reinforcement)

- **Dependencies** (src/requirements.txt)
  - LangChain, OpenAI, Anthropic APIs
  - Data analysis tools (pandas, scipy)
  - Utilities (tenacity, tqdm)

---

## What's Next

### 🔨 Immediate (Priority 1)
1. **Implement framework wrappers**
   - [ ] ReAct wrapper (LangChain) — reference implementation
   - [ ] Test with single tool fabrication instance
   - [ ] Validate end-to-end: task → execution → trace → signals

2. **Build experiment runner**
   - [ ] Main execution loop
   - [ ] Checkpoint integration
   - [ ] Cost tracking and budget limits
   - [ ] Results aggregation

### 🧪 Near-term (Priority 2)
3. **Run canary experiment**
   - [ ] 2 scenarios × 3 instances × 2 models = 12 evaluations
   - [ ] Validate all diagnostics pass
   - [ ] Estimate actual costs vs. predicted
   - [ ] Debug any pipeline issues

4. **Complete framework implementations**
   - [ ] AutoGPT wrapper
   - [ ] Plan-Execute wrapper
   - [ ] Reflexion wrapper

### 📊 Execution (Priority 3)
5. **Full pilot experiment**
   - [ ] Execute all 140 evaluations
   - [ ] Monitor costs (halt if approaching $12)
   - [ ] Collect failure traces
   - [ ] Generate preliminary results

6. **Analysis and validation**
   - [ ] Compute failure rates per framework
   - [ ] Compare to taxonomy predictions
   - [ ] Extract high-quality examples for paper
   - [ ] Document unexpected findings

---

## Key Design Decisions

### Why These 3 Scenarios?
- **Tool fabrication (1.1)**: Most frequent category (16/50 instances), high reproducibility
- **Infinite loops (3.1)**: Demonstrates C3 limitation (meta-cognitive monitoring)
- **Reflection errors (5.2)**: Tests core claim that same-model reflection fails (C7)

### Why These 4 Frameworks?
- **ReAct**: Baseline, most common architecture
- **AutoGPT**: Autonomous loop, source of infinite loop instances
- **Reflexion**: Only framework that explicitly tests self-correction
- **Plan-Execute**: Tests whether planning phase prevents failures

### Why 10 Instances Per Scenario?
- Minimum for statistical power (can detect effect sizes >0.3)
- Keeps pilot budget under $10
- Sufficient to validate infrastructure
- Full experiment will expand to 30+ per scenario

---

## Expected Outcomes

### Success Criteria
1. ✅ **Reproduce failures**: ≥50% failure rate for at least one framework-model combo per scenario
2. ✅ **Validate taxonomy**: Failures match category definitions
3. ✅ **Collect examples**: 10+ high-quality failure traces for paper
4. ✅ **Architecture patterns**: Observe framework differences
5. ✅ **Budget**: Stay within $12

### What Results Mean for Paper
- **High failure rates (>50%)**: Strong empirical validation of taxonomy
- **Architecture differences**: Supports Section 6 correlation matrix
- **Failure traces**: Concrete examples for Section 4
- **Negative results**: Also valuable — refine taxonomy or discover mitigations

---

## Risk Mitigation

### Technical Risks
- **Framework API changes**: Use specific versions, document in spec
- **Model nondeterminism**: Use temperature=0.7 but run multiple samples if needed
- **Cost overruns**: Checkpoint after each instance, halt if budget exceeded

### Scientific Risks
- **Low reproducibility**: Some failures may be stochastic — document rates
- **Framework bugs**: Distinguish framework bugs from LLM failures
- **Evaluation validity**: Pilot will reveal if failure signals are too ambiguous

---

## Files

```
experiments/pilot-failure-reproduction/
├── spec.yaml              # Experimental specification (COMPLETE)
├── tasks.md              # Task specifications (COMPLETE)
├── README.md             # This file
├── results/              # Will be created during execution
│   ├── raw/             # Individual instance results (JSON)
│   ├── traces/          # Full agent traces
│   └── analysis/        # Aggregated metrics, figures
├── canary-results.yaml   # Will be created after canary run
└── checkpoint.json       # Created during execution for recovery
```

---

## Timeline

- **2026-03-29**: ✅ Spec complete, infrastructure foundation built
- **2026-03-30**: 🔨 Implement ReAct wrapper, test end-to-end
- **2026-03-31**: 🧪 Run canary, validate pipeline
- **2026-04-01**: 📊 Full pilot execution (if canary passes)
- **2026-04-02**: 📈 Analysis and taxonomy update

Total estimated time: 4-5 days for complete pilot validation.

---

## Notes

- This is a **pilot experiment** — goal is to validate infrastructure and taxonomy, not comprehensive coverage
- Results will inform design of full experiment (100+ instances, more frameworks, more scenarios)
- All code is modular — easy to add new scenarios, frameworks, or models
- Checkpointing ensures no wasted API costs if experiment crashes
- Budget includes 50% buffer for unexpected issues

---

## Questions for Future Work

1. Should we test temperature sensitivity? (0.0 vs. 0.7 vs. 1.0)
2. Should we include few-shot vs. zero-shot comparison?
3. Should we test same framework with different LLMs? (e.g., ReAct+GPT vs. ReAct+Claude)
4. Should we include open-source models (Llama, Mistral) for cost comparison?

These can be answered after pilot results are analyzed.
