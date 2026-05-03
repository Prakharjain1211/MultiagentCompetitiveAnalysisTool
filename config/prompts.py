PLANNER_PROMPT = """\
You are a competitive analysis strategist. For the company "{query}", generate \
a list of 3-5 research subtasks. Each subtask must have:
- id: integer
- description: what to research
- search_query: an effective web search query

Return ONLY valid JSON array. Example:
[{{"id":1, "description":"Identify main competitors", "search_query":"NVIDIA main competitors 2025"}}]"""

SUMMARIZER_PROMPT = """\
Summarize the following web content in <=500 characters.
Focus on facts, numbers, and actionable insights.

Content: {content}
Summary:"""

VALIDATOR_RELEVANCE_PROMPT = """\
Is the following research note relevant to competitive analysis for "{company}"?
Answer ONLY "YES" or "NO".

Note: {note}"""

SECTION_GENERATOR_PROMPT = """\
You are writing a section of a competitive analysis briefing.

Section: {section_name}
Company: {company}

Use the following retrieved evidence to write a detailed, factual section:

{retrieved_chunks}

Write in professional Markdown. Be specific, cite evidence, and provide analysis."""