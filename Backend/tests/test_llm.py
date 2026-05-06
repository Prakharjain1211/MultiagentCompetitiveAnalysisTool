"""Tests for src.tools.llm module."""

import pytest
from unittest.mock import patch, MagicMock

from src.tools.llm import LLMClient


class TestLLMClientInit:
    def test_default_model(self):
        with patch("src.tools.llm.OpenAI"):
            client = LLMClient()
            assert client.model == "gpt-4o-mini"

    def test_custom_model(self):
        with patch("src.tools.llm.OpenAI"):
            client = LLMClient(model="gpt-4")
            assert client.model == "gpt-4"

    def test_default_temperature(self):
        with patch("src.tools.llm.OpenAI"):
            client = LLMClient()
            assert client.temperature == 0.2

    def test_custom_temperature(self):
        with patch("src.tools.llm.OpenAI"):
            client = LLMClient(temperature=0.8)
            assert client.temperature == 0.8


class TestLLMClientChat:
    @patch("src.tools.llm.OpenAI")
    def test_returns_stripped_response(self, mock_openai_cls):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "  Hello world  "
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_cls.return_value = mock_client

        llm = LLMClient()
        result = llm.chat([{"role": "user", "content": "Hi"}])

        assert result == "Hello world"

    @patch("src.tools.llm.OpenAI")
    def test_passes_messages_to_api(self, mock_openai_cls):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "OK"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_cls.return_value = mock_client

        llm = LLMClient()
        messages = [{"role": "user", "content": "Test"}]
        llm.chat(messages)

        call_kwargs = mock_client.chat.completions.create.call_args[1]
        assert call_kwargs["messages"] == messages

    @patch("src.tools.llm.OpenAI")
    def test_uses_model_override(self, mock_openai_cls):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "OK"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_cls.return_value = mock_client

        llm = LLMClient(model="gpt-4o-mini")
        llm.chat([{"role": "user", "content": "Hi"}], model="gpt-4")

        call_kwargs = mock_client.chat.completions.create.call_args[1]
        assert call_kwargs["model"] == "gpt-4"

    @patch("src.tools.llm.OpenAI")
    def test_fallback_on_first_model_failure(self, mock_openai_cls):
        mock_client = MagicMock()
        call_count = 0

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("Primary failed")
            mock_resp = MagicMock()
            mock_resp.choices[0].message.content = "Fallback worked"
            return mock_resp

        mock_client.chat.completions.create.side_effect = side_effect
        mock_openai_cls.return_value = mock_client

        llm = LLMClient()
        result = llm.chat([{"role": "user", "content": "Hi"}])

        assert result == "Fallback worked"
        assert call_count == 2

    @patch("src.tools.llm.OpenAI")
    def test_raises_runtime_error_when_all_models_fail(self, mock_openai_cls):
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = Exception("All failed")
        mock_openai_cls.return_value = mock_client

        llm = LLMClient()
        with pytest.raises(RuntimeError, match="LLM call failed after all fallbacks"):
            llm.chat([{"role": "user", "content": "Hi"}])

    @patch("src.tools.llm.OpenAI")
    def test_passes_temperature(self, mock_openai_cls):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "OK"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_cls.return_value = mock_client

        llm = LLMClient(temperature=0.7)
        llm.chat([{"role": "user", "content": "Hi"}])

        call_kwargs = mock_client.chat.completions.create.call_args[1]
        assert call_kwargs["temperature"] == 0.7
