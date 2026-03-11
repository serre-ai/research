"""Unit and integration tests for model clients."""

from __future__ import annotations

import os
import time
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from clients import create_client, AnthropicClient, OpenAIClient, VLLMClient
from evaluate import ModelClient


# ============================================================================
# Factory tests
# ============================================================================


class TestCreateClient:
    """Tests for the create_client() factory."""

    def test_unknown_provider_raises(self):
        with pytest.raises(ValueError, match="Unknown provider 'foobar'"):
            create_client("foobar:some-model", api_key="fake")

    def test_missing_colon_raises(self):
        with pytest.raises(ValueError, match="Invalid model spec"):
            create_client("gpt-4o", api_key="fake")

    def test_empty_string_raises(self):
        with pytest.raises(ValueError, match="Invalid model spec"):
            create_client("", api_key="fake")

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"})
    @patch("clients.anthropic_client.anthropic.Anthropic")
    def test_anthropic_provider(self, mock_cls):
        client = create_client("anthropic:claude-haiku-4-5-20251001")
        assert isinstance(client, AnthropicClient)
        assert client.model_name == "claude-haiku-4-5-20251001"

    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch("clients.openai_client.openai.OpenAI")
    def test_openai_provider(self, mock_cls):
        client = create_client("openai:gpt-4o")
        assert isinstance(client, OpenAIClient)
        assert client.model_name == "gpt-4o"

    def test_vllm_provider(self):
        client = create_client("vllm:meta-llama/Meta-Llama-3.1-70B-Instruct")
        assert isinstance(client, VLLMClient)
        assert client.model_name == "meta-llama/Meta-Llama-3.1-70B-Instruct"

    def test_all_clients_are_model_clients(self):
        """Every client class must be a subclass of ModelClient."""
        for cls in [AnthropicClient, OpenAIClient, VLLMClient]:
            assert issubclass(cls, ModelClient)


# ============================================================================
# AnthropicClient tests
# ============================================================================


class TestAnthropicClient:
    """Unit tests for AnthropicClient with mocked SDK."""

    @patch("clients.anthropic_client.anthropic.Anthropic")
    def _make_client(self, mock_cls, model="claude-haiku-4-5-20251001"):
        client = AnthropicClient(model, api_key="fake-key")
        return client, mock_cls.return_value

    def test_query_formats_messages(self):
        client, mock_api = self._make_client()

        # Build a mock response
        text_block = SimpleNamespace(type="text", text="The answer is 42")
        usage = SimpleNamespace(input_tokens=10, output_tokens=5)
        mock_api.messages.create.return_value = SimpleNamespace(
            content=[text_block], usage=usage
        )

        result, latency = client.query("What is the answer?", system_prompt="Be brief.")
        assert result == "The answer is 42"
        assert latency > 0

        call_kwargs = mock_api.messages.create.call_args[1]
        assert call_kwargs["model"] == "claude-haiku-4-5-20251001"
        assert call_kwargs["messages"] == [{"role": "user", "content": "What is the answer?"}]
        assert call_kwargs["system"] == "Be brief."
        assert call_kwargs["max_tokens"] == 512

    def test_query_no_system_prompt(self):
        client, mock_api = self._make_client()

        text_block = SimpleNamespace(type="text", text="hello")
        usage = SimpleNamespace(input_tokens=5, output_tokens=3)
        mock_api.messages.create.return_value = SimpleNamespace(
            content=[text_block], usage=usage
        )

        client.query("hi")
        call_kwargs = mock_api.messages.create.call_args[1]
        assert "system" not in call_kwargs

    def test_cost_tracking(self):
        client, mock_api = self._make_client()

        text_block = SimpleNamespace(type="text", text="ok")
        # 100 input, 50 output for claude-haiku-4-5-20251001
        # Cost: 100 * 0.80/1M + 50 * 4.00/1M = 0.00008 + 0.0002 = 0.00028
        usage = SimpleNamespace(input_tokens=100, output_tokens=50)
        mock_api.messages.create.return_value = SimpleNamespace(
            content=[text_block], usage=usage
        )

        client.query("test")
        assert client.total_tokens == 150
        assert abs(client.total_cost_usd - 0.00028) < 1e-8
        assert abs(client.get_cost() - 0.00028) < 1e-8

    def test_cost_accumulates(self):
        client, mock_api = self._make_client()

        text_block = SimpleNamespace(type="text", text="ok")
        usage = SimpleNamespace(input_tokens=100, output_tokens=50)
        mock_api.messages.create.return_value = SimpleNamespace(
            content=[text_block], usage=usage
        )

        client.query("test1")
        client.query("test2")
        client.query("test3")

        assert client.total_tokens == 450  # 150 * 3
        assert abs(client.total_cost_usd - 0.00028 * 3) < 1e-8

    def test_unknown_model_cost_is_zero(self):
        client, mock_api = self._make_client(model="claude-unknown-model")

        text_block = SimpleNamespace(type="text", text="ok")
        usage = SimpleNamespace(input_tokens=100, output_tokens=50)
        mock_api.messages.create.return_value = SimpleNamespace(
            content=[text_block], usage=usage
        )

        client.query("test")
        assert client.total_cost_usd == 0.0
        assert client.total_tokens == 150

    def test_retry_on_rate_limit(self):
        import anthropic as anthropic_mod

        client, mock_api = self._make_client()

        text_block = SimpleNamespace(type="text", text="ok")
        usage = SimpleNamespace(input_tokens=10, output_tokens=5)
        good_response = SimpleNamespace(content=[text_block], usage=usage)

        # Mock response for the RateLimitError
        mock_http_response = MagicMock()
        mock_http_response.status_code = 429
        mock_http_response.headers = {}

        # First call raises RateLimitError, second succeeds
        mock_api.messages.create.side_effect = [
            anthropic_mod.RateLimitError(
                message="rate limited",
                response=mock_http_response,
                body=None,
            ),
            good_response,
        ]

        result, _ = client.query("test")
        assert result == "ok"
        assert mock_api.messages.create.call_count == 2

    def test_missing_api_key_raises(self):
        with patch.dict(os.environ, {}, clear=True):
            # Remove ANTHROPIC_API_KEY if it exists
            os.environ.pop("ANTHROPIC_API_KEY", None)
            with patch("clients.anthropic_client.anthropic.Anthropic"):
                with pytest.raises(ValueError, match="API key required"):
                    AnthropicClient("test-model")

    def test_timeout_on_api_call(self):
        import anthropic as anthropic_mod

        client, mock_api = self._make_client()

        mock_api.messages.create.side_effect = anthropic_mod.APITimeoutError(
            request=MagicMock()
        )

        with pytest.raises(anthropic_mod.APITimeoutError):
            client.query("test")


