"""
Synthesizer node — produces the final competitive analysis briefing.

Pipeline:
  1. Chunk all research notes via TextChunker.
  2. Index chunks into VectorStore.
  3. For each of 4 briefing sections, retrieve top-3 relevant chunks.
  4. Call LLM per section with the retrieved context.
  5. Assemble sections into a final Markdown report.

Usage:
    from src.graph.nodes.synthesizer import SynthesizerNode
    synthesizer = SynthesizerNode()
    state = synthesizer.call(state)
"""

from config.prompts import SECTION_GENERATOR_PROMPT
from src.graph.state import ResearchState
from src.rag.chunker import TextChunker
from src.rag.vector_store import VectorStore
from src.tools.llm import LLMClient


# Standard sections for a competitive analysis briefing.
SECTIONS = [
    "Company Overview & Market Position",
    "Competitor Landscape",
    "Product & Strategy Analysis",
    "Strengths, Weaknesses & Recommendations",
]


class SynthesizerNode:
    """Generates a structured Markdown briefing from research notes using RAG.

    Attributes:
        llm: LLMClient for section generation.
        chunker: TextChunker for splitting notes.
        vector_store: VectorStore for RAG retrieval.
    """

    def __init__(
        self,
        llm: LLMClient | None = None,
        chunker: TextChunker | None = None,
        vector_store: VectorStore | None = None,
    ):
        self.llm = llm or LLMClient()
        self.chunker = chunker or TextChunker()
        self.vector_store = vector_store or VectorStore()

    def call(self, state: ResearchState) -> ResearchState:
        """Generate the final report by chunking, indexing, retrieving, and writing.

        Clears any previous vector store data, indexes the current notes,
        retrieves per-section evidence, and calls the LLM to write each section.

        Args:
            state: Research state with notes populated.

        Returns:
            Updated state with final_report containing the full Markdown briefing.
        """
        # 1. Chunk and index notes into the vector store.
        self.vector_store.clear()
        documents = self.chunker.chunk(state["notes"])
        self.vector_store.index(documents)

        # 2. Generate each section using RAG retrieval.
        sections = []
        company = state["original_query"]

        for section_name in SECTIONS:
            retrieved = self.vector_store.retrieve(section_name, k=3)
            chunks_text = "\n\n".join(doc.page_content for doc in retrieved)

            prompt = SECTION_GENERATOR_PROMPT.format(
                section_name=section_name,
                company=company,
                retrieved_chunks=chunks_text,
            )

            section_content = self.llm.chat([
                {"role": "system", "content": "You are a competitive analysis expert writing a professional briefing."},
                {"role": "user", "content": prompt},
            ])
            sections.append(f"## {section_name}\n\n{section_content}")

        # 3. Assemble final report.
        header = f"# Competitive Analysis: {company}\n\n"
        state["final_report"] = header + "\n\n---\n\n".join(sections)

        return state