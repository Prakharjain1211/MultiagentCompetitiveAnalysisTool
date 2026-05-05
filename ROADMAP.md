# Competitive Analysis Research Tool — Production Roadmap

## Architecture Overview

```
┌────────────────────────────────────────────────────────────────--------┐
│                     LangGraph State Graph                              │
│                                                                        │
│   [planner_node] ──→ [validator_node] ──→ [researcher_node]            │
│        ↑                                  │                            │
│        └────── (retry loop: invalid) ──────┘                           │
│                                              ↓                         │
│                                     [all done?] ──→ [synthesizer_node] │
│                                                                        │
│                         RAG Vector Store                               │
│                    (Chroma + all-MiniLM-L6-v2)                         │
│                      ↑ chunk & embed notes                             │
│                      ↑ retrieve per section                            │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Production Folder Structure

```
competitive-analysis-tool/
│
├── README.md                       # Project overview & quickstart
├── ROADMAP.md                      # This file
├── requirements.txt                # Pinned dependencies
├── pyproject.toml                  # PEP 621 project metadata
├── .env.example                    # Template for secrets
├── .gitignore
│
├── config/
│   ├── __init__.py
│   ├── settings.py                 # Central config (env vars, defaults)
│   └── prompts.py                  # All LLM prompt templates
│
├── src/
│   ├── __init__.py
│   ├── main.py                     # Entry point: CLI arg parsing → run graph
│   │
│   ├── graph/
│   │   ├── __init__.py
│   │   ├── state.py                # State TypedDict definition
│   │   ├── graph_builder.py        # LangGraph construction (nodes, edges, compile)
│   │   └── nodes/
│   │       ├── __init__.py
│   │       ├── planner.py          # Subtask decomposition, query generation
│   │       ├── researcher.py       # Web search + scrape + summarize
│   │       ├── validator.py        # Validate researcher output (content, relevance)
│   │       └── synthesizer.py      # RAG-enhanced report generation
│   │
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── vector_store.py         # Chroma wrapper: create, persist, retrieve
│   │   └── chunker.py              # Text splitting with overlap
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── web_search.py           # DuckDuckGo primary + Tavily fallback
│   │   ├── scraper.py              # requests + BeautifulSoup + UA rotation
│   │   └── llm.py                  # OpenAI chat wrapper (chat completions)
│   │
│   └── utils/
│       ├── __init__.py
│       ├── logger.py               # Structured logging (loguru or stdlib)
│       └── text.py                 # Clean HTML, truncate, chunk helpers
│
├── tests/
│   ├── __init__.py
│   ├── test_planner.py
│   ├── test_researcher.py
│   ├── test_synthesizer.py
│   ├── test_graph.py
│   └── test_rag.py
│
├── data/
│   └── chroma_db/                  # Chroma persistence (gitignored)
│
└── notebooks/
    └── exploration.ipynb           # Prototyping & debugging
```

---

## Step-by-Step Implementation Roadmap

### Phase 1: Foundation (Day 1)

| Step | File | What to Build |
|------|------|---------------|
| 1.1 | `requirements.txt` | Pin all dependencies: `langgraph`, `langchain`, `langchain-chroma`, `chromadb`, `sentence-transformers`, `duckduckgo-search`, `tavily`, `requests`, `beautifulsoup4`, `openai`, `pydantic`, `python-dotenv`, `loguru` |
| 1.2 | `pyproject.toml` | PEP 621 metadata, Python 3.10+ classifier |
| 1.3 | `.env.example` | `OPENAI_API_KEY=sk-...`, `TAVILY_API_KEY=tvly-...` |
| 1.4 | `config/settings.py` | `Settings` class via `pydantic-settings` loading `.env`. Expose: `OPENAI_API_KEY`, `TAVILY_API_KEY`, `MAX_RETRIES=3`, `MAX_CHUNK_SIZE=500`, `CHUNK_OVERLAP=50`, `TOP_K_RETRIEVAL=3`, `USER_AGENTS` list |
| 1.5 | `config/prompts.py` | All prompt templates as constants (see below) |
| 1.6 | `src/utils/logger.py` | Configure `loguru` logger with console + file sinks, structured format |
| 1.7 | `src/utils/text.py` | `clean_html(raw_html)`, `truncate(text, max_chars)`, `split_sentences(text)` |

### Phase 2: Tools Layer (Day 2)

| Step | File | What to Build |
|------|------|---------------|
| 2.1 | `src/tools/llm.py` | `LLMClient` class wrapping `openai.OpenAI`. Method `chat(messages, model="gpt-4o-mini", temperature=0.2)` with 15s timeout. Fallback model chain on rate-limit. |
| 2.2 | `src/tools/web_search.py` | `WebSearchTool` class. Method `search(query, max_results=5)` → list of `{title, url, snippet}`. Primary: `DDGS().text(query, max_results)`. On exception → fallback to `TavilyClient().search(query, max_results)`. Both return normalized results. |
| 2.3 | `src/tools/scraper.py` | `WebScraper` class. Method `scrape(url, timeout=10)` → cleaned text. Rotate User-Agent from list every call. Respect `robots.txt` (check via `urllib.robotparser`). Handle HTTP errors, connection timeouts, oversized pages (truncate at 50KB). Return `{"url": ..., "content": ..., "success": bool, "error": ...}`. |

### Phase 3: RAG Layer (Day 3)

| Step | File | What to Build |
|------|------|---------------|
| 3.1 | `src/rag/chunker.py` | `TextChunker` class. Method `chunk(texts: List[str])` → `List[Document]`. Use `RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50, separators=["\n\n", "\n", ". ", " "])`. |
| 3.2 | `src/rag/vector_store.py` | `VectorStore` class. Uses `HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")`. Wraps `Chroma` (in-memory with optional `persist_directory`). Methods: `index(documents)`, `retrieve(query, k=3)` → `List[Document]`, `clear()`. Log number of indexed chunks. |

