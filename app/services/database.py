"""
Database service for LearnCrafter MVP.
Single Responsibility: Database operations only.
"""
from typing import Optional, List, Dict, Any
from supabase import create_client, Client
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class DatabaseService:
    """Database service for Supabase operations."""
    
    def __init__(self):
        """Initialize Supabase client."""
        self.client: Client = create_client(
            settings.supabase_url,
            settings.supabase_key
        )
    
    # Course Operations
    async def create_course(self, course_data: Dict[str, Any]) -> str:
        """Create a new course."""
        try:
            response = self.client.table('courses').insert(course_data).execute()
            return response.data[0]['id']
        except Exception as e:
            logger.error(f"Failed to create course: {e}")
            raise
    
    async def get_course(self, course_id: str) -> Optional[Dict[str, Any]]:
        """Get a course by ID."""
        try:
            response = self.client.table('courses').select('*').eq('id', course_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Failed to get course {course_id}: {e}")
            raise
    
    async def update_course(self, course_id: str, update_data: Dict[str, Any]) -> bool:
        """Update a course."""
        try:
            response = self.client.table('courses').update(update_data).eq('id', course_id).execute()
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"Failed to update course {course_id}: {e}")
            raise
    
    async def delete_course(self, course_id: str) -> bool:
        """Delete a course (cascades to modules and concepts)."""
        try:
            response = self.client.table('courses').delete().eq('id', course_id).execute()
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"Failed to delete course {course_id}: {e}")
            raise
    
    async def list_courses(self, page: int = 1, size: int = 20) -> List[Dict[str, Any]]:
        """List courses with pagination."""
        try:
            offset = (page - 1) * size
            response = self.client.table('courses').select('*').order('created_at', desc=True).range(offset, offset + size - 1).execute()
            return response.data
        except Exception as e:
            logger.error(f"Failed to list courses: {e}")
            raise
    
    async def count_courses(self) -> int:
        """Count total courses."""
        try:
            response = self.client.table('courses').select('id', count='exact').execute()
            return response.count or 0
        except Exception as e:
            logger.error(f"Failed to count courses: {e}")
            raise
    
    # Module Operations
    async def create_module(self, module_data: Dict[str, Any]) -> str:
        """Create a new module."""
        try:
            response = self.client.table('modules').insert(module_data).execute()
            return response.data[0]['id']
        except Exception as e:
            logger.error(f"Failed to create module: {e}")
            raise
    
    async def get_module(self, module_id: str) -> Optional[Dict[str, Any]]:
        """Get a module by ID."""
        try:
            response = self.client.table('modules').select('*').eq('id', module_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Failed to get module {module_id}: {e}")
            raise
    
    async def get_modules_by_course(self, course_id: str) -> List[Dict[str, Any]]:
        """Get all modules for a course."""
        try:
            response = self.client.table('modules').select('*').eq('course_id', course_id).order('order_index').execute()
            return response.data
        except Exception as e:
            logger.error(f"Failed to get modules for course {course_id}: {e}")
            raise
    
    async def update_module(self, module_id: str, update_data: Dict[str, Any]) -> bool:
        """Update a module."""
        try:
            response = self.client.table('modules').update(update_data).eq('id', module_id).execute()
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"Failed to update module {module_id}: {e}")
            raise
    
    async def delete_module(self, module_id: str) -> bool:
        """Delete a module (cascades to concepts)."""
        try:
            response = self.client.table('modules').delete().eq('id', module_id).execute()
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"Failed to delete module {module_id}: {e}")
            raise
    
    # Concept Operations
    async def create_concept(self, concept_data: Dict[str, Any]) -> str:
        """Create a new concept."""
        try:
            response = self.client.table('concepts').insert(concept_data).execute()
            return response.data[0]['id']
        except Exception as e:
            logger.error(f"Failed to create concept: {e}")
            raise
    
    async def get_concept(self, concept_id: str) -> Optional[Dict[str, Any]]:
        """Get a concept by ID."""
        try:
            response = self.client.table('concepts').select('*').eq('id', concept_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Failed to get concept {concept_id}: {e}")
            raise
    
    async def get_concepts_by_module(self, module_id: str) -> List[Dict[str, Any]]:
        """Get all concepts for a module."""
        try:
            response = self.client.table('concepts').select('*').eq('module_id', module_id).order('order_index').execute()
            return response.data
        except Exception as e:
            logger.error(f"Failed to get concepts for module {module_id}: {e}")
            raise
    
    async def update_concept(self, concept_id: str, update_data: Dict[str, Any]) -> bool:
        """Update a concept."""
        try:
            response = self.client.table('concepts').update(update_data).eq('id', concept_id).execute()
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"Failed to update concept {concept_id}: {e}")
            raise
    
    async def delete_concept(self, concept_id: str) -> bool:
        """Delete a concept."""
        try:
            response = self.client.table('concepts').delete().eq('id', concept_id).execute()
            return len(response.data) > 0
        except Exception as e:
            logger.error(f"Failed to delete concept {concept_id}: {e}")
            raise
    
    # Nested Queries
    async def get_course_with_modules(self, course_id: str) -> Optional[Dict[str, Any]]:
        """Get complete course with nested modules and concepts."""
        try:
            # Get course
            course = await self.get_course(course_id)
            if not course:
                return None
            
            # Get modules with concepts
            modules = await self.get_modules_by_course(course_id)
            for module in modules:
                module['concepts'] = await self.get_concepts_by_module(module['id'])
            
            course['modules'] = modules
            return course
        except Exception as e:
            logger.error(f"Failed to get course with modules {course_id}: {e}")
            raise


# Global database service instance
db_service = DatabaseService() 