# Modal Integration

## Overview

Modal provides on-demand GPU compute that scales to zero. We already have Modal access. This integration builds a reusable eval runner that lets Kit dispatch eval jobs to Modal instead of (or alongside) rate-limited APIs, enabling open-weight model evaluation at a fraction of the API cost.

The key insight: Modal functions can expose HTTP endpoints, so the existing eval harness can call them like any other model API — same interface, different backend.

## API Details

- **SDK:** `modal` Python package (Python-first, called from orchestrator via subprocess or webhook)
- **Auth:** `MODAL_TOKEN_ID` + `MODAL_TOKEN_SECRET` env vars (already configured)
- **GPU pricing:** H100 ~$3.50/hr, A100-80GB ~$2.78/hr, A10G ~$1.10/hr (pay per second, scale to zero)
- **Key feature:** Cached model weights via Modal volumes — first load is slow, subsequent invocations start in seconds
- **Cost:** Variable. Estimated $10-15 per full eval sweep of an open model (121k instances).

### Recommended Inference Stack

- **Engine:** vLLM (best balance of performance and ease of use) or SGLang (best for FP8 on H100/H200)
- **Models (priority targets):**
  - Llama 3.1 70B / 405B (Meta, Apache 2.0)
  - Qwen3-72B / Qwen3-8B-FP8 (Alibaba, Apache 2.0)
  - DeepSeek-V3 (DeepSeek, MIT)
  - Mistral Large 2 (Mistral, Apache 2.0)
  - Gemma 2 27B (Google, permissive)
- **Quantization:** FP8 on H100s for 70B+ models. BF16 for smaller models.

### Cost Comparison: API vs Modal

| Model | API Cost (121k instances) | Modal Cost (est.) | Savings |
|-------|--------------------------|-------------------|---------|
| Llama 3.1 70B | ~$40 via OpenRouter | ~$12 on H100 | 70% |
| Qwen3-72B | ~$35 via OpenRouter | ~$12 on H100 | 66% |
| DeepSeek-V3 | ~$25 via OpenRouter | ~$10 on H100 | 60% |
| Any 8B model | ~$5 via OpenRouter | ~$3 on A10G | 40% |

Modal wins decisively for large models and batch workloads. API is still better for one-off small requests.

## Integration Architecture

### Modal App: `modal/eval_runner.py`

Location: `modal/` directory at project root.

```
modal/
├── eval_runner.py      # Main Modal app — vLLM inference endpoint
├── models.py           # Model configs (weights path, GPU type, quantization)
├── requirements.txt    # vllm, torch
└── README.md
```

The Modal app:
1. Downloads model weights to a Modal volume (one-time, cached)
2. Starts vLLM server with the model loaded
3. Exposes an OpenAI-compatible HTTP endpoint (`/v1/chat/completions`)
4. Accepts batch requests, returns results
5. Scales to zero when idle

### Orchestrator Module: `orchestrator/src/modal-runner.ts`

TypeScript module that:
1. Maintains a registry of Modal app URLs per model
2. Provides `runEvalBatch(model, instances[])` — sends batch to Modal endpoint
3. Falls back to API if Modal is unavailable
4. Logs cost based on GPU-seconds used
5. Reports results to the same DB tables as API-based evals

### How Kit Uses It

```
Kit heartbeat:
  1. Check eval pipeline for pending work
  2. For open-weight models → dispatch to Modal
  3. For API-only models (Claude, GPT) → dispatch to API
  4. Results flow to same eval_results table
  5. Log to W&B (if integrated)
```

### Batch Eval Flow

```
Kit → modal-runner.ts → HTTP POST to Modal endpoint
                          ↓
                    vLLM on H100 processes batch
                          ↓
                    Results JSON back to modal-runner.ts
                          ↓
                    INSERT INTO eval_results
                          ↓
                    Budget event logged (cost = GPU-seconds × rate)
```

## Use Cases

| Use Case | Description |
|----------|-------------|
| **Open model evals** | Run Llama, Qwen, DeepSeek, Mistral on the B1-B9 reasoning benchmark tasks. Expands model coverage from 9 → 13+ models. |
| **Ablation studies** | Test different temperatures, system prompts, few-shot examples. API evals make this expensive; Modal makes it cheap. |
| **Reproducibility** | Pin exact model weights and inference config. No silent model updates. |
| **Heavy analysis** | Bootstrap CIs across 121k instances on GPU instead of the VPS's 2 vCPUs. |
| **Future: fine-tuning** | If the research direction requires it, Modal supports training workloads too. |

## Roadmap

### Phase 1: Eval Runner MVP (INT-1)
- [ ] Create `modal/` directory with eval_runner.py
- [ ] Implement vLLM inference for one model (Qwen3-8B-FP8 as test)
- [ ] Create Modal volume for model weight caching
- [ ] Test: send 100 eval instances, verify results match API-based eval format
- [ ] Create `orchestrator/src/modal-runner.ts` — HTTP client for Modal endpoint
- [ ] Wire into Kit's eval dispatch logic as alternative backend

### Phase 2: Multi-Model Support (INT-2)
- [ ] Add model configs for Llama 3.1 70B, Qwen3-72B, DeepSeek-V3, Mistral Large 2
- [ ] Create separate Modal apps per model family (different GPU requirements)
- [ ] Build model selection logic in modal-runner.ts
- [ ] Run full B1-B9 eval on Qwen3-8B-FP8 as validation
- [ ] Cost tracking: log GPU-seconds and compute cost to budget_events

### Phase 3: Full Eval Coverage (INT-3)
- [ ] Run B1-B9 × 3 conditions on all target open models
- [ ] Compare results with API-based evals for consistency
- [ ] Integrate with W&B for experiment tracking (if available)
- [ ] Add open-model results to reasoning-gaps paper

### Phase 4: Advanced (INT-4+)
- [ ] Ablation studies: temperature sweeps, system prompt variants
- [ ] GPU-accelerated statistical analysis (bootstrap CIs on full dataset)
- [ ] Explore fine-tuning experiments if research direction warrants

## References

- [Modal vLLM Example](https://modal.com/docs/examples/vllm_inference)
- [Modal High-Performance LLM Inference Guide](https://modal.com/docs/guide/high-performance-llm-inference)
- [Modal GPU Pricing](https://modal.com/pricing)
- [vLLM Documentation](https://docs.vllm.ai/)
