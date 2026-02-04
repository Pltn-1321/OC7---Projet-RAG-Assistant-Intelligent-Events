"""LangChain LLM factory module.

This module provides factory functions to create ChatMistralAI instances
with configurable parameters for different use cases (generation, classification).
"""

from langchain_mistralai import ChatMistralAI

from src.config.settings import settings


def get_llm(
    temperature: float | None = None,
    max_tokens: int | None = None,
    model: str | None = None,
) -> ChatMistralAI:
    """Create and return a ChatMistralAI instance.

    Args:
        temperature: Override the default temperature (0.0-2.0).
            If None, uses settings.llm_temperature.
        max_tokens: Override the default max tokens.
            If None, uses settings.max_tokens.
        model: Override the default model name.
            If None, uses settings.llm_model.

    Returns:
        ChatMistralAI: A configured LangChain chat model instance.

    Example:
        # Default generation LLM
        llm = get_llm()

        # Classification LLM (deterministic)
        classifier = get_llm(temperature=0, max_tokens=10)
    """
    return ChatMistralAI(
        model=model if model is not None else settings.llm_model,
        api_key=settings.mistral_api_key,
        temperature=temperature if temperature is not None else settings.llm_temperature,
        max_tokens=max_tokens if max_tokens is not None else settings.max_tokens,
    )