### Phase 4: State & Graph Nodes (Day 4-5)

| Step | File | What to Build |
|------|------|---------------|
| 4.1 | `src/graph/state.py` | Define `ResearchState(TypedDict)`: `original_query`, `subtasks: List[Subtask]`, `current_subtask_idx: int`, `notes: List[str]`, `retry_count: int`, `max_retries: int`, `final_report: str`, `errors: List[str]`. Also define `Subtask(TypedDict)`: `id`, `description`, `search_query`, `status` (pending/in_progress/done/failed), `result`. |
| 4.2 | `src/graph/nodes/planner.py` | `PlannerNode` class. `call(state)` → updates `state["subtasks"]`. Calls LLM with prompt: *"Given the company {query}, break down competitive analysis into 3-5 subtasks. Return JSON array of {{id, description, search_query}}."* Parses JSON, sets all subtask status to "pending". |
| 4.3 | `src/graph/nodes/researcher.py` | `ResearcherNode` class. `call(state)` → picks the next pending subtask (`state["subtasks"][state["current_subtask_idx"]]`). Calls `WebSearchTool` with the subtask's search query, gets top 3 results. Calls `WebScraper` on each URL. Calls `LLMClient` to summarize extracted text into ≤500 chars. Appends to `state["notes"]`. Marks subtask as "done". |
| 4.4 | `src/graph/nodes/validator.py` | `ValidatorNode` class. `call(state)` → checks the last note: non-empty, ≥50 chars, content relevance (LLM call: *"Is this summary relevant to competitive analysis for {company}? Answer YES/NO."*). If valid: increment `current_subtask_idx`. If invalid: increment `retry_count`, refine search query via LLM, reset current subtask to "pending". If `retry_count > max_retries`: mark as "failed", skip. |
| 4.5 | `src/graph/nodes/synthesizer.py` | `SynthesizerNode` class. `call(state)` → (a) Take `state["notes"]`, chunk via `TextChunker`, index into `VectorStore`. (b) For each of 4 sections, `retrieve` top-3 chunks. (c) Call LLM per section with prompt + retrieved chunks as context. (d) Assemble into final Markdown. Store in `state["final_report"]`. |

### Phase 5: Graph Wiring (Day 5)

| Step | File | What to Build |
|------|------|---------------|
| 5.1 | `src/graph/graph_builder.py` | `build_research_graph() → CompiledStateGraph`: |
|      |      | - `StateGraph(ResearchState)` |
|      |      | - `add_node("planner", planner_node)` |
|      |      | - `add_node("researcher", researcher_node)` |
|      |      | - `add_node("validator", validator_node)` |
|      |      | - `add_node("synthesizer", synthesizer_node)` |
|      |      | - `add_edge(START, "planner")` |
|      |      | - `add_edge("planner", "researcher")` |
|      |      | - `add_conditional_edges("researcher", route_after_researcher)`: |
|      |      |   - If `current_subtask_idx < len(subtasks)` and all valid → "validator" |
|      |      |   - Else → "synthesizer" |
|      |      | - `add_conditional_edges("validator", route_after_validator)`: |
|      |      |   - If valid → "researcher" (next subtask) |
|      |      |   - If invalid & retry_count ≤ max_retries → "researcher" (retry same subtask) |
|      |      |   - If invalid & exhausted → "researcher" (skip to next) |
|      |      | - `add_edge("synthesizer", END)` |
|      |      | - `compile()` with `checkpointer` for debugging |

