"""
LLM service for LearnCrafter MVP.
Single Responsibility: AI content generation only.
"""
import google.generativeai as genai
from typing import Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class LLMService:
    """Service for Google Gemini LLM operations."""
    
    def __init__(self):
        """Initialize Gemini client."""
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(
            model_name=settings.gemini_model,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=settings.gemini_max_tokens,
                temperature=settings.gemini_temperature
            )
        )
    
    async def generate_content(self, prompt: str) -> str:
        """
        Generate content using Google Gemini API.
        
        Args:
            prompt: The prompt to send to the LLM
            
        Returns:
            Generated content as string
            
        Raises:
            Exception: If generation fails
        """
        try:
            # Generate content using Gemini
            response = self.model.generate_content(prompt)
            
            if not response or not response.text:
                raise Exception("Empty response from Gemini")
            
            return response.text
            
        except genai.types.BlockedPromptException as e:
            logger.error(f"Gemini blocked prompt: {e}")
            raise Exception("Content generation blocked due to safety concerns.")
            
        except Exception as e:
            logger.error(f"Unexpected error in content generation: {e}")
            raise Exception(f"Content generation failed: {str(e)}")
    
    async def validate_response(self, content: str) -> bool:
        """
        Basic validation of generated content.
        
        Args:
            content: Generated content to validate
            
        Returns:
            True if content is valid, False otherwise
        """
        if not content or len(content.strip()) == 0:
            return False
        
        # Check if content contains basic HTML structure
        if "<html" not in content.lower() and "<!doctype" not in content.lower():
            return False
        
        # Check content length
        if len(content) > settings.max_content_length:
            return False
        
        return True
    
    async def estimate_tokens(self, text: str) -> int:
        """
        Rough estimation of token count for Gemini.
        
        Args:
            text: Text to estimate tokens for
            
        Returns:
            Estimated token count
        """
        # Rough estimation: 1 token ≈ 4 characters for Gemini
        return len(text) // 4
    
    async def generate_with_safety_settings(self, prompt: str, safety_level: str = "medium") -> str:
        """
        Generate content with custom safety settings.
        
        Args:
            prompt: The prompt to send to the LLM
            safety_level: Safety level (low, medium, high)
            
        Returns:
            Generated content as string
        """
        try:
            # Configure safety settings based on level
            safety_settings = self._get_safety_settings(safety_level)
            
            model = genai.GenerativeModel(
                model_name=settings.gemini_model,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=settings.gemini_max_tokens,
                    temperature=settings.gemini_temperature
                ),
                safety_settings=safety_settings
            )
            
            response = model.generate_content(prompt)
            
            if not response or not response.text:
                raise Exception("Empty response from Gemini")
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error in safe content generation: {e}")
            raise Exception(f"Safe content generation failed: {str(e)}")
    
    def _get_safety_settings(self, level: str):
        """Get safety settings based on level."""
        if level == "low":
            return [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_NONE"
                }
            ]
        elif level == "high":
            return [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                }
            ]
        else:  # medium (default)
            return [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_LOW_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_LOW_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_LOW_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_LOW_AND_ABOVE"
                }
            ] 