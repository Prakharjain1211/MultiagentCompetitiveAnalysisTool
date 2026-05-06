"""Tests for src.api module (FastAPI endpoints)."""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from src.api import app, _runs


@pytest.fixture(autouse=True)
def clear_runs():
    """Clear the in-memory run store before each test."""
    _runs.clear()
    yield
    _runs.clear()


@pytest.fixture
def client():
    return TestClient(app)


class TestHealthEndpoint:
    def test_health_returns_ok(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


class TestAnalyzeEndpoint:
    @patch("src.api._graph")
    def test_submit_analysis_returns_202(self, mock_graph, client):
        response = client.post("/analyze", json={"company": "NVIDIA"})
        assert response.status_code == 202
        data = response.json()
        assert "run_id" in data
        assert data["status"] == "pending"

    @patch("src.api._graph")
    def test_submit_analysis_uses_default_model(self, mock_graph, client):
        response = client.post("/analyze", json={"company": "NVIDIA"})
        assert response.status_code == 202

    @patch("src.api._graph")
    def test_submit_analysis_with_custom_model(self, mock_graph, client):
        response = client.post("/analyze", json={"company": "NVIDIA", "model": "gpt-4"})
        assert response.status_code == 202


class TestGetAnalysisEndpoint:
    @patch("src.api._graph")
    def test_get_completed_analysis(self, mock_graph, client):
        mock_graph.invoke.return_value = {
            "final_report": "# Report",
            "subtasks": [],
            "errors": [],
        }

        submit = client.post("/analyze", json={"company": "NVIDIA"})
        run_id = submit.json()["run_id"]

        response = client.get(f"/analyze/{run_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["run_id"] == run_id

    def test_get_nonexistent_run_returns_404(self, client):
        response = client.get("/analyze/nonexistent-id")
        assert response.status_code == 404

    @patch("src.api._graph")
    def test_get_analysis_includes_errors(self, mock_graph, client):
        mock_graph.invoke.return_value = {
            "final_report": "",
            "subtasks": [],
            "errors": ["Test error"],
        }

        submit = client.post("/analyze", json={"company": "NVIDIA"})
        run_id = submit.json()["run_id"]

        response = client.get(f"/analyze/{run_id}")
        data = response.json()
        assert "errors" in data


class TestAnalyzeRequestModel:
    def test_request_requires_company(self):
        from src.api import AnalyzeRequest
        with pytest.raises(Exception):
            AnalyzeRequest()

    def test_request_default_model(self):
        from src.api import AnalyzeRequest
        req = AnalyzeRequest(company="NVIDIA")
        assert req.model == "gpt-4o-mini"

    def test_request_custom_model(self):
        from src.api import AnalyzeRequest
        req = AnalyzeRequest(company="NVIDIA", model="gpt-4")
        assert req.model == "gpt-4"
