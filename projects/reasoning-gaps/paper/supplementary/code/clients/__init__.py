"""Model client implementations for ReasonGap evaluation.

Factory function ``create_client()`` maps a model spec string like
``"anthropic:claude-haiku-4-5-20251001"`` to the appropriate client class.
"""

from __future__ import annotations

from evaluate import ModelClient

from .anthropic_client import AnthropicClient
from .openai_client import OpenAIClient
from .openrouter_client import OpenRouterClient
from .vllm_client import VLLMClient

__all__ = [
    "AnthropicClient",
    "OpenAIClient",
    "OpenRouterClient",
    "VLLMClient",
    "ModelClient",
    "create_client",
]

_PROVIDER_MAP: dict[str, type[ModelClient]] = {
    "anthropic": AnthropicClient,
    "openai": OpenAIClient,
    "openrouter": OpenRouterClient,
    "vllm": VLLMClient,
}


def create_client(model_spec: str, **kwargs) -> ModelClient:
    """Create a model client from a ``provider:model_name`` spec string.

    Examples:
        >>> client = create_client("anthropic:claude-haiku-4-5-20251001")
        >>> client = create_client("openai:gpt-4o")
        >>> client = create_client("vllm:meta-llama/Meta-Llama-3.1-70B-Instruct", base_url="http://gpu:8000/v1")

    Args:
        model_spec: String in ``"provider:model_name"`` format.
        **kwargs: Additional keyword arguments passed to the client constructor.

    Returns:
        A ModelClient subclass instance.

    Raises:
        ValueError: If the provider is unknown or the spec is malformed.
    """
    if ":" not in model_spec:
        raise ValueError(
            f"Invalid model spec '{model_spec}'. "
            f"Expected format 'provider:model_name' "
            f"(e.g., 'anthropic:claude-haiku-4-5-20251001'). "
            f"Known providers: {', '.join(sorted(_PROVIDER_MAP))}."
        )

    provider, model_name = model_spec.split(":", 1)

    if provider not in _PROVIDER_MAP:
        raise ValueError(
            f"Unknown provider '{provider}'. "
            f"Known providers: {', '.join(sorted(_PROVIDER_MAP))}."
        )

    client_class = _PROVIDER_MAP[provider]
    return client_class(model_name, **kwargs)
