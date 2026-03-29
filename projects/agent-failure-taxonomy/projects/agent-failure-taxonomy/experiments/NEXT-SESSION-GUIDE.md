# Next Session Guide: Framework Implementation

**For**: Experimenter Agent (Session 9+)
**Status**: Infrastructure foundation complete (60%)
**Next Priority**: Implement framework wrappers

---

## Where We Are

✅ **COMPLETED (Session 8, 2026-03-29)**
- Experimental spec designed (spec.yaml, tasks.md)
- Base type system (Task, AgentTrace, FailureSignals)
- Task generator for tool fabrication scenario
- Failure extractors for all 3 scenarios
- Checkpointing and cost tracking structure
- Dependencies defined (requirements.txt)

⏳ **IN PROGRESS**
- Framework wrappers (0/4 complete)
- Experiment runner (not started)

📋 **NOT STARTED**
- Canary experiment
- Full pilot experiment
- Results analysis

---

## What to Do Next

### Priority 1: Implement ReAct Wrapper (Reference Implementation)

**File**: `src/frameworks/react.py`

**Goal**: Create a working ReAct wrapper that:
1. Implements the `AgentFramework` abstract interface
2. Uses LangChain's ReAct agent
3. Executes a task and returns a complete `AgentTrace`
4. Tracks API calls, costs, and tool usage

**Testing**: Use one tool fabrication instance to validate end-to-end:
```bash
python src/frameworks/react.py --test
```

**Success Criteria**:
- Executes tool_fab_1 successfully
- Returns AgentTrace with all required fields
- Failure extractor correctly identifies tool fabrication
- Cost tracking works
- Takes <5 minutes to run single instance

**Example Structure**:
```python
from langchain.agents import AgentExecutor, create_react_agent
from ..base_types import AgentFramework, Task, AgentTrace

class ReactFramework(AgentFramework):
    def execute(self, task: Task, config: AgentConfig) -> AgentTrace:
        # 1. Convert task.available_tools to LangChain tools
        # 2. Create ReAct agent with tools
        # 3. Execute with timeout
        # 4. Capture all intermediate steps
        # 5. Track token usage and cost
        # 6. Return AgentTrace
        pass
```

---

### Priority 2: Build Experiment Runner

**File**: `src/run_experiment.py`

**Goal**: Main script that:
1. Loads spec.yaml
2. Generates task instances
3. Executes each instance with appropriate framework
4. Checkpoints after each instance
5. Halts if budget exceeded
6. Saves results to JSON

**CLI**:
```bash
python src/run_experiment.py \
  --spec experiments/pilot-failure-reproduction/spec.yaml \
  --output experiments/pilot-failure-reproduction/results/ \
  [--canary-only] \
  [--resume checkpoint.json]
```

**Key Features**:
- Progress bar (tqdm)
- Graceful error handling (one instance failure doesn't kill experiment)
- Budget monitoring (halt before exceeding max)
- Checkpoint every 5 instances
- Structured logging

---

### Priority 3: Run Canary

**Command**:
```bash
python src/run_experiment.py \
  --spec experiments/pilot-failure-reproduction/spec.yaml \
  --canary-only \
  --output experiments/pilot-failure-reproduction/
```

**Diagnostics to Validate** (from spec.yaml):
1. `pipeline_completion`: All instances produce output
2. `extraction_failure_rate`: <10% extraction failures
3. `cost_per_instance`: Within 2x of estimate ($0.057)
4. `timeout_rate`: <30%

**Output**: `canary-results.yaml` with pass/fail for each diagnostic

**Expected Result**: All critical diagnostics pass, cost within estimate

---

### Priority 4: Implement Remaining Frameworks

After ReAct works, implement:
- **AutoGPT** (src/frameworks/autogpt.py)
- **Plan-Execute** (src/frameworks/plan_execute.py)
- **Reflexion** (src/frameworks/reflexion.py)

Use ReAct as template. Main differences:
- AutoGPT: Different agent loop, goal-based
- Plan-Execute: Separate planning and execution phases
- Reflexion: Adds reflection loop after execution

---

### Priority 5: Full Pilot Execution

**Command**:
```bash
python src/run_experiment.py \
  --spec experiments/pilot-failure-reproduction/spec.yaml \
  --output experiments/pilot-failure-reproduction/results/
```

**Monitoring**:
- Watch cumulative cost (halt at $10, max $12)
- Check checkpoint file for progress
- Tail logs for errors

**Expected Duration**: 4-6 hours (140 evaluations)

**Output Files**:
```
experiments/pilot-failure-reproduction/results/
├── raw/
│   ├── tool_fab_1_react_gpt4o.json
│   ├── tool_fab_1_react_claude.json
│   └── ...  (140 files)
├── traces/
│   └── ... (full agent traces)
├── checkpoint.json
└── summary.json
```

---

## Common Issues & Solutions

### Issue: LangChain version conflicts
**Solution**: Pin versions in requirements.txt, use venv

### Issue: API rate limits
**Solution**: Add retry logic with exponential backoff (tenacity)

### Issue: Timeout handling
**Solution**: Use threading.Timer or asyncio.wait_for

### Issue: Tool hallucination not detected
**Solution**: Check that available_tools list is correctly passed to agent

### Issue: Cost exceeds estimate
**Solution**: Reduce max_tokens or use cheaper model for testing

---

## Quick Reference

### Key Files
- `src/base_types.py` - All type definitions
- `src/tasks/tool_fabrication.py` - Task generator
- `src/evaluation/extractors.py` - Failure detection
- `experiments/pilot-failure-reproduction/spec.yaml` - Experiment spec
- `experiments/pilot-failure-reproduction/tasks.md` - Task details

### Run Tests
```bash
pytest src/tests/
```

### Check Dependencies
```bash
pip install -r src/requirements.txt
```

### Set API Keys
```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

---

## Success Metrics for Next Session

- [ ] ReAct wrapper working end-to-end
- [ ] Experiment runner executes canary successfully
- [ ] Canary diagnostics all pass
- [ ] Cost estimates validated (within 2x)
- [ ] At least 1-2 framework wrappers complete

**If achieved**: Ready for full pilot execution (Session 10)

---

## Estimated Time

- ReAct wrapper: 2-3 hours
- Experiment runner: 2-3 hours
- Canary run: 30 minutes
- Debugging: 1-2 hours
- **Total**: 6-8 hours (1-2 sessions)

---

## Notes

- Start with ReAct — it's the most standard framework
- Test each component independently before integration
- Use dry-run mode (no API calls) for initial testing
- Commit after each working component
- Update status.yaml after significant progress

Good luck! The infrastructure is solid, now we just need to wire it up.
