# Experimental Protocol: Controlled Agent Failure Reproduction

**Date**: 2026-03-29
**Version**: 1.0
**Status**: Draft for critic review
**Budget**: Under $100 for pilot phase

---

## Objective

Empirically validate the failure taxonomy through controlled reproduction experiments across multiple agent architectures. This establishes:

1. **Frequency distribution**: Quantify how often each failure type occurs
2. **Architecture correlation**: Confirm which architectures exhibit which failures
3. **Reproducibility**: Validate that literature failures can be systematically reproduced
4. **Taxonomy validation**: Test whether categories are distinct and observable

---

## Framework Selection

### Selection Criteria
- **Open-source**: Must be publicly available and runnable
- **Documented**: Well-documented APIs and architecture
- **Actively used**: Production deployments exist
- **Architecture diversity**: Cover different agent design patterns
- **LLM-agnostic**: Should work with multiple LLMs (GPT-4, Claude, etc.)

### Selected Frameworks

#### 1. ReAct (LangChain implementation)
**Architecture**: Observation → Reasoning → Action loop
**Why selected**: Most common architecture, well-documented failure patterns
**Known failure modes**: Infinite loops (3.1), context exhaustion (4.3), tool hallucination (1.1)
**Implementation**: LangChain AgentExecutor with ReAct prompt template
**Priority**: HIGH

#### 2. Reflexion (official implementation)
**Architecture**: Actor-Evaluator-Reflector with episodic memory
**Why selected**: Represents self-correction approach, has documented degeneration failures
**Known failure modes**: Confirmation bias (5.2), degeneration-of-thought (5.2), complexity plateaus
**Implementation**: Official Reflexion repo (Python)
**Priority**: HIGH

#### 3. Plan-and-Execute (LangChain implementation)
**Architecture**: Upfront planning → sequential execution with replanning
**Why selected**: Alternative to reactive planning, different failure profile
**Known failure modes**: False completion (5.1), state verification absence (4.1)
**Implementation**: LangChain PlanAndExecute agent
**Priority**: MEDIUM

#### 4. AutoGPT (official implementation)
**Architecture**: Autonomous loop with memory and tool use
**Why selected**: Real-world production system with well-documented failures
**Known failure modes**: Infinite loops (3.1), web hallucinations (2.2), progress monitoring (3.1)
**Implementation**: AutoGPT CLI
**Priority**: MEDIUM (if budget/time permits)

**Decision**: Start with ReAct and Reflexion (HIGH priority). Add Plan-and-Execute if pilot succeeds.

---

## Failure Mode Selection

### Selection Criteria
- **High reproducibility**: Easy or High (80%+ success rate from literature)
- **High impact**: Task failure or severe degradation, not minor issues
- **Category coverage**: At least 1 failure from each major category
- **Architecture specificity**: Failures that should differ across architectures
- **Observable**: Clear success/failure criterion

### Selected Failure Modes (Pilot Phase)

#### Failure 1: Tool Hallucination (Category 1.1)
**Description**: Agent fabricates plausible but non-existent tools
**Source**: Instance 18 (tool count scaling)
**Test design**:
- Provide agent with 20+ tools (some real, some described but not implemented)
- Task requires using existing tools only
- Success: Agent only calls implemented tools
- Failure: Agent invents or calls non-existent tools
**Frameworks**: ReAct, Plan-and-Execute
**Expected**: ReAct higher rate (tight loop, less planning)
**Reproducibility**: Easy
**Priority**: 1

#### Failure 2: Infinite Loop (Category 3.1)
**Description**: Agent repeats same action without progress detection
**Source**: Instance 14 (AutoGPT), Instance 33 (ReAct)
**Test design**:
- Ambiguous task ("research topic X and summarize")
- No explicit termination criteria
- Success: Agent completes or asks for clarification within 15 iterations
- Failure: Agent loops (same action 3+ consecutive times) or exceeds iteration limit
**Frameworks**: ReAct, AutoGPT
**Expected**: ReAct high rate (no explicit progress monitoring)
**Reproducibility**: Medium (task-dependent)
**Priority**: 2

