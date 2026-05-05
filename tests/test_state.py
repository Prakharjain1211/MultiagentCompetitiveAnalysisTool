"""Tests for src.graph.state module."""

import pytest
from src.graph.state import ResearchState, Subtask


class TestSubtask:
    def test_subtask_has_required_fields(self):
        subtask: Subtask = {
            "id": 1,
            "description": "Test description",
            "search_query": "test query",
            "status": "pending",
            "result": "",
        }
        assert subtask["id"] == 1
        assert subtask["description"] == "Test description"
        assert subtask["search_query"] == "test query"
        assert subtask["status"] == "pending"
        assert subtask["result"] == ""


class TestResearchState:
    def test_initial_state_structure(self):
        state: ResearchState = {
            "original_query": "NVIDIA",
            "subtasks": [],
            "current_subtask_idx": 0,
            "notes": [],
            "retry_count": 0,
            "max_retries": 3,
            "final_report": "",
            "errors": [],
        }
        assert state["original_query"] == "NVIDIA"
        assert state["subtasks"] == []
        assert state["current_subtask_idx"] == 0
        assert state["notes"] == []
        assert state["retry_count"] == 0
        assert state["max_retries"] == 3
        assert state["final_report"] == ""
        assert state["errors"] == []

    def test_state_mutable_updates(self):
        state: ResearchState = {
            "original_query": "NVIDIA",
            "subtasks": [],
            "current_subtask_idx": 0,
            "notes": [],
            "retry_count": 0,
            "max_retries": 3,
            "final_report": "",
            "errors": [],
        }
        state["notes"].append("Test note")
        state["retry_count"] += 1

        assert len(state["notes"]) == 1
        assert state["retry_count"] == 1

    def test_state_with_subtasks(self):
        subtask: Subtask = {
            "id": 1,
            "description": "Research competitors",
            "search_query": "NVIDIA competitors",
            "status": "pending",
            "result": "",
        }
        state: ResearchState = {
            "original_query": "NVIDIA",
            "subtasks": [subtask],
            "current_subtask_idx": 0,
            "notes": [],
            "retry_count": 0,
            "max_retries": 3,
            "final_report": "",
            "errors": [],
        }
        assert len(state["subtasks"]) == 1
        assert state["subtasks"][0]["description"] == "Research competitors"
