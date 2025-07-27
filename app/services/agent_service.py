from app.services.course_service import CourseService
from app.services.database import DatabaseService


class AgentService:
    def __init__(self, course_service: CourseService, db_service: DatabaseService):
        self.course_service = course_service
        self.db_service = db_service

    async def create_course_structure(self, topic: str, level: str, num_modules: int):
        course_plan = await self._get_course_plan(topic, level, num_modules)
        if not course_plan:
            return None

        course_data = {
            "title": course_plan["course_title"],
            "description": course_plan["course_description"],
            "topic": topic,
            "level": level,
        }
        course_id = await self.db_service.create_course(course_data)
        return course_id

    async def _get_course_plan(self, topic, level, num_modules):
        course_service = CourseService()
        prompt = f"Create a course plan for {topic} at {level} level."
        return await course_service.generate_content(prompt)
