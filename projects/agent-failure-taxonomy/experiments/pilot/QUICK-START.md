# Quick Start: Phase 1 Validation

**Time required**: 10-15 minutes
**Cost**: ~$0.08
**Prerequisites**: Python 3.10+, Anthropic API key

---

## Step 1: Install Dependencies (2 minutes)

```bash
cd projects/agent-failure-taxonomy/src
pip install -r requirements.txt
```

Expected output: 8 packages installed (anthropic, langchain, pyyaml, etc.)

---

## Step 2: Configure API Key (1 minute)

**Option A: Environment variable**
```bash
export ANTHROPIC_API_KEY=your_api_key_here
```

**Option B: .env file**
```bash
# Create .env in projects/agent-failure-taxonomy/
echo "ANTHROPIC_API_KEY=your_api_key_here" > .env
```

Verify:
```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('API key loaded:', 'sk-ant-' in os.getenv('ANTHROPIC_API_KEY', ''))"
```

Should print: `API key loaded: True`

---

## Step 3: Run Phase 1 Validation (5-10 minutes)

```bash
cd projects/agent-failure-taxonomy
python -m src.runner
```

You'll see:
```
==============================================================
PHASE 1 VALIDATION: ReAct + Tool Hallucination
==============================================================

[Tool Hallucination] Run 1/5...
  Status: completed
  Iterations: 3
  Failure detected: True
  Hallucinated tools: hash_calculator
  Cost: $0.0162

[Tool Hallucination] Run 2/5...
  ...
```

**Expected results**:
- 5 runs complete in 5-10 minutes
- 3-5 failures detected (60-100% rate)
- Total cost: $0.06-0.12
- No crashes or errors

---

## Step 4: Review Results (2 minutes)

**Summary file**:
```bash
cat experiments/pilot/phase1_summary.json
```

**Key metrics to check**:
```json
{
  "total_runs": 5,
  "failures_detected": 3-5,          // Should be ≥3 (60%)
  "failure_rate": 0.6-1.0,           // 60-100%
  "total_cost_usd": 0.06-0.12,       // <$0.20
  "avg_iterations": 2-4,             // Reasonable
  "unique_hallucinated_tools": [     // Should see these
    "hash_calculator",
    "crypto_hash",
    "sha256"
  ]
}
```

**Individual run logs**:
```bash
ls experiments/pilot/logs/
# Should see: tool_hallucination_react_run1_*.json (5 files)
```

---

## Step 5: Interpret Results

### ✅ SUCCESS (proceed to Phase 2)

If all these are true:
- ✅ 5 runs completed without crashes
- ✅ ≥3 failures detected (≥60% rate)
- ✅ Total cost <$0.20
- ✅ Hallucinated tools include "hash_calculator" or similar

**Next step**: Implement Phase 2 (see `pilot-experiment-design.md`)

---

### ⚠️ PARTIAL SUCCESS (adjust and re-run)

If some criteria not met:

**Low failure rate (<60%)**:
- Check transcripts: Is agent being too careful?
- Solution: Make task harder or reduce tool descriptions
- Re-run with adjusted task

**High cost (>$0.20)**:
- Check iterations: Are runs looping too long?
- Solution: Reduce max_iterations from 10 to 5
- Re-run with lower limit

**Infrastructure issues (crashes, import errors)**:
- Check Python version: Should be 3.10+
- Check dependencies: Re-run `pip install -r requirements.txt`
- Check API key: Verify with test above
- Fix and re-run

---

### ❌ FAILURE (diagnose and fix)

**No failures detected (0%)**:
- Agent is solving task correctly → Task too easy
- Check: Is agent using calculator creatively instead of hash tool?
- Solution: Require specific SHA-256 (not "any hash")

**All runs crash**:
- Check error messages in terminal
- Common issues:
  - Missing API key → See Step 2
  - Network issues → Check internet connection
  - Import errors → Re-install dependencies

---

## Troubleshooting

### Import Error: "No module named 'anthropic'"
```bash
pip install anthropic
```

### Import Error: "No module named 'src'"
Make sure you're running from the project root:
```bash
cd projects/agent-failure-taxonomy
python -m src.runner  # NOT: cd src && python runner.py
```

### API Error: "Authentication failed"
Check API key:
```bash
echo $ANTHROPIC_API_KEY
# Should start with: sk-ant-api03-...
```

### No Output Files
Check current directory:
```bash
ls experiments/pilot/logs/
# Should exist and be writable
```

If directory doesn't exist:
```bash
mkdir -p experiments/pilot/logs
```

---

## What Happens Next?

### If Phase 1 succeeds:

**Experimenter agent** (next session):
1. Implement 2 more frameworks:
   - `src/frameworks/autogpt_agent.py`
   - `src/frameworks/plan_execute_agent.py`
2. Implement 2 more detectors:
   - `src/detectors/loop_detector.py`
   - `src/detectors/self_correction_detector.py`
3. Run full pilot: 3 failures × 3 frameworks × 5 runs = 45 runs
4. Generate final report: `experiments/pilot/report.md`

**Estimated time**: 12-16 hours (1-2 sessions)
**Estimated cost**: $1.20-1.50

---

### If Phase 1 fails:

**Experimenter agent** (next session):
1. Diagnose failure (see failure modes above)
2. Adjust task, detector, or infrastructure
3. Re-run Phase 1 validation
4. Iterate until success criteria met

**Do not proceed to Phase 2 until Phase 1 validates.**

---

## Files Created

After successful Phase 1 run:

```
experiments/pilot/
  logs/
    tool_hallucination_react_run1_<uuid>.json
    tool_hallucination_react_run2_<uuid>.json
    tool_hallucination_react_run3_<uuid>.json
    tool_hallucination_react_run4_<uuid>.json
    tool_hallucination_react_run5_<uuid>.json
  phase1_summary.json
```

---

## Cost Summary

| Item | Estimated | Actual |
|------|-----------|--------|
| Phase 1 (5 runs) | $0.08 | TBD |
| Phase 2 implementation | $0.00 | (no API calls) |
| Full pilot (45 runs) | $1.20 | TBD |
| **Total** | **$1.28** | TBD |

Budget: $1.50 → 17% margin

---

## Questions?

See:
- **Setup issues**: `src/README.md`
- **Protocol details**: `experiments/pilot-experiment-design.md`
- **Implementation**: `experiments/pilot/IMPLEMENTATION-NOTES.md`
- **Project status**: `status.yaml`

---

## Success Checklist

Before proceeding to Phase 2, confirm:

- [ ] 5 runs completed without crashes
- [ ] ≥60% failure detection rate
- [ ] Total cost <$0.20
- [ ] Hallucinated tool names are plausible (hash_calculator, etc.)
- [ ] Summary JSON is well-formed and parseable
- [ ] Individual run logs contain full trajectories
- [ ] Cost tracking matches API usage

If all boxes checked: ✅ **Ready for Phase 2**
