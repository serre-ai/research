# Integration Roadmap — APIs & Services

External API and service integrations for the Serre AI autonomous research platform. This is a **parallel workstream** to the [Intelligence Stack Master Roadmap](../MASTER-ROADMAP.md) — that roadmap covers internal capabilities (knowledge graph, event bus, research planner), this one covers external service integrations.

Sprint labels use the `INT-` prefix to distinguish from OpenClaw sprints (1-9) and Intelligence Stack sprints (1-10).

## Relationship to Other Roadmaps

| Roadmap | Scope | Location |
|---------|-------|----------|
| [Master Roadmap](../MASTER-ROADMAP.md) | Intelligence Stack — internal capabilities (KG, events, planner, verification) | `docs/MASTER-ROADMAP.md` |
| [OpenClaw Roadmap](../../openclaw/ROADMAP.md) | Collective agent framework — forum, governance, heartbeats, triggers | `openclaw/ROADMAP.md` |
| **This Roadmap** | External APIs/services — literature, compute, search, observability | `docs/integrations/ROADMAP.md` |

### Synergies with Intelligence Stack

| Master Sprint | Integration Sprint | Synergy |
|---------------|-------------------|---------|
| Sprint 6: Literature Intelligence | INT-1: Semantic Scholar | S6 builds the monitor; INT-1 provides the data source. Build INT-1 first. |
| Sprint 7: Closed-Loop Experiments | INT-2: Modal multi-model | S7 designs experiment loops; INT-2 provides cheap compute to run them. |
| Sprint 5: Verification Layer | INT-3: Serper | S5 verifies claims; INT-3 lets it search for external evidence. |
| Sprint 10: Meta-Learning | INT-4: W&B | S10 analyzes effectiveness; INT-4 provides the experiment tracking data. |

**Recommended execution:** Run INT-1 and INT-2 before or in parallel with Intelligence Stack Phase 2 (Sprints 4-8). The external services provide data and compute that the intelligence modules consume.

---

## Integration Index

| Integration | Cost | Status | Primary Agent | Doc |
|-------------|------|--------|---------------|-----|
| [Semantic Scholar](./semantic-scholar.md) | Free | Planned | Noor | Literature graph, citation tracking, paper recommendations |
| [Modal](./modal.md) | ~$10-15/eval sweep | Planned (access exists) | Kit | GPU compute for open-weight model evals |
| [HuggingFace Hub](./huggingface-hub.md) | Free | Planned | Kit | Model/dataset discovery, leaderboard data |
| [Serper](./serper.md) | Free (2.5k/mo) | Planned | All agents | Web search for grounding and discovery |
| [Weights & Biases](./wandb.md) | Free tier | Planned | Kit | Experiment tracking and dashboards |

## Dependencies

```
Semantic Scholar ─────────────────────────┐
                                          ├─→ Full literature pipeline
Serper ───────────────────────────────────┘

HuggingFace Hub ──┐
                   ├─→ Full eval pipeline (open models)
Modal ────────────┘

W&B ──────────────────→ Observability layer (benefits from Modal + eval data)
```

Semantic Scholar and HuggingFace Hub are independent foundations — no dependencies, zero cost.
Modal depends on HuggingFace Hub for model discovery (which models to run).
W&B benefits from everything upstream (more data to track).
Serper is fully independent.

---

## Sprint Plan

### INT-1: Foundations — Literature + Model Discovery
**Timeline:** Week of 2026-03-17
**Theme:** Free APIs, zero risk, immediate value
**Prerequisite:** None (can start immediately)

#### Team A: Literature Pipeline (Noor + Eli)
- [ ] Request Semantic Scholar API key
- [ ] Build `orchestrator/src/semantic-scholar.ts` — HTTP client with rate limiting
- [ ] Build `openclaw/skills/semantic-scholar/` — skill commands (search, paper, citations, recommend, author)
- [ ] Wire into Noor's heartbeat: after arxiv scan, run recommendations on top findings
- [ ] Test: search "chain-of-thought reasoning" and verify structured results

**Eli builds the infra, Noor validates it works for research.**

