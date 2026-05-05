# Competitive Analysis Research Tool

An AI-powered research assistant that produces structured competitive analysis briefings. Uses **LangGraph** for orchestration, **RAG** (Retrieval-Augmented Generation) for evidence grounding, and **multi-provider web search** for data collection.

Given a company name, it autonomously decomposes the task into research subtasks, searches the web, scrapes and summarizes content, validates relevance, and synthesizes a professional Markdown report.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   LangGraph State Graph                     │
│                                                             │
│   [planner_node] ──→ [researcher_node] ──→ [validator_node] │
│        ↑                        │                           │
│        └────── (retry loop) ─────┘                           │
│                                      ↓                       │
│                             [synthesizer_node]               │
│                                    │                         │
│                         RAG Vector Store                     │
│                    (Chroma + all-MiniLM-L6-v2)               │
│                     ↑ chunk & embed notes                    │
│                     ↑ retrieve per section                   │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Planner** — LLM decomposes the query into 3-5 research subtasks with search queries
2. **Researcher** — For each subtask: web search → scrape top URLs → LLM summarize
3. **Validator** — Checks summary length & relevance (LLM-based YES/NO), retries with refined queries on failure
4. **Synthesizer** — Chunks all notes → embeds into Chroma → RAG-retrieves per section → generates 4-section Markdown report

---

## Features

- **Autonomous research pipeline** — no manual prompting, just a company name
- **Multi-provider web search** — DuckDuckGo (free) with automatic Tavily fallback
- **Smart retry logic** — invalid/irrelevant results trigger query refinement and re-scraping
- **RAG-enhanced report generation** — vector search grounds each section in relevant evidence
- **Rich CLI output** — color-coded subtask tables, progress spinners, syntax-highlighted reports
- **Respectful scraping** — User-Agent rotation, `robots.txt` compliance, 50KB page truncation
- **LLM fallback chain** — auto-falls back to cheaper models on rate limits

---

## Quickstart

### Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- OpenAI API key ([get one here](https://platform.openai.com/api-keys))

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/competitive-analysis-tool.git
cd competitive-analysis-tool

# Create and activate virtual environment
uv venv .venv
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Install dependencies
uv pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### Run

```bash
python -m src.main "NVIDIA"
```

Options:

```bash
python -m src.main "NVIDIA" --model gpt-4o-mini --output briefing.md
```

| Argument | Default | Description |
|----------|---------|-------------|
| `company` | (required) | Company or topic to analyze |
| `--model` | `gpt-4o-mini` | OpenAI model to use |
| `--output` | None | File path to save the Markdown report |

---

## Project Structure

```
competitive-analysis-tool/
├── config/
│   ├── settings.py          # pydantic-settings (env vars, defaults)
│   └── prompts.py           # All LLM prompt templates
├── src/
│   ├── main.py              # CLI entry point
│   ├── graph/
│   │   ├── state.py         # ResearchState & Subtask TypedDicts
│   │   ├── graph_builder.py # LangGraph construction & compilation
│   │   └── nodes/
│   │       ├── planner.py    # Subtask decomposition
│   │       ├── researcher.py # Web search + scrape + summarize
│   │       ├── validator.py  # Quality & relevance validation
│   │       └── synthesizer.py# RAG-enhanced report generation
│   ├── rag/
│   │   ├── chunker.py       # RecursiveCharacterTextSplitter
│   │   └── vector_store.py  # Chroma + all-MiniLM-L6-v2
│   ├── tools/
│   │   ├── llm.py           # OpenAI client with fallback chain
│   │   ├── web_search.py    # DuckDuckGo → Tavily fallback
│   │   └── scraper.py       # requests + BeautifulSoup + UA rotation
│   └── utils/
│       ├── logger.py        # Loguru configuration
│       └── text.py          # clean_html, truncate, split_sentences
├── tests/                   # Unit tests (pytest)
├── data/chroma_db/          # Vector store persistence (gitignored)
├── requirements.txt
├── pyproject.toml
└── .env.example
```

---

## How It Works

### Planner

Sends the company name to the LLM with a structured prompt requesting 3-5 research subtasks. Each subtask includes a description and an optimized web search query. The LLM responds with JSON, which is parsed and initialized with `pending` status.

### Researcher

For the current pending subtask:
1. Executes the search query via DuckDuckGo (falls back to Tavily on failure)
2. Scrapes the top 3 result URLs for clean text
3. Sends each page to the LLM for summarization (≤500 chars)
4. Combines summaries into one note appended to state

### Validator

Checks the most recent note:
- **Length gate** — must be ≥50 characters
- **Relevance gate** — LLM answers YES/NO to "Is this relevant to {company}?"

Pass → advance to next subtask. Fail (with retries left) → LLM refines the search query, resets subtask to `pending` for retry. Fail (exhausted) → mark `failed`, skip to next.

### Synthesizer

1. Chunks all collected notes via `RecursiveCharacterTextSplitter`
2. Embeds chunks and indexes into Chroma
3. For each of 4 briefing sections, retrieves top-3 relevant chunks
4. Feeds chunks as context to the LLM per section
5. Assembles sections into a final Markdown report

---

## Configuration

All configuration is managed via `config/settings.py` using `pydantic-settings`. Set values in `.env`:

```env
OPENAI_API_KEY=sk-...           # Required
TAVILY_API_KEY=tvly-...         # Optional (Tavily fallback)
```

Key defaults you can override in `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_RETRIES` | `3` | Max retries per subtask |
| `MAX_CHUNK_SIZE` | `500` | Max characters per RAG chunk |
| `CHUNK_OVERLAP` | `50` | Overlap between chunks |
| `TOP_K_RETRIEVAL` | `3` | Chunks retrieved per section |

---

## Running Tests

```bash
pytest tests/ -v
```

---

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Graph framework** | LangGraph | Native state management, conditional edges, retry loops |
| **Vector store** | Chroma (in-memory) | Zero config, FAISS optional; embeddings run locally |
| **Embedding model** | all-MiniLM-L6-v2 | 384-dim, fast, free, sufficient for short chunks |
| **Web search** | DDG → Tavily fallback | DDG is free/no-key; Tavily is paid but reliable |
| **LLM** | GPT-4o-mini | Cheap (~$0.15/1M tokens), fast, good instruction following |
| **Validation** | LLM-based relevance check | More accurate than keyword heuristics |

---

## Roadmap

- [x] Phase 1: Foundation — config, utils, env setup
- [x] Phase 2: Tools — LLM client, web search, scraper
- [x] Phase 3: RAG — chunker, vector store
- [x] Phase 4: Graph nodes — planner, researcher, validator, synthesizer
- [x] Phase 5: Graph wiring — LangGraph topology
- [x] Phase 6: CLI — argument parsing, rich output
- [ ] Phase 7: Testing — unit tests for all modules
- [ ] Phase 8: Hardening — retries, backoff, error handling

See [ROADMAP.md](ROADMAP.md) for full details.

---

## License

MIT