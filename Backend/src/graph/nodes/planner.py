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
import re

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

    @staticmethod
    def _extract_json(text: str) -> str:
        """Extract the first JSON array or object from arbitrary text."""
        text = text.strip()
        text = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        text = text.strip("'\"")
        brace = text.find("{")
        bracket = text.find("[")
        if bracket != -1 and (brace == -1 or bracket < brace):
            start = bracket
            end = text.rfind("]")
        elif brace != -1:
            start = brace
            end = text.rfind("}")
        else:
            raise ValueError(f"No JSON array or object found in response: {text[:200]}")
        if end == -1:
            raise ValueError(f"Unmatched bracket — no closing delimiter found: {text[start:start+200]}")
        return text[start:end+1]

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

        try:
            clean = self._extract_json(response)
            raw = json.loads(clean)
        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(f"Failed to parse planner JSON output: {e}\nRaw: {response}") from e

        if isinstance(raw, dict):
            raw = [raw]

        state["subtasks"] = [
            {
                "id": item.get("id", i),
                "description": item.get("description", ""),
                "search_query": item.get("search_query", item.get("description", query)),
                "status": "pending",
                "result": "",
            }
            for i, item in enumerate(raw)
        ]
        state["current_subtask_idx"] = 0
        state["retry_count"] = 0
        state["notes"] = []
        state["errors"] = []

        return state