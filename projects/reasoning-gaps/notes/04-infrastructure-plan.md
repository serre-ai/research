# Infrastructure Plan

## Compute Resources

### Server 1: GPU Inference
- **Purpose**: Run open-source LLMs for empirical evaluation
- **Spec**: Hetzner dedicated GPU — 1× A100 80GB, 64GB+ RAM, NVMe
- **Software**: vLLM or TGI inference server
- **Models**: Llama 3.x (8B, 70B), Mistral (7B, Large), Qwen (7B, 72B)
- **Cost**: ~€300/month
- **Use cases**:
  - Batch evaluation of diagnostic benchmark suite across model families and scales
  - CoT ablation experiments (varying CoT budget)
  - Reproduction of key results (GSM-Symbolic, Alice in Wonderland) on open models
  - Scale analysis: same tasks across 4+ sizes per family

### Server 2: General Compute
- **Purpose**: Orchestration, CI, dashboard, data processing
- **Spec**: Hetzner AX42 — Ryzen 7, 64GB RAM, 2× NVMe
- **Software**: Deepwork orchestrator, benchmark runner, web dashboard, LaTeX CI
- **Cost**: ~€55/month

## Monthly Budget Allocation

| Item | Cost |
|---|---|
| GPU server (A100 80GB) | ~€300 |
| Compute server (AX42) | ~€55 |
| Claude/GPT API (proprietary evals) | ~$200 |
| Firecrawl + misc APIs | ~$50 |
| **Total** | **~$650–700** |

Headroom of ~$300/month for burst usage or additional API calls.

## Model Evaluation Matrix

| Family | Sizes | Access Method |
|---|---|---|
| Claude | Haiku, Sonnet, Opus | API |
| GPT | GPT-4o-mini, GPT-4o, o3 | API |
| Llama 3.x | 8B, 70B | Local (Server 1) |
| Mistral | 7B, Large | Local (Server 1) |
| Qwen | 7B, 72B | Local (Server 1) |

## Architecture

```
Server 1 (GPU)                    Server 2 (Compute)
┌─────────────────────┐          ┌─────────────────────┐
│ vLLM inference       │          │ Deepwork orchestrator│
│ ├ Llama 3.x 70B     │◄────────│ ├ Agent sessions     │
│ ├ Llama 3.x 8B      │  API    │ ├ Benchmark runner   │
│ ├ Mistral Large      │  calls  │ ├ Results DB         │
│ ├ Qwen 72B           │          │ ├ Web dashboard      │
│ └ Custom fine-tunes  │          │ └ LaTeX CI           │
└─────────────────────┘          └─────────────────────┘
         │                                │
         └──────── Both call ─────────────┘
                     │
              Claude / GPT APIs
              (proprietary evals)
```

## Provisioning (when servers are available)

1. Server 1: Install CUDA, vLLM, download base models, set up API endpoint
2. Server 2: Install Node.js, clone deepwork repo, set up orchestrator, configure CI
3. Both: SSH keys, firewall rules, WireGuard VPN between servers
4. Benchmark runner on Server 2 orchestrates evaluation across all endpoints (local vLLM + cloud APIs)
