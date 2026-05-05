"""Tests for src.graph.nodes.planner module."""

import pytest
from unittest.mock import patch, MagicMock

from src.graph.nodes.planner import PlannerNode
from src.graph.state import ResearchState


def make_state(query: str = "NVIDIA") -> ResearchState:
    return {
        "original_query": query,
        "subtasks": [],
        "current_subtask_idx": 0,
        "notes": [],
        "retry_count": 0,
        "max_retries": 3,
        "final_report": "",
        "errors": [],
    }


class TestPlannerNode:
    @patch("src.graph.nodes.planner.LLMClient")
    def test_creates_subtasks_from_llm_response(self, mock_llm_cls):
        mock_llm = MagicMock()
        mock_llm.chat.return_value = (
            '[{"id": 1, "description": "Find competitors", "search_query": "NVIDIA competitors"}]'
        )
        mock_llm_cls.return_value = mock_llm

        planner = PlannerNode()
        state = make_state()
        result = planner.call(state)

        assert len(result["subtasks"]) == 1
        assert result["subtasks"][0]["id"] == 1
        assert result["subtasks"][0]["description"] == "Find competitors"
        assert result["subtasks"][0]["status"] == "pending"
        assert result["subtasks"][0]["result"] == ""

    @patch("src.graph.nodes.planner.LLMClient")
    def test_sets_initial_state_fields(self, mock_llm_cls):
        mock_llm = MagicMock()
        mock_llm.chat.return_value = '[{"id": 1, "description": "Test", "search_query": "q"}]'
        mock_llm_cls.return_value = mock_llm

        planner = PlannerNode()
        state = make_state()
        state["notes"] = ["old note"]
        state["errors"] = ["old error"]
        state["retry_count"] = 5
        result = planner.call(state)

        assert result["current_subtask_idx"] == 0
        assert result["retry_count"] == 0
        assert result["notes"] == []
        assert result["errors"] == []

    @patch("src.graph.nodes.planner.LLMClient")
    def test_strips_markdown_fences(self, mock_llm_cls):
        mock_llm = MagicMock()
        mock_llm.chat.return_value = '```json\n[{"id": 1, "description": "Test", "search_query": "q"}]\n```'
        mock_llm_cls.return_value = mock_llm

        planner = PlannerNode()
        state = make_state()
        result = planner.call(state)

        assert len(result["subtasks"]) == 1

    @patch("src.graph.nodes.planner.LLMClient")
    def test_raises_on_invalid_json(self, mock_llm_cls):
        mock_llm = MagicMock()
        mock_llm.chat.return_value = "not valid json at all"
        mock_llm_cls.return_value = mock_llm

        planner = PlannerNode()
        state = make_state()

        with pytest.raises(ValueError, match="Failed to parse planner JSON"):
            planner.call(state)

    @patch("src.graph.nodes.planner.LLMClient")
    def test_uses_injected_llm(self, mock_llm_cls):
        mock_llm = MagicMock()
        mock_llm.chat.return_value = '[{"id": 1, "description": "Test", "search_query": "q"}]'

        planner = PlannerNode(llm=mock_llm)
        state = make_state()
        planner.call(state)

        mock_llm.chat.assert_called_once()
        mock_llm_cls.assert_not_called()

    @patch("src.graph.nodes.planner.LLMClient")
    def test_sends_correct_prompt(self, mock_llm_cls):
        mock_llm = MagicMock()
        mock_llm.chat.return_value = '[{"id": 1, "description": "Test", "search_query": "q"}]'
        mock_llm_cls.return_value = mock_llm

        planner = PlannerNode()
        state = make_state(query="Tesla")
        planner.call(state)

        call_args = mock_llm.chat.call_args[0][0]
        assert len(call_args) == 2
        assert call_args[0]["role"] == "system"
        assert "Tesla" in call_args[1]["content"]

    @patch("src.graph.nodes.planner.LLMClient")
    def test_handles_multiple_subtasks(self, mock_llm_cls):
        mock_llm = MagicMock()
        mock_llm.chat.return_value = (
            '[{"id": 1, "description": "Competitors", "search_query": "q1"},'
            '{"id": 2, "description": "Products", "search_query": "q2"},'
            '{"id": 3, "description": "Pricing", "search_query": "q3"}]'
        )
        mock_llm_cls.return_value = mock_llm

        planner = PlannerNode()
        state = make_state()
        result = planner.call(state)

        assert len(result["subtasks"]) == 3
        assert result["subtasks"][0]["search_query"] == "q1"
        assert result["subtasks"][2]["description"] == "Pricing"
