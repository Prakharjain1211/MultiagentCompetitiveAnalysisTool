"""
Central configuration module for the Competitive Analysis Tool.

Uses pydantic-settings to load environment variables from a `.env` file
and provide typed defaults for all configurable parameters.

Usage:
    from config.settings import settings
    api_key = settings.openai_api_key
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file.

    Attributes:
        openai_api_key: OpenAI API key for LLM calls.
        tavily_api_key: Tavily API key for web search fallback (optional).
        max_retries: Maximum number of retry attempts for failed subtasks.
        max_chunk_size: Maximum character length of text chunks for RAG indexing.
        chunk_overlap: Number of overlapping characters between adjacent chunks.
        top_k_retrieval: Number of top chunks to retrieve per RAG query.
        user_agents: List of User-Agent strings rotated by the scraper.
        model_config: Pydantic config — loads from .env file with UTF-8 encoding.
    """

    openai_api_key: str = ""
    tavily_api_key: str = ""
    max_retries: int = 3
    max_chunk_size: int = 500
    chunk_overlap: int = 50
    top_k_retrieval: int = 3

    user_agents: list[str] = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/118.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
    ]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


# Singleton instance — import this everywhere instead of instantiating Settings directly.
settings = Settings()