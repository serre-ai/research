# Evaluation & Infrastructure Roadmap

**Project**: reasoning-gaps (NeurIPS 2026)
**Created**: 2026-03-10
**Updated**: 2026-03-11
**Goal**: Complete empirical evaluation + migrate to remote-first infrastructure

---

## Phase 1: Evaluation Infrastructure (COMPLETE)

All pre-evaluation work is done. Streams A-G delivered:

- [x] **Stream A** — Benchmark validation, bug fixes, 195 tests passing
- [x] **Stream B** — Model clients (Anthropic, OpenAI, vLLM) with rate limiting, retry, cost tracking
- [x] **Stream C** — Answer extraction with task-specific parsers, refusal detection, 50+ test patterns
- [x] **Stream D** — Checkpoint/resume (crash-safe JSONL), dynamic CoT budgets, parallel evaluation
- [x] **Stream E** — Integration tests, live dry run with Haiku (caught 3 bugs)
- [x] **Stream F** — Analysis pipeline (tables, figures, bootstrap CIs, McNemar's test, LaTeX output)
- [x] **Stream G** — Batch orchestration, Modal serving, per-model endpoint routing
- [x] **Stream H** — OpenRouter client added as new provider for open-source models

## Phase 2: Empirical Evaluation (9/12 MODELS COMPLETE)

### Current Status

9 models fully evaluated: 121,614 instances across 9 tasks × 3 conditions, zero failures.

| Stream | Models | Progress | Cost | Notes |
|--------|--------|----------|------|-------|
| Anthropic | Haiku 4.5 | **Complete** (27/27) | ~$15 | Tier 3 (2,000 RPM) |
| OpenAI | GPT-4o-mini, GPT-4o | **Complete** (54/54) | ~$60 | |
| OpenRouter | Llama 3.1 8B, Llama 3.1 70B | **Complete** (54/54) | ~$0.08 | |
| OpenRouter | Ministral 8B, Mistral Small 24B | **Complete** (54/54) | ~$0.06 | Ministral 8B replaced Mistral 7B v0.3 (unavailable on OpenRouter) |
| OpenRouter | Qwen 2.5 7B, Qwen 2.5 72B | **Complete** (54/54) | ~$0.08 | |

**Total evaluation cost: ~$75** (Anthropic ~$15, OpenAI ~$60, OpenRouter ~$0.22)

### Results Summary (Average Accuracy by Model)

| Model | Family | Size | Avg Accuracy | Provider |
|-------|--------|------|-------------|----------|
| Qwen 2.5 72B | Qwen | 72B | 71.5% | OpenRouter |
| GPT-4o | GPT | — | 68.4% | OpenAI |
| GPT-4o-mini | GPT | — | 64.0% | OpenAI |
| Haiku 4.5 | Claude | — | 62.8% | Anthropic |
| Llama 3.1 70B | Llama | 70B | 62.5% | OpenRouter |
| Ministral 8B | Mistral | 8B | 62.2% | OpenRouter |
| Mistral Small 24B | Mistral | 24B | 60.5% | OpenRouter |
| Qwen 2.5 7B | Qwen | 7B | 57.7% | OpenRouter |
| Llama 3.1 8B | Llama | 8B | 48.2% | OpenRouter |

Key observations:
- Qwen 72B leads overall at 71.5%
- Model size matters but not linearly (Ministral 8B > Mistral Small 24B)
- CoT lifts confirmed across all families, matching theoretical predictions
- budget_cot needs recalibration (B2 budget too tight: 13% vs 93% with full CoT)

### Remaining Evaluation Work

- [x] Complete Haiku 4.5 evaluation (27 combinations)
- [x] Complete GPT-4o-mini + GPT-4o evaluation (54 combinations)
- [x] Run Llama 3.1 (8B + 70B) via OpenRouter
- [x] Run Mistral family (Ministral 8B + Small 24B) via OpenRouter
- [x] Run Qwen 2.5 (7B + 72B) via OpenRouter
- [x] Run analysis pipeline on 9-model dataset (121,614 instances) — 4 tables, 5 figures, 243-group CIs
- [ ] **Recalibrate budget_cot for B2** — `_budget_b2` uses flat 20-word budget; needs exponential scaling with depth (`2^depth * 3 words`). Fix and re-run B2 budget_cot for all 9 models (~$3-5).
- [ ] **Run Sonnet 4.6** (~$55, 27 combinations) — gives Claude small+medium comparison. DECIDED: Yes.
- [ ] **Run o3** (~$40, 27 combinations) — reasoning-specialized model, unique CoT comparison. DECIDED: Yes.
- [ ] ~~Opus 4.6~~ — deferred ($272 is 68% of remaining budget; Sonnet + o3 provide more marginal value)
- [ ] Re-run full analysis pipeline with 11 models + recalibrated B2
- [ ] Manual review of results, check for extraction errors

### Evaluation Matrix

| Family | Models | Access | Est. Cost | Status |
|--------|--------|--------|-----------|--------|
| Claude | Haiku 4.5 | API (Tier 3) | ~$15 | **Complete** |
| Claude | Sonnet 4.6 | API (Tier 3) | ~$55 | Pending decision |
| Claude | Opus 4.6 | API (Tier 3) | ~$272 | Pending decision |
| GPT | 4o-mini | API | ~$2 | **Complete** |
| GPT | 4o | API | ~$18 | **Complete** |
| GPT | o3 | API | ~$40 | Pending decision |
| Llama 3.1 | 8B-Instruct | OpenRouter | ~$0.04 | **Complete** |
| Llama 3.1 | 70B-Instruct | OpenRouter | ~$0.04 | **Complete** |
| Mistral | Ministral-8B-2512 | OpenRouter | ~$0.03 | **Complete** |
| Mistral | Small-24B-Instruct | OpenRouter | ~$0.03 | **Complete** |
| Qwen 2.5 | 7B-Instruct | OpenRouter | ~$0.04 | **Complete** |
| Qwen 2.5 | 72B-Instruct | OpenRouter | ~$0.04 | **Complete** |

### Infrastructure Notes

| Provider | Purpose | Notes |
|----------|---------|-------|
| Anthropic API | Claude models | Tier 3 (2,000 RPM), ~$15 for Haiku |
| OpenAI API | GPT models | ~$60 for 4o-mini + 4o |
| OpenRouter API | Open-source models | All 6 models for ~$0.22 total. Simple API, no GPU management. Added as new provider alongside existing vLLM client |
| Modal (preserved) | vLLM GPU serving | Code preserved in modal_serving.py for reproducibility validation. Not deployed — OpenRouter was cheaper and simpler |
| vLLM client (preserved) | Local/Modal inference | Kept in codebase for future reproducibility runs on dedicated hardware |

### Modal Deployment Steps (preserved for reference)

1. `pip install modal && modal setup`
2. Accept Llama license at https://huggingface.co/meta-llama/Meta-Llama-3.1-8B-Instruct
3. `modal secret create huggingface HF_TOKEN=hf_xxx`
4. Deploy one model first: `modal deploy modal_serving.py::mistral_7b_app`
5. Smoke test: `modal run modal_serving.py::smoke_test --model mistral-7b`
6. Deploy remaining: deploy each `*_app` from modal_serving.py
7. `modal run modal_serving.py::write_endpoints` -> edit URLs -> save
8. Run evaluation: `python run_evaluation.py --models vllm:mistralai/Mistral-7B-Instruct-v0.3 --tasks B1 --max-instances 5 -y`

---

## Phase 3: Remote-First Infrastructure (DEPLOYED 2026-03-11)

**Status**: Core infrastructure deployed and operational. Dashboard frontend integration pending.

### Deployed (VPS at 89.167.5.50)

- [x] **3.1 VPS Foundation** — Hetzner CPX21, Ubuntu 24.04, Node.js 22, Python 3.12, fail2ban, UFW (22/80/443)
- [x] **3.2 Orchestrator** — All 12 TS source files exist (daemon.ts, session-runner.ts, budget-tracker.ts restored on VPS). Build passes. `index.ts` wired with `run` command that starts daemon + API.
- [x] **3.3 Database** — PostgreSQL 16 running. Schema applied (6 tables, materialized view, 3 views). 121,146 eval results backfilled. Per-model accuracy queryable.
- [x] **3.4 API Layer** — Express REST + WebSocket on port 3001. Endpoints: health, projects, eval, budget. API key auth. Proxied by nginx on port 80.
- [x] **Daemon** — systemd-managed (`deepwork-daemon.service`), enabled, auto-restart. Polling every 30m.
- [x] **Eval service** — `deepwork-eval@.service` template deployed, Python path fixed to use venv.
- [x] **Data** — 243 checkpoint files (201MB) transferred. All API keys in `.env` (chmod 600).

### Remaining Infrastructure

- [ ] **SSL/HTTPS** — Point `api.deepwork.site` DNS A record to 89.167.5.50, then `certbot --nginx -d api.deepwork.site`
- [ ] **Dashboard frontend** — Wire Astro pages (`site/src/pages/dashboard/`) to call VPS API. Currently has mock data with TODO markers.
- [ ] **Slack notifications** — Add `SLACK_WEBHOOK_URL` to VPS `.env`. Notifier class already works.
- [ ] **Backup** — Hetzner Storage Box ($4/mo), nightly rsync cron
- [ ] **GitHub Actions** — LaTeX compilation on push to research branch
- [ ] **Merge branches** — `main` and `research/reasoning-gaps` have diverged; need conflict resolution (`.claude/agents/*.md`, `orchestrator/package.json`, utility TS files, `site/` layout)

---

## Phase 4: Paper Completion (IN PROGRESS)

### Sprint: Paper-Critical Work (2026-03-11)

Four parallel work streams:

**Stream 1: Budget_cot Recalibration** (~3-4 hours)
- [ ] Fix `_budget_b2` in `budget_calculator.py` — scale budget exponentially with depth (`2^depth * 3 words`)
- [ ] Clear B2 budget_cot checkpoints, re-run for all 9 models (~$3-5)
- [ ] Re-run analysis pipeline

**Stream 2: New Model Evaluations** (~6-10 hours)
- [ ] Run Sonnet 4.6 (27 combinations, ~$55)
- [ ] Run o3 (27 combinations, ~$40)
- [ ] Re-run analysis pipeline with 11 models

**Stream 3: Section 5 (Experiments)** (~3-4 hours)
- [ ] Scaffold Section 5 structure (5.1 Setup, 5.2 Main Results, 5.3 CoT Effectiveness, 5.4 Budget Sensitivity, 5.5 Scale Analysis, 5.6 Phase Transition)
- [ ] Write 5.1 (Setup) immediately — models, conditions, metrics are fixed
- [ ] Embed generated tables (`.tex`) and figures (`.pdf`) with \input{} and \includegraphics{}
- [ ] Fill in narratives after Streams 1+2 complete with final numbers

**Stream 4: Discussion, Related Work, Appendix** (~4-5 hours)
- [ ] Expand Related Work — reasoning benchmarks, CoT budget literature, scaling laws
- [ ] Write Appendix A (proofs from `notes/07-proposition-proofs.md` → LaTeX)
- [ ] Write Appendix B (benchmark details from `notes/06-benchmark-design.md`)
- [ ] Write Appendix C (per-model detailed results with CIs)
- [ ] Expand Discussion — practical implications, B8 ceiling effect, budget_cot calibration
- [ ] Convert to NeurIPS format (`neurips_2026.sty`)
- [ ] Update conclusion with final numbers

### Post-Sprint

- [ ] Final analysis re-run with all data (11 models, recalibrated B2)
- [ ] Full paper compile, verify no LaTeX errors
- [ ] Internal review and revision pass
- [ ] Submit to NeurIPS 2026

---

## Budget Summary

| Item | Spent | Notes |
|------|-------|-------|
| Anthropic API (Haiku eval) | ~$15 | Complete |
| OpenAI API (GPT-4o-mini + 4o) | ~$60 | Complete |
| OpenRouter (6 open-source models) | ~$0.22 | Complete |
| Hetzner VPS | $8/mo | Deployed, running |
| **Planned: Sonnet 4.6** | **~$55** | 27 combinations |
| **Planned: o3** | **~$40** | 27 combinations |
| **Planned: B2 recalibration** | **~$3-5** | 9 models, budget_cot only |
| **Total spent** | **~$83** | |
| **Total planned** | **~$98** | |
| **Remaining budget** | **~$267** | Ample for revision rounds |

---

## Implementation Order (Updated 2026-03-11)

~~Completed:~~
- ~~1. Analysis Pipeline~~ ✅ (121,614 instances, 4 tables, 5 figures)
- ~~2-10. VPS Infrastructure~~ ✅ (deployed: daemon, API, PostgreSQL, nginx, systemd)

**Current priorities (paper-critical path):**

1. **Budget_cot fix + re-run** — Fix B2, re-run 9 models. Hours 0-4.
2. **Sonnet 4.6 + o3 eval** — Run 54 new combinations. Hours 0-10.
3. **Section 5 writing** — Scaffold now, fill after data final. Hours 0-12.
4. **Discussion + Related Work + Appendix** — Can start immediately. Hours 0-12.
5. **Integration** — Merge, final analysis, compile, review. Hours 12-14.
6. **SSL + Dashboard wiring** — After paper sprint. Days 12-14.
7. **Slack + backup** — After paper sprint. Day 14+.