#### Failure 3: Context Degradation (Category 4.3)
**Description**: Performance drops significantly with long context
**Source**: Instance 49 (systematic across models)
**Test design**:
- Multi-step task requiring tracking 10+ pieces of information
- Gradually increase context with irrelevant intermediate observations
- Success: Agent maintains >80% task completion rate
- Failure: Completion rate drops below 50% at 16k+ tokens
**Frameworks**: ReAct, Plan-and-Execute
**Expected**: Both affected, but Plan-and-Execute might handle better (upfront planning)
**Reproducibility**: Easy (fundamental LLM limitation)
**Priority**: 3

#### Failure 4: Self-Correction Failure / Confirmation Bias (Category 5.2)
**Description**: Reflexion repeats same error despite reflection
**Source**: Instance 43 (Reflexion degeneration)
**Test design**:
- Task with subtle constraint that initial attempt likely violates
- Agent reflects and retries up to 3 times
- Success: Agent identifies and corrects error after reflection
- Failure: Agent repeats same error or degenerates
**Frameworks**: Reflexion only
**Expected**: High failure rate on complex constraints (C7 fundamental limitation)
**Reproducibility**: High
**Priority**: 4

#### Failure 5: False Completion (Category 5.1)
**Description**: Agent reports task complete when incomplete
**Source**: Instance 19 (false state reporting)
**Test design**:
- Multi-step task with explicit completion criteria
- Success: Agent only claims completion when all criteria met
- Failure: Agent claims completion with missing requirements
**Frameworks**: ReAct, Plan-and-Execute
**Expected**: Plan-and-Execute might be worse (relies on internal state model)
**Reproducibility**: Medium (depends on task complexity)
**Priority**: 5

#### Failure 6: State Divergence (Category 4.1)
**Description**: Agent's internal model diverges from actual state
**Source**: Instance 25 (false state reporting)
**Test design**:
- Task involving file operations (create, modify, delete)
- Success: Agent's state reports match actual filesystem state
- Failure: Agent claims action succeeded but state unchanged, or vice versa
**Frameworks**: ReAct, Plan-and-Execute
**Expected**: Both affected (C5 fundamental limitation)
**Reproducibility**: Medium
**Priority**: 6

**Pilot scope**: Start with Failures 1, 2, 4 (one from each high-priority category: tool-use, planning, self-correction). These are Easy/High reproducibility and cover three different architectures.

---

## Task Design

### General Principles
- **Deterministic ground truth**: Every task must have verifiable correct answer
- **Minimal ambiguity**: Clear success criteria to avoid evaluation disputes
- **Realistic complexity**: Not toy problems, but representative of real agent use
- **Failure-inducing**: Designed to trigger specific failure modes
- **Cost-efficient**: Keep per-instance cost low (<$0.50 per run)

### Task Templates

#### Task 1: Tool Selection with Scaling (Failure 1)
**Scenario**: Research assistant with 25 tools (15 real, 10 placeholders)
**Query**: "Find recent papers on [topic] and summarize key findings"
**Real tools**:
- `arxiv_search(query)` → returns paper list
- `get_paper_abstract(arxiv_id)` → returns abstract
- `web_search(query)` → returns URLs
- `fetch_url(url)` → returns content
- [11 other real tools]
**Placeholder tools**:
- Described in system prompt but not implemented
- e.g., "semantic_scholar_search", "pubmed_search", "summarize_papers"
**Success criterion**: Agent only calls implemented tools, task completes
**Failure criterion**: Agent calls non-existent tool OR fabricates tool name
**Ground truth**: List of allowed tool calls
**Instances**: 10 different topics (varied difficulty)
**Cost estimate**: ~$0.30 per run (5-10 LLM calls)

#### Task 2: Ambiguous Research Task (Failure 2)
**Scenario**: Research assistant with web search and note-taking
**Query**: "Research [ambiguous topic] and tell me what you find" (no specific deliverable)
**Tools**: `web_search`, `read_url`, `take_notes`, `complete_task`
**Success criterion**: Agent produces summary OR asks clarifying questions within 15 iterations
**Failure criterion**: Agent loops (same action 3+ times) OR exceeds 15 iterations without progress
**Ground truth**: Action sequence log + manual review for progress
**Instances**: 5 different ambiguous topics
**Cost estimate**: ~$0.50 per run (could be expensive if loops)
**Mitigation**: Hard iteration cap at 15

