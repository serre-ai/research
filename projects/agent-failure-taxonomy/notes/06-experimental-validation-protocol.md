# Experimental Validation Protocol for Agent Failure Taxonomy

**Date**: 2026-03-27
**Status**: Design complete, ready for implementation
**Purpose**: Validate taxonomy categories through controlled reproduction of key failure modes
**Budget Constraint**: <$5 per session, experiments >$2 require pre-registration

---

## Executive Summary

This protocol validates the 9-category taxonomy through controlled experiments reproducing 6 high-priority failures across 3 frameworks. We prioritize highly reproducible failures (80%+ from dataset) with clear success/failure criteria. Total estimated cost: $45-75 for full validation, $8-12 for pilot.

**Recommended pilot**: 3 failures (tool fabrication, infinite loop, context degradation) on LangGraph only to validate infrastructure before full deployment.

---

## 1. Framework Selection

### Selected Frameworks (3 of 4)

#### Framework 1: LangGraph (LangChain)
**Rationale**:
- Most mature and documented ReAct implementation
- Excellent tooling for observation/debugging
- Rich GitHub issue history validates real-world failures
- Free tier available (OpenAI/Anthropic backends)
- Strong community support for troubleshooting

**Implementation effort**: Low (2-4 hours)
- Well-documented quickstart
- pip install langchain langgraph
- Minimal boilerplate

**Cost per test**: $0.50-2.00
- Depends on model (GPT-4o-mini vs GPT-4)
- Most tests completable in <10 turns

---

#### Framework 2: AutoGPT
**Rationale**:
- Canonical autonomous loop architecture
- Well-documented infinite loop and web hallucination failures (Instances 14, 15)
- Active development with version history for reproducibility
- Representative of production autonomous agents

**Implementation effort**: Medium (4-6 hours)
- Requires docker setup or local install
- Configuration for specific tasks
- May need API key management

**Cost per test**: $1.00-3.00
- Autonomous loops consume more tokens
- Need iteration limits to prevent runaway costs

---

#### Framework 3: OpenAI Swarm (Multi-Agent)
**Rationale**:
- Lightweight, minimal multi-agent framework from OpenAI
- Easy to implement for testing coordination failures
- Well-suited for error propagation experiments (Instance 21)
- Recently released, good documentation

**Implementation effort**: Low (2-3 hours)
- Simple Python library
- Minimal dependencies
- Clear examples

**Cost per test**: $0.50-1.50
- Short multi-agent conversations
- Can use GPT-4o-mini for cost control

---

### Framework NOT Selected: Plan-then-Execute (Custom)

**Reason for exclusion**: Would require custom implementation as no standard framework exists. Implementation effort (8-12 hours) exceeds validation timeline. Can validate plan-then-execute failures theoretically through literature analysis rather than empirical reproduction.

**Alternative**: If needed, can implement minimal plan-then-execute with LangGraph's planning patterns (adds 4 hours, $10-15 in testing).

---

## 2. Failure Selection and Test Design

### Selection Criteria
1. **Reproducibility**: Easy or High (80% of dataset)
2. **Category coverage**: 1-2 failures per major category
3. **Clear success criteria**: Objective pass/fail determination
4. **Cost-effective**: Completable in <20 agent turns
5. **Architecture diversity**: Failures spanning multiple frameworks

### Selected Failures (6 total)

---

### Failure 1: Tool Fabrication (Instance 18, Category 1.1)
**Priority**: Critical (fundamental LLM limitation C6)

**Test Design**:
- **Framework**: LangGraph
- **Setup**: Provide 15-20 tools with similar names/functions
- **Task**: "Find the current stock price of NVIDIA and calculate the compound annual growth rate over the past 5 years"
- **Expected failure**: Agent fabricates plausible tool (e.g., "calculate_cagr") not in registry

**Success Criteria**:
- PASS: Agent calls non-existent tool at least once in 5 trials
- FAIL: Agent only calls registered tools
- **Detection method**: Parse tool call logs for function names not in registry

