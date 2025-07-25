"""
Prompt service for LearnCrafter MVP.
Single Responsibility: Prompt generation from markdown files.
"""
import json
import os
from typing import Dict, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class PromptService:
    """Service for loading and formatting prompts from markdown files."""
    
    def __init__(self):
        """Initialize prompt service with configuration."""
        self.prompts_dir = Path(__file__).parent.parent / "prompts"
        self.config_file = self.prompts_dir / "prompts.json"
        self.prompt_config = self._load_prompt_config()
    
    def _load_prompt_config(self) -> Dict[str, Any]:
        """Load prompt configuration from JSON file."""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load prompt config: {e}")
            return {"prompts": {}}
    
    def _load_prompt_template(self, prompt_id: str) -> Optional[str]:
        """Load prompt template from markdown file."""
        try:
            if prompt_id not in self.prompt_config.get("prompts", {}):
                logger.error(f"Prompt ID '{prompt_id}' not found in configuration")
                return None
            
            prompt_info = self.prompt_config["prompts"][prompt_id]
            file_path = self.prompts_dir / prompt_info["file"]
            
            if not file_path.exists():
                logger.error(f"Prompt file not found: {file_path}")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
                
        except Exception as e:
            logger.error(f"Failed to load prompt template for '{prompt_id}': {e}")
            return None
    
    def _format_prompt(self, template: str, variables: Dict[str, Any]) -> str:
        """Format prompt template with provided variables."""
        try:
            formatted_prompt = template
            
            # Replace variables in the template
            for key, value in variables.items():
                placeholder = f"{{{key}}}"
                if placeholder in formatted_prompt:
                    # Handle different data types
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
        
        formatted_items = []
        for i, item in enumerate(items, 1):
            formatted_items.append(f"{i}. {item}")
        
        return "\n".join(formatted_items)
    
    def get_prompt(self, prompt_id: str, variables: Dict[str, Any]) -> Optional[str]:
        """
        Get a formatted prompt by ID with variables.
        
        Args:
            prompt_id: The prompt identifier from config
            variables: Dictionary of variables to format the prompt
            
        Returns:
            Formatted prompt string or None if failed
        """
        try:
            # Load the prompt template
            template = self._load_prompt_template(prompt_id)
            if not template:
                return None
            
            # Format the prompt with variables
            formatted_prompt = self._format_prompt(template, variables)
            
            logger.info(f"Successfully loaded and formatted prompt: {prompt_id}")
            return formatted_prompt
            
        except Exception as e:
            logger.error(f"Failed to get prompt '{prompt_id}': {e}")
            return None
    
    def generate_concept_prompt(self, concept_data: Any, 
                               module_context: Optional[dict] = None,
                               course_context: Optional[dict] = None) -> str:
        """
        Generate a prompt for concept content generation.
        
        Args:
            concept_data: Concept generation request data
            module_context: Optional module context
            course_context: Optional course context
            
        Returns:
            Formatted prompt string
        """
        try:
            # Prepare variables for the prompt
            variables = {
                "title": getattr(concept_data, 'title', 'Unknown'),
                "description": getattr(concept_data, 'description', 'No description provided'),
                "objectives": self._format_list(getattr(concept_data, 'learning_objectives', [])),
                "prerequisites": self._format_list(getattr(concept_data, 'prerequisites', [])),
                "module_context": "No module context",
                "level": "beginner"
            }
            
            # Get module context if available
            if module_context:
                variables["module_context"] = f"{module_context.get('title', '')} - {module_context.get('description', '')}"
            
            # Get course level if available
            if course_context:
                variables["level"] = course_context.get('level', 'beginner')
            
            # Get the formatted prompt
            prompt = self.get_prompt("concept_generation", variables)
            
            if not prompt:
                raise Exception("Failed to load concept generation prompt")
            
            return prompt
            
        except Exception as e:
            logger.error(f"Failed to generate concept prompt: {e}")
            raise Exception(f"Prompt generation failed: {str(e)}")
    
    def generate_regeneration_prompt(self, concept_title: str, 
                                   current_content: str,
                                   feedback: Optional[str] = None) -> str:
        """
        Generate a prompt for content regeneration.
        
        Args:
            concept_title: Title of the concept
            current_content: Current content to improve
            feedback: Optional feedback for improvement
            
        Returns:
            Formatted regeneration prompt
        """
        try:
            variables = {
                "concept_title": concept_title,
                "current_content": current_content[:1000] + "..." if len(current_content) > 1000 else current_content,
                "feedback": feedback or "No specific feedback provided"
            }
            
            prompt = self.get_prompt("concept_regeneration", variables)
            
            if not prompt:
                raise Exception("Failed to load concept regeneration prompt")
            
            return prompt
            
        except Exception as e:
            logger.error(f"Failed to generate regeneration prompt: {e}")
            raise Exception(f"Regeneration prompt generation failed: {str(e)}")
    
    def generate_validation_prompt(self, content: str) -> str:
        """
        Generate a prompt for content validation.
        
        Args:
            content: Content to validate
            
        Returns:
            Validation prompt
        """
        try:
            variables = {
                "content": content[:2000] + "..." if len(content) > 2000 else content
            }
            
            prompt = self.get_prompt("content_validation", variables)
            
            if not prompt:
                raise Exception("Failed to load content validation prompt")
            
            return prompt
            
        except Exception as e:
            logger.error(f"Failed to generate validation prompt: {e}")
            raise Exception(f"Validation prompt generation failed: {str(e)}")
    
    def generate_safety_prompt(self, content: str) -> str:
        """
        Generate a prompt for content safety validation.
        
        Args:
            content: Content to validate for safety
            
        Returns:
            Safety validation prompt
        """
        try:
            variables = {
                "content": content[:1500] + "..." if len(content) > 1500 else content
            }
            
            prompt = self.get_prompt("safety_check", variables)
            
            if not prompt:
                raise Exception("Failed to load safety check prompt")
            
            return prompt
            
        except Exception as e:
            logger.error(f"Failed to generate safety prompt: {e}")
            raise Exception(f"Safety prompt generation failed: {str(e)}")
    
    def list_available_prompts(self) -> Dict[str, Any]:
        """List all available prompts and their configurations."""
        return self.prompt_config.get("prompts", {})
    
    def reload_config(self) -> bool:
        """Reload prompt configuration from file."""
        try:
            self.prompt_config = self._load_prompt_config()
            logger.info("Prompt configuration reloaded successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to reload prompt configuration: {e}")
            return False 