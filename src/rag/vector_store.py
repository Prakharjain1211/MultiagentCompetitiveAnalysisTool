"""
Vector store module for RAG-based retrieval.

Wraps Chroma with HuggingFace sentence embeddings (all-MiniLM-L6-v2).
Supports in-memory and persistent modes. Provides index, retrieve,
and clear operations with logging.

Usage:
    from src.rag.vector_store import VectorStore
    store = VectorStore(persist_directory="data/chroma_db")
    store.index(documents)
    results = store.retrieve("competitor market share", k=3)
"""

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

from loguru import logger

from config.settings import settings


class VectorStore:
    """Chroma-based vector store with local embeddings.

    Uses all-MiniLM-L6-v2 (384-dim, fast, free) via HuggingFace for
    embedding. Supports optional persistence to disk.

    Attributes:
        embedder: HuggingFace embedding model instance.
        db: Chroma vector store instance.
    """

    def __init__(self, persist_directory: str | None = None):
        """Initialise the embedding model and Chroma store.

        Args:
            persist_directory: Optional path for Chroma persistence.
                               If None, runs in-memory only.
        """
        self._persist_directory = persist_directory
        self.embedder = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
        )
        self.db = Chroma(
            embedding_function=self.embedder,
            persist_directory=persist_directory,
        )

    def index(self, documents: list[Document]) -> int:
        """Index a list of documents into the vector store.

        Adds documents to Chroma and logs the total chunk count.
        Persists to disk if a persist_directory was configured.

        Args:
            documents: List of LangChain Documents to index.

        Returns:
            Number of documents indexed.
        """
        if not documents:
            logger.warning("No documents to index")
            return 0

        self.db.add_documents(documents)
        logger.info(f"Indexed {len(documents)} chunks into vector store")
        return len(documents)

    def retrieve(self, query: str, k: int | None = None) -> list[Document]:
        """Retrieve the top-k most relevant documents for a query.

        Performs a similarity search against the indexed embeddings.

        Args:
            query: Natural language query string.
            k: Number of results to return (default from settings).

        Returns:
            List of LangChain Document objects sorted by relevance.
        """
        top_k = k or settings.top_k_retrieval
        results = self.db.similarity_search(query, k=top_k)
        logger.debug(f"Retrieved {len(results)} chunks for query: {query[:50]}...")
        return results

    def clear(self) -> None:
        """Delete all documents from the vector store.

        Useful between runs to avoid stale data from previous analyses.
        Re-creates the Chroma instance so subsequent operations work.
        """
        self.db.delete_collection()
        # Re-create the Chroma instance so the collection is usable again.
        self.db = Chroma(
            embedding_function=self.embedder,
            persist_directory=self._persist_directory,
        )
        logger.info("Vector store cleared")