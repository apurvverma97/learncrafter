"""
Course service for LearnCrafter MVP.
Single Responsibility: AI-powered course content and structure generation.
"""

import logging

from app.core.config import settings
from app.services.llm_providers import (
    GeminiProvider,
    LLMProvider,
    OpenAIProvider,
)

logger = logging.getLogger(__name__)


class CourseService:
    """Service for orchestrating LLM operations for course creation."""

    def __init__(self):
        """Initialize CourseService with the selected LLM provider."""
        self.provider = self._get_provider()

    def _get_provider(self) -> LLMProvider:
        """Get the LLM provider based on the configuration."""
        if settings.llm_provider == "openai":
            logger.info("Using OpenAI LLM provider.")
            return OpenAIProvider()
        elif settings.llm_provider == "gemini":
            logger.info("Using Gemini LLM provider.")
            return GeminiProvider()
        else:
            raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")

    async def generate_content(self, prompt: str) -> str:
        """
        Generate content using the selected LLM provider.

        Args:
            prompt: The prompt to send to the LLM

        Returns:
            Generated content as string

        Raises:
            Exception: If generation fails
        """
        try:
            return await self.provider.generate_content(prompt)
        except Exception as e:
            logger.error(f"Unexpected error in content generation: {e}")
            raise Exception(f"Content generation failed: {str(e)}")
