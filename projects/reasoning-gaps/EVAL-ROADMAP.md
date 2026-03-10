# Evaluation Readiness Roadmap

**Project**: reasoning-gaps (NeurIPS 2026)
**Created**: 2026-03-10
**Goal**: Production-ready evaluation infrastructure for 216K-evaluation empirical run

## Overview

Before running the full ReasonGap evaluation (9 tasks × 5 difficulties × 100 instances × 4 conditions × 12 models = 216K evaluations), we need to validate every layer of the pipeline. This roadmap ensures we don't burn $150+ in API costs on buggy infrastructure.

## Known Issues in Current Code

1. **B1 (Majority)**: Tie-breaking always forces answer to "1" — biases distribution
2. **B5 (Graph Reach)**: `ensure_path` alternates by index but doesn't validate actual yes/no balance
3. **B7 (3-SAT)**: DPLL solver has mutation risk in assignment dict; difficulty 5 (n=64) may be slow
4. **B9 (Negation)**: Prompt prefix "Is it true that..." adds implicit interpretation layer
5. **Answer extraction**: Naive last-line approach; no handling for markdown, refusals, etc.
6. **Budget_cot**: Static budget instead of dynamic computation from task difficulty
7. **Zero tests**: No tests for ground truth, answer extraction, or instance distributions
8. **No checkpoint/resume**: Crash = lost progress on multi-hour runs

## Work Streams

```
Stream A (Benchmark Validation)  ←── BLOCKING
    │
    ├── Stream B (Model Clients)
    ├── Stream C (Answer Extraction)
    └── Stream D (Pipeline Hardening)
            │
            └── Stream E (Integration Tests + Dry Run)
                    │
                    ├── Stream F (Analysis Pipeline)
                    └── Stream G (Batch Orchestration + Modal)
```

### Stream A — Benchmark Validation & Bug Fixes [BLOCKING]

**Goal**: Every generator produces correct, unbiased, reproducible instances.

- [ ] pytest suite for all 9 tasks (B1-B9)
  - [ ] Ground truth correctness (independently verify each answer algorithm)
  - [ ] Deterministic generation (same seed → identical output)
  - [ ] Schema validation (all required fields, correct types)
  - [ ] Distribution checks (balanced yes/no for B5, B7)
  - [ ] Edge cases (min/max difficulty, n_instances=1)
- [ ] Fix B1 tie-breaking bias (randomize direction)
- [ ] Fix B5 balance verification
- [ ] Stress-test B7 DPLL solver against brute-force
- [ ] Fix B9 prompt ambiguity
- [ ] Generate full benchmark data, validate, commit

### Stream B — Model Clients

**Goal**: Reliable, rate-limited, cost-tracked API clients.

- [ ] `AnthropicClient` (Claude Haiku 4.5, Sonnet 4.6, Opus 4.6)
- [ ] `OpenAIClient` (GPT-4o-mini, GPT-4o, o3)
- [ ] `VLLMClient` (OpenAI-compatible endpoint for local models)
- [ ] Rate limiting (configurable RPM per provider)
- [ ] Retry with exponential backoff + jitter
- [ ] Timeout handling
- [ ] Cost tracking per request (input/output tokens × price)
- [ ] Unit tests with mocked responses
- [ ] Optional live smoke tests

### Stream C — Answer Extraction Hardening

**Goal**: Robust answer parsing across diverse model response formats.

- [ ] Handle markdown formatting (`**True**`, `*Yes*`, backticks)
- [ ] Handle numbered answers, bullet points
- [ ] Task-specific normalization (case-insensitive, synonyms)
- [ ] Refusal/non-answer detection
- [ ] Comprehensive test suite: 50+ realistic response patterns
- [ ] Per-task answer validators

### Stream D — Pipeline Hardening

**Goal**: Evaluation survives 72-hour runs without losing progress.

- [ ] Checkpoint/resume: incremental result saving, skip completed instances
- [ ] Dynamic `budget_cot` from task metadata (log(n) for B2, O(k) for B3/B4)
- [ ] `tool_augmented` condition: sandboxed Python code execution
- [ ] Async parallel evaluation (configurable concurrency)
- [ ] Result deduplication
- [ ] Structured logging (replace print statements)

### Stream E — Integration Tests & Dry Run

**Goal**: Prove the full pipeline works end-to-end.

- [ ] Integration test: 5 instances/task → DummyClient → results JSON → verify schema
- [ ] Live dry run: 2 instances × 2 tasks × Haiku → verify correctness manually
- [ ] Validate answer extraction on actual model responses
- [ ] Cost estimation script: compute expected spend before full run

### Stream F — Analysis Pipeline

**Goal**: Raw results → paper-ready tables and figures.

- [ ] Aggregation: per-run JSONs → unified pandas DataFrame
- [ ] Core tables: accuracy by task × model × condition × difficulty
- [ ] CoT lift analysis: (CoT - direct accuracy) by gap type
- [ ] Scale analysis: accuracy by model size within families
- [ ] Statistical testing: bootstrap 95% CIs, McNemar's test
- [ ] Plotting: accuracy-vs-difficulty curves, CoT lift heatmap, phase transition (B7)
- [ ] LaTeX table generation (NeurIPS format)

### Stream G — Batch Orchestration & Infrastructure ✅

**Goal**: One command runs the full 216K evaluation.

- [ ] Modal setup: vLLM serving for open-source models
- [x] Batch runner: iterate models × tasks × conditions, manage concurrency
- [x] Cost estimation pre-flight check
- [x] Progress monitoring (% complete, ETA, spend)
- [x] Result collection into analysis-ready format

## Definition of Ready

All must be true before the full eval run:

1. ✅ All benchmark tests pass (100% ground truth independently verified)
2. ✅ Answer extraction tests pass on 50+ realistic response patterns
3. ✅ At least 1 real model evaluated on 10 instances/task, results manually reviewed
4. ✅ Checkpoint/resume tested (kill + restart a run)
5. ✅ Cost estimate computed and within budget ($150 API + GPU)
6. ✅ Analysis pipeline produces correct output on dry-run data
7. ✅ Benchmark data committed and checksummed

## Evaluation Matrix

| Family | Models | Access | Est. Cost |
|--------|--------|--------|-----------|
| Claude | Haiku 4.5, Sonnet 4.6, Opus 4.6 | API | ~$40 |
| GPT | GPT-4o-mini, GPT-4o, o3 | API | ~$60 |
| Llama 3 | 8B, 70B | vLLM (Modal) | ~$20 GPU |
| Mistral | 7B, Large | vLLM (Modal) | ~$15 GPU |
| Qwen | 7B, 72B | vLLM (Modal) | ~$15 GPU |

**Total**: ~$150 for full run (4,500 instances × 4 conditions × 12 models)

## Timeline

- **Day 1**: Streams A + B + C in parallel
- **Day 2**: Stream D + E (after A validates)
- **Day 3**: Streams F + G
- **Day 4**: Dry run, manual review, go/no-go
- **Day 5+**: Full evaluation run (48-72 hours)
