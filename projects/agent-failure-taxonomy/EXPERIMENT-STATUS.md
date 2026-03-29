# 🧪 Experiment Status: Pilot Failure Reproduction

**Last Updated**: 2026-03-29 (Session 8)
**Status**: ✅ Infrastructure complete, ready for execution

---

## Quick Start

```bash
# Install dependencies
cd projects/agent-failure-taxonomy
pip install -r src/requirements.txt

# Run canary (1 instance, $0.10)
python src/run_experiment.py --spec experiments/pilot-failure-reproduction/spec.yaml --canary

# If canary passes, run full pilot (18 instances, $9-15)
python src/run_experiment.py --spec experiments/pilot-failure-reproduction/spec.yaml
```

---

## What's Ready

✅ **Experimental protocol** (`experiments/pilot-failure-reproduction/spec.yaml`)
- 3 failure modes: tool hallucination, infinite loops, false completion
- 9 tasks with ground truth
- 2 models: gpt-4o-mini, claude-3-5-sonnet
- 18 total instances

✅ **Infrastructure** (`src/`)
- ReAct agent wrapper with logging
- 9 task definitions
- Automated failure detection (4 types)
- Structured logging and cost tracking
- Main experiment runner

✅ **Documentation**
- Full execution plan: `experiments/pilot-failure-reproduction/README.md`
- Session summary: `SESSION-8-SUMMARY.md`

---

## Next Steps

### 1. Canary Run (IMMEDIATE)
- **Purpose**: Validate pipeline before full run
- **Cost**: $0.10
- **Command**: `python src/run_experiment.py --spec experiments/pilot-failure-reproduction/spec.yaml --canary`

### 2. Full Pilot (After canary passes)
- **Scope**: 18 instances
- **Cost**: $9-15
- **Timeline**: ~30-60 minutes

### 3. Analysis
- Compute failure rates by category
- Test predictions (P1-P3)
- Spot-check detector accuracy
- Write findings in `analysis.md`

---

## Success Criteria

**Pilot succeeds if**:
- ✅ ≥2 of 3 failure categories reproduced at >30% rate
- ✅ Automated detection ≥80% accurate
- ✅ Total cost <$20

**This validates**: Taxonomy is empirically grounded (not anecdotal)

---

## Files Generated

```
experiments/pilot-failure-reproduction/
├── spec.yaml                    # Experiment protocol
├── README.md                    # Execution plan
├── canary-results/             # Canary outputs (after run)
│   ├── {instance}.json         # Trace file
│   └── canary_summary.json     # Diagnostics
└── results/                    # Full pilot outputs (after run)
    ├── {instance}.json × 18    # Trace files
    ├── full_summary.json       # Aggregate stats
    └── analysis.md             # Findings (manual)
```

---

## Budget

| Item | Cost | Status |
|------|------|--------|
| Canary | $0.10 | Ready |
| Full pilot | $9-15 | Ready |
| Buffer | $5 | Reserved |
| **Total** | **~$15** | **Within $645 available** |

---

## Infrastructure Overview

**7 Python modules** (1,407 lines):

1. `frameworks/react_agent.py` — LangChain ReAct wrapper
2. `tasks/task_definitions.py` — 9 tasks with ground truth
3. `utils/logger.py` — Execution logging, cost tracking
4. `utils/failure_detection.py` — Automated classification
5. `run_experiment.py` — Main runner (canary + full modes)
6. `requirements.txt` — Dependencies
7. `README.md` — Documentation

---

## Predictions Being Tested

**P1: Tool Hallucination Scales with Tool Count**
- Hypothesis: Hallucination rate increases ≥20% from 5 → 20 tools
- Tests: C6 (Tool Grounding) limitation

**P2: Infinite Loops on Ambiguous Tasks**
- Hypothesis: ≥50% of ambiguous tasks timeout or show no progress
- Tests: C3 (Meta-Cognitive Monitoring) limitation

**P3: False Completion on Complex Tasks**
- Hypothesis: ≥30% of complex tasks end with <80% requirements met
- Tests: C3 + C7 (Self-Correction) limitations

---

## Routing Status: ✅ FIXED

**Historical issue** (Sessions -7 to -1, 2026-03-25):
- 7 consecutive wrong agent assignments (Researcher instead of Experimenter)
- $14-35 wasted, 0 progress

**Session 8 test** (2026-03-29):
- ✅ Experimenter correctly assigned
- ✅ Major progress made (infrastructure complete)
- ✅ Routing logic validated

**Conclusion**: Phase-based scheduling now works correctly.

---

## Contact

See full details:
- Experimental design: `experiments/pilot-failure-reproduction/README.md`
- Session summary: `SESSION-8-SUMMARY.md`
- Project status: `status.yaml`
