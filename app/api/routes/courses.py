"""
Course API routes for LearnCrafter MVP.
Single Responsibility: Course management endpoints only.
"""

import logging
import uuid
from datetime import datetime
from typing import Annotated, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Path, Query

from app.agents.course_publisher import CoursePublishingAgent
from app.models.schemas import (
    CourseCreate,
    CourseLevel,
    CoursePublishJobRequest,
    CoursePublishJobResponse,
    CoursePublishJobStatus,
    CourseResponse,
    CourseTopic,
    CourseUpdate,
    CourseWithModules,
    JobStatus,
    Page,
)
from app.services.course_service import CourseService
from app.services.database import DatabaseService, db_service, get_db_service

logger = logging.getLogger(__name__)

# In-memory job tracking (in production, use Redis or database)
job_tracker = {}

router = APIRouter(prefix="/courses", tags=["courses"])


@router.post(
    "/publishJob",
    response_model=CoursePublishJobResponse,
    status_code=202,
)
async def publish_course_job(
    job_request: CoursePublishJobRequest, background_tasks: BackgroundTasks
):
    """
    Starts an asynchronous job to create a new course, modules and concepts.
    """
    job_id = str(uuid.uuid4())

    # Beautiful logging for job initiation
    logger.info("=" * 80)
    logger.info("🎯 COURSE PUBLISHING JOB INITIATED")
    logger.info("=" * 80)
    logger.info(f"📋 Job ID: {job_id}")
    logger.info(f"📚 Topic: {job_request.topic.value}")
    logger.info(f"📊 Level: {job_request.level.value}")
    expected_modules = len(job_request.modules) if job_request.modules else job_request.num_modules
    logger.info(f"📖 Expected Modules: {expected_modules}")
    logger.info(f"📝 Concepts per Module: {job_request.concepts_per_module}")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"⏰ Timestamp: {timestamp}")
    logger.info("=" * 80)

    # Initialize job tracking
    job_tracker[job_id] = {
        "job_id": job_id,
        "status": JobStatus.PENDING,
        "progress_percentage": 0.0,
        "current_step": "Initializing",
        "total_steps": 0,
        "completed_steps": 0,
        "course_id": None,
        "error_message": None,
        "start_time": datetime.now(),
        "estimated_completion": None,
    }

    # Initialize services and agent
    course_service = CourseService()
    agent = CoursePublishingAgent(course_service=course_service, db_service=db_service)

    # Add the long-running task to the background
    background_tasks.add_task(agent.publish_course, job_request)

    logger.info(f"✅ Background task queued successfully for Job ID: {job_id}")

    return CoursePublishJobResponse(
        job_id=job_id,
        message="Course publishing job started successfully. Check logs for progress.",
    )


@router.get("/publishJob/{job_id}/status", response_model=CoursePublishJobStatus)
async def get_job_status(job_id: str = Path(..., description="Job ID")):
    """
    Get the status of a course publishing job.
    """
    if job_id not in job_tracker:
        raise HTTPException(status_code=404, detail="Job not found")

    job_info = job_tracker[job_id]
    return CoursePublishJobStatus(**job_info)


@router.post("/", response_model=CourseResponse, status_code=201)
async def create_course(course: CourseCreate):
    """Create a new course."""
    try:
        course_data = course.model_dump()
        course_id = await db_service.create_course(course_data)
        course_data = await db_service.get_course(course_id)
        return CourseResponse(**course_data)
    except Exception as e:
        logger.error(f"Failed to create course: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=Page)
async def list_courses(
    db: Annotated[DatabaseService, Depends(get_db_service)],
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    topic: Optional[CourseTopic] = Query(None, description="Filter by topic"),
    level: Optional[CourseLevel] = Query(None, description="Filter by level"),
    search: Optional[str] = Query(None, description="Search term for title/description"),
):
    """List courses with pagination and filtering."""
    try:
        courses = await db.list_courses(level, topic, search)
        total_courses = await db.count_courses(level, topic, search)
        return Page(
            data=courses,
            page=page,
            size=size,
            pages=(total_courses + size - 1) // size,
        )
    except Exception as e:
        logger.error(f"Failed to list courses: {e}")
        raise HTTPException(status_code=500, detail="Failed to list courses")


@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(course_id: str = Path(..., description="Course ID")):
    """Get a specific course by ID."""
    try:
        course = await db_service.get_course(course_id)
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        return CourseResponse(**course)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get course {course_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{course_id}/full", response_model=CourseWithModules)
async def get_course_with_modules(course_id: str = Path(..., description="Course ID")):
    """Get complete course with nested modules and concepts."""
    try:
        course_data = await db_service.get_course_with_modules(course_id)
        if not course_data:
            raise HTTPException(status_code=404, detail="Course not found")
        return CourseWithModules(**course_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get course with modules {course_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: str = Path(..., description="Course ID"),
    course_update: CourseUpdate = None,
):
    """Update a course."""
    try:
        # Check if course exists
        existing_course = await db_service.get_course(course_id)
        if not existing_course:
            raise HTTPException(status_code=404, detail="Course not found")

        # Prepare update data
        update_data = course_update.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="No update data provided")

        # Update course
        success = await db_service.update_course(course_id, update_data)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update course")

        # Return updated course
        updated_course = await db_service.get_course(course_id)
        return CourseResponse(**updated_course)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update course {course_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{course_id}")
async def delete_course(course_id: str = Path(..., description="Course ID")):
    """Delete a course (cascades to modules and concepts)."""
    try:
        # Check if course exists
        existing_course = await db_service.get_course(course_id)
        if not existing_course:
            raise HTTPException(status_code=404, detail="Course not found")

        # Delete course
        success = await db_service.delete_course(course_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete course")

        return {"message": "Course deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete course {course_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
