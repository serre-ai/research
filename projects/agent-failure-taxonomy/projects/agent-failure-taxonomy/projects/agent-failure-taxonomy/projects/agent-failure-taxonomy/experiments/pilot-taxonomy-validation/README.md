# Pilot Experiment: Taxonomy Validation

**Status**: Infrastructure complete, ready for implementation phase
**Created**: 2026-03-30
**Estimated Cost**: $2-4

## Overview

This pilot experiment validates the agent failure taxonomy through controlled reproduction of three high-priority failure modes across two agent architectures.

## Goals

1. **Infrastructure validation**: Test experiment framework, logging, and failure detection
2. **Taxonomy validation**: Confirm taxonomy categories are observable in controlled settings
3. **Architecture correlation**: Quantify which architectures exhibit which failure modes

## Scope

- **Frameworks**: ReAct, Plan-then-Execute
- **Scenarios**: Tool fabrication (1.1), Infinite loops (3.1), False completion (5.1)
- **Instances**: 10 per scenario = 30 tasks
- **Executions**: 2 frameworks × 3 scenarios × 10 instances = 60 total runs

## Files

- `protocol.md` - Detailed experimental protocol
- `spec.yaml` - Pre-registration specification (awaiting critic review)
- `tasks/tool_fabrication_tasks.json` - 10 stock price tasks (missing tool)
- `tasks/infinite_loop_tasks.json` - 10 ambiguous improvement tasks
- `tasks/false_completion_tasks.json` - 10 git setup tasks (silent failures)

## Infrastructure (Implemented)

### Core Components

- `src/frameworks/base.py` - Base agent interface with execution tracking
- `src/frameworks/react.py` - ReAct agent implementation (Yao et al. 2023)
- `src/tools/simulated.py` - Tool registry with scenario-specific toolsets

### Data Structures

- `AgentStep` - Single step trace (thought, action, observation, tokens, cost)
- `AgentExecution` - Complete execution record
- `AgentOutcome` - Final results and metrics

### Tool Sets

**Tool Fabrication** (22 tools):
- Includes: web search, Python REPL, weather, email, calendar, database, etc.
- Deliberately omits: stock price tools
- Tests: C6 (Tool Grounding) + C1 (Factual Grounding)

**Infinite Loop** (3 tools):
- read_document, edit_document, search_web
- Documents return same content after edits
- Tests: C3 (Meta-Cognitive Monitoring)

**False Completion** (3 tools):
- run_bash_command, write_file, read_file
- Git commands fail silently after init
- Tests: C3 (Monitoring) + C7 (Self-Correction)

## Next Steps

### Phase 1: Complete Implementation
1. Implement Plan-then-Execute agent (`src/frameworks/plan_execute.py`)
2. Build experiment executor (`src/executor.py`)
3. Add failure analysis module (`src/failure_detector.py`)
4. Create logging utilities (`src/logger.py`)

### Phase 2: Canary Run
1. Run 8 executions (2 frameworks × 2 scenarios × 2 instances)
2. Validate: pipeline completion, cost estimation, logging infrastructure
3. Confirm at least one target failure observed
4. Adjust based on results

### Phase 3: Full Pilot
1. Execute all 60 runs
2. Log full execution traces
3. Classify failures against taxonomy
4. Compute metrics and statistics

### Phase 4: Analysis
1. Calculate failure reproduction rates
2. Test architecture differences (Fisher's exact test)
3. Validate taxonomy mapping
4. Generate summary report

## Expected Outcomes

### Minimum Viable
- ✅ Infrastructure runs without errors
- ✅ Reproduce ≥2/3 failures in ≥30% of instances
- ✅ Costs within $2-4 estimate (max 2× overage)

### Strong Outcome
- ✅ Reproduce all 3 failures in ≥40% of instances
- ✅ Significant architecture differences observed
- ✅ Taxonomy cleanly classifies ≥90% of failures

## Theoretical Grounding

### Taxonomy Categories Tested
- **1.1**: Tool-Use Failures → Selection Failures (Tool Fabrication)
- **3.1**: Planning Failures → Progress Monitoring (Infinite Loops)
- **5.1**: Self-Correction Failures → Verification Failures (False Completion)

### LLM Capabilities Tested
- **C1**: Factual Grounding
- **C3**: Meta-Cognitive Monitoring
- **C6**: Tool Grounding
- **C7**: Self-Correction Capability

### Architecture Patterns
- **ReAct**: Tight observation-action loop (expected: more loops, fewer false completions)
- **Plan-then-Execute**: Planning-execution separation (expected: more false completions, fewer loops)

## Budget

- **Per instance**: $0.05 (estimated)
- **Canary**: $0.40 (8 instances)
- **Full pilot**: $3.00 (60 instances)
- **Max allowed**: $6.00 (2× buffer)

## Success Metrics

- **Failure reproduction rate**: % of instances where target failure manifests
- **Taxonomy mapping accuracy**: % of failures cleanly mapped to categories
- **Architecture differentiation**: Statistical significance of architecture differences
- **Cost accuracy**: Actual vs. estimated cost ratio

## Timeline

- **Session 1** (2026-03-30): Protocol design ✅, spec creation ✅, infrastructure ✅, tasks ✅
- **Session 2**: Complete implementation (Plan-then-Execute, executor, logging)
- **Session 3**: Canary run + validation + adjustments
- **Session 4**: Full pilot execution (60 runs)
- **Session 5**: Analysis and reporting

## Notes

This pilot is intentionally scoped small to validate methodology before expanding to full experiment with 4 frameworks, 6-8 scenarios, and 30 instances per scenario.

If successful, establishes infrastructure for comprehensive architecture-failure correlation analysis that differentiates our work from Shah et al. (2026) through controlled empirical validation.