# ============================================================================
# OpenAIClient tests
# ============================================================================


class TestOpenAIClient:
    """Unit tests for OpenAIClient with mocked SDK."""

    @patch("clients.openai_client.openai.OpenAI")
    def _make_client(self, mock_cls, model="gpt-4o"):
        client = OpenAIClient(model, api_key="fake-key")
        return client, mock_cls.return_value

    def _mock_response(self, text="hello", input_tokens=10, output_tokens=5):
        """Build a mock OpenAI chat completion response."""
        message = SimpleNamespace(content=text)
        choice = SimpleNamespace(message=message)
        usage = SimpleNamespace(
            prompt_tokens=input_tokens,
            completion_tokens=output_tokens,
        )
        return SimpleNamespace(choices=[choice], usage=usage)

    def test_query_formats_messages(self):
        client, mock_api = self._make_client()
        mock_api.chat.completions.create.return_value = self._mock_response("42")

        result, latency = client.query("What is 6*7?", system_prompt="Be concise.")
        assert result == "42"
        assert latency > 0

        call_kwargs = mock_api.chat.completions.create.call_args[1]
        assert call_kwargs["model"] == "gpt-4o"
        assert call_kwargs["messages"] == [
            {"role": "system", "content": "Be concise."},
            {"role": "user", "content": "What is 6*7?"},
        ]
        assert call_kwargs["max_tokens"] == 512

    def test_query_no_system_prompt(self):
        client, mock_api = self._make_client()
        mock_api.chat.completions.create.return_value = self._mock_response("hi")

        client.query("hello")
        call_kwargs = mock_api.chat.completions.create.call_args[1]
        assert call_kwargs["messages"] == [
            {"role": "user", "content": "hello"},
        ]

    def test_o3_reasoning_model_format(self):
        """o3 should fold system prompt into user message and use max_completion_tokens."""
        client, mock_api = self._make_client(model="o3")
        mock_api.chat.completions.create.return_value = self._mock_response("4")

        client.query("What is 2+2?", system_prompt="Be brief.")
        call_kwargs = mock_api.chat.completions.create.call_args[1]

        # o3 should not have a system message
        assert len(call_kwargs["messages"]) == 1
        assert call_kwargs["messages"][0]["role"] == "user"
        assert "Be brief." in call_kwargs["messages"][0]["content"]
        assert "What is 2+2?" in call_kwargs["messages"][0]["content"]

        # Should use max_completion_tokens, not max_tokens
        assert "max_completion_tokens" in call_kwargs
        assert "max_tokens" not in call_kwargs

    def test_cost_tracking(self):
        client, mock_api = self._make_client()
        mock_api.chat.completions.create.return_value = self._mock_response(
            "ok", input_tokens=1000, output_tokens=500
        )

        client.query("test")
        # gpt-4o: 1000 * 2.50/1M + 500 * 10.00/1M = 0.0025 + 0.005 = 0.0075
        assert client.total_tokens == 1500
        assert abs(client.total_cost_usd - 0.0075) < 1e-8

    def test_cost_accumulates(self):
        client, mock_api = self._make_client()
        mock_api.chat.completions.create.return_value = self._mock_response(
            "ok", input_tokens=100, output_tokens=50
        )

        client.query("a")
        client.query("b")
        assert client.total_tokens == 300
        # 2 * (100 * 2.50/1M + 50 * 10.00/1M) = 2 * 0.00075 = 0.0015
        assert abs(client.total_cost_usd - 0.0015) < 1e-8

    def test_retry_on_rate_limit(self):
        import openai as openai_mod

        client, mock_api = self._make_client()

        mock_http_response = MagicMock()
        mock_http_response.status_code = 429
        mock_http_response.headers = {}

        mock_api.chat.completions.create.side_effect = [
            openai_mod.RateLimitError(
                message="rate limited",
                response=mock_http_response,
                body=None,
            ),
            self._mock_response("ok"),
        ]

        result, _ = client.query("test")
        assert result == "ok"
        assert mock_api.chat.completions.create.call_count == 2

    def test_missing_api_key_raises(self):
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("OPENAI_API_KEY", None)
            with patch("clients.openai_client.openai.OpenAI"):
                with pytest.raises(ValueError, match="API key required"):
                    OpenAIClient("test-model")

    def test_timeout_on_api_call(self):
        import openai as openai_mod

        client, mock_api = self._make_client()
        mock_api.chat.completions.create.side_effect = openai_mod.APITimeoutError(
            request=MagicMock()
        )

        with pytest.raises(openai_mod.APITimeoutError):
            client.query("test")


