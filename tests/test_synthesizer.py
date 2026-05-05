"""Tests for src.graph.nodes.synthesizer module."""

import pytest
from unittest.mock import patch, MagicMock

from langchain_core.documents import Document

from src.graph.nodes.synthesizer import SynthesizerNode, SECTIONS
from src.graph.state import ResearchState


def make_state_with_notes() -> ResearchState:
    return {
        "original_query": "NVIDIA",
        "subtasks": [],
        "current_subtask_idx": 0,
        "notes": [
            "NVIDIA is a leader in GPU and AI chips. Competitors include AMD and Intel.",
            "Market share for AI accelerators is dominated by NVIDIA with 80%+.",
        ],
        "retry_count": 0,
        "max_retries": 3,
        "final_report": "",
        "errors": [],
    }


class TestSynthesizerNode:
    @patch("src.graph.nodes.synthesizer.VectorStore")
    @patch("src.graph.nodes.synthesizer.TextChunker")
    @patch("src.graph.nodes.synthesizer.LLMClient")
    def test_generates_final_report(self, mock_llm_cls, mock_chunker_cls, mock_vs_cls):
        mock_chunker = MagicMock()
        mock_chunker.chunk.return_value = [Document(page_content="chunk1")]
        mock_chunker_cls.return_value = mock_chunker

        mock_vs = MagicMock()
        mock_vs.retrieve.return_value = [Document(page_content="evidence")]
        mock_vs_cls.return_value = mock_vs

        mock_llm = MagicMock()
        mock_llm.chat.return_value = "Section content"
        mock_llm_cls.return_value = mock_llm

        synthesizer = SynthesizerNode()
        state = make_state_with_notes()
        result = synthesizer.call(state)

        assert result["final_report"].startswith("# Competitive Analysis: NVIDIA")
        for section in SECTIONS:
            assert f"## {section}" in result["final_report"]

    @patch("src.graph.nodes.synthesizer.VectorStore")
    @patch("src.graph.nodes.synthesizer.TextChunker")
    @patch("src.graph.nodes.synthesizer.LLMClient")
    def test_clears_vector_store_before_indexing(self, mock_llm_cls, mock_chunker_cls, mock_vs_cls):
        mock_chunker = MagicMock()
        mock_chunker.chunk.return_value = []
        mock_chunker_cls.return_value = mock_chunker

        mock_vs = MagicMock()
        mock_vs_cls.return_value = mock_vs

        mock_llm = MagicMock()
        mock_llm.chat.return_value = "content"
        mock_llm_cls.return_value = mock_llm

        synthesizer = SynthesizerNode()
        state = make_state_with_notes()
        synthesizer.call(state)

        mock_vs.clear.assert_called_once()

    @patch("src.graph.nodes.synthesizer.VectorStore")
    @patch("src.graph.nodes.synthesizer.TextChunker")
    @patch("src.graph.nodes.synthesizer.LLMClient")
    def test_chunks_notes(self, mock_llm_cls, mock_chunker_cls, mock_vs_cls):
        mock_chunker = MagicMock()
        mock_chunker.chunk.return_value = []
        mock_chunker_cls.return_value = mock_chunker

        mock_vs = MagicMock()
        mock_vs.retrieve.return_value = []
        mock_vs_cls.return_value = mock_vs

        mock_llm = MagicMock()
        mock_llm.chat.return_value = "content"
        mock_llm_cls.return_value = mock_llm

        synthesizer = SynthesizerNode()
        state = make_state_with_notes()
        synthesizer.call(state)

        mock_chunker.chunk.assert_called_once_with(state["notes"])

    @patch("src.graph.nodes.synthesizer.VectorStore")
    @patch("src.graph.nodes.synthesizer.TextChunker")
    @patch("src.graph.nodes.synthesizer.LLMClient")
    def test_indexes_documents(self, mock_llm_cls, mock_chunker_cls, mock_vs_cls):
        docs = [Document(page_content="chunk1")]
        mock_chunker = MagicMock()
        mock_chunker.chunk.return_value = docs
        mock_chunker_cls.return_value = mock_chunker

        mock_vs = MagicMock()
        mock_vs.retrieve.return_value = []
        mock_vs_cls.return_value = mock_vs

        mock_llm = MagicMock()
        mock_llm.chat.return_value = "content"
        mock_llm_cls.return_value = mock_llm

        synthesizer = SynthesizerNode()
        state = make_state_with_notes()
        synthesizer.call(state)

        mock_vs.index.assert_called_once_with(docs)

    @patch("src.graph.nodes.synthesizer.VectorStore")
    @patch("src.graph.nodes.synthesizer.TextChunker")
    @patch("src.graph.nodes.synthesizer.LLMClient")
    def test_retrieves_per_section(self, mock_llm_cls, mock_chunker_cls, mock_vs_cls):
        mock_chunker = MagicMock()
        mock_chunker.chunk.return_value = []
        mock_chunker_cls.return_value = mock_chunker

        mock_vs = MagicMock()
        mock_vs.retrieve.return_value = []
        mock_vs_cls.return_value = mock_vs

        mock_llm = MagicMock()
        mock_llm.chat.return_value = "content"
        mock_llm_cls.return_value = mock_llm

        synthesizer = SynthesizerNode()
        state = make_state_with_notes()
        synthesizer.call(state)

        assert mock_vs.retrieve.call_count == len(SECTIONS)

    def test_uses_injected_dependencies(self):
        mock_llm = MagicMock()
        mock_chunker = MagicMock()
        mock_vs = MagicMock()

        mock_chunker.chunk.return_value = []
        mock_vs.retrieve.return_value = []
        mock_llm.chat.return_value = "content"

        synthesizer = SynthesizerNode(llm=mock_llm, chunker=mock_chunker, vector_store=mock_vs)
        state = make_state_with_notes()
        synthesizer.call(state)

        mock_llm.chat.assert_called()
        mock_chunker.chunk.assert_called_once()
        mock_vs.clear.assert_called_once()


class TestSynthesizerSections:
    def test_sections_has_four_items(self):
        assert len(SECTIONS) == 4

    def test_sections_contains_company_overview(self):
        assert any("Company Overview" in s for s in SECTIONS)

    def test_sections_contains_competitor_landscape(self):
        assert any("Competitor Landscape" in s for s in SECTIONS)
