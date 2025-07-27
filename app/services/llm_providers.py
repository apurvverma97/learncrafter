"""
LLM provider interface and implementations for LearnCrafter MVP.
"""

from abc import ABC, abstractmethod

import google.generativeai as genai
import openai

from app.core.config import settings


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def generate_content(self, prompt: str) -> str:
        pass


class GeminiProvider(LLMProvider):
    """Google Gemini LLM provider."""

    def __init__(self):
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(
            model_name=settings.gemini_model,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=settings.gemini_max_tokens,
                temperature=settings.gemini_temperature,
            ),
        )

    async def generate_content(self, prompt: str) -> str:
        try:
            response = self.model.generate_content(prompt)
            if not response or not response.text:
                raise Exception("Empty response from Gemini")
            return response.text
        except genai.types.BlockedPromptException as e:
            raise Exception(f"Content generation blocked due to safety concerns: {e}")
        except Exception as e:
            raise Exception(f"Content generation failed: {e}")


class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider."""

    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.max_tokens = settings.openai_max_tokens
        self.temperature = settings.openai_temperature

    async def generate_content(self, prompt: str) -> str:
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
            if not response or not response.choices:
                raise Exception("Empty response from OpenAI")
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Content generation failed: {e}")