#### Task 3: Multi-Step Memory Task (Failure 3)
**Scenario**: Travel planning with growing context
**Query**: "Plan a trip to [city] considering [10 constraints]"
**Tools**: `search_flights`, `search_hotels`, `check_weather`, `get_attractions`
**Context inflation**: Add irrelevant travel blog excerpts between real observations (target 16k tokens)
**Success criterion**: Final plan satisfies all 10 constraints
**Failure criterion**: Plan violates 3+ constraints OR agent loses track of requirements
**Ground truth**: Constraint checklist
**Instances**: 5 different cities with varying constraint sets
**Cost estimate**: ~$0.40 per run (large context but deterministic)

#### Task 4: Constraint Satisfaction with Reflection (Failure 4)
**Scenario**: Code generation with subtle constraints
**Query**: "Write a function that [does X] satisfying constraints: [C1, C2, C3 (subtle)]"
**Tools**: `write_code`, `run_tests`, `reflect_on_error`
**Reflexion setup**: Agent can reflect and retry up to 3 times
**Success criterion**: Code passes all tests AND satisfies subtle constraint
**Failure criterion**: Agent fails constraint after 3 reflection attempts
**Ground truth**: Test suite + manual constraint verification
**Instances**: 5 different coding tasks with subtle constraints
**Cost estimate**: ~$0.60 per run (3 reflection rounds)

---

## Experimental Design

### Phase 1: Pilot (Current)
**Goal**: Validate infrastructure and reproduce 3 failure modes
**Scope**:
- 2 frameworks (ReAct, Reflexion)
- 3 failure modes (tool hallucination, infinite loops, self-correction)
- 5 instances per failure mode
- 2 LLMs (GPT-4, Claude 3.5 Sonnet)
**Total runs**: 2 frameworks × 3 failures × 5 instances × 2 LLMs = 60 runs
**Estimated cost**: $25-35 (avg $0.40/run)
**Success criteria**:
- ≥50% reproduction rate for each failure mode
- Clear differentiation between frameworks
- Infrastructure handles all runs without manual intervention

### Phase 2: Validation (If pilot succeeds)
**Goal**: Full taxonomy validation across all frameworks
**Scope**:
- 3-4 frameworks
- 6-8 failure modes
- 10 instances per failure mode
- 3 LLMs
**Total runs**: ~540-960 runs
**Estimated cost**: $200-400
**Timeline**: After pilot analysis and protocol refinement

---

## Infrastructure Requirements

### Core Components

#### 1. Framework Wrappers (`src/frameworks/`)
**Purpose**: Unified interface for different agent frameworks
**Components**:
- `base_agent.py`: Abstract base class for all agents
- `react_agent.py`: LangChain ReAct wrapper
- `reflexion_agent.py`: Reflexion wrapper
- `plan_execute_agent.py`: Plan-and-Execute wrapper

**Interface**:
```python
class BaseAgent:
    def run_task(self, task: Task, tools: List[Tool]) -> AgentRun
    def get_trace(self) -> List[AgentStep]
    def reset(self)
```

#### 2. Task Generators (`src/tasks/`)
**Purpose**: Generate task instances with ground truth
**Components**:
- `tool_selection_task.py`: Generate tasks with tool scaling
- `ambiguous_research_task.py`: Generate open-ended research tasks
- `memory_task.py`: Generate multi-constraint tasks with context inflation
- `reflection_task.py`: Generate constraint satisfaction tasks

**Interface**:
```python
class TaskGenerator:
    def generate(self, seed: int, difficulty: int) -> Task
    def verify(self, agent_output: Any) -> VerificationResult
```

#### 3. Failure Detectors (`src/detectors/`)
**Purpose**: Automatically detect failure modes from agent traces
**Components**:
- `tool_hallucination_detector.py`: Detect fabricated tool calls
- `loop_detector.py`: Detect infinite loops and stagnation
- `state_divergence_detector.py`: Compare agent state to ground truth
- `false_completion_detector.py`: Verify task completion claims

**Interface**:
```python
class FailureDetector:
    def detect(self, trace: List[AgentStep], ground_truth: Any) -> FailureReport
```

