#!/usr/bin/env python3
"""
Simple test to verify Gemini integration works.
"""
import asyncio
import logging
import sys
from pathlib import Path

from app.core.config import settings
from app.services.course_service import CourseService
from app.services.prompt_service import PromptService

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))


# Configure logging
logging.basicConfig(level=logging.INFO)


async def main():
    """Main function to run the integration test."""

    # Initialize services
    prompt_service = PromptService()
    course_service = CourseService()

    # Define test concept data
    test_concept = {
        "title": "Test Concept",
        "description": "A test concept for verification",
        "module_context": "Test Module",
        "learning_objectives": ["Learn something", "Understand basics"],
        "prerequisites": ["Basic knowledge"],
    }

    try:
        # Generate prompt
        prompt = await prompt_service.generate_concept_prompt(test_concept)
        logging.info("Generated Prompt:\n" + prompt)

        # Generate content
        generated_content = await course_service.generate_content(prompt)
        logging.info("\nGenerated Content:\n" + generated_content)

        # Validate response (basic check)
        if "<html>" in generated_content and "</html>" in generated_content:
            logging.info("Validation Passed: Basic HTML structure found.")
        else:
            logging.error("Validation Failed: Basic HTML structure not found.")

    except Exception as e:
        logging.error(f"An error occurred: {e}")


if __name__ == "__main__":
    # Ensure GEMINI_API_KEY is set
    if not settings.gemini_api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")

    # Run the integration test
    asyncio.run(main())
