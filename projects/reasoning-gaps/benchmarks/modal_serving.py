"""Modal GPU deployment for vLLM inference endpoints.

Deploys open-source models on Modal's serverless GPU infrastructure using vLLM.
Each model runs as an ASGI web app with standard OpenAI-compatible endpoints
at /v1/chat/completions — no client changes needed.

Prerequisites:
    1. pip install modal && modal setup
    2. HuggingFace token (Llama requires license acceptance at meta-llama org)
    3. modal secret create huggingface HF_TOKEN=hf_xxx

Usage:
    # Deploy all models (scale-to-zero, billed only when active)
    modal deploy modal_serving.py

    # Smoke test a single model
    modal run modal_serving.py::smoke_test --model mistral-7b

    # Check health of all deployed endpoints
    modal run modal_serving.py::check_health

    # Generate vllm_endpoints.json for the evaluation runner
    modal run modal_serving.py::write_endpoints

    # After deployment, the VLLMClient connects via:
    # VLLM_BASE_URL=https://<user>--reasongap-<model>-serve.modal.run/v1
"""

from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path

import modal

# ---------------------------------------------------------------------------
# Model configurations
# ---------------------------------------------------------------------------

MODEL_CONFIGS: dict[str, dict] = {
    # Tier 1: Small models (7-8B) — L4 GPU, ~16GB VRAM
    "llama-8b": {
        "hf_model": "meta-llama/Meta-Llama-3.1-8B-Instruct",
        "served_name": "meta-llama/Meta-Llama-3.1-8B-Instruct",
        "gpu": "l4",
        "gpu_count": 1,
        "max_model_len": 4096,
        "quantization": None,
        "gated": True,
    },
    "mistral-7b": {
        "hf_model": "mistralai/Mistral-7B-Instruct-v0.3",
        "served_name": "mistralai/Mistral-7B-Instruct-v0.3",
        "gpu": "l4",
        "gpu_count": 1,
        "max_model_len": 4096,
        "quantization": None,
        "gated": False,
    },
    "qwen-7b": {
        "hf_model": "Qwen/Qwen2.5-7B-Instruct",
        "served_name": "Qwen/Qwen2.5-7B-Instruct",
        "gpu": "l4",
        "gpu_count": 1,
        "max_model_len": 4096,
        "quantization": None,
        "gated": False,
    },
    # Tier 2: Medium model (24B) — A100-80GB, ~48GB VRAM in FP16
    "mistral-24b": {
        "hf_model": "mistralai/Mistral-Small-24B-Instruct-2501",
        "served_name": "mistralai/Mistral-Small-24B-Instruct-2501",
        "gpu": "a100-80gb",
        "gpu_count": 1,
        "max_model_len": 4096,
        "quantization": None,
        "gated": False,
    },
    # Tier 3: Large models (70B+) — A100-80GB with AWQ INT4 quantization
    "llama-70b": {
        "hf_model": "hugging-quants/Meta-Llama-3.1-70B-Instruct-AWQ-INT4",
        "served_name": "meta-llama/Meta-Llama-3.1-70B-Instruct",
        "gpu": "a100-80gb",
        "gpu_count": 1,
        "max_model_len": 4096,
        "quantization": "awq",
        "gated": True,
    },
    "qwen-72b": {
        "hf_model": "Qwen/Qwen2.5-72B-Instruct-AWQ",
        "served_name": "Qwen/Qwen2.5-72B-Instruct",
        "gpu": "a100-80gb",
        "gpu_count": 1,
        "max_model_len": 4096,
        "quantization": "awq",
        "gated": False,
    },
}

# ---------------------------------------------------------------------------
# Modal image: vLLM + dependencies, model weights baked in
# ---------------------------------------------------------------------------

def _build_image(config: dict) -> modal.Image:
    """Build a Modal image with vLLM and pre-downloaded model weights."""
    img = (
        modal.Image.debian_slim(python_version="3.12")
        .pip_install(
            "vllm>=0.6.0",
            "torch>=2.4.0",
            "transformers>=4.44.0",
            "huggingface_hub[hf_transfer]",
            "fastapi",
        )
        .env({"HF_HUB_ENABLE_HF_TRANSFER": "1"})
    )

    # Pre-download model weights into the image for fast cold starts.
    # This runs at image build time, not at container startup.
    hf_model = config["hf_model"]
    img = img.run_commands(
        f"python -c \""
        f"from huggingface_hub import snapshot_download; "
        f"snapshot_download('{hf_model}', ignore_patterns=['*.gguf', '*.ggml'])"
        f"\"",
        secrets=[modal.Secret.from_name("huggingface")],
    )
    return img


# ---------------------------------------------------------------------------
# One Modal app per model (separate deployments for independent scaling)
# ---------------------------------------------------------------------------