**Reproducibility**: Easy (systematic with tool count scaling)

**Estimated cost**: $1.50-2.50
- 5 trials × 5-10 turns × GPT-4o-mini
- Can use GPT-4 for 1-2 trials to test model variance

**Implementation complexity**: Low
- Standard LangGraph setup
- JSON tool registry
- Simple task

**Quantitative metrics**:
- Fabrication rate across trials
- Number of tools at which fabrication occurs
- Types of fabrications (plausible vs implausible names)

---

### Failure 2: Infinite Loop Without Progress (Instance 14, Category 3.1)
**Priority**: Critical (meta-cognitive monitoring C3)

**Test Design**:
- **Framework**: AutoGPT
- **Setup**: Standard AutoGPT with GPT-4o, 50-iteration limit
- **Task**: "Research the history of the fictional country of Wakanda and create a timeline of its major events" (impossible task, no real information)
- **Expected failure**: Agent loops searching different sources without recognizing impossibility

**Success Criteria**:
- PASS: Agent repeats similar search actions >10 times without progress
- FAIL: Agent terminates with "task impossible" or similar within 10 iterations
- **Detection method**: Automated analysis of action sequences using edit distance similarity (>0.8 similarity = loop)

**Reproducibility**: Medium (requires ambiguous/impossible task)

**Estimated cost**: $2.00-4.00
- Limited to 50 iterations max
- 3 trials with different impossible tasks
- GPT-4o for realistic behavior

**Implementation complexity**: Medium
- AutoGPT setup and configuration
- Iteration tracking infrastructure
- Action similarity analysis script

**Quantitative metrics**:
- Iteration count before manual stop
- Action similarity scores over time
- Number of unique vs repeated actions

---

### Failure 3: Reflexion Confirmation Bias (Instance 43, Category 5.2)
**Priority**: High (self-correction capability C7)

**Test Design**:
- **Framework**: LangGraph (custom Reflexion implementation)
- **Setup**: Simple Reflexion loop (actor → evaluator → reflector → retry)
- **Task**: Math reasoning problem with common misconception (e.g., "If 5 machines make 5 widgets in 5 minutes, how long for 100 machines to make 100 widgets?")
- **Expected failure**: Agent gets initial answer wrong, reflection doesn't correct misconception, repeats same error

**Success Criteria**:
- PASS: Agent repeats same incorrect answer across 3+ reflection iterations despite negative feedback
- FAIL: Agent corrects answer after reflection
- **Detection method**: Parse answer extraction across iterations, check for correction

**Reproducibility**: High (systematic on problems with common misconceptions)

**Estimated cost**: $1.00-2.00
- 3 reflection iterations
- 3 trials with different problems
- GPT-4o-mini sufficient

**Implementation complexity**: Medium
- Custom Reflexion loop implementation
- Answer extraction and comparison
- Reflection prompt engineering

**Quantitative metrics**:
- Correction rate after N reflections
- Types of reflection feedback (generic vs specific)
- Whether reflections acknowledge error vs rationalize it

---

### Failure 4: Context Degradation (Instance 49, Category 4.3)
**Priority**: Critical (long-range coherence C2, fundamental limit)

**Test Design**:
- **Framework**: LangGraph
- **Setup**: Multi-turn conversation with information scattered throughout
- **Task**: "Here are 20 facts about a person [insert facts]. After reading all facts, answer: What is their favorite food mentioned in fact #7?"
- **Expected failure**: Performance degrades as context grows, information in middle lost

**Success Criteria**:
- PASS: Accuracy drops >30% for facts positioned at 12k-24k tokens vs facts at <2k tokens (3+ trials)
- FAIL: No significant positional bias
- **Detection method**: Controlled A/B test with same facts at different positions

**Reproducibility**: Easy (systematic across models)

