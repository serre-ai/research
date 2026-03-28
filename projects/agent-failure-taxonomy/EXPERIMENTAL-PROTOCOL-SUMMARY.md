# Experimental Validation Protocol - Quick Reference

**Full protocol**: See `/projects/agent-failure-taxonomy/notes/06-experimental-validation-protocol.md`

---

## TL;DR

**Goal**: Validate taxonomy by reproducing 6 key failures across 3 frameworks
**Cost**: $8-12 pilot, $45-75 full protocol
**Timeline**: 2-3 weeks
**Recommendation**: Start with 3-failure pilot on LangGraph only

---

## Pilot Experiment (Recommended First Step)

### Scope
- **3 failures**: Tool fabrication, Infinite loop, Context degradation
- **1 framework**: LangGraph only
- **Cost**: $8-12
- **Time**: 10 hours over 2 days

### Success Criteria
Reproduce at least 2 of 3 failures reliably

### Next Steps if Pilot Succeeds
Proceed to full 6-failure, 3-framework protocol

---

## Full Protocol

### Framework Selection (3 frameworks)

1. **LangGraph** (ReAct)
   - Implementation: 2-4 hours
   - Cost per test: $0.50-2.00
   - Rationale: Mature, documented, free tier

2. **AutoGPT** (Autonomous Loop)
   - Implementation: 4-6 hours
   - Cost per test: $1.00-3.00
   - Rationale: Representative autonomous agent

3. **OpenAI Swarm** (Multi-Agent)
   - Implementation: 2-3 hours
   - Cost per test: $0.50-1.50
   - Rationale: Lightweight, easy coordination testing

---

### Failure Selection (6 failures)

| # | Failure | Category | Framework | Priority | Cost | Reproducibility |
|---|---------|----------|-----------|----------|------|-----------------|
| 1 | Tool Fabrication | 1.1 Tool-Use | LangGraph | Critical | $2.50 | Easy |
| 2 | Infinite Loop | 3.1 Planning | AutoGPT | Critical | $4.00 | Medium |
| 3 | Reflexion Bias | 5.2 Self-Correction | LangGraph | High | $2.00 | High |
| 4 | Context Degradation | 4.3 State Tracking | LangGraph | Critical | $3.00 | Easy |
| 5 | Error Amplification | 7.2 Propagation | Swarm | Medium | $1.50 | Medium |
| 6 | JSON Non-Recovery | 6.2 Error Recovery | LangGraph | Medium | $1.00 | Medium |

**Total**: $14.00 (optimized) to $22.00 (conservative)

---

### Category Coverage

- ✅ Category 1: Tool-Use (Failure 1)
- ✅ Category 3: Planning (Failure 2)
- ✅ Category 4: State Tracking (Failure 4)
- ✅ Category 5: Self-Correction (Failure 3)
- ✅ Category 6: Error Recovery (Failure 6)
- ✅ Category 7: Error Propagation (Failure 5)

**Coverage**: 6 of 9 categories (66%)

---

## Success Criteria

### Automated Detection

- **Tool Fabrication**: Parse tool calls vs registry (≥1 in 5 trials)
- **Infinite Loop**: Action similarity analysis (>10 repeated actions)
- **Reflexion Bias**: Answer extraction (same wrong answer 3+ times)
- **Context Degradation**: Position-based accuracy (>30% drop mid-context)
- **JSON Non-Recovery**: Log parsing (error + no retry)

### Semi-Automated

- **Error Amplification**: Manual review (error present + fabrications)

---

## Resource Estimates

### Time
- Infrastructure setup: 8-12 hours
- Per-test execution: 30-60 minutes
- Total: 2-3 days

### Cost
- Pilot: $8-12
- Full protocol: $45-75
- With model comparison: +$30-50
- With scaling analysis: +$15-25

### Requirements
- OpenAI API key (required)
- Anthropic API key (optional)
- Local machine (no GPU)
- ~100MB storage

---

## Risk Mitigation

### Cost Control
- Strict iteration limits
- Use GPT-4o-mini where possible
- Real-time cost tracking

### Technical
- Pilot validates infrastructure
- Pin model versions
- Fallback instances prepared

### Experimental
- Manual review of borderline cases
- Adjustable thresholds
- High-reproducibility instances selected

---

## Deliverables

1. **Code**: GitHub repo with reproduction scripts
2. **Data**: Conversation logs, metrics, analysis notebooks
3. **Report**: 15-20 page validation report
4. **Paper sections**: Methods, Results, Discussion drafts

---

## Decision Points

### After Pilot (2 days)
- **If ≥2 failures reproduced**: Proceed to full protocol
- **If <2 failures reproduced**: Adjust test design or substitute instances

### After Full Protocol (3 weeks)
- **If ≥4 failures reproduced**: Strong validation, proceed to paper
- **If 2-3 failures reproduced**: Partial validation, refine boundaries
- **If <2 failures reproduced**: Re-examine taxonomy structure

---

## Quick Start (Pilot)

### Day 1
1. Setup LangGraph environment (2 hours)
2. Implement tool fabrication test (1 hour)
3. Run 5 trials, validate detection (2 hours)
4. Implement infinite loop test (1 hour)
5. Run 3 trials, validate detection (2 hours)

### Day 2
1. Implement context degradation test (1 hour)
2. Run 10 positional trials (1 hour)
3. Data analysis and documentation (2 hours)
4. Go/no-go decision

---

## Contact Points for Questions

1. **Budget approval**: Need $8-12 for pilot or $45-75 for full
2. **Model preference**: GPT-4o vs GPT-4o-mini vs Claude?
3. **Timeline**: Can complete in 2-3 weeks?
4. **Failure prioritization**: Any changes to recommended 6?

---

**Status**: Ready for immediate execution
**Next action**: Set up LangGraph environment and begin pilot
**Full details**: `/projects/agent-failure-taxonomy/notes/06-experimental-validation-protocol.md`