### Phase 6: Entry Point & CLI (Day 6)

| Step | File | What to Build |
|------|------|---------------|
| 6.1 | `src/main.py` | `argparse` with positional `company` argument. Optional `--model` (default gpt-4o-mini), `--output` file path. Build graph, invoke with `ResearchState(original_query=company)`. Print execution log (node transitions, timestamps, retries). Print vector store stats. Print per-section retrieved chunks. Print final Markdown report. |
| 6.2 | `src/main.py` | Add `rich` or simple `print()` formatting: colored node names, progress bars for subtasks, clear section separators. |

### Phase 7: Testing (Day 7)

| Step | File | What to Build |
|------|------|---------------|
| 7.1 | `tests/test_planner.py` | Mock LLM → verify subtask JSON parsing |
| 7.2 | `tests/test_researcher.py` | Mock web search + scraper → verify summary generation |
| 7.3 | `tests/test_synthesizer.py` | Feed fake notes → verify chunking, retrieval, section generation |
| 7.4 | `tests/test_graph.py` | Full graph mock test with simulated state transitions |
| 7.5 | `tests/test_rag.py` | Test chunker overlap logic, vector store index/retrieve roundtrip |

---

## Data Flow Diagram (Per Run)

```
User Input: "NVIDIA"
       │
       ▼
┌──────────────────────────────┐
│  planner_node                │
│  LLM: "NVIDIA competitive    │
│        analysis subtasks"    │
│  Output: 5 subtasks          │
│  e.g. [Find competitors,     │
│         Market positioning,  │
│         Recent news, ...]    │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│  researcher_node             │
│  For subtask #1:             │
│  Search DDG → Top 3 URLs    │
│  Scrape each → Clean text   │
│  LLM summarize → Note (≤500)│
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│  validator_node              │
│  Check length ≥ 50 chars     │
│  LLM: "Relevant? YES/NO"     │
│  Valid  ──→ next subtask      │
│  Invalid ──→ retry (refine   │
│               query, re-scrape)│
└──────────┬───────────────────┘
           │
           ▼ (all subtasks done)
┌──────────────────────────────┐
│  synthesizer_node            │
│  All notes → Chunk → Embed   │
│  → Index into Chroma          │
│                              │
│  For each section:           │
│    Query Chroma → top-3      │
│    chunks as context         │
│    LLM generates section     │
│                              │
│  Assemble final Markdown     │
└──────────┬───────────────────┘
           │
           ▼
     Final Briefing (stdout + file)
```

---

## Prompt Templates (`config/prompts.py`)

### Planner Prompt
```
You are a competitive analysis strategist. For the company "{query}", generate
a list of 3-5 research subtasks. Each subtask must have:
- id: integer
- description: what to research
- search_query: an effective web search query

Return ONLY valid JSON array. Example:
[{{"id":1, "description":"Identify main competitors", "search_query":"NVIDIA main competitors 2025"}}]
```

### Summarizer Prompt (used in researcher)
```
Summarize the following web content in ≤500 characters.
Focus on facts, numbers, and actionable insights.

Content: {content}
Summary:
```

### Validator Relevance Prompt
```
Is the following research note relevant to competitive analysis for "{company}"?
Answer ONLY "YES" or "NO".

Note: {note}
```

### Section Generator Prompt (used in synthesizer)
```
You are writing a section of a competitive analysis briefing.

Section: {section_name}
Company: {company}

Use the following retrieved evidence to write a detailed, factual section:

{retrieved_chunks}

Write in professional Markdown. Be specific, cite evidence, and provide analysis.
```

---

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Graph framework** | LangGraph | Native state management, conditional edges, retry loops, checkpointer support |
| **Vector store** | Chroma (in-memory) | Zero config, FAISS optional; sentence-transformers runs locally (no API cost) |
| **Embedding model** | all-MiniLM-L6-v2 | 384-dim, fast, free, good enough for short-to-medium text chunks |
| **Web search** | DuckDuckGo → Tavily fallback | DDG is free/no-key; Tavily is paid but more reliable — failover pattern |
| **LLM** | OpenAI GPT-4o-mini | Cheap (~$0.15/1M tokens), fast, good instruction following |
| **State persistence** | No external DB for state | LangGraph's built-in checkpointer suffices; state is ephemeral per run |
| **Validation** | LLM-based relevance check | More accurate than keyword heuristics; catches off-topic or hallucinated notes |

