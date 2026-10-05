import os

from crewai import LLM


def get_llm(temperature: float = 0.2) -> LLM:
    """Return the LLM used by every agent.

    MODEL can be any LiteLLM model string, e.g.
      ollama/qwen3:8b (default, fully local)
      openai/gpt-4o-mini (needs OPENAI_API_KEY)
    """
    model = os.getenv("MODEL", "ollama/qwen3:8b")
    kwargs = {"model": model, "temperature": temperature}
    if model.startswith("ollama/"):
        kwargs["base_url"] = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    return LLM(**kwargs)
