"""Tests for src.graph.nodes.validator module."""

import pytest
from unittest.mock import patch, MagicMock

from src.graph.nodes.validator import ValidatorNode
from src.graph.state import ResearchState


def make_state_with_note(note: str = "Good relevant note about NVIDIA competitors and market") -> ResearchState:
    return {
        "original_query": "NVIDIA",
        "subtasks": [
            {
                "id": 1,
                "description": "Find competitors",
                "search_query": "NVIDIA competitors 2025",
                "status": "done",
                "result": "",
            }
        ],
        "current_subtask_idx": 0,
        "notes": [note],
        "retry_count": 0,
        "max_retries": 3,
        "final_report": "",
        "errors": [],
    }


class TestValidatorNode:
    @patch("src.graph.nodes.validator.LLMClient")
    def test_advances_on_relevant_note(self, mock_llm_cls):
        mock_llm = MagicMock()
        mock_llm.chat.return_value = "YES"
        mock_llm_cls.return_value = mock_llm

        validator = ValidatorNode()
        state = make_state_with_note()
        result = validator.call(state)

        assert result["current_subtask_idx"] == 1
        assert result["retry_count"] == 0

    @patch("src.graph.nodes.validator.LLMClient")
    def test_retries_on_irrelevant_note(self, mock_llm_cls):
        mock_llm = MagicMock()
        mock_llm.chat.return_value = "NO"
        mock_llm_cls.return_value = mock_llm

        validator = ValidatorNode()
        state = make_state_with_note(note="Cooking recipes for pasta")
        result = validator.call(state)

        assert result["retry_count"] == 1
        assert result["subtasks"][0]["status"] == "pending"

    def test_advances_on_empty_notes_list(self):
        validator = ValidatorNode()
        state = make_state_with_note(note="")
        state["notes"] = []
        result = validator.call(state)

        assert "no notes to validate" in result["errors"][0]

    def test_retries_on_short_note(self):
        validator = ValidatorNode()
        state = make_state_with_note(note="short")
        state["retry_count"] = 0
        state["max_retries"] = 3

        with patch.object(validator, "_refine_query", return_value="better query"):
            result = validator.call(state)

        assert result["retry_count"] == 1
        assert result["subtasks"][0]["status"] == "pending"
        assert result["subtasks"][0]["search_query"] == "better query"

    def test_fails_subtask_after_max_retries_short_note(self):
        validator = ValidatorNode()
        state = make_state_with_note(note="short")
        state["retry_count"] = 3
        state["max_retries"] = 3

        result = validator.call(state)

        assert result["subtasks"][0]["status"] == "failed"
        assert result["current_subtask_idx"] == 1
        assert result["retry_count"] == 0

    def test_fails_subtask_after_max_retries_irrelevant(self):
        with patch("src.graph.nodes.validator.LLMClient") as mock_llm_cls:
            mock_llm = MagicMock()
            mock_llm.chat.return_value = "NO"
            mock_llm_cls.return_value = mock_llm

            validator = ValidatorNode()
            state = make_state_with_note(note="completely irrelevant")
            state["retry_count"] = 3
            state["max_retries"] = 3

            result = validator.call(state)

            assert result["subtasks"][0]["status"] == "failed"
            assert result["current_subtask_idx"] == 1

    @patch("src.graph.nodes.validator.LLMClient")
    def test_refine_query_returns_stripped_response(self, mock_llm_cls):
        mock_llm = MagicMock()
        mock_llm.chat.return_value = "  refined query  "
        mock_llm_cls.return_value = mock_llm

        validator = ValidatorNode()
        subtask = {
            "id": 1,
            "description": "Test",
            "search_query": "old query",
            "status": "pending",
            "result": "",
        }
        result = validator._refine_query(subtask, "NVIDIA")

        assert result == "refined query"

    @patch("src.graph.nodes.validator.LLMClient")
    def test_case_insensitive_yes(self, mock_llm_cls):
        mock_llm = MagicMock()
        mock_llm.chat.return_value = "yes"
        mock_llm_cls.return_value = mock_llm

        validator = ValidatorNode()
        state = make_state_with_note()
        result = validator.call(state)

        assert result["current_subtask_idx"] == 1

    @patch("src.graph.nodes.validator.LLMClient")
    def test_handles_whitespace_in_yes_response(self, mock_llm_cls):
        mock_llm = MagicMock()
        mock_llm.chat.return_value = "  YES  "
        mock_llm_cls.return_value = mock_llm

        validator = ValidatorNode()
        state = make_state_with_note()
        result = validator.call(state)

        assert result["current_subtask_idx"] == 1
