"""
Core agent for orchestrating the automated creation of courses.
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.models.schemas import ConceptPlan, CoursePublishJobRequest, ModulePlan
from app.services.course_service import CourseService
from app.services.database import DatabaseService

logger = logging.getLogger(__name__)

# Beautiful logging constants
LOG_SEPARATOR = "=" * 80
LOG_SUBSEPARATOR = "-" * 60
PROGRESS_BAR_WIDTH = 50

COURSE_PLANNER_PROMPT = """
As an expert instructional designer, create a comprehensive course plan
for the topic "{topic}" at a {level} level.
The plan should include a course title, a brief course description,
and a list of {num_modules} module titles and their descriptions.
Respond in JSON format with the keys: "course_title", "course_description",
"module_plans" (a list of objects with "module_title"
and "module_description").
"""

CONCEPT_DETAIL_PROMPT = """
For the module "{module_title}" in a course about "{topic}",
generate a list of {num_concepts} key concepts.
For each concept, provide a title, a brief description, a list of 2-3
learning objectives, and a list of 1-2 prerequisites.
Respond in JSON format with a single key "concepts" which is a list of
objects. Each object should have keys: "concept_title",
"concept_description", "learning_objectives", "prerequisites".
"""


class CoursePublishingAgent:
    """Orchestrates the creation of a new course with comprehensive logging."""

    def __init__(self, course_service: CourseService, db_service: DatabaseService):
        self.course_service = course_service
        self.db_service = db_service
        self.job_id: Optional[str] = None
        self.course_id: Optional[str] = None
        self.start_time: Optional[float] = None
        self.total_steps = 0
        self.current_step = 0

    def _log_header(self, message: str):
        """Log a beautiful header message."""
        logger.info("")
        logger.info(LOG_SEPARATOR)
        logger.info(f"🚀 {message}")
        logger.info(LOG_SEPARATOR)

    def _log_subheader(self, message: str):
        """Log a beautiful subheader message."""
        logger.info("")
        logger.info(LOG_SUBSEPARATOR)
        logger.info(f"📋 {message}")
        logger.info(LOG_SUBSEPARATOR)

    def _log_progress(self, step: int, total: int, message: str, course_id: str = None):
        """Log progress with a beautiful progress bar."""
        percentage = (step / total) * 100
        filled_width = int((step / total) * PROGRESS_BAR_WIDTH)
        bar = "█" * filled_width + "░" * (PROGRESS_BAR_WIDTH - filled_width)

        timestamp = datetime.now().strftime("%H:%M:%S")
        course_info = f" | Course: {course_id}" if course_id else ""

        logger.info(f"[{timestamp}] [{bar}] {percentage:5.1f}% | {message}{course_info}")

    def _log_success(self, message: str, course_id: str = None):
        """Log a success message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        course_info = f" | Course: {course_id}" if course_id else ""
        logger.info(f"[{timestamp}] ✅ {message}{course_info}")

    def _log_error(self, message: str, course_id: str = None):
        """Log an error message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        course_info = f" | Course: {course_id}" if course_id else ""
        logger.error(f"[{timestamp}] ❌ {message}{course_info}")

    def _log_info(self, message: str, course_id: str = None):
        """Log an info message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        course_info = f" | Course: {course_id}" if course_id else ""
        logger.info(f"[{timestamp}] ℹ️  {message}{course_info}")

    def _log_duration(self, start_time: float):
        """Log the duration of an operation."""
        duration = time.time() - start_time
        logger.info(f"⏱️  Operation completed in {duration:.2f} seconds")

    async def publish_course(
        self, job_request: CoursePublishJobRequest, llm_delay_seconds: float = None
    ):
        """
        Executes the full course creation pipeline with comprehensive logging.
        """
        # Use configurable delay from settings if not provided
        if llm_delay_seconds is None:
            from app.core.config import settings

            llm_delay_seconds = settings.llm_delay_seconds

        # Initialize job tracking
        self.job_id = str(uuid.uuid4())
        self.start_time = time.time()

        # Calculate total steps for progress tracking
        num_modules = len(job_request.modules) if job_request.modules else job_request.num_modules
        num_concepts_per_module = job_request.concepts_per_module
        self.total_steps = (
            3 + num_modules + (num_modules * num_concepts_per_module)
        )  # Course + Modules + Concepts

        self._log_header("COURSE PUBLISHING JOB STARTED")
        self._log_info(f"Job ID: {self.job_id}")
        self._log_info(f"Topic: {job_request.topic.value}")
        self._log_info(f"Level: {job_request.level.value}")
        self._log_info(f"Expected Modules: {num_modules}")
        self._log_info(f"Concepts per Module: {num_concepts_per_module}")
        self._log_info(f"Total Steps: {self.total_steps}")

        try:
            # Step 1: Plan Course and Modules (10% of total progress)
            self.current_step += 1
            self._log_progress(
                self.current_step, self.total_steps, "Planning course structure", self.course_id
            )
            course_plan = await self._plan_course_and_modules(job_request, llm_delay_seconds)
            self._log_success("Course planning completed", self.course_id)

            # Step 2: Create Course in Database (15% of total progress)
            self.current_step += 1
            self._log_progress(
                self.current_step,
                self.total_steps,
                "Creating course entry in database",
                self.course_id,
            )
            course_id = await self._create_course_entry(job_request, course_plan)
            if not course_id:
                self._log_error("Failed to create course entry - aborting job", self.course_id)
                return

            self.course_id = course_id
            self._log_success(f"Course created with ID: {course_id}", self.course_id)

            # Step 3: Create Modules and Concepts (75% of total progress)
            await self._create_modules_and_concepts(
                course_id, job_request, course_plan["module_plans"], llm_delay_seconds
            )

            # Final success message
            total_duration = time.time() - self.start_time
            self._log_header("COURSE PUBLISHING JOB COMPLETED SUCCESSFULLY")
            self._log_success(
                f"Course '{course_plan['course_title']}' published successfully", self.course_id
            )
            self._log_info(f"Job ID: {self.job_id}", self.course_id)
            self._log_info(f"Course ID: {course_id}", self.course_id)
            self._log_info(f"Total Duration: {total_duration:.2f} seconds", self.course_id)
            self._log_info(
                f"Total Steps Completed: {self.current_step}/{self.total_steps}", self.course_id
            )

        except Exception as e:
            self._log_error(f"Course publishing job failed: {str(e)}", self.course_id)
            if self.start_time:
                total_duration = time.time() - self.start_time
                self._log_info(f"Job failed after {total_duration:.2f} seconds", self.course_id)
            raise

    async def _plan_course_and_modules(
        self, job_request: CoursePublishJobRequest, llm_delay_seconds: float = 45.0
    ) -> Dict[str, Any]:
        """
        Generates the course plan with detailed logging.
        """
        step_start_time = time.time()

        if job_request.course_title and job_request.modules:
            self._log_info("Using manually provided course and module plan", self.course_id)
            course_plan = {
                "course_title": job_request.course_title,
                "course_description": job_request.course_description or "",
                "module_plans": [
                    {
                        "module_title": m.title,
                        "module_description": m.description or "",
                    }
                    for m in job_request.modules
                ],
            }
            self._log_info(
                f"Manual plan includes {len(course_plan['module_plans'])} modules", self.course_id
            )
        else:
            self._log_info("Generating course plan via LLM", self.course_id)

            # Add configurable delay before LLM call
            if llm_delay_seconds > 0:
                self._log_info(
                    f"⏳ Adding {llm_delay_seconds}s delay before LLM call for rate limiting",
                    self.course_id,
                )
                await asyncio.sleep(llm_delay_seconds)
                self._log_info("✅ Delay completed, proceeding with LLM call", self.course_id)

            prompt = COURSE_PLANNER_PROMPT.format(
                topic=job_request.topic.value,
                level=job_request.level.value,
                num_modules=job_request.num_modules,
            )
            response_text = await self.course_service.generate_content(prompt)
            course_plan = json.loads(response_text)
            self._log_info(
                f"LLM generated plan includes {len(course_plan['module_plans'])} modules",
                self.course_id,
            )

        self._log_duration(step_start_time)
        return course_plan

    async def _create_course_entry(
        self, job_request: CoursePublishJobRequest, course_plan: Dict[str, Any]
    ) -> str:
        """Creates the course entry in the database with detailed logging."""
        step_start_time = time.time()

        course_data = {
            "title": course_plan["course_title"],
            "description": course_plan["course_description"],
            "topic": job_request.topic.value,
            "level": job_request.level.value,
        }

        self._log_info(f"Creating course: '{course_data['title']}'", self.course_id)
        self._log_info(
            f"Topic: {course_data['topic']}, Level: {course_data['level']}", self.course_id
        )

        try:
            course_id = await self.db_service.create_course(course_data)
            self._log_success("Course entry created successfully", course_id)
            self._log_duration(step_start_time)
            return course_id
        except Exception as e:
            self._log_error(f"Failed to create course entry in database: {e}", self.course_id)
            self._log_duration(step_start_time)
            return None

    async def _create_modules_and_concepts(
        self,
        course_id: str,
        job_request: CoursePublishJobRequest,
        module_plans: List[Dict[str, Any]],
        llm_delay_seconds: float = 45.0,
    ):
        """
        Iterates through modules and their concepts with detailed progress tracking.
        """
        self._log_subheader("CREATING MODULES AND CONCEPTS")
        self._log_info(f"Starting creation of {len(module_plans)} modules", course_id)

        for i, module_plan_data in enumerate(module_plans):
            # Update module plan structure
            if "module_title" in module_plan_data:
                module_plan_data["title"] = module_plan_data.pop("module_title")
            if "module_description" in module_plan_data:
                module_plan_data["description"] = module_plan_data.pop("module_description")

            module_plan = ModulePlan(**module_plan_data)

            # Progress for module creation
            self.current_step += 1
            self._log_progress(
                self.current_step,
                self.total_steps,
                f"Creating module {i+1}/{len(module_plans)}: '{module_plan.title}'",
                course_id,
            )

            # Create Module Entry
            module_id = await self._create_module_entry(course_id, module_plan, i + 1)
            if not module_id:
                self._log_error(
                    f"Failed to create module '{module_plan.title}' - skipping", course_id
                )
                continue

            # Plan and Create Concepts
            manual_concepts = self._get_manual_concepts(job_request, module_plan.title)
            concept_plans = await self._plan_concepts(
                job_request, module_plan.title, manual_concepts, llm_delay_seconds
            )

            await self._create_concept_entries(
                module_id, concept_plans, course_id, "concept_generation"
            )

    async def _create_module_entry(
        self, course_id: str, module_plan: ModulePlan, order_index: int
    ) -> str:
        """Creates a single module entry with detailed logging."""
        step_start_time = time.time()

        module_data = {
            "course_id": course_id,
            "title": module_plan.title,
            "description": module_plan.description,
            "order_index": order_index,
        }

        self._log_info(f"Creating module: '{module_plan.title}' (Order: {order_index})", course_id)

        try:
            module_id = await self.db_service.create_module(module_data)
            self._log_success(f"Module '{module_plan.title}' created successfully", course_id)
            self._log_duration(step_start_time)
            return module_id
        except Exception as e:
            self._log_error(f"Failed to create module '{module_plan.title}': {e}", course_id)
            self._log_duration(step_start_time)
            return None

    def _get_manual_concepts(
        self, job_request: CoursePublishJobRequest, module_title: str
    ) -> List[ConceptPlan]:
        """Check if manual concepts were provided for a given module."""
        if job_request.modules:
            for module in job_request.modules:
                if module.title == module_title and module.concepts:
                    self._log_info(
                        f"Found {len(module.concepts)} manual concepts for module '{module_title}'",
                        self.course_id,
                    )
                    return module.concepts
        return None

    async def _plan_concepts(
        self,
        job_request: CoursePublishJobRequest,
        module_title: str,
        manual_concepts: List[ConceptPlan],
        llm_delay_seconds: float = 45.0,
    ) -> List[ConceptPlan]:
        """
        Generates concept plans for a module with detailed logging.
        """
        step_start_time = time.time()

        if manual_concepts:
            self._log_info(
                f"Using {len(manual_concepts)} manually provided concepts for module "
                f"'{module_title}'",
                self.course_id,
            )
            self._log_duration(step_start_time)
            return manual_concepts

        self._log_info(
            f"Generating {job_request.concepts_per_module} concepts for module "
            f"'{module_title}' via LLM",
            self.course_id,
        )

        # Add configurable delay before LLM call
        if llm_delay_seconds > 0:
            self._log_info(
                f"⏳ Adding {llm_delay_seconds}s delay before LLM call for rate limiting",
                self.course_id,
            )
            await asyncio.sleep(llm_delay_seconds)
            self._log_info("✅ Delay completed, proceeding with LLM call", self.course_id)

        prompt = CONCEPT_DETAIL_PROMPT.format(
            topic=job_request.topic.value,
            module_title=module_title,
            num_concepts=job_request.concepts_per_module,
        )
        response_text = await self.course_service.generate_content(prompt)
        concept_data = json.loads(response_text)

        concepts = []
        for c in concept_data.get("concepts", []):
            if "concept_title" in c:
                c["title"] = c.pop("concept_title")
            if "concept_description" in c:
                c["description"] = c.pop("concept_description")
            concepts.append(ConceptPlan(**c))

        self._log_info(
            f"Generated {len(concepts)} concepts for module '{module_title}'", self.course_id
        )
        self._log_duration(step_start_time)
        return concepts

    async def _create_concept_entries(
        self,
        module_id: str,
        concept_plans: List[ConceptPlan],
        course_id: str,
        workflow_step: str = "concept_generation",
    ):
        """Creates all concept entries for a given module with progress tracking."""
        self._log_info(f"Creating {len(concept_plans)} concepts for module", course_id)

        for i, concept_plan in enumerate(concept_plans):
            # Progress for concept creation
            self.current_step += 1
            self._log_progress(
                self.current_step,
                self.total_steps,
                f"Creating concept {i+1}/{len(concept_plans)}: '{concept_plan.title}'",
                course_id,
            )

            step_start_time = time.time()

            try:
                # Create concept with workflow step
                concept_data = {
                    "module_id": module_id,
                    "title": concept_plan.title,
                    "description": concept_plan.description,
                    "order_index": i + 1,
                    "learning_objectives": concept_plan.learning_objectives,
                    "prerequisites": concept_plan.prerequisites,
                    "content": "",  # Start with empty content
                }

                # Create the concept entry first
                concept_id = await self.db_service.create_concept(concept_data)

                # Generate content using the workflow step
                from app.services.prompt_service import PromptService

                prompt_service = PromptService()

                # Get module context for better prompt generation
                module_data = await self.db_service.get_module(module_id)
                module_context = (
                    {
                        "title": module_data.get("title", ""),
                        "description": module_data.get("description", ""),
                    }
                    if module_data
                    else None
                )

                # Generate content using the specified workflow step
                prompt = await prompt_service.generate_concept_prompt(
                    concept_plan, module_context=module_context, workflow_step=workflow_step
                )
                content = await self.course_service.generate_content(prompt)

                # Update concept with generated content
                await self.db_service.update_concept(concept_id, {"content": content})

                self._log_success(
                    f"Concept '{concept_plan.title}' created successfully with workflow step "
                    f"'{workflow_step}'",
                    course_id,
                )
                self._log_duration(step_start_time)
            except Exception as e:
                self._log_error(f"Failed to create concept '{concept_plan.title}': {e}", course_id)
                self._log_duration(step_start_time)
