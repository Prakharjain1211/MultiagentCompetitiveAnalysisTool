"""
Planner node — decomposes a company query into research subtasks.

Uses the LLM to generate 3-5 structured subtasks with search queries,
then initializes their statuses to "pending" for downstream processing.

Usage:
    from src.graph.nodes.planner import PlannerNode
    planner = PlannerNode()
    state = planner.call(state)
"""

import json

from config.prompts import PLANNER_PROMPT
from src.graph.state import ResearchState
from src.tools.llm import LLMClient


class PlannerNode:
    """Generates a list of research subtasks from the user's query.

    Attributes:
        llm: LLMClient instance for chat completions.
    """

    def __init__(self, llm: LLMClient | None = None):
        self.llm = llm or LLMClient()

    def call(self, state: ResearchState) -> ResearchState:
        """Break the original query into 3-5 research subtasks.

        Sends the PLANNER_PROMPT to the LLM with the query, parses the
        JSON response, and initialises each subtask's status to "pending".

        Args:
            state: Current research state with original_query populated.

        Returns:
            Updated state with subtasks list populated.

        Raises:
            ValueError: If the LLM response cannot be parsed as valid JSON.
        """
        query = state["original_query"]
        prompt = PLANNER_PROMPT.format(query=query)

        response = self.llm.chat([
            {"role": "system", "content": "You are a competitive analysis strategist. Output only valid JSON."},
            {"role": "user", "content": prompt},
        ])

        # Strip markdown fences if the LLM wraps JSON in ```json ... ```
        clean = response.strip().removeprefix("```json").removesuffix("```").strip()

        try:
            subtask_list = json.loads(clean)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse planner JSON output: {e}\nRaw: {response}") from e

        # Normalise into Subtask TypedDicts.
        state["subtasks"] = [
            {
                "id": item["id"],
                "description": item["description"],
                "search_query": item["search_query"],
                "status": "pending",
                "result": "",
            }
            for item in subtask_list
        ]
        state["current_subtask_idx"] = 0
        state["retry_count"] = 0
        state["notes"] = []
        state["errors"] = []

        return state