# ============================================================================
# VLLMClient tests
# ============================================================================


class TestVLLMClient:
    """Unit tests for VLLMClient with mocked httpx."""

    def _make_client(self, model="meta-llama/Meta-Llama-3.1-70B-Instruct", base_url="http://fake:8000/v1"):
        client = VLLMClient(model, base_url=base_url)
        return client

    def _mock_response(self, text="hello", input_tokens=10, output_tokens=5):
        """Build a mock httpx response mimicking OpenAI-compatible API."""
        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = {
            "choices": [{"message": {"content": text}}],
            "usage": {
                "prompt_tokens": input_tokens,
                "completion_tokens": output_tokens,
            },
        }
        resp.raise_for_status = MagicMock()
        return resp

    @patch("clients.vllm_client.httpx.Client")
    def test_query_formats_request(self, mock_client_cls):
        mock_http = mock_client_cls.return_value
        mock_http.post.return_value = self._mock_response("42")

        client = VLLMClient("test-model", base_url="http://gpu:8000/v1")
        result, latency = client.query("What is 6*7?", system_prompt="Be concise.")

        assert result == "42"
        assert latency > 0

        call_args = mock_http.post.call_args
        assert call_args[0][0] == "http://gpu:8000/v1/chat/completions"

        payload = call_args[1]["json"]
        assert payload["model"] == "test-model"
        assert payload["messages"] == [
            {"role": "system", "content": "Be concise."},
            {"role": "user", "content": "What is 6*7?"},
        ]

    @patch("clients.vllm_client.httpx.Client")
    def test_query_no_system_prompt(self, mock_client_cls):
        mock_http = mock_client_cls.return_value
        mock_http.post.return_value = self._mock_response("hi")

        client = VLLMClient("test-model", base_url="http://gpu:8000/v1")
        client.query("hello")

        payload = mock_http.post.call_args[1]["json"]
        assert payload["messages"] == [
            {"role": "user", "content": "hello"},
        ]

    @patch("clients.vllm_client.httpx.Client")
    def test_token_tracking(self, mock_client_cls):
        mock_http = mock_client_cls.return_value
        mock_http.post.return_value = self._mock_response("ok", 100, 50)

        client = VLLMClient("test-model", base_url="http://fake:8000/v1")
        client.query("test")
        assert client.total_tokens == 150

    @patch("clients.vllm_client.httpx.Client")
    def test_cost_always_zero(self, mock_client_cls):
        mock_http = mock_client_cls.return_value
        mock_http.post.return_value = self._mock_response("ok", 1000, 500)

        client = VLLMClient("test-model", base_url="http://fake:8000/v1")
        client.query("test")
        assert client.total_cost_usd == 0.0
        assert client.get_cost() == 0.0

    @patch("clients.vllm_client.httpx.Client")
    def test_retry_on_http_error(self, mock_client_cls):
        import httpx as httpx_mod

        mock_http = mock_client_cls.return_value

        # Create a proper 429 response
        error_response = MagicMock()
        error_response.status_code = 429
        error_response.headers = {}
        error_response.text = "rate limited"
        error_request = MagicMock()

        mock_http.post.side_effect = [
            httpx_mod.HTTPStatusError(
                message="rate limited",
                request=error_request,
                response=error_response,
            ),
            self._mock_response("ok"),
        ]

        client = VLLMClient("test-model", base_url="http://fake:8000/v1")
        result, _ = client.query("test")
        assert result == "ok"
        assert mock_http.post.call_count == 2

    @patch("clients.vllm_client.httpx.Client")
    def test_timeout_handling(self, mock_client_cls):
        import httpx as httpx_mod

        mock_http = mock_client_cls.return_value
        mock_http.post.side_effect = httpx_mod.ReadTimeout("timed out")

        client = VLLMClient("test-model", base_url="http://fake:8000/v1")
        # ReadTimeout is retryable, but after 5 attempts it should reraise
        with pytest.raises(httpx_mod.ReadTimeout):
            client.query("test")

    def test_default_base_url(self):
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("VLLM_BASE_URL", None)
            client = VLLMClient("test-model")
            assert client._base_url == "http://localhost:8000/v1"

    def test_env_base_url(self):
        with patch.dict(os.environ, {"VLLM_BASE_URL": "http://custom:9000/v1"}):
            client = VLLMClient("test-model")
            assert client._base_url == "http://custom:9000/v1"

    def test_trailing_slash_stripped(self):
        client = VLLMClient("test-model", base_url="http://gpu:8000/v1/")
        assert client._base_url == "http://gpu:8000/v1"


