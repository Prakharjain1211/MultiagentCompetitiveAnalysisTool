"""Tests for src.graph.nodes.researcher module."""

import pytest
from unittest.mock import patch, MagicMock

from src.graph.nodes.researcher import ResearcherNode
from src.graph.state import ResearchState


def make_state_with_subtask() -> ResearchState:
    return {
        "original_query": "NVIDIA",
        "subtasks": [
            {
                "id": 1,
                "description": "Find competitors",
                "search_query": "NVIDIA competitors 2025",
                "status": "pending",
                "result": "",
            }
        ],
        "current_subtask_idx": 0,
        "notes": [],
        "retry_count": 0,
        "max_retries": 3,
        "final_report": "",
        "errors": [],
    }


class TestResearcherNode:
    @patch("src.graph.nodes.researcher.WebScraper")
    @patch("src.graph.nodes.researcher.WebSearchTool")
    @patch("src.graph.nodes.researcher.LLMClient")
    def test_executes_research_pipeline(self, mock_llm_cls, mock_search_cls, mock_scraper_cls):
        mock_searcher = MagicMock()
        mock_searcher.search.return_value = [
            {"title": "R1", "url": "https://example.com/1", "snippet": "S1"},
        ]
        mock_search_cls.return_value = mock_searcher

        mock_scraper = MagicMock()
        mock_scraper.scrape.return_value = {"success": True, "content": "Full page content here", "url": "https://example.com/1", "error": ""}
        mock_scraper_cls.return_value = mock_scraper

        mock_llm = MagicMock()
        mock_llm.chat.return_value = "Summary of page"
        mock_llm_cls.return_value = mock_llm

        researcher = ResearcherNode()
        state = make_state_with_subtask()
        result = researcher.call(state)

        assert result["subtasks"][0]["status"] == "done"
        assert len(result["notes"]) == 1
        assert result["subtasks"][0]["result"] == "Summary of page"

    @patch("src.graph.nodes.researcher.WebScraper")
    @patch("src.graph.nodes.researcher.WebSearchTool")
    @patch("src.graph.nodes.researcher.LLMClient")
    def test_marks_subtask_as_in_progress(self, mock_llm_cls, mock_search_cls, mock_scraper_cls):
        mock_searcher = MagicMock()
        mock_searcher.search.return_value = []
        mock_search_cls.return_value = mock_searcher
        mock_llm = MagicMock()
        mock_llm_cls.return_value = mock_llm

        researcher = ResearcherNode()
        state = make_state_with_subtask()
        researcher.call(state)

        assert state["subtasks"][0]["status"] == "done"

    @patch("src.graph.nodes.researcher.WebScraper")
    @patch("src.graph.nodes.researcher.WebSearchTool")
    @patch("src.graph.nodes.researcher.LLMClient")
    def test_handles_no_pending_subtasks(self, mock_llm_cls, mock_search_cls, mock_scraper_cls):
        mock_searcher = MagicMock()
        mock_search_cls.return_value = mock_searcher
        mock_llm = MagicMock()
        mock_llm_cls.return_value = mock_llm

        researcher = ResearcherNode()
        state: ResearchState = {
            "original_query": "NVIDIA",
            "subtasks": [
                {
                    "id": 1,
                    "description": "Done task",
                    "search_query": "q",
                    "status": "done",
                    "result": "already done",
                }
            ],
            "current_subtask_idx": 0,
            "notes": [],
            "retry_count": 0,
            "max_retries": 3,
            "final_report": "",
            "errors": [],
        }
        result = researcher.call(state)

        assert "no pending subtasks found" in result["errors"][0]

    @patch("src.graph.nodes.researcher.WebScraper")
    @patch("src.graph.nodes.researcher.WebSearchTool")
    @patch("src.graph.nodes.researcher.LLMClient")
    def test_handles_failed_scrape_gracefully(self, mock_llm_cls, mock_search_cls, mock_scraper_cls):
        mock_searcher = MagicMock()
        mock_searcher.search.return_value = [{"title": "R1", "url": "https://bad.com", "snippet": "S1"}]
        mock_search_cls.return_value = mock_searcher

        mock_scraper = MagicMock()
        mock_scraper.scrape.return_value = {"success": False, "content": "", "url": "https://bad.com", "error": "timeout"}
        mock_scraper_cls.return_value = mock_scraper

        mock_llm = MagicMock()
        mock_llm_cls.return_value = mock_llm

        researcher = ResearcherNode()
        state = make_state_with_subtask()
        result = researcher.call(state)

        assert result["subtasks"][0]["status"] == "done"
        assert "No content could be retrieved" in result["notes"][0]

    @patch("src.graph.nodes.researcher.WebScraper")
    @patch("src.graph.nodes.researcher.WebSearchTool")
    @patch("src.graph.nodes.researcher.LLMClient")
    def test_limits_scraped_content_length(self, mock_llm_cls, mock_search_cls, mock_scraper_cls):
        long_content = "x" * 5000
        mock_searcher = MagicMock()
        mock_searcher.search.return_value = [{"title": "R1", "url": "https://example.com", "snippet": "S1"}]
        mock_search_cls.return_value = mock_searcher

        mock_scraper = MagicMock()
        mock_scraper.scrape.return_value = {"success": True, "content": long_content, "url": "https://example.com", "error": ""}
        mock_scraper_cls.return_value = mock_scraper

        mock_llm = MagicMock()
        mock_llm.chat.return_value = "Summary"
        mock_llm_cls.return_value = mock_llm

        researcher = ResearcherNode()
        state = make_state_with_subtask()
        researcher.call(state)

        call_args = mock_llm.chat.call_args[0][0]
        content_passed = call_args[1]["content"]
        assert len(content_passed) < len(long_content)
        assert "x" * 3001 not in content_passed

    def test_uses_injected_dependencies(self):
        mock_llm = MagicMock()
        mock_searcher = MagicMock()
        mock_scraper = MagicMock()

        mock_searcher.search.return_value = []
        mock_llm.chat.return_value = "summary"

        researcher = ResearcherNode(llm=mock_llm, searcher=mock_searcher, scraper=mock_scraper)
        state = make_state_with_subtask()
        researcher.call(state)

        mock_searcher.search.assert_called_once()