def _create_model_app(model_key: str, config: dict):
    """Create a complete Modal app for one model."""

    model_app = modal.App(f"reasongap-{model_key}")

    gpu_spec = config["gpu"]
    if gpu_spec == "l4":
        gpu = modal.gpu.L4(count=config["gpu_count"])
    elif gpu_spec == "a10g":
        gpu = modal.gpu.A10G(count=config["gpu_count"])
    elif gpu_spec == "a100-80gb":
        gpu = modal.gpu.A100(count=config["gpu_count"], size="80GB")
    else:
        raise ValueError(f"Unknown GPU: {gpu_spec}")

    image = _build_image(config)

    @model_app.cls(
        image=image,
        gpu=gpu,
        secrets=[modal.Secret.from_name("huggingface")],
        container_idle_timeout=300,
        allow_concurrent_inputs=32,
        timeout=600,
    )
    class Model:
        hf_model: str = config["hf_model"]
        served_name: str = config["served_name"]
        max_model_len: int = config["max_model_len"]
        quantization: str | None = config["quantization"]

        @modal.enter()
        def load(self):
            """Load the vLLM engine on container startup."""
            from vllm.engine.arg_utils import AsyncEngineArgs
            from vllm.engine.async_llm_engine import AsyncLLMEngine

            kwargs = dict(
                model=self.hf_model,
                served_model_name=[self.served_name],
                max_model_len=self.max_model_len,
                dtype="auto",
                trust_remote_code=True,
                enforce_eager=False,
                gpu_memory_utilization=0.90,
            )
            if self.quantization:
                kwargs["quantization"] = self.quantization

            self.engine = AsyncLLMEngine.from_engine_args(
                AsyncEngineArgs(**kwargs)
            )
            print(f"Engine ready: {self.hf_model}")

        @modal.asgi_app()
        def serve(self):
            """Expose an OpenAI-compatible ASGI app.

            Provides:
              POST /v1/chat/completions
              GET  /health
            """
            import uuid
            from fastapi import FastAPI, Request
            from fastapi.responses import JSONResponse

            web = FastAPI(title=f"ReasonGap vLLM: {self.served_name}")
            engine = self.engine

            @web.get("/health")
            async def health():
                return {"status": "ok", "model": self.served_name}

            @web.post("/v1/chat/completions")
            async def chat_completions(request: Request):
                from vllm import SamplingParams

                body = await request.json()
                messages = body.get("messages", [])
                max_tokens = body.get("max_tokens", 512)
                temperature = body.get("temperature", 0)
                top_p = body.get("top_p", 1.0)
                seed = body.get("seed", None)

                # Apply chat template via tokenizer
                tokenizer = await engine.get_tokenizer()
                prompt = tokenizer.apply_chat_template(
                    messages, tokenize=False, add_generation_prompt=True,
                )

                params = SamplingParams(
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    seed=seed,
                )

                request_id = str(uuid.uuid4())
                final_output = None
                async for output in engine.generate(
                    prompt, params, request_id
                ):
                    final_output = output

                text = final_output.outputs[0].text
                prompt_tok = len(final_output.prompt_token_ids)
                completion_tok = len(final_output.outputs[0].token_ids)

                return JSONResponse({
                    "id": f"chatcmpl-{request_id[:8]}",
                    "object": "chat.completion",
                    "created": int(time.time()),
                    "model": self.served_name,
                    "choices": [{
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": text,
                        },
                        "finish_reason": "stop",
                    }],
                    "usage": {
                        "prompt_tokens": prompt_tok,
                        "completion_tokens": completion_tok,
                        "total_tokens": prompt_tok + completion_tok,
                    },
                })

            return web

    Model.__name__ = f"Model_{model_key}"
    Model.__qualname__ = f"Model_{model_key}"
    return model_app, Model


# ---------------------------------------------------------------------------
# Create all model apps
# ---------------------------------------------------------------------------

_apps: dict[str, tuple[modal.App, type]] = {}
for _key, _cfg in MODEL_CONFIGS.items():
    _apps[_key] = _create_model_app(_key, _cfg)

# The main app used by `modal deploy modal_serving.py` deploys nothing by
# itself — individual models are deployed separately:
#   modal deploy modal_serving.py::llama_8b_app
# Or use the deploy_all entrypoint to deploy them all at once.

# Expose individual apps as module-level variables for `modal deploy`
llama_8b_app = _apps["llama-8b"][0]
mistral_7b_app = _apps["mistral-7b"][0]
qwen_7b_app = _apps["qwen-7b"][0]
mistral_24b_app = _apps["mistral-24b"][0]
llama_70b_app = _apps["llama-70b"][0]
qwen_72b_app = _apps["qwen-72b"][0]

# Main app for utility entrypoints (smoke_test, write_endpoints, etc.)
app = modal.App("reasongap-utils")


# ---------------------------------------------------------------------------
# Utility: deploy all models
# ---------------------------------------------------------------------------

