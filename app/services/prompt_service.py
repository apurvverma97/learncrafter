"""
Prompt service for LearnCrafter MVP.
Single Responsibility: Formatting prompts with variables.
"""

import logging
from typing import Any, Dict, Optional

from app.services.database import db_service

logger = logging.getLogger(__name__)


class PromptService:
    """Service for loading and formatting prompts from the database."""

    async def get_prompt_template(self, prompt_id: str) -> Optional[str]:
        """Load prompt template from the database."""
        try:
            prompt_data = await db_service.get_prompt(prompt_id)
            if not prompt_data:
                logger.error(f"Prompt '{prompt_id}' not found in the database.")
                return None
            return prompt_data.get("template")
        except Exception as e:
            logger.error(f"Failed to load prompt template for '{prompt_id}': {e}")
            return None

    def _format_prompt(self, template: str, variables: Dict[str, Any]) -> str:
        """Format prompt template with provided variables."""
        try:
            formatted_prompt = template
            for key, value in variables.items():
                placeholder = f"{{{key}}}"
                if placeholder in formatted_prompt:
                    if isinstance(value, list):
                        formatted_value = self._format_list(value)
                    elif value is None:
                        formatted_value = "Not specified"
                    else:
                        formatted_value = str(value)
                    formatted_prompt = formatted_prompt.replace(placeholder, formatted_value)
            return formatted_prompt
        except Exception as e:
            logger.error(f"Failed to format prompt: {e}")
            return template

    def _format_list(self, items: list) -> str:
        """Format a list of items for prompt inclusion."""
        if not items:
            return "None specified"
        return "\n".join([f"- {item}" for item in items])

    async def get_prompt(self, prompt_id: str, variables: Dict[str, Any]) -> Optional[str]:
        """
        Get a formatted prompt by ID with variables, fetching from db.
        """
        try:
            template = await self.get_prompt_template(prompt_id)
            if not template:
                return None
            return self._format_prompt(template, variables)
        except Exception as e:
            logger.error(f"Failed to get prompt '{prompt_id}': {e}")
            return None

    async def get_valid_prompt_ids(self) -> list[str]:
        """Get list of valid prompt IDs from the database."""
        try:
            prompts = await db_service.list_prompts()
            return [prompt["prompt_id"] for prompt in prompts]
        except Exception as e:
            logger.error(f"Failed to fetch valid prompt IDs: {e}")
            return []

    async def get_prompt_by_workflow_step(self, workflow_step: str) -> Optional[str]:
        """Get prompt ID for a specific workflow step."""
        valid_prompts = await self.get_valid_prompt_ids()

        # Map workflow steps to prompt IDs
        workflow_mapping = {
            "concept_regeneration": "concept_regeneration",
            "content_validation": "content_validation",
            "concept_generation": "concept_generation",
        }

        prompt_id = workflow_mapping.get(workflow_step)
        if prompt_id and prompt_id in valid_prompts:
            return prompt_id

        logger.warning(f"Prompt ID for workflow step '{workflow_step}' not found or invalid")
        return None

    async def generate_concept_prompt(
        self,
        concept_data: Any,
        module_context: Optional[dict] = None,
        course_context: Optional[dict] = None,
        workflow_step: str = "concept_generation",
    ) -> str:
        """Generate a prompt for concept content generation."""
        # Get the appropriate prompt ID for the workflow step
        prompt_id = await self.get_prompt_by_workflow_step(workflow_step)
        if not prompt_id:
            # Fallback to default concept_generation
            prompt_id = "concept_generation"
            logger.warning(f"Using fallback prompt ID: {prompt_id}")

        variables = {
            "title": getattr(concept_data, "title", "Unknown"),
            "description": getattr(concept_data, "description", "No description provided"),
            "objectives": getattr(concept_data, "learning_objectives", []),
            "prerequisites": getattr(concept_data, "prerequisites", []),
            "module_context": (
                f"{module_context.get('title', '')} - " f"{module_context.get('description', '')}"
                if module_context
                else "No module context"
            ),
            "level": (course_context.get("level", "beginner") if course_context else "beginner"),
        }
        prompt = await self.get_prompt(prompt_id, variables)
        if not prompt:
            raise Exception(f"Failed to generate concept prompt for workflow step: {workflow_step}")
        return prompt

    async def generate_regeneration_prompt(
        self,
        concept_title: str,
        current_content: str,
        feedback: Optional[str] = None,
        workflow_step: str = "concept_regeneration",
    ) -> str:
        """Generate a prompt for content regeneration."""
        try:
            # Get the appropriate prompt ID for the workflow step
            prompt_id = await self.get_prompt_by_workflow_step(workflow_step)
            if not prompt_id:
                # Fallback to default concept_regeneration
                prompt_id = "concept_regeneration"
                logger.warning(f"Using fallback prompt ID: {prompt_id}")

            variables = {
                "concept_title": concept_title,
                "current_content": (
                    current_content[:1000] + "..."
                    if len(current_content) > 1000
                    else current_content
                ),
                "feedback": feedback or "No specific feedback provided",
            }

            prompt = await self.get_prompt(prompt_id, variables)

            if not prompt:
                raise Exception(
                    f"Failed to load concept regeneration prompt for workflow step: {workflow_step}"
                )

            return prompt

        except Exception as e:
            logger.error(f"Failed to generate regeneration prompt: {e}")
            raise Exception(f"Regeneration prompt generation failed: {str(e)}")

    async def generate_validation_prompt(
        self, content: str, workflow_step: str = "content_validation"
    ) -> str:
        """
        Generate a prompt for content validation.

        Args:
            content: Content to validate
            workflow_step: Workflow step for validation

        Returns:
            Validation prompt
        """
        try:
            # Get the appropriate prompt ID for the workflow step
            prompt_id = await self.get_prompt_by_workflow_step(workflow_step)
            if not prompt_id:
                # Fallback to default content_validation
                prompt_id = "content_validation"
                logger.warning(f"Using fallback prompt ID: {prompt_id}")

            variables = {"content": (content[:2000] + "..." if len(content) > 2000 else content)}

            prompt = await self.get_prompt(prompt_id, variables)

            if not prompt:
                raise Exception(
                    f"Failed to load content validation prompt for workflow step: {workflow_step}"
                )

            return prompt

        except Exception as e:
            logger.error(f"Failed to generate validation prompt: {e}")
            raise Exception(f"Validation prompt generation failed: {str(e)}")

    async def generate_safety_prompt(self, content: str) -> str:
        """
        Generate a prompt for content safety validation.

        Args:
            content: Content to validate for safety

        Returns:
            Safety validation prompt
        """
        try:
            variables = {"content": (content[:1500] + "..." if len(content) > 1500 else content)}

            prompt = await self.get_prompt("safety_check", variables)

            if not prompt:
                raise Exception("Failed to load safety check prompt")

            return prompt

        except Exception as e:
            logger.error(f"Failed to generate safety prompt: {e}")
            raise Exception(f"Safety prompt generation failed: {str(e)}")

    def list_available_prompts(self) -> Dict[str, Any]:
        """List all available prompts and their configurations."""
        return {}

    def reload_config(self) -> bool:
        """Reload prompt configuration from file."""
        return False
