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

# # Prompt for the PlannerNode — asks the LLM to break a company into
# # 3-5 research subtasks with JSON output format.
# PLANNER_PROMPT = """\
# You are a competitive analysis strategist. For the company "{query}", generate \
# a list of 3-5 research subtasks. Each subtask must have:
# - id: integer
# - description: what to research
# - search_query: an effective web search query

# Return ONLY valid JSON array. Example:
# [{{"id":1, "description":"Identify main competitors", "search_query":"NVIDIA main competitors 2025"}}]"""

# # Prompt used by the ResearcherNode to distill scraped page text into
# # a concise summary <= 500 characters, preserving facts and numbers.
# SUMMARIZER_PROMPT = """\
# Summarize the following web content in <=500 characters.
# Focus on facts, numbers, and actionable insights.

# Content: {content}
# Summary:"""

# # Prompt for the ValidatorNode — checks whether a research note is
# # on-topic for the company under analysis. Expects single-word answer.
# VALIDATOR_RELEVANCE_PROMPT = """\
# Is the following research note relevant to competitive analysis for "{company}"?
# Answer ONLY "YES" or "NO".

# Note: {note}"""

# # Prompt for the SynthesizerNode — generates one section of the final
# # Markdown briefing using retrieved RAG chunks as evidence context.
# SECTION_GENERATOR_PROMPT = """\
# You are writing a section of a competitive analysis briefing.

# Section: {section_name}
# Company: {company}

# Use the following retrieved evidence to write a detailed, factual section:

# {retrieved_chunks}

# Write in professional Markdown. Be specific, cite evidence, and provide analysis."""

PLANNER_PROMPT = """\
You are an elite competitive intelligence strategist.

Your goal is NOT general research. Your goal is to uncover:
- What the company "{query}" is CURRENTLY working on
- What they are investing in
- What strategic direction they are moving toward

Focus ONLY on high-signal, recent, and forward-looking intelligence.

Generate 4-6 research subtasks. Each subtask MUST target a specific intelligence signal category:

Allowed categories:
- "news" → recent announcements, launches, partnerships
- "earnings" → earnings calls, executive statements, strategy
- "patents" → R&D direction, filed innovations
- "social" → market sentiment, developer reactions, early signals
- "web" → supporting context if needed

Each subtask must include:
- id: integer
- type: one of [news, earnings, patents, social, web]
- description: what strategic signal this task is trying to uncover
- search_query: a highly specific query optimized for recent or forward-looking results

Guidelines:
- Prioritize RECENT (last 3–6 months) and FUTURE-facing signals
- Avoid generic tasks like "company overview"
- Avoid redundant subtasks
- Focus on: product launches, new platforms, partnerships, hiring trends, research direction

Return ONLY a valid JSON array.

Example:
[
  {{
    "id": 1,
    "type": "news",
    "description": "Identify recent AI product launches and partnerships",
    "search_query": "NVIDIA latest AI announcements partnerships 2026"
  }},
  {{
    "id": 2,
    "type": "earnings",
    "description": "Extract strategic priorities from latest earnings call",
    "search_query": "NVIDIA earnings call transcript 2026 strategy AI data center"
  }}
]
"""

SUMMARIZER_PROMPT = """\
You are a competitive intelligence analyst.

Your job is NOT to summarize casually, but to extract HIGH-VALUE STRATEGIC SIGNALS.

From the content below, extract:
- Recent developments (last 3–6 months)
- New products, platforms, or features
- Partnerships, acquisitions, or expansions
- R&D direction or innovation signals
- Executive statements indicating future strategy

Output:
- Maximum 500 characters
- Dense, factual, no fluff
- Focus on "what they are doing now" and "where they are going"

Content:
{content}

Strategic Summary:"""

VALIDATOR_RELEVANCE_PROMPT = """\
You are a strict competitive intelligence filter.

Determine if the following note contains HIGH-VALUE, RECENT, and ACTIONABLE intelligence about "{company}".

Accept ONLY if the note includes at least one:
- Recent development (last 6 months)
- Product launch or platform update
- Strategic move (partnership, expansion, hiring trend)
- R&D or innovation signal
- Executive insight (earnings, leadership statements)

Reject if:
- Generic company info
- Old or outdated information
- Vague or non-actionable content

Answer ONLY "YES" or "NO".

Note:
{note}
"""

SECTION_GENERATOR_PROMPT = """\
You are a senior competitive intelligence analyst.

You are writing a high-impact section of a competitive briefing.

Section: {section_name}
Company: {company}

Use ONLY the retrieved evidence below.

Your goal is to:
1. Identify what the company is CURRENTLY working on
2. Highlight key strategic moves and innovations
3. Explain WHY these moves matter (competitive advantage, direction)
4. Infer future direction where possible

Guidelines:
- Be specific and factual (no fluff)
- Prioritize recent and forward-looking insights
- Do NOT repeat chunks verbatim — synthesize
- Highlight implications for competitors

Evidence:
{retrieved_chunks}

Output:
- Professional Markdown
- Insight-driven (not just descriptive)
- Focus on strategy, not history
"""
