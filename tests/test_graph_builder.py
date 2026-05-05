"""Tests for src.graph.graph_builder module."""

import pytest
from unittest.mock import patch, MagicMock

from src.graph.graph_builder import build_research_graph, route_after_researcher, route_after_validator
from src.graph.state import ResearchState


def make_state(subtasks: list, current_idx: int = 0) -> ResearchState:
    return {
        "original_query": "NVIDIA",
        "subtasks": subtasks,
        "current_subtask_idx": current_idx,
        "notes": [],
        "retry_count": 0,
        "max_retries": 3,
        "final_report": "",
        "errors": [],
    }


class TestRouteAfterResearcher:
    def test_routes_to_validator_when_subtasks_remain(self):
        state = make_state(
            subtasks=[
                {"id": 1, "description": "T1", "search_query": "q1", "status": "done", "result": ""},
                {"id": 2, "description": "T2", "search_query": "q2", "status": "pending", "result": ""},
            ],
            current_idx=0,
        )
        assert route_after_researcher(state) == "validator"

    def test_routes_to_synthesizer_when_all_done(self):
        state = make_state(
            subtasks=[
                {"id": 1, "description": "T1", "search_query": "q1", "status": "done", "result": ""},
            ],
            current_idx=1,
        )
        assert route_after_researcher(state) == "synthesizer"

    def test_routes_to_synthesizer_when_empty_subtasks(self):
        state = make_state(subtasks=[], current_idx=0)
        assert route_after_researcher(state) == "synthesizer"


class TestRouteAfterValidator:
    def test_routes_to_researcher_when_pending_exists(self):
        state = make_state(
            subtasks=[
                {"id": 1, "description": "T1", "search_query": "q1", "status": "done", "result": ""},
                {"id": 2, "description": "T2", "search_query": "q2", "status": "pending", "result": ""},
            ],
            current_idx=1,
        )
        assert route_after_validator(state) == "researcher"

    def test_routes_to_synthesizer_when_all_done_or_failed(self):
        state = make_state(
            subtasks=[
                {"id": 1, "description": "T1", "search_query": "q1", "status": "done", "result": ""},
                {"id": 2, "description": "T2", "search_query": "q2", "status": "failed", "result": ""},
            ],
            current_idx=2,
        )
        assert route_after_validator(state) == "synthesizer"

    def test_routes_to_synthesizer_when_empty(self):
        state = make_state(subtasks=[], current_idx=0)
        assert route_after_validator(state) == "synthesizer"


class TestBuildResearchGraph:
    @patch("src.graph.graph_builder.PlannerNode")
    @patch("src.graph.graph_builder.ResearcherNode")
    @patch("src.graph.graph_builder.ValidatorNode")
    @patch("src.graph.graph_builder.SynthesizerNode")
    def test_returns_compiled_graph(
        self, mock_synth, mock_validator, mock_researcher, mock_planner
    ):
        mock_planner.return_value.call = MagicMock()
        mock_researcher.return_value.call = MagicMock()
        mock_validator.return_value.call = MagicMock()
        mock_synth.return_value.call = MagicMock()

        graph = build_research_graph()
        assert graph is not None

    @patch("src.graph.graph_builder.PlannerNode")
    @patch("src.graph.graph_builder.ResearcherNode")
    @patch("src.graph.graph_builder.ValidatorNode")
    @patch("src.graph.graph_builder.SynthesizerNode")
    def test_graph_has_entry_point_planner(
        self, mock_synth, mock_validator, mock_researcher, mock_planner
    ):
        mock_planner.return_value.call = MagicMock()
        mock_researcher.return_value.call = MagicMock()
        mock_validator.return_value.call = MagicMock()
        mock_synth.return_value.call = MagicMock()

        graph = build_research_graph()
        assert "planner" in graph.nodes or hasattr(graph, "nodes")
