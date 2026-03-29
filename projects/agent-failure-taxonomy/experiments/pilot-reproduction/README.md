# Pilot Reproduction Experiment

This experiment validates the taxonomy through controlled reproduction of 3 high-priority failure modes across 2 agent architectures.

## Experiment Design

- **Frameworks**: ReAct, Reflexion
- **LLMs**: GPT-4 Turbo, Claude 3.5 Sonnet
- **Failure modes**: Tool hallucination, infinite loops, self-correction failure
- **Total runs**: 80 (40 instances × 2 LLMs)
- **Budget**: $32 estimated, $50 max

## Hypotheses

1. **Tool hallucination**: ReAct agents will hallucinate tools in ≥50% of runs with 20+ tools
2. **Infinite loops**: ReAct agents will enter loops in ≥40% of ambiguous tasks
3. **Self-correction failure**: Reflexion agents will fail self-correction in ≥60% of complex constraint tasks

## Running the Experiment

### Prerequisites

```bash
# Install dependencies
cd src/
pip install -r requirements.txt

# Set API keys
export OPENAI_API_KEY="..."
export ANTHROPIC_API_KEY="..."
```

### Canary Run (REQUIRED before full run)

```bash
# Run canary to validate infrastructure
python -m src.eval.runner \
  --experiment pilot-reproduction \
  --mode canary \
  --output experiments/pilot-reproduction/canary-results.yaml
```

**Canary must pass all diagnostics before proceeding to full run.**

### Full Run (After canary passes)

```bash
# Run full experiment
python -m src.eval.runner \
  --experiment pilot-reproduction \
  --mode full \
  --output experiments/pilot-reproduction/results/
```

## Expected Outputs

- `canary-results.yaml` — Canary diagnostic results
- `results/` — Per-run JSON files with traces
- `results/summary.json` — Aggregate statistics
- `results/analysis.md` — Preliminary analysis report

## Status

- [x] Protocol designed
- [x] Spec created (awaiting critic review)
- [ ] Infrastructure implemented
- [ ] Canary run
- [ ] Full run
- [ ] Analysis

## Success Criteria

- Infrastructure: All components execute without errors
- Reproduction: ≥2 of 3 failure modes reproduce at ≥50% rate
- Validation: Manual review confirms detector accuracy (≥85%)

See `spec.yaml` for full experiment specification.
