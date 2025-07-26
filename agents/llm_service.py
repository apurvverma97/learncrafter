import logging
import json
import google.generativeai as genai
from typing import Dict, Any

from .config import settings


class LLMService:
    """LLM service for Gemini operations."""

    def __init__(self):
        """Initialize the Gemini client."""
        try:
            if not settings.gemini_api_key or "your_api_key_here" in settings.gemini_api_key:
                logging.error("GEMINI_API_KEY is not set. Please add it to your .env file.")
                raise ValueError("GEMINI_API_KEY is not configured.")
            genai.configure(api_key=settings.gemini_api_key)
            self.model = genai.GenerativeModel(settings.gemini_model)
        except Exception as e:
            logging.error(f"Failed to initialize Gemini client: {e}")
            raise

    async def refine_prompt(self, prompt: str) -> Dict[str, Any]:
        """Refines a prompt to get a structured JSON output."""
        logging.info("Refining prompt...")
        try:
            generation_config = genai.GenerationConfig(
                max_output_tokens=settings.gemini_max_tokens,
                temperature=settings.gemini_temperature
            )
            response = await self.model.generate_content_async(
                prompt,
                generation_config=generation_config
            )
            cleaned_text = response.text.strip().replace('```json', '').replace('```', '').strip()
            return json.loads(cleaned_text)
        except Exception as e:
            logging.error(f"Error in prompt refinement: {e}")
            raise Exception(f"Prompt refinement failed: {str(e)}") 