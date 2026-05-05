"""Tests for src.tools.web_search module."""

import pytest
from unittest.mock import patch, MagicMock

from src.tools.web_search import WebSearchTool


class TestWebSearchToolInit:
    @patch("src.tools.web_search.settings")
    def test_init_without_tavily_key(self, mock_settings):
        mock_settings.tavily_api_key = ""
        tool = WebSearchTool()
        assert tool.tavily_client is None

    @patch("src.tools.web_search.settings")
    @patch("src.tools.web_search.TavilyClient")
    def test_init_with_tavily_key(self, mock_tavily_cls, mock_settings):
        mock_settings.tavily_api_key = "test-key"
        mock_client = MagicMock()
        mock_tavily_cls.return_value = mock_client
        tool = WebSearchTool()
        assert tool.tavily_client is mock_client


class TestWebSearchToolSearch:
    @patch("src.tools.web_search.DDGS")
    def test_search_returns_normalized_results(self, mock_ddgs_cls):
        mock_ddgs = MagicMock()
        mock_ddgs.text.return_value = [
            {"title": "Result 1", "href": "https://example.com/1", "body": "Snippet 1"},
            {"title": "Result 2", "href": "https://example.com/2", "body": "Snippet 2"},
        ]
        mock_ddgs_cls.return_value = mock_ddgs

        tool = WebSearchTool()
        results = tool.search("test query", max_results=2)

        assert len(results) == 2
        assert results[0]["title"] == "Result 1"
        assert results[0]["url"] == "https://example.com/1"
        assert results[0]["snippet"] == "Snippet 1"

    @patch("src.tools.web_search.DDGS")
    def test_search_passes_max_results_to_ddg(self, mock_ddgs_cls):
        mock_ddgs = MagicMock()
        mock_ddgs.text.return_value = []
        mock_ddgs_cls.return_value = mock_ddgs

        tool = WebSearchTool()
        tool.search("query", max_results=7)

        mock_ddgs.text.assert_called_once_with("query", max_results=7)

    @patch("src.tools.web_search.DDGS")
    def test_search_handles_missing_keys_gracefully(self, mock_ddgs_cls):
        mock_ddgs = MagicMock()
        mock_ddgs.text.return_value = [{"title": "Only title"}]
        mock_ddgs_cls.return_value = mock_ddgs

        tool = WebSearchTool()
        results = tool.search("query")

        assert results[0]["title"] == "Only title"
        assert results[0]["url"] == ""
        assert results[0]["snippet"] == ""

    @patch("src.tools.web_search.settings")
    @patch("src.tools.web_search.TavilyClient")
    @patch("src.tools.web_search.DDGS")
    def test_fallback_to_tavily_on_ddg_failure(self, mock_ddgs_cls, mock_tavily_cls, mock_settings):
        mock_settings.tavily_api_key = "test-key"
        mock_ddgs = MagicMock()
        mock_ddgs.text.side_effect = Exception("DDG failed")
        mock_ddgs_cls.return_value = mock_ddgs

        mock_tavily = MagicMock()
        mock_tavily.search.return_value = {
            "results": [{"title": "T", "url": "https://t.com", "content": "C"}]
        }
        mock_tavily_cls.return_value = mock_tavily

        tool = WebSearchTool()
        results = tool.search("query")

        assert len(results) == 1
        assert results[0]["title"] == "T"

    def test_raises_error_when_ddg_fails_and_no_tavily(self):
        import config.settings as settings_mod
        original_tavily = settings_mod.settings.tavily_api_key

        with patch("src.tools.web_search.DDGS") as mock_ddgs_cls:
            mock_ddgs = MagicMock()
            mock_ddgs.text.side_effect = Exception("DDG failed")
            mock_ddgs_cls.return_value = mock_ddgs

            try:
                settings_mod.settings.tavily_api_key = ""
                tool = WebSearchTool()
                with pytest.raises(RuntimeError):
                    tool.search("query")
            finally:
                settings_mod.settings.tavily_api_key = original_tavily
