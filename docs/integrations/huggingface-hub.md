# HuggingFace Hub Integration

## Overview

HuggingFace Hub hosts 2M+ models and 500k+ datasets with programmatic access via REST API and client libraries. For a research platform studying reasoning capabilities, this provides: model discovery (finding which models to evaluate), dataset sourcing (pulling benchmark data), and leaderboard cross-referencing (comparing our results against community benchmarks).

Has first-class TypeScript support via `@huggingface/hub` npm package — fits naturally into the orchestrator.

## API Details

- **Base URL:** `https://huggingface.co/api`
- **Auth:** Bearer token via `Authorization` header (free account)
- **Rate limit:** Generous for metadata queries. Downloads may be rate-limited for large files.
- **Cost:** $0
- **Env var:** `HF_TOKEN`
- **TypeScript SDK:** `@huggingface/hub`

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/models` | GET | Search/filter models by task, library, author, tags |
| `/api/models/{id}` | GET | Model card, config, files, downloads, likes |
| `/api/datasets` | GET | Search/filter datasets by task, size, language |
| `/api/datasets/{id}` | GET | Dataset card, splits, features, download counts |
| `/api/spaces` | GET | Search for demo apps and benchmarks |

### Useful Query Parameters

```
# Find reasoning-relevant models
GET /api/models?search=reasoning&pipeline_tag=text-generation&sort=downloads&limit=20

# Find benchmark datasets
GET /api/datasets?search=reasoning+benchmark&sort=downloads&limit=20

# Get model config (quantization, architecture)
GET /api/models/meta-llama/Llama-3.1-70B-Instruct
```

### TypeScript SDK Usage

```typescript
import { listModels, modelInfo } from "@huggingface/hub";

// Search for models
for await (const model of listModels({
  search: { query: "reasoning" },
  additionalFields: ["downloads", "pipeline_tag"],
})) {
  console.log(model.id, model.downloads);
}

// Get model details
const info = await modelInfo({ name: "meta-llama/Llama-3.1-70B-Instruct" });
console.log(info.config);  // architecture, quantization options
```

## Integration Architecture

### New Skill: `huggingface`

Location: `openclaw/skills/huggingface/`

Commands:
- `huggingface models "<query>" [--task text-generation] [--sort downloads]` — search models
- `huggingface model <id>` — model card, config, architecture details
- `huggingface datasets "<query>" [--sort downloads]` — search datasets
- `huggingface dataset <id>` — dataset card, splits, features
- `huggingface leaderboard [--benchmark open_llm]` — current leaderboard standings

### Orchestrator Module: `orchestrator/src/huggingface.ts`

TypeScript module using `@huggingface/hub`:
- Model search and metadata retrieval
- Dataset search and split info
- Caching: model/dataset metadata cached for 24h (doesn't change often)
- Pairs with Modal: "this model exists, here's its quantization config" → Modal downloads and runs it

### Modal Synergy

The critical pairing:

```
Kit asks: "What 70B models could we evaluate?"
  → huggingface models --task text-generation --sort downloads
  → Returns: Llama-3.1-70B-Instruct, Qwen3-72B, DeepSeek-V3, etc.
  → Kit checks: is there an FP8 quantized variant?
  → huggingface model Qwen/Qwen3-72B-FP8 → yes, exists
  → Kit dispatches Modal eval job for Qwen3-72B-FP8
```

HuggingFace answers "what to run." Modal answers "how to run it."

## Use Cases by Agent

| Agent | Use Case |
|-------|----------|
| **Kit** | Primary user. Model discovery for evals. Dataset sourcing for benchmarks. Leaderboard comparison. |
| **Noor** | Track new model releases in relevant categories. Search for reasoning-specific datasets. |
| **Vera** | Verify model claims. "Is this model actually SOTA on this benchmark?" Cross-check against HF leaderboard. |
| **Maren** | Reference model metadata in paper (parameter counts, training data, license). Accurate model descriptions. |
| **Eli** | Check model architecture details when building eval infrastructure. |

## Roadmap

### Phase 1: TypeScript Client + Skill (Sprint 10)
- [ ] Add `@huggingface/hub` to orchestrator package.json
- [ ] Create `orchestrator/src/huggingface.ts` — model search, dataset search, model info
- [ ] Create `openclaw/skills/huggingface/` — skill wrapper
- [ ] Add `HF_TOKEN` to VPS `.env`
- [ ] Manual test: search for reasoning benchmark models and datasets

### Phase 2: Model Registry (Sprint 11)
- [ ] Create `model_registry` DB table tracking evaluated + candidate models
- [ ] Populate with current 9 models from reasoning-gaps evals
- [ ] Build "candidate discovery" query: models similar to evaluated ones but not yet tested
- [ ] Wire into Kit's heartbeat: suggest new models to evaluate

### Phase 3: Leaderboard Integration (Sprint 12)
- [ ] Pull Open LLM Leaderboard data via HF API
- [ ] Cross-reference our reasoning-gaps results with general leaderboard rankings
- [ ] Auto-generate comparison table for the paper
- [ ] Feed into Vera's review: "our rankings diverge from the leaderboard here — investigate"

## References

- [HuggingFace Hub Documentation](https://huggingface.co/docs/hub/en/index)
- [HuggingFace Hub JS Library](https://huggingface.co/docs/huggingface.js/hub/README)
- [@huggingface/hub npm](https://www.npmjs.com/package/@huggingface/hub)
- [Hub REST API](https://huggingface.co/docs/hub/api)