#### Team B: Model Discovery + Modal Bootstrap (Kit + Eli)
- [ ] Add `@huggingface/hub` to orchestrator package.json
- [ ] Build `orchestrator/src/huggingface.ts` — model search, dataset search, model info
- [ ] Build `openclaw/skills/huggingface/` — skill commands (models, model, datasets, dataset)
- [ ] Create `modal/` directory at project root
- [ ] Build `modal/eval_runner.py` — vLLM inference for Qwen3-8B-FP8 (test model)
- [ ] Create Modal volume for cached model weights
- [ ] Test: send 100 eval instances to Modal, verify results

**Kit drives model selection and eval testing. Eli builds Modal infra.**

#### Deploy checklist
- [ ] Add env vars to VPS: `SEMANTIC_SCHOLAR_API_KEY`, `HF_TOKEN`
- [ ] Deploy new skills to `openclaw/skills/`
- [ ] `npm run build --workspace=orchestrator` passes
- [ ] Manual test of Semantic Scholar from VPS
- [ ] Manual test of HuggingFace model search from VPS
- [ ] Modal eval runner returns valid results for 100 test instances

---

### INT-2: Compute + Search — Expand Reach
**Timeline:** Week of 2026-03-24
**Theme:** Open-model evals + web search
**Prerequisite:** INT-1 (Modal bootstrap, HuggingFace client)

#### Team A: Modal Multi-Model (Kit + Eli)
- [ ] Add model configs: Llama 3.1 70B, Qwen3-72B, DeepSeek-V3, Mistral Large 2
- [ ] Create separate Modal apps per model family (GPU sizing varies)
- [ ] Build `orchestrator/src/modal-runner.ts` — HTTP client, model routing, fallback to API
- [ ] Cost tracking: log GPU-seconds and cost to budget_events
- [ ] Run full B1-B9 eval on Qwen3-8B-FP8 as end-to-end validation
- [ ] Create `model_registry` DB table — track evaluated + candidate models

**First real eval sweep on open model. Proves the pipeline end-to-end.**

#### Team B: Web Search (Noor + Eli)
- [ ] Sign up for Serper free tier
- [ ] Build `orchestrator/src/serper.ts` — HTTP client with budget cap (200/day)
- [ ] Build `openclaw/skills/web-search/` — search, scholar, news, verify commands
- [ ] Firecrawl pairing: `fetch` subcommand pipes Serper URL → Firecrawl extraction
- [ ] Wire into Noor's heartbeat: web search for blog posts about competitor work
- [ ] Budget integration: $0.001/query to budget_events

#### Team C: Citation Tracking (Noor + Lev)
- [ ] Create `paper_tracking` and `citation_snapshots` DB tables
- [ ] Seed with reasoning-gaps reference list (~30 papers)
- [ ] Build weekly citation sweep cron job
- [ ] Add citation velocity to Sol's standup and Lev's digest

#### Deploy checklist
- [ ] Add env vars to VPS: `SERPER_API_KEY`
- [ ] Deploy Modal multi-model configs
- [ ] Deploy Serper skill
- [ ] Deploy citation tracking tables
- [ ] Full B1-B9 eval on one open model completes successfully
- [ ] Web search returns results from VPS

---

### INT-3: Observability + Full Coverage
**Timeline:** Week of 2026-03-31
**Theme:** W&B dashboards + open model eval sweep
**Prerequisite:** INT-2 (Modal multi-model, eval pipeline proven)

#### Team A: W&B Integration (Kit + Eli)
- [ ] Create `deepwork-research` W&B team
- [ ] Build `orchestrator/src/wandb-logger.ts` — eval run logging, budget logging
- [ ] Backfill: log existing 121k eval results as historical W&B runs
- [ ] Wire into session-runner.ts and modal-runner.ts — auto-log on eval completion
- [ ] Create dashboards: Eval Overview, CoT Lift Analysis, Cost Tracking

#### Team B: Open Model Eval Sweep (Kit)
- [ ] Run B1-B9 × 3 conditions on Llama 3.1 70B
- [ ] Run B1-B9 × 3 conditions on Qwen3-72B
- [ ] Run B1-B9 × 3 conditions on DeepSeek-V3
- [ ] Run B1-B9 × 3 conditions on Mistral Large 2
- [ ] All results logged to both PostgreSQL and W&B

