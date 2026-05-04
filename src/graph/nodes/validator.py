"""
Validator node — checks research note quality and relevance.

Validates the most recent note in state for:
  - Non-empty and >= 50 characters.
  - Relevance to the original company query (LLM-based YES/NO check).

On success: advances current_subtask_idx.
On failure: increments retry_count, refines the search query, resets
the current subtask to "pending" for re-execution. Exhausted retries
mark the subtask as "failed" and skip it.

Usage:
    from src.graph.nodes.validator import ValidatorNode
    validator = ValidatorNode()
    state = validator.call(state)
"""

from config.prompts import VALIDATOR_RELEVANCE_PROMPT
from src.graph.state import ResearchState, Subtask
from src.tools.llm import LLMClient
from config.settings import settings


class ValidatorNode:
    """Validates research note quality and relevance.

    Attributes:
        llm: LLMClient for relevance checking.
    """

    def __init__(self, llm: LLMClient | None = None):
        self.llm = llm or LLMClient()

    def _refine_query(self, subtask: Subtask, company: str) -> str:
        """Ask the LLM to suggest a refined search query for retry.

        Args:
            subtask: The failed subtask needing a better query.
            company: The original company being researched.

        Returns:
            A refined search query string.
        """
        prompt = (
            f"The following research result for '{subtask['description']}' "
            f"was not relevant to competitive analysis for {company}. "
            f"Suggest a more specific web search query:"
        )
        response = self.llm.chat([
            {"role": "system", "content": "Suggest a single improved search query."},
            {"role": "user", "content": prompt},
        ])
        return response.strip()

    def call(self, state: ResearchState) -> ResearchState:
        """Validate the most recent research note.

        Performs length check and LLM relevance check on the last note.
        Advances or retries the current subtask based on results.

        Args:
            state: Research state with at least one note to validate.

        Returns:
            Updated state with adjusted subtask indices or retry counts.
        """
        if not state["notes"]:
            state["errors"].append("ValidatorNode: no notes to validate")
            return state

        last_note = state["notes"][-1]
        company = state["original_query"]
        idx = state["current_subtask_idx"]

        # Length check: must be non-empty and >= 50 characters.
        if len(last_note) < 50:
            state["retry_count"] += 1
            if state["retry_count"] > (state["max_retries"] or settings.max_retries):
                state["subtasks"][idx]["status"] = "failed"
                state["current_subtask_idx"] = idx + 1
                state["retry_count"] = 0
                state["errors"].append(f"Subtask {idx} failed after max retries (empty note)")
            else:
                refined = self._refine_query(state["subtasks"][idx], company)
                state["subtasks"][idx]["search_query"] = refined
                state["subtasks"][idx]["status"] = "pending"
            return state

        # Relevance check: LLM-based YES/NO.
        prompt = VALIDATOR_RELEVANCE_PROMPT.format(company=company, note=last_note)
        relevance = self.llm.chat([
            {"role": "system", "content": "Answer ONLY YES or NO."},
            {"role": "user", "content": prompt},
        ])
        relevance = relevance.strip().upper()

        if relevance == "YES":
            # Valid — advance to next subtask.
            state["current_subtask_idx"] = idx + 1
            state["retry_count"] = 0
        else:
            # Not relevant — retry or skip.
            state["retry_count"] += 1
            if state["retry_count"] > (state["max_retries"] or settings.max_retries):
                state["subtasks"][idx]["status"] = "failed"
                state["current_subtask_idx"] = idx + 1
                state["retry_count"] = 0
                state["errors"].append(f"Subtask {idx} failed after max retries (irrelevant)")
            else:
                refined = self._refine_query(state["subtasks"][idx], company)
                state["subtasks"][idx]["search_query"] = refined
                state["subtasks"][idx]["status"] = "pending"

        return state