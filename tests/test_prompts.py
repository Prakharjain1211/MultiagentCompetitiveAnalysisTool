"""Tests for config.prompts module."""

import pytest
from config.prompts import (
    PLANNER_PROMPT,
    SUMMARIZER_PROMPT,
    VALIDATOR_RELEVANCE_PROMPT,
    SECTION_GENERATOR_PROMPT,
)


class TestPlannerPrompt:
    def test_contains_query_placeholder(self):
        assert "{query}" in PLANNER_PROMPT

    def test_formatted_with_company(self):
        result = PLANNER_PROMPT.format(query="NVIDIA")
        assert "NVIDIA" in result

    def test_mentions_json(self):
        assert "JSON" in PLANNER_PROMPT

    def test_mentions_subtask_fields(self):
        assert "id" in PLANNER_PROMPT
        assert "description" in PLANNER_PROMPT
        assert "search_query" in PLANNER_PROMPT


class TestSummarizerPrompt:
    def test_contains_content_placeholder(self):
        assert "{content}" in SUMMARIZER_PROMPT

    def test_formatted_with_content(self):
        result = SUMMARIZER_PROMPT.format(content="Some web content here")
        assert "Some web content here" in result

    def test_mentions_character_limit(self):
        assert "500" in SUMMARIZER_PROMPT


class TestValidatorRelevancePrompt:
    def test_contains_company_placeholder(self):
        assert "{company}" in VALIDATOR_RELEVANCE_PROMPT

    def test_contains_note_placeholder(self):
        assert "{note}" in VALIDATOR_RELEVANCE_PROMPT

    def test_formatted_correctly(self):
        result = VALIDATOR_RELEVANCE_PROMPT.format(company="Tesla", note="Some note")
        assert "Tesla" in result
        assert "Some note" in result

    def test_mentions_yes_or_no(self):
        assert "YES" in VALIDATOR_RELEVANCE_PROMPT
        assert "NO" in VALIDATOR_RELEVANCE_PROMPT


class TestSectionGeneratorPrompt:
    def test_contains_section_placeholder(self):
        assert "{section_name}" in SECTION_GENERATOR_PROMPT

    def test_contains_company_placeholder(self):
        assert "{company}" in SECTION_GENERATOR_PROMPT

    def test_contains_retrieved_chunks_placeholder(self):
        assert "{retrieved_chunks}" in SECTION_GENERATOR_PROMPT

    def test_formatted_correctly(self):
        result = SECTION_GENERATOR_PROMPT.format(
            section_name="Overview",
            company="Apple",
            retrieved_chunks="chunk1\nchunk2",
        )
        assert "Overview" in result
        assert "Apple" in result
        assert "chunk1" in result
