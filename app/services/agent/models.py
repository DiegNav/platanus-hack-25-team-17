"""OpenAI model configuration for agent."""

import logging

from langchain_openai import ChatOpenAI

from app.config import settings

logger = logging.getLogger(__name__)


def initialize_openai_model(temperature: float = 0.2) -> ChatOpenAI:
    """Initialize OpenAI model with LangChain.

    Args:
        temperature: Model temperature for consistency (default 0.2)

    Returns:
        ChatOpenAI: Initialized model

    Raises:
        ValueError: If OPENAI_API_KEY not configured
    """
    if not settings.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not configured in environment variables")

    return ChatOpenAI(
        model="gpt-4o-mini",
        api_key=settings.OPENAI_API_KEY,
        temperature=temperature,
        max_tokens=2048,
    )

