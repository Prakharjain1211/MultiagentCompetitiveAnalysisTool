"""
LLM prompt templates used across all graph nodes.

Each constant is a string template with {placeholders} to be formatted
at call time with the relevant context (company name, content, etc.).

Prompts included:
    - PLANNER_PROMPT: Subtask decomposition from a company name.
    - SUMMARIZER_PROMPT: Condense scraped web content to <=500 chars.
    - VALIDATOR_RELEVANCE_PROMPT: YES/NO check on research note relevance.
    - SECTION_GENERATOR_PROMPT: Generate a briefing section from RAG context.
"""

# Prompt for the PlannerNode — asks the LLM to break a company into
# 3-5 research subtasks with JSON output format.
PLANNER_PROMPT = """\
You are a competitive analysis strategist. For the company "{query}", generate \
a list of 3-5 research subtasks. Each subtask must have:
- id: integer
- description: what to research
- search_query: an effective web search query

Return ONLY valid JSON array. Example:
[{{"id":1, "description":"Identify main competitors", "search_query":"NVIDIA main competitors 2025"}}]"""

# Prompt used by the ResearcherNode to distill scraped page text into
# a concise summary <= 500 characters, preserving facts and numbers.
SUMMARIZER_PROMPT = """\
Summarize the following web content in <=500 characters.
Focus on facts, numbers, and actionable insights.

Content: {content}
Summary:"""

# Prompt for the ValidatorNode — checks whether a research note is
# on-topic for the company under analysis. Expects single-word answer.
VALIDATOR_RELEVANCE_PROMPT = """\
Is the following research note relevant to competitive analysis for "{company}"?
Answer ONLY "YES" or "NO".

Note: {note}"""

# Prompt for the SynthesizerNode — generates one section of the final
# Markdown briefing using retrieved RAG chunks as evidence context.
SECTION_GENERATOR_PROMPT = """\
You are writing a section of a competitive analysis briefing.

Section: {section_name}
Company: {company}

Use the following retrieved evidence to write a detailed, factual section:

{retrieved_chunks}

Write in professional Markdown. Be specific, cite evidence, and provide analysis."""