#### 4. Evaluation Pipeline (`src/eval/`)
**Purpose**: Run experiments with checkpointing and logging
**Components**:
- `runner.py`: Execute experiment runs with checkpointing
- `logger.py`: Structured logging of all agent actions
- `analyzer.py`: Aggregate results and compute statistics

#### 5. Cost Tracking (`src/utils/cost_tracker.py`)
**Purpose**: Track API costs and halt if budget exceeded
**Features**:
- Per-run cost tracking
- Cumulative cost monitoring
- Automatic halt at budget limit

---

## Success Criteria

### Infrastructure Success
- [ ] All framework wrappers can execute sample tasks
- [ ] Task generators produce valid instances
- [ ] Failure detectors correctly identify known failures
- [ ] Checkpointing enables crash recovery
- [ ] Cost tracking prevents budget overruns

### Reproduction Success (Per Failure Mode)
- [ ] **High reproducibility (≥80%)**: Failure consistently reproduced across runs
- [ ] **Medium reproducibility (50-79%)**: Failure reproduced in majority of runs
- [ ] **Low reproducibility (<50%)**: Failure rarely reproduced → revisit task design

### Taxonomy Validation Success
- [ ] **Category distinction**: Different failure modes yield different detector signatures
- [ ] **Architecture correlation**: Predicted architecture differences confirmed
- [ ] **False positive rate <10%**: Detectors don't fire on successful runs
- [ ] **Manual review agreement >90%**: Human reviewers agree with detector judgments

---

## Risk Mitigation

### Risk 1: Cost Overruns
**Mitigation**:
- Hard budget cap enforced by cost tracker
- Start with smallest LLM (GPT-4 Turbo, Claude Haiku)
- Iteration limits on all tasks
- Pilot phase before full runs

### Risk 2: Framework Installation Complexity
**Mitigation**:
- Use Docker containers for each framework
- Pin all dependency versions
- Provide setup scripts with error handling

### Risk 3: Non-Reproducibility
**Mitigation**:
- Start with "Easy" reproducibility failures
- Multiple instances per failure mode (N=5 minimum)
- Document environment details (LLM version, framework version, random seed)
- If failure doesn't reproduce, document why (not a failure of the study)

### Risk 4: Evaluation Ambiguity
**Mitigation**:
- Prefer automated detectors over manual judgment
- When manual review needed, use clear rubrics
- Multiple raters for ambiguous cases
- Report inter-rater reliability

---

## Timeline

### Week 1 (Current): Infrastructure Setup
- Day 1-2: Framework wrappers for ReAct and Reflexion
- Day 3: Task generators for 3 pilot failure modes
- Day 4: Failure detectors
- Day 5: Integration testing

### Week 2: Pilot Experiments
- Day 1: Run pilot (60 runs)
- Day 2-3: Analysis and manual review
- Day 4: Refine protocol based on pilot results
- Day 5: Document findings

### Week 3+: Full Validation (If approved)
- Expand to all failure modes and frameworks
- Full statistical analysis
- Paper results section

---

## Output Format

### Per-Run Data
```json
{
  "run_id": "react_tool_hallucination_001_gpt4",
  "framework": "react",
  "failure_mode": "tool_hallucination",
  "task_id": "tool_selection_001",
  "llm": "gpt-4-turbo",
  "timestamp": "2026-03-29T10:00:00Z",
  "trace": [/* agent steps */],
  "ground_truth": {/* expected behavior */},
  "detector_results": {
    "tool_hallucination_detected": true,
    "fabricated_tools": ["semantic_scholar_search"],
    "confidence": 0.95
  },
  "cost_usd": 0.32,
  "outcome": "failure_reproduced"
}
```

### Aggregate Analysis
- Frequency table: Failure mode × Framework → Reproduction rate
- Architecture correlation matrix
- Cost summary
- Manual review agreement statistics

---

## Next Steps

1. **Create experiment pre-registration spec** (`experiments/pilot-reproduction/spec.yaml`)
2. **Build infrastructure** (`src/` components)
3. **Run pilot** (3 failure modes × 2 frameworks)
4. **Analyze and refine**
5. **Submit for critic review** before full validation

---

## Document Status

**Status**: Draft protocol complete
**Ready for**: Infrastructure implementation
**Estimated pilot cost**: $25-35
**Estimated full cost**: $200-400
**Timeline**: 2-3 weeks for pilot + analysis