**Estimated cost**: $2.00-3.00
- 10 trials with different fact positions
- Need sufficient context (16k-32k tokens)
- GPT-4o (larger context window)

**Implementation complexity**: Low
- Simple Q&A task
- Automated fact generation and positioning
- Accuracy tracking

**Quantitative metrics**:
- Accuracy by token position (0-8k, 8k-16k, 16k-24k, 24k-32k)
- Plotting performance curve
- Replication of NoLiMa findings

---

### Failure 5: Multi-Agent Error Amplification (Instance 21, Category 7.2)
**Priority**: Medium (error propagation validation)

**Test Design**:
- **Framework**: OpenAI Swarm
- **Setup**: 3-agent system (researcher → analyst → reporter), each passes information to next
- **Task**: "Research the population of Springfield" (ambiguous - many Springfields)
- **Seed error**: First agent makes small mistake (e.g., confuses Springfield, IL with Springfield, MA)
- **Expected failure**: Error amplifies through chain, final report treats error as fact

**Success Criteria**:
- PASS: Error propagates and amplifies (later agents don't question, add supporting details for wrong Springfield)
- FAIL: Later agents catch and correct error
- **Detection method**: Manual review of final output for error presence + supporting fabrications

**Reproducibility**: Medium (requires careful setup)

**Estimated cost**: $1.00-2.00
- 3-agent chain
- 5 trials with different ambiguous queries
- GPT-4o-mini sufficient

**Implementation complexity**: Low-Medium
- Swarm setup straightforward
- Need handoff logic
- Error injection strategy

**Quantitative metrics**:
- Error propagation rate across trials
- Number of supporting fabrications added
- Whether any agent questions the error

---

### Failure 6: JSON Parsing Error Non-Recovery (Instance 28, Category 6.2)
**Priority**: Medium (architectural correctable, validates category 6)

**Test Design**:
- **Framework**: LangGraph (using create_react_agent)
- **Setup**: Tool with complex nested JSON schema
- **Task**: "Use the update_user_profile tool to set nested preferences"
- **Expected failure**: Agent generates malformed JSON, no automatic retry

**Success Criteria**:
- PASS: Agent generates malformed JSON at least once in 5 trials AND does not auto-retry
- FAIL: JSON always valid OR automatic retry occurs
- **Detection method**: Parse execution logs for JSON validation errors and retry attempts

**Reproducibility**: Medium (probabilistic JSON generation errors)

**Estimated cost**: $0.50-1.00
- 5-10 trials
- Short conversations
- GPT-4o-mini (more prone to JSON errors than GPT-4)

**Implementation complexity**: Low
- Standard LangGraph setup
- Complex JSON schema definition
- Error log parsing

**Quantitative metrics**:
- JSON error rate
- Whether framework attempts retry
- Success after manual retry prompt

---

## 3. Success Criteria Summary Table

| Failure | Category | Detection Method | Threshold | Automation Level |
|---------|----------|------------------|-----------|------------------|
| Tool Fabrication | 1.1 Tool-Use | Parse tool calls vs registry | ≥1 fabrication in 5 trials | Fully automated |
| Infinite Loop | 3.1 Planning | Action similarity analysis | >10 repeated actions | Fully automated |
| Reflexion Bias | 5.2 Self-Correction | Answer extraction across iterations | Same wrong answer 3+ times | Fully automated |
| Context Degradation | 4.3 State Tracking | Position-based accuracy | >30% accuracy drop mid-context | Fully automated |
| Error Amplification | 7.2 Error Propagation | Manual output review | Error present + fabrications | Semi-automated |
| JSON Non-Recovery | 6.2 Error Recovery | Log parsing for retries | Error + no retry attempt | Fully automated |

**Automation**: 5 of 6 tests fully automatable, enabling low-cost replication across models.

---

## 4. Resource Estimates

### Time Estimates

**Infrastructure setup**: 8-12 hours total
- LangGraph environment: 2 hours
- AutoGPT setup: 4 hours
- OpenAI Swarm setup: 1 hour
- Test automation scripts: 3-5 hours

**Per-test execution**: 30-60 minutes each
- Run trials: 10-20 min
- Data collection: 5-10 min
- Analysis: 10-20 min
- Documentation: 5-10 min

**Total execution time**: 3-6 hours for all 6 tests

**Full protocol timeline**: 2-3 days (including setup)

---

### Cost Estimates

**Per-Test Costs** (with ranges for model choices):

| Test | Min Cost (GPT-4o-mini) | Max Cost (GPT-4) | Recommended |
|------|------------------------|------------------|-------------|
| Tool Fabrication | $1.50 | $4.00 | $2.50 |
| Infinite Loop | $2.00 | $6.00 | $4.00 |
| Reflexion Bias | $1.00 | $3.00 | $2.00 |
| Context Degradation | $2.00 | $5.00 | $3.00 |
| Error Amplification | $1.00 | $2.50 | $1.50 |
| JSON Non-Recovery | $0.50 | $1.50 | $1.00 |

**Total estimated cost**: $45-75
- Conservative estimate (GPT-4 for most tests): $60-75
- Optimized estimate (GPT-4o-mini where possible): $45-55
- **Requires pre-registration** (>$2 per experiment)

**Cost control strategies**:
1. Use GPT-4o-mini for initial trials, GPT-4 for validation only
2. Strict iteration limits (prevent runaway loops)
3. Batch trials with same setup
4. Cache tool/prompt configurations

---

### Additional Resource Needs

**Compute**: Local machine sufficient (no GPU needed)

**APIs**:
- OpenAI API key (required)
- Anthropic API key (optional, for Claude comparison)

**Storage**: ~100MB for logs and results

**Personnel**: 1 researcher (can be fully self-executed)

---

## 5. Pilot Experiment Recommendation

### Pilot Scope: 3 Failures on 1 Framework

**Selected failures for pilot**:
1. **Tool Fabrication** (Instance 18) - validates Category 1
2. **Infinite Loop** (Instance 14) - validates Category 3
3. **Context Degradation** (Instance 49) - validates Category 4

**Framework**: LangGraph only (defer AutoGPT and Swarm to full deployment)

**Rationale**:
- These 3 failures span different categories (tool-use, planning, state tracking)
- All have clear, automatable success criteria
- LangGraph is lowest implementation effort
- Combined cost: $8-12 (within single-session budget)
- Tests all critical infrastructure (tool handling, iteration tracking, context management)

---

### Pilot Success Criteria

**Infrastructure validation**:
- ✅ Can reproduce at least 2 of 3 failures reliably
- ✅ Automated detection scripts work correctly
- ✅ Data collection captures all needed metrics
- ✅ Cost stays within $12 budget
- ✅ Execution time <3 hours

**If pilot succeeds**: Proceed to full 6-test protocol with all 3 frameworks

**If pilot fails (<2 failures reproduced)**:
- Re-evaluate test design
- Adjust task prompts
- Consider model changes
- May need to substitute different failures

---

### Pilot Timeline

**Day 1 Morning** (3 hours):
- LangGraph environment setup
- Implement tool fabrication test
- Run 5 trials, validate detection

**Day 1 Afternoon** (3 hours):
- Implement infinite loop test
- Run 3 trials with iteration limits
- Validate action similarity detection

**Day 2 Morning** (2 hours):
- Implement context degradation test
- Run 10 positional trials
- Generate accuracy plots

**Day 2 Afternoon** (2 hours):
- Data analysis and documentation
- Success/failure determination
- Decision on full protocol

**Total pilot time**: 10 hours over 2 days

---

## 6. Full Experiment Extensions (Post-Pilot)

### Model Comparison (Optional, +$30-50)

If pilot succeeds, can extend to compare models:
- GPT-4o vs GPT-4o-mini vs GPT-4
- Claude 3.5 Sonnet vs Claude 3 Opus
- Open source (Llama 3.1 70B via TogetherAI)

**Value**: Maps failure modes to specific model capabilities (C1-C8)

---

### Architecture Variants (Optional, +$20-30)

Test same failures with architecture modifications:
- ReAct with external memory
- Reflexion with multi-model critics
- Autonomous loop with progress metrics

**Value**: Validates mitigation strategies from taxonomy

---

### Scaling Analysis (Optional, +$15-25)

Systematically vary:
- Number of tools (5, 10, 20, 50) for tool fabrication
- Context length (8k, 16k, 32k, 64k) for degradation
- Chain length (2, 3, 5 agents) for error propagation

**Value**: Quantifies scaling relationships

---

## 7. Data Collection and Analysis Plan

### Automated Metrics (per test run)

**All tests**:
- Timestamp and model ID
- Total tokens consumed
- Total cost
- Number of iterations/turns
- Success/failure determination

**Test-specific**:
- Tool fabrication: Tool names called, fabrication count, tool registry size
- Infinite loop: Action sequence, similarity scores, unique action count
- Reflexion: Answer per iteration, reflection content, correction success
- Context degradation: Accuracy per position bucket, token counts
- Error amplification: Error presence, supporting fabrications, agent transcripts
- JSON recovery: JSON error count, retry attempts, manual correction needed

### Qualitative Analysis

**For each failure**:
- Representative conversation transcripts (2-3 examples)
- Failure mode annotations
- Comparison to literature description
- Unexpected behaviors or variations

### Output Format

**Per-test report**:
```
## Test: [Failure Name]
**Date**: [timestamp]
**Model**: [model ID]
**Trials**: [n]
**Success rate**: [x/n failures reproduced]

### Quantitative Results
[Tables and plots]

### Qualitative Observations
[Narrative analysis]

### Taxonomy Validation
- Category confirmed: [yes/no]
- Sub-category confirmed: [yes/no]
- Root cause alignment: [high/medium/low]
- Reproducibility validated: [yes/no]
```

**Aggregate report**:
- Cross-test comparison table
- Category coverage matrix
- Cost and time actuals vs estimates
- Recommendations for taxonomy refinement

---

## 8. Risk Mitigation

### Technical Risks

**Risk**: Framework setup fails or is overly complex
- **Mitigation**: Pilot with LangGraph only, well-documented
- **Fallback**: Use simpler custom implementations

**Risk**: Failures don't reproduce as expected
- **Mitigation**: Selected Easy/High reproducibility instances (80%)
- **Fallback**: Substitute with alternate instances from same category

**Risk**: Cost overruns from runaway loops
- **Mitigation**: Strict iteration limits, timeout functions
- **Monitoring**: Real-time cost tracking per API call

---

### Experimental Risks

**Risk**: Success criteria too strict (false negatives)
- **Mitigation**: Pilot validates detection thresholds
- **Adjustment**: Can relax thresholds based on pilot data

**Risk**: Success criteria too loose (false positives)
- **Mitigation**: Manual review of borderline cases
- **Adjustment**: Tighten thresholds if needed

**Risk**: Confounding factors (e.g., model updates mid-experiment)
- **Mitigation**: Pin specific model versions, document API version
- **Monitoring**: Track model release dates

---

### Resource Risks

**Risk**: Exceeds $75 budget
- **Mitigation**: Use GPT-4o-mini aggressively, strict limits
- **Fallback**: Reduce trials per test (5 → 3)

**Risk**: Exceeds timeline
- **Mitigation**: Pilot identifies time sinks early
- **Fallback**: Prioritize subset (4 tests instead of 6)

---

## 9. Expected Outcomes and Deliverables

### Validation Outcomes (3 categories)

**Strong validation** (4-6 failures reproduced reliably):
- Taxonomy categories empirically confirmed
- Can proceed to paper writing with high confidence
- Include quantitative failure rates in publication

**Partial validation** (2-3 failures reproduced):
- Core categories validated
- May need boundary refinement
- Include caveats about reproduction conditions

**Weak validation** (<2 failures reproduced):
- Re-examine taxonomy structure
- May indicate literature failures not generalizable
- Need different test designs or more instances

---

### Deliverables

1. **Experimental data** (code + logs + results)
   - GitHub repository with reproduction scripts
   - Raw conversation logs (anonymized)
   - Analysis notebooks (Jupyter)

2. **Validation report** (15-20 pages)
   - Methods section ready for paper
   - Results tables and figures
   - Taxonomy refinements based on findings

3. **Replication package**
   - Docker containers for reproducibility
   - Step-by-step setup guide
   - Cost and time actuals for planning

4. **Paper sections** (draft)
   - Methods: "Experimental Validation"
   - Results: "Empirical Failure Reproduction"
   - Discussion: "Limitations and Boundary Conditions"

---

## 10. Integration with Paper Timeline

### Current Status
- Taxonomy development complete (9 categories, 50 instances)
- Ready for empirical validation

### With Pilot (1 week)
- **Week 1**: Pilot experiment (3 tests, LangGraph)
- **Week 2**: Analysis and decision point
- **Outcome**: Go/no-go for full protocol

### With Full Protocol (2-3 weeks)
- **Week 1**: Pilot (3 tests)
- **Week 2**: Full protocol remaining tests (3 tests, 2 frameworks)
- **Week 3**: Analysis, replication package, paper integration
- **Outcome**: Validated taxonomy ready for publication

### Paper Deadline: ACL 2027 (February 2027)
- **Current date**: March 2026
- **Time available**: 11 months
- **Validation timeline**: 2-3 weeks
- **Status**: Excellent - validation can complete in April 2026, leaving 10 months for writing

---

## 11. Alternative Approaches Considered

### Approach 1: Survey Practitioners
**Pros**: Real-world validation, practitioner perspective
**Cons**: Slow response rates, subjective, hard to quantify
**Decision**: Complementary, not primary validation

### Approach 2: Analyze Public Agent Logs
**Pros**: Large-scale data, real usage patterns
**Cons**: Privacy concerns, unclear task context, noisy labels
**Decision**: Future work, not feasible for initial validation

### Approach 3: Build Comprehensive Benchmark
**Pros**: Systematic coverage, reusable
**Cons**: High development cost (weeks), scope creep risk
**Decision**: Too expensive for validation, could be follow-up contribution

### Approach 4: Theoretical Validation Only
**Pros**: No implementation cost, fast
**Cons**: Lacks empirical grounding, less convincing to reviewers
**Decision**: Insufficient alone, combine with experimental validation

**Selected approach (controlled experiments)** balances cost, timeline, and rigor.

---

## 12. Success Metrics for Overall Protocol

### Minimum Success Criteria
- ✅ Reproduce at least 4 of 6 failures reliably (>80% trial success)
- ✅ Validate at least 5 of 9 taxonomy categories empirically
- ✅ Stay within $75 budget
- ✅ Complete within 3 weeks
- ✅ Produce replicable methods for paper

### Stretch Goals
- Reproduce all 6 failures
- Model comparison (GPT-4 vs Claude)
- Quantify scaling relationships
- Public replication package

---

## Appendix A: Instance-to-Test Mapping

| Test # | Instance ID | Instance Name | Category | Sub-category | Framework |
|--------|-------------|---------------|----------|--------------|-----------|
| 1 | 18 | Tool count scaling | 1 Tool-Use | 1.1 Selection | LangGraph |
| 2 | 14 | AutoGPT infinite loop | 3 Planning | 3.1 Progress monitoring | AutoGPT |
| 3 | 43 | Reflexion degeneration | 5 Self-Correction | 5.2 Reflection | LangGraph |
| 4 | 49 | Context rot <50% | 4 State Tracking | 4.3 Context mgmt | LangGraph |
| 5 | 21 | MAS error consensus | 7 Error Propagation | 7.2 Spatial | Swarm |
| 6 | 28 | JSON parsing non-recovery | 6 Error Recovery | 6.2 Error handling | LangGraph |

---

## Appendix B: Cost Breakdown Detail

### API Pricing (as of March 2026)

**GPT-4o**:
- Input: $2.50 / 1M tokens
- Output: $10.00 / 1M tokens
- Average cost per 10-turn conversation: $0.50-1.00

**GPT-4o-mini**:
- Input: $0.15 / 1M tokens
- Output: $0.60 / 1M tokens
- Average cost per 10-turn conversation: $0.05-0.15

**Claude 3.5 Sonnet** (optional):
- Input: $3.00 / 1M tokens
- Output: $15.00 / 1M tokens
- Average cost per 10-turn conversation: $0.60-1.20

### Conservative Budget (all GPT-4o)
- Tool fabrication: 5 trials × $0.50 = $2.50
- Infinite loop: 3 trials × $1.50 = $4.50
- Reflexion: 3 trials × $0.70 = $2.10
- Context degradation: 10 trials × $0.30 = $3.00
- Error amplification: 5 trials × $0.40 = $2.00
- JSON recovery: 10 trials × $0.10 = $1.00
**Total**: $15.10

### Optimized Budget (GPT-4o-mini where possible)
- Tool fabrication: $1.50 (mini sufficient)
- Infinite loop: $4.00 (need GPT-4o for realistic behavior)
- Reflexion: $1.00 (mini sufficient)
- Context degradation: $3.00 (need GPT-4o for context length)
- Error amplification: $1.00 (mini sufficient)
- JSON recovery: $0.50 (mini more error-prone, better test)
**Total**: $11.00

**Pilot budget** (3 tests, LangGraph): $8.50

---

## Appendix C: Automation Scripts (Pseudocode)

### Tool Fabrication Detector
```python
def detect_tool_fabrication(tool_calls, registry):
    fabrications = []
    for call in tool_calls:
        if call.function_name not in registry:
            fabrications.append(call.function_name)
    return len(fabrications) > 0, fabrications
```

### Infinite Loop Detector
```python
def detect_infinite_loop(actions, threshold=0.8, window=5):
    for i in range(len(actions) - window):
        window_actions = actions[i:i+window]
        similarities = []
        for j in range(len(window_actions)-1):
            sim = edit_distance_similarity(
                window_actions[j],
                window_actions[j+1]
            )
            similarities.append(sim)
        if np.mean(similarities) > threshold:
            return True, i
    return False, -1
```

### Context Degradation Analyzer
```python
def analyze_context_degradation(results):
    # results: [(token_position, correct: bool)]
    buckets = {
        '0-8k': [],
        '8k-16k': [],
        '16k-24k': [],
        '24k-32k': []
    }
    for pos, correct in results:
        bucket = get_bucket(pos)
        buckets[bucket].append(correct)

    accuracies = {k: np.mean(v) for k, v in buckets.items()}
    degradation = accuracies['0-8k'] - accuracies['16k-24k']
    return degradation > 0.30, accuracies
```

---

## Document Status

**Ready for**: Immediate pilot execution
**Next steps**:
1. Set up LangGraph environment
2. Implement pilot test #1 (tool fabrication)
3. Run 5 trials and validate detection
4. Proceed to tests #2 and #3
5. Analyze results and decide on full protocol

**Questions for human review**:
1. Budget approval for $8-12 pilot (or $45-75 full protocol)?
2. Preference for model (GPT-4o vs GPT-4o-mini vs Claude)?
3. Timeline constraints (can complete in 2-3 weeks)?
4. Any specific failures to prioritize over recommendations?

**Confidence**: High (0.85) - protocol is practical, well-scoped, and aligned with taxonomy goals