---

## How LangGraph Replaces Manual Validation Loops

Without LangGraph, you'd write procedural `while` loops with manual state dicts, error-prone retry counters, and tangled control flow. LangGraph provides:

- **Declarative graph structure**: Nodes are pure functions of state; edges define flow declaratively.
- **Conditional routing**: `route_after_validator` returns a node name string — LangGraph handles the jump.
- **Built-in state management**: The `State` TypedDict is automatically passed between nodes, persisted, and checkpointed.
- **Retry loops as cycles**: The planner→researcher→validator→(back to researcher) cycle is just a graph edge — no special loop constructs needed.
- **Debugging**: LangGraph's `get_state()` and checkpointer let you inspect state at any point.
- **Parallelism**: Future subtasks can run in parallel via `Send()` — LangGraph natively supports fan-out.

### Without LangGraph (messy):
```python
state = {"subtasks": [], "notes": [], ...}
while state["current_idx"] < len(state["subtasks"]):
    result = researcher(state)
    state["notes"].append(result)
    if not validator(state):
        state["retry_count"] += 1
        if state["retry_count"] > 3:
            state["current_idx"] += 1
            state["retry_count"] = 0
    else:
        state["current_idx"] += 1
```

### With LangGraph (clean):
```python
graph = StateGraph(ResearchState)
graph.add_node("researcher", researcher_node)
graph.add_node("validator", validator_node)
graph.add_conditional_edges(
    "validator",
    route_after_validator,
    {"next_subtask": "researcher", "retry": "researcher", "done": "synthesizer"}
)
```

---

## How RAG Improves Synthesis

Without RAG, the Synthesizer receives all notes as a single concatenated string. Problems:
- **Lost context**: Notes about different topics bleed together in the LLM context window.
- **Irrelevant generation**: The LLM might ignore specific evidence and hallucinate.

With RAG:
1. **Chunking** breaks notes into topical segments.
2. **Vector search** finds the *most relevant chunks* for each section.
3. **Per-section retrieval** ensures each section is grounded in the right evidence.
4. **Fact anchoring**: The LLM sees "Market positioning" chunks when writing that section, reducing hallucination.
5. **Traceability**: Retrieved chunks can be cited/disclosed in the output, improving trust.

---

## How to Run

```bash
# 1. Clone and enter directory
cd competitive-analysis-tool

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate   # Windows
source .venv/bin/activate  # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set environment variables
#    Copy .env.example → .env and fill in your keys
#    OPENAI_API_KEY is required
#    TAVILY_API_KEY is optional (fallback)

# 5. Run the tool
python -m src.main "NVIDIA"

# 6. Optional: save output to file
python -m src.main "NVIDIA" --output briefing.md

# 7. Run tests
pytest tests/ -v
```

---

## `requirements.txt` (Pinned)

```
langgraph>=0.2.0,<1.0.0
langchain>=0.3.0,<1.0.0
langchain-community>=0.3.0,<1.0.0
langchain-chroma>=0.2.0,<1.0.0
chromadb>=0.5.0,<1.0.0
sentence-transformers>=3.0.0,<4.0.0
duckduckgo-search>=7.0.0,<8.0.0
tavily>=0.5.0,<1.0.0
requests>=2.32.0,<3.0.0
beautifulsoup4>=4.12.0,<5.0.0
openai>=1.55.0,<2.0.0
pydantic>=2.0.0,<3.0.0
pydantic-settings>=2.0.0,<3.0.0
python-dotenv>=1.0.0,<2.0.0
loguru>=0.7.0,<1.0.0
lxml>=5.0.0,<6.0.0
tenacity>=9.0.0,<10.0.0
rich>=13.0.0,<14.0.0
pytest>=8.0.0,<9.0.0
pytest-asyncio>=0.24.0,<1.0.0
```

---

## Summary of Estimated Effort

| Phase | Days | Deliverable |
|-------|------|-------------|
| Foundation | 1 | Config, utils, env setup |
| Tools | 1 | LLM client, web search, scraper |
| RAG | 1 | Chunker, vector store |
| Graph nodes | 2 | 4 nodes with state management |
| Graph wiring | 1 | Build & compile LangGraph |
| Entry point | 1 | CLI, output formatting |
| Testing | 1 | Unit tests for all modules |
| Hardening | 1 | Retries, backoff, error handling |
| **Total** | **9 days** | **Runnable production tool** |
