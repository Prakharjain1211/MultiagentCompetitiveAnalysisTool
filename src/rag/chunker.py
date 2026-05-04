"""
Text chunking module for RAG preprocessing.

Splits research notes into overlapping chunks suitable for embedding
and vector search. Uses LangChain's RecursiveCharacterTextSplitter to
preserve semantic boundaries (paragraphs > sentences > phrases).

Usage:
    from src.rag.chunker import TextChunker
    chunker = TextChunker(chunk_size=500, chunk_overlap=50)
    documents = chunker.chunk(["note 1 text...", "note 2 text..."])
"""

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from config.settings import settings


class TextChunker:
    """Splits text documents into overlapping chunks for RAG indexing.

    Uses RecursiveCharacterTextSplitter with a cascading separator list
    to keep semantically related text together.

    Attributes:
        splitter: Configured LangChain text splitter instance.
    """

    def __init__(self, chunk_size: int | None = None, chunk_overlap: int | None = None):
        """Initialise the chunker with configurable size and overlap.

        Args:
            chunk_size: Maximum characters per chunk (default from settings).
            chunk_overlap: Overlap characters between chunks (default from settings).
        """
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size or settings.max_chunk_size,
            chunk_overlap=chunk_overlap or settings.chunk_overlap,
            separators=["\n\n", "\n", ". ", " "],
            length_function=len,
        )

    def chunk(self, texts: list[str]) -> list[Document]:
        """Split a list of text strings into LangChain Document chunks.

        Each chunk preserves the source text index in metadata for
        traceability back to the original research note.

        Args:
            texts: List of text strings to be chunked.

        Returns:
            List of LangChain Document objects, each with page_content
            and metadata (source_index).
        """
        documents = []
        for idx, text in enumerate(texts):
            chunks = self.splitter.split_text(text)
            for chunk in chunks:
                documents.append(Document(
                    page_content=chunk,
                    metadata={"source_index": idx},
                ))
        return documents