#### Team C: Cross-Reference + Competing Work (Noor + Vera)
- [ ] HuggingFace leaderboard cross-reference against our eval results
- [ ] Semantic Scholar competing work scanner (recommendations-based)
- [ ] Serper Google Scholar as complement to Semantic Scholar
- [ ] Auto-generate comparison tables for the paper

#### Deploy checklist
- [ ] W&B dashboards accessible at wandb.ai/deepwork-research
- [ ] 4 new open models fully evaluated
- [ ] Model coverage: 9 API + 4 open = 13 models
- [ ] Leaderboard comparison table generated
- [ ] Competing work scanner running in Noor's heartbeat

---

### INT-4: Polish + Paper Integration
**Timeline:** Week of 2026-04-07
**Theme:** Wire everything into the paper
**Prerequisite:** INT-3 (all integrations live, eval data collected)

#### All Teams
- [ ] Wire W&B into budget-tracker.ts for live cost dashboards
- [ ] Log paper drafts as W&B artifacts (versioned)
- [ ] Add open-model results to reasoning-gaps paper
- [ ] Update paper's "Models" section with expanded model coverage
- [ ] Update paper's "Results" section with 13-model analysis
- [ ] Ablation studies on Modal: temperature sweeps, prompt variants
- [ ] Final citation check: any new competing work since INT-1?
- [ ] Paper Progress dashboard on W&B

---

## Agent Assignments Summary

| Agent | INT-1 | INT-2 | INT-3 | INT-4 |
|-------|-------|-------|-------|-------|
| **Eli** | S2 client + HF client + Modal bootstrap | Modal multi-model + Serper client | W&B logger | Bug fixes |
| **Kit** | HF model discovery + Modal test | Modal validation eval + model registry | Open model eval sweep + W&B | Ablation studies |
| **Noor** | S2 skill testing | Web search testing + citation tracking | Competitor scanner | Final lit review |
| **Vera** | — | — | Leaderboard cross-ref | Paper review |
| **Sol** | Dispatch + coordinate | Dispatch + coordinate | Dispatch + coordinate | Dispatch + coordinate |
| **Lev** | — | Citation tracking in digest | — | — |
| **Maren** | — | — | — | Paper integration |
| **Rho** | — | — | Challenge open-model results | Challenge paper claims |
| **Sage** | — | — | — | Pre-submission retrospective |

## Execution Timeline

```
Week of 03/17:  INT-1 (S2 + HF + Modal bootstrap)
Week of 03/24:  INT-2 (Modal multi-model + Serper + citations)
Week of 03/31:  INT-3 (W&B + open model sweep + cross-reference)
Week of 04/07:  INT-4 (Paper integration + ablations + polish)
```

Can run in parallel with Intelligence Stack sprints:
```
INT-1 ─── INT-2 ─── INT-3 ─── INT-4
  │         │         │
  │    IS Sprint 1+3  │    IS Sprint 4+5+6
  └─ feeds into ──────┘─── feeds into ───→ IS Sprint 7 (Closed-Loop)
```

## Budget Impact

| Integration | Monthly Cost | One-time Setup |
|-------------|-------------|----------------|
| Semantic Scholar | $0 | API key request |
| HuggingFace Hub | $0 | Free account + token |
| Serper | $0-5 | Free tier signup |
| W&B | $0 | Free tier signup |
| Modal | $40-60 for full sweep | Already configured |
| **Total** | **$40-65** | **~1 hour setup** |

Current monthly budget: $1,000. This adds ~$50-65/month while roughly doubling the platform's research capabilities (13 models instead of 9, live dashboards, citation tracking, web grounding).

## Success Criteria

By end of INT-4:
- [ ] 13+ models evaluated on B1-B9 × 3 conditions
- [ ] Live W&B dashboards accessible from browser
- [ ] Weekly citation tracking on 30+ reference papers
- [ ] Agents can web-search and ground their claims
- [ ] Open-model evals cost <$15 per sweep (vs ~$40+ via API)
- [ ] Paper updated with expanded model coverage and results
- [ ] All integrations budget-tracked through existing budget_events pipeline
