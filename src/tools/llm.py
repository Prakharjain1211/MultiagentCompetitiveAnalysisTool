"""
LLM client wrapper around the OpenAI API.

Provides a simple `chat()` method that handles model selection, fallback
on rate-limit errors, and consistent response formatting. All calls go
through a single OpenAI client instance per LLMClient object.

Usage:
    from src.tools.llm import LLMClient
    llm = LLMClient(model="gpt-4o-mini")
    reply = llm.chat([{"role": "user", "content": "Hello"}])
"""

from openai import OpenAI

from config.settings import settings


class LLMClient:
    """Wraps the OpenAI chat completions API with fallback support.

    Attributes:
        client: The underlying openai.OpenAI instance.
        model: Primary model identifier (default: gpt-4o-mini).
        temperature: Sampling temperature for response generation.
        fallback_models: Ordered list of models to try on failure.
    """

    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0.2):
        """Initialise the LLM client.

        Args:
            model: OpenAI model identifier to use for chat completions.
            temperature: Sampling temperature (0.0 = deterministic, 1.0 = creative).
        """
        # Create a single reusable client; 15s timeout prevents hangs.
        self.client = OpenAI(api_key=settings.openai_api_key, timeout=15)
        self.model = model
        self.temperature = temperature
        # Fallback chain: primary -> cheaper alternatives on rate-limit / errors.
        self.fallback_models = ["gpt-4o-mini", "gpt-3.5-turbo"]

    def chat(self, messages: list[dict], model: str | None = None) -> str:
        """Send a chat completion request with automatic fallback.

        Iterates through the primary model and fallback list until one
        succeeds. Raises RuntimeError only if all models fail.

        Args:
            messages: List of message dicts following OpenAI format
                      (e.g. [{"role": "user", "content": "..."}]).
            model: Optional override model; uses instance default if None.

        Returns:
            The response content string, stripped of leading/trailing whitespace.

        Raises:
            RuntimeError: If every model in the fallback chain fails.
        """
        # Build the ordered list of models to attempt.
        models_to_try = [model or self.model, *self.fallback_models]
        last_error = None

        # Try each model sequentially; first success short-circuits.
        for m in models_to_try:
            try:
                response = self.client.chat.completions.create(
                    model=m,
                    messages=messages,
                    temperature=self.temperature,
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                # Record the error and fall through to next model.
                last_error = e
                continue

        # All fallbacks exhausted — surface the last error.
        raise RuntimeError(f"LLM call failed after all fallbacks: {last_error}")