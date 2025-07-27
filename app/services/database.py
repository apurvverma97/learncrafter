"""
Database service for LearnCrafter MVP.
Single Responsibility: Database operations only.
"""

import logging
from typing import Any, Dict, List, Optional

from app.repositories.supabase import SupabaseDAO

logger = logging.getLogger(__name__)


class DatabaseService:
    """Orchestrates database operations using a DAO."""

    def __init__(self, dao: Optional[SupabaseDAO] = None):
        """Initialize the service with a DAO instance."""
        self.dao = dao or SupabaseDAO()

    async def create_course(self, course_data: Dict[str, Any]) -> str:
        """Create a new course."""
        result = self.dao.insert("courses", course_data)
        return result["id"]

    async def get_course(self, course_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific course by ID."""
        return self.dao.get("courses", {"id": course_id})

    async def get_course_by_title(self, course_title: str) -> Optional[Dict[str, Any]]:
        """Get a specific course by title."""
        return self.dao.get("courses", {"title": course_title})

    async def update_course(self, course_id: str, course_data: Dict[str, Any]) -> bool:
        """Update an existing course."""
        return self.dao.update("courses", {"id": course_id}, course_data)

    async def delete_course(self, course_id: str) -> bool:
        """Delete a course."""
        return self.dao.delete("courses", {"id": course_id})

    async def list_courses(
        self,
        level: Optional[str] = None,
        topic: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """List all courses with optional filtering."""
        filters = {}
        if level:
            filters["level"] = level
        if topic:
            filters["topic"] = topic
        if search:
            filters["title"] = f"%{search}%"
        return self.dao.list_query("courses", filters)

    async def count_courses(
        self,
        level: Optional[str] = None,
        topic: Optional[str] = None,
        search: Optional[str] = None,
    ) -> int:
        """Count all courses with optional filtering."""
        filters = {}
        if level:
            filters["level"] = level
        if topic:
            filters["topic"] = topic
        if search:
            filters["title"] = f"%{search}%"
        return self.dao.count_query("courses", filters)

    async def create_module(self, module_data: Dict[str, Any]) -> str:
        """Create a new module."""
        result = self.dao.insert("modules", module_data)
        return result["id"]

    async def get_module(self, module_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific module by ID."""
        return self.dao.get("modules", {"id": module_id})

    async def get_modules_by_course(self, course_id: str) -> List[Dict[str, Any]]:
        """Get all modules for a given course."""
        return self.dao.list_query("modules", {"course_id": course_id}, order_by="order_index")

    async def update_module(self, module_id: str, module_data: Dict[str, Any]) -> bool:
        """Update an existing module."""
        return self.dao.update("modules", {"id": module_id}, module_data)

    async def delete_module(self, module_id: str) -> bool:
        """Delete a module."""
        return self.dao.delete("modules", {"id": module_id})

    async def create_concept(self, concept_data: Dict[str, Any]) -> str:
        """Create a new concept."""
        result = self.dao.insert("concepts", concept_data)
        return result["id"]

    async def get_concept(self, concept_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific concept by ID."""
        return self.dao.get("concepts", {"id": concept_id})

    async def get_concepts_by_module(self, module_id: str) -> List[Dict[str, Any]]:
        """Get all concepts for a given module."""
        return self.dao.list_query("concepts", {"module_id": module_id}, order_by="order_index")

    async def update_concept(self, concept_id: str, concept_data: Dict[str, Any]) -> bool:
        """Update an existing concept."""
        return self.dao.update("concepts", {"id": concept_id}, concept_data)

    async def delete_concept(self, concept_id: str) -> bool:
        """Delete a concept."""
        return self.dao.delete("concepts", {"id": concept_id})

    async def create_prompt(self, prompt_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new prompt."""
        return self.dao.insert("prompts", prompt_data)

    async def get_prompt(self, prompt_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific prompt by ID."""
        return self.dao.get("prompts", {"prompt_id": prompt_id})

    async def list_prompts(self) -> List[Dict[str, Any]]:
        """List all prompts."""
        return self.dao.list_query("prompts")

    async def update_prompt(self, prompt_id: str, prompt_data: Dict[str, Any]) -> bool:
        """Update an existing prompt."""
        return self.dao.update("prompts", {"prompt_id": prompt_id}, prompt_data)

    async def delete_prompt(self, prompt_id: str) -> bool:
        """Delete a prompt."""
        return self.dao.delete("prompts", {"prompt_id": prompt_id})

    async def get_course_with_modules(self, course_id: str) -> Optional[Dict[str, Any]]:
        """Get a course with all its modules and concepts."""
        try:
            # Get the course
            course = self.dao.get("courses", {"id": course_id})
            if not course:
                return None

            # Get modules for this course
            modules = self.dao.list_query(
                "modules", {"course_id": course_id}, order_by="order_index"
            )

            # Get concepts for each module
            for module in modules:
                concepts = self.dao.list_query(
                    "concepts", {"module_id": module["id"]}, order_by="order_index"
                )
                module["concepts"] = concepts

            course["modules"] = modules
            return course
        except Exception as e:
            logger.error(f"Failed to get course with modules {course_id}: {e}")
            return None


# Global database service instance
db_service = DatabaseService()


def get_db_service() -> DatabaseService:
    """Get the global database service instance."""
    return db_service