@app.local_entrypoint()
def deploy_all():
    """Deploy all models to Modal.

    Usage: modal run modal_serving.py::deploy_all
    """
    for key in MODEL_CONFIGS:
        print(f"\nDeploying {key}...")
        try:
            result = subprocess.run(
                ["modal", "deploy", __file__, f"--name", f"reasongap-{key}"],
                capture_output=True, text=True,
            )
            if result.returncode == 0:
                print(f"  {key}: deployed successfully")
            else:
                print(f"  {key}: FAILED")
                print(f"  {result.stderr[:200]}")
        except Exception as e:
            print(f"  {key}: ERROR - {e}")


# ---------------------------------------------------------------------------
# Utility: smoke test
# ---------------------------------------------------------------------------

@app.local_entrypoint()
def smoke_test(model: str = "mistral-7b"):
    """Smoke test a deployed model endpoint.

    Usage: modal run modal_serving.py::smoke_test --model mistral-7b
    """
    import httpx

    if model not in MODEL_CONFIGS:
        print(f"Unknown model: {model}")
        print(f"Available: {', '.join(MODEL_CONFIGS.keys())}")
        return

    config = MODEL_CONFIGS[model]

    # Load endpoint URLs
    endpoints = _load_endpoints()
    served_name = config["served_name"]

    if served_name not in endpoints:
        print(f"No endpoint URL for {served_name}")
        print("Run 'modal run modal_serving.py::write_endpoints' first")
        return

    base_url = endpoints[served_name].rstrip("/")
    print(f"Testing {served_name} at {base_url}")

    client = httpx.Client(timeout=120)

    # Health check
    try:
        resp = client.get(f"{base_url.replace('/v1', '')}/health")
        print(f"Health: {resp.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")

    # Chat completion
    payload = {
        "messages": [
            {"role": "system", "content": "Answer with just the number."},
            {"role": "user", "content": "What is 2 + 3?"},
        ],
        "max_tokens": 32,
        "temperature": 0,
        "seed": 42,
    }

    print("Sending test request...")
    start = time.time()
    try:
        resp = client.post(f"{base_url}/chat/completions", json=payload)
        resp.raise_for_status()
        data = resp.json()
        latency = time.time() - start

        content = data["choices"][0]["message"]["content"]
        usage = data["usage"]
        print(f"Response: {content}")
        print(f"Tokens: {usage}")
        print(f"Latency: {latency:.1f}s")

        if "5" in content:
            print("PASS")
        else:
            print(f"WARN: expected '5' in response")
    except Exception as e:
        print(f"Request failed: {e}")


# ---------------------------------------------------------------------------
# Utility: write endpoint config
# ---------------------------------------------------------------------------

def _load_endpoints() -> dict[str, str]:
    """Load vllm_endpoints.json if it exists."""
    path = Path(__file__).resolve().parent / "vllm_endpoints.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}


@app.local_entrypoint()
def write_endpoints():
    """Generate vllm_endpoints.json template.

    After deploying models, fill in the actual URLs from Modal's output.
    Each model's URL follows the pattern:
        https://<user>--reasongap-<model_key>-model-<key>-serve.modal.run/v1

    Usage: modal run modal_serving.py::write_endpoints
    """
    endpoints = {}
    for key, config in MODEL_CONFIGS.items():
        served_name = config["served_name"]
        # Template URL — user must replace <user> with their Modal username
        endpoints[served_name] = (
            f"https://<user>--reasongap-{key}-model-{key.replace('-', '')}-serve.modal.run/v1"
        )

    output_path = Path(__file__).resolve().parent / "vllm_endpoints.json"
    with open(output_path, "w") as f:
        json.dump(endpoints, f, indent=2)

    print(f"Wrote {output_path}")
    print()
    print("Template (update <user> with your Modal username):")
    print(json.dumps(endpoints, indent=2))
    print()
    print("After deploying, find actual URLs in Modal dashboard or deploy output.")
    print("The evaluation runner reads this file to route vLLM requests.")


# ---------------------------------------------------------------------------
# Utility: check health
# ---------------------------------------------------------------------------

@app.local_entrypoint()
def check_health():
    """Check health of all deployed model endpoints.

    Usage: modal run modal_serving.py::check_health
    """
    import httpx

    endpoints = _load_endpoints()
    if not endpoints:
        print("No vllm_endpoints.json found. Run write_endpoints first.")
        return

    client = httpx.Client(timeout=30)
    all_ok = True

    for model_name, base_url in endpoints.items():
        print(f"  {model_name}...", end=" ", flush=True)
        health_url = base_url.rstrip("/").replace("/v1", "") + "/health"
        try:
            resp = client.get(health_url, timeout=60)
            if resp.status_code == 200:
                print("OK")
            else:
                print(f"ERROR ({resp.status_code})")
                all_ok = False
        except Exception as e:
            print(f"UNREACHABLE ({type(e).__name__})")
            all_ok = False

    print()
    if all_ok:
        print("All endpoints healthy.")
    else:
        print("Some endpoints are down. Check Modal dashboard.")
