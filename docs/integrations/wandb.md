# Weights & Biases Integration

## Overview

Weights & Biases (W&B) provides experiment tracking, interactive dashboards, comparison tables, and artifact versioning. It replaces the custom one-shot analysis pipeline with a live, queryable experiment registry.

The current analysis pipeline (`projects/reasoning-gaps/benchmarks/results/analysis/`) produces static LaTeX tables and PNG figures. W&B makes this dynamic: every eval run is logged, dashboards update in real time, and you (Oddur) can inspect results from a browser without SSH.

## API Details

- **SDK:** `wandb` npm package (or Python `wandb` package — both available)
- **Auth:** `WANDB_API_KEY` env var
- **Free tier:** Unlimited experiments, 100GB storage, public projects only (sufficient for this project)
- **Paid:** $50/user/month for private projects (not needed unless we want privacy)
- **Cost:** $0 on free tier
- **Entity:** Create a `serre-ai` team on wandb.ai

### Key Concepts

| Concept | Maps To |
|---------|---------|
| **Project** | `reasoning-gaps`, `agent-failure-taxonomy` |
| **Run** | One eval run: model × task × condition |
| **Metrics** | accuracy, cot_lift, latency_ms, cost_usd |
| **Config** | model, task, condition, difficulty, n_instances |
| **Artifact** | Paper PDFs, figure PNGs, LaTeX tables |
| **Table** | Full eval_results for interactive exploration |

### Python SDK Usage (Modal + W&B pairing)

```python
import wandb

run = wandb.init(
    project="reasoning-gaps",
    name="qwen3-72b_B3_cot",
    config={
        "model": "qwen3-72b",
        "task": "B3",
        "condition": "cot",
        "n_instances": 200,
    },
)

# Log metrics after eval
run.log({
    "accuracy": 0.847,
    "cot_lift": 0.156,
    "latency_ms": 2340,
    "cost_usd": 1.23,
})

# Log full results as a Table
table = wandb.Table(columns=["instance_id", "correct", "difficulty", "response_tokens"])
for result in results:
    table.add_data(result.id, result.correct, result.difficulty, result.tokens)
run.log({"results": table})

run.finish()
```

### TypeScript SDK Usage (Orchestrator)

```typescript
import wandb from "@wandb/sdk";

// Log eval run from orchestrator
await wandb.init({ project: "reasoning-gaps" });
await wandb.log({ accuracy: 0.847, cot_lift: 0.156 });
await wandb.finish();
```

## Integration Architecture

### Orchestrator Integration: `orchestrator/src/wandb-logger.ts`

Module that wraps W&B logging:
- `logEvalRun(model, task, condition, results)` — creates a W&B run with config + metrics
- `logBudgetEvent(event)` — logs cost data as metrics
- `logArtifact(path, type)` — uploads paper drafts, figures as versioned artifacts

### Where Logging Happens

| Event | Trigger Point | What's Logged |
|-------|--------------|---------------|
| Eval run completes | `session-runner.ts` after eval | accuracy, cot_lift, latency, cost, config |
| Modal eval completes | `modal-runner.ts` after batch | Same as above, plus gpu_seconds |
| Budget event | `budget-tracker.ts` on record | cost_usd, provider, project, model |
| Paper draft saved | Agent commit to paper/ | Paper PDF as artifact |
| Analysis figures | Analysis pipeline | PNG/PDF figures as artifacts |

### Dashboard Structure

Create these W&B dashboards:

1. **Eval Overview** — All models × tasks heatmap of accuracy. Filter by condition.
2. **CoT Lift Analysis** — CoT lift by task type (depth, serial, intractability, architectural).
3. **Cost Tracking** — Daily spend by provider, cumulative monthly.
4. **Model Comparison** — Side-by-side runs for any two models on the same task.
5. **Paper Progress** — Artifact versions over time showing paper evolution.

## Use Cases by Agent

| Agent | Use Case |
|-------|----------|
| **Kit** | Primary logger. Every eval run → W&B. Checks dashboards for anomalies. |
| **Vera** | Reviews W&B dashboards instead of static tables. Interactive comparison. |
| **Sol** | Checks cost dashboard for budget projections. Sees eval progress at a glance. |
| **Maren** | Pulls figures directly from W&B artifacts for paper. Ensures figures match data. |
| **Noor** | Logs literature scan results as runs (papers found, relevance scores). |

## Roadmap

### Phase 1: Eval Run Logging (INT-3)
- [ ] Create `serre-ai` team on wandb.ai
- [ ] Add `wandb` to orchestrator dependencies (or Python venv on VPS)
- [ ] Create `orchestrator/src/wandb-logger.ts` — core logging module
- [ ] Backfill: log existing 121k eval results as historical runs
- [ ] Create Eval Overview dashboard

### Phase 2: Live Integration (INT-4)
- [ ] Wire wandb-logger into session-runner.ts — auto-log on eval completion
- [ ] Wire wandb-logger into modal-runner.ts — auto-log Modal evals
- [ ] Wire into budget-tracker.ts — log cost events
- [ ] Create Cost Tracking and CoT Lift dashboards

### Phase 3: Artifact Tracking (Sprint 14)
- [ ] Log paper drafts as versioned artifacts
- [ ] Log analysis figures as artifacts linked to source runs
- [ ] Build Paper Progress dashboard
- [ ] Wire Maren to pull latest artifacts when writing

## Alternatives Considered

- **MLflow** — Open source, self-hosted. More work to set up and maintain on VPS. W&B's hosted free tier avoids ops burden.
- **Neptune** — Similar to W&B. Smaller community, less documentation.
- **Custom DB views** — What we have now. Works but static, no interactive exploration, no browser access.

W&B was chosen for: zero ops overhead (hosted), free tier sufficient, best dashboarding, largest community (most examples/docs).

## References

- [W&B Documentation](https://docs.wandb.ai/)
- [W&B Experiments Overview](https://docs.wandb.ai/models/track)
- [W&B Pricing](https://wandb.ai/site/pricing/)
- [W&B JavaScript SDK](https://www.npmjs.com/package/@wandb/sdk)
