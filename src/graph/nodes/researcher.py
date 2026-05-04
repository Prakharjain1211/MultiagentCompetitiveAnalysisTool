"""
Researcher node — executes web research for a single subtask.

For the current pending subtask:
  1. Runs a web search to get top 3 URLs.
  2. Scrapes each URL for clean text.
  3. Summarizes the scraped content via LLM.
  4. Appends the summary to state notes.

Usage:
    from src.graph.nodes.researcher import ResearcherNode
    researcher = ResearcherNode()
    state = researcher.call(state)
"""

from config.prompts import SUMMARIZER_PROMPT
from src.graph.state import ResearchState
from src.tools.llm import LLMClient
from src.tools.web_search import WebSearchTool
from src.tools.scraper import WebScraper


class ResearcherNode:
    """Researches the current subtask by searching, scraping, and summarising.

    Attributes:
        llm: LLMClient for summarization.
        searcher: WebSearchTool for finding relevant URLs.
        scraper: WebScraper for extracting page content.
    """

    def __init__(
        self,
        llm: LLMClient | None = None,
        searcher: WebSearchTool | None = None,
        scraper: WebScraper | None = None,
    ):
        self.llm = llm or LLMClient()
        self.searcher = searcher or WebSearchTool()
        self.scraper = scraper or WebScraper()

    def call(self, state: ResearchState) -> ResearchState:
        """Execute web research for the current pending subtask.

        Finds the first subtask with status "pending", marks it as
        "in_progress", searches the web, scrapes top results, summarizes,
        and appends to state notes.

        Args:
            state: Research state with subtasks list.

        Returns:
            Updated state with the current subtask researched and notes appended.
        """
        # Locate the first pending subtask.
        subtask = None
        idx = None
        for i, st in enumerate(state["subtasks"]):
            if st["status"] == "pending":
                subtask = st
                idx = i
                break

        if subtask is None:
            # No pending subtasks — nothing to do.
            state["errors"].append("ResearcherNode: no pending subtasks found")
            return state

        # Mark as in progress.
        state["subtasks"][idx]["status"] = "in_progress"

        # Web search for the subtask's query.
        results = self.searcher.search(subtask["search_query"], max_results=3)

        # Scrape each result URL and collect content.
        summaries = []
        for result in results:
            url = result.get("url", "")
            if not url:
                continue

            scrape_result = self.scraper.scrape(url)
            if not scrape_result["success"]:
                continue

            content = scrape_result["content"][:3000]  # limit per page
            summary = self.llm.chat([
                {"role": "system", "content": "You summarize web content concisely."},
                {"role": "user", "content": SUMMARIZER_PROMPT.format(content=content)},
            ])
            summaries.append(summary)

        # Combine individual summaries into one note per subtask.
        combined = " ".join(summaries) if summaries else "No content could be retrieved."
        state["notes"].append(combined)
        state["subtasks"][idx]["result"] = combined
        state["subtasks"][idx]["status"] = "done"

        return state