# ============================================================================
# Integration tests (require API keys, skipped by default)
# ============================================================================


@pytest.mark.integration
class TestAnthropicIntegration:
    """Smoke tests against the real Anthropic API."""

    @pytest.fixture(autouse=True)
    def skip_without_key(self):
        if not os.environ.get("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not set")

    def test_simple_query(self):
        client = AnthropicClient("claude-haiku-4-5-20251001")
        result, latency = client.query("What is 2+2? Answer with just the number.")
        assert "4" in result
        assert latency > 0
        assert client.total_tokens > 0
        assert client.total_cost_usd > 0


@pytest.mark.integration
class TestOpenAIIntegration:
    """Smoke tests against the real OpenAI API."""

    @pytest.fixture(autouse=True)
    def skip_without_key(self):
        if not os.environ.get("OPENAI_API_KEY"):
            pytest.skip("OPENAI_API_KEY not set")

    def test_simple_query(self):
        client = OpenAIClient("gpt-4o-mini")
        result, latency = client.query("What is 2+2? Answer with just the number.")
        assert "4" in result
        assert latency > 0
        assert client.total_tokens > 0
        assert client.total_cost_usd > 0


@pytest.mark.integration
class TestVLLMIntegration:
    """Smoke tests against a real vLLM server."""

    @pytest.fixture(autouse=True)
    def skip_without_url(self):
        if not os.environ.get("VLLM_BASE_URL"):
            pytest.skip("VLLM_BASE_URL not set")

    def test_simple_query(self):
        model = os.environ.get("VLLM_MODEL", "meta-llama/Meta-Llama-3.1-70B-Instruct")
        client = VLLMClient(model)
        result, latency = client.query("What is 2+2? Answer with just the number.")
        assert "4" in result
        assert latency > 0
