"""Tests for src.rag.chunker module."""

import pytest
from unittest.mock import patch, MagicMock

from langchain_core.documents import Document

from src.rag.chunker import TextChunker


class TestTextChunkerInit:
    def test_default_settings(self):
        with patch("src.rag.chunker.settings") as mock_settings:
            mock_settings.max_chunk_size = 500
            mock_settings.chunk_overlap = 50
            chunker = TextChunker()
            assert chunker.splitter._chunk_size == 500
            assert chunker.splitter._chunk_overlap == 50

    def test_custom_chunk_size(self):
        chunker = TextChunker(chunk_size=1000, chunk_overlap=100)
        assert chunker.splitter._chunk_size == 1000
        assert chunker.splitter._chunk_overlap == 100


class TestTextChunkerChunk:
    def test_chunks_single_short_text(self):
        chunker = TextChunker(chunk_size=500, chunk_overlap=0)
        texts = ["This is a short test sentence."]
        docs = chunker.chunk(texts)

        assert len(docs) == 1
        assert isinstance(docs[0], Document)
        assert docs[0].page_content == "This is a short test sentence."
        assert docs[0].metadata["source_index"] == 0

    def test_preserves_source_index(self):
        chunker = TextChunker(chunk_size=500, chunk_overlap=0)
        texts = ["First note.", "Second note."]
        docs = chunker.chunk(texts)

        indices = [doc.metadata["source_index"] for doc in docs]
        assert 0 in indices
        assert 1 in indices

    def test_empty_input_returns_empty_list(self):
        chunker = TextChunker(chunk_size=500, chunk_overlap=0)
        docs = chunker.chunk([])
        assert docs == []

    def test_empty_string_in_list(self):
        chunker = TextChunker(chunk_size=500, chunk_overlap=0)
        docs = chunker.chunk([""])
        assert docs == []

    def test_splits_long_text_into_multiple_chunks(self):
        chunker = TextChunker(chunk_size=20, chunk_overlap=5)
        long_text = "word1 word2 word3 word4 word5 word6 word7 word8"
        docs = chunker.chunk([long_text])

        assert len(docs) > 1
        for doc in docs:
            assert doc.metadata["source_index"] == 0

    def test_multiple_notes(self):
        chunker = TextChunker(chunk_size=500, chunk_overlap=0)
        texts = [
            "Note one about company A.",
            "Note two about company B.",
        ]
        docs = chunker.chunk(texts)

        assert len(docs) == 2
        assert docs[0].metadata["source_index"] == 0
        assert docs[1].metadata["source_index"] == 1
