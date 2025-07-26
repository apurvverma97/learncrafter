"""
Course API routes for LearnCrafter MVP.
Single Responsibility: Course management endpoints only.
"""
from fastapi import APIRouter, HTTPException, Query, Path
from typing import List, Optional
from app.models.schemas import (
    CourseCreate, CourseUpdate, CourseResponse, CourseWithModules,
    PaginationParams, PaginatedCourseResponse
)
from app.services.database import db_service
from app.models.schemas import CourseLevel, CourseTopic
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/courses", tags=["courses"])


@router.post("/", response_model=CourseResponse, status_code=201)
async def create_course(course: CourseCreate):
    """Create a new course."""
    try:
        course_data = course.dict()
        course_id = await db_service.create_course(course_data)
        course_data = await db_service.get_course(course_id)
        return CourseResponse(**course_data)
    except Exception as e:
        logger.error(f"Failed to create course: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=PaginatedCourseResponse)
async def list_courses(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    topic: Optional[CourseTopic] = Query(None, description="Filter by topic"),
    level: Optional[CourseLevel] = Query(None, description="Filter by level"),
    search: Optional[str] = Query(None, description="Search term for title/description")
):
    """List courses with pagination and filtering."""
    try:
        # Get courses with pagination and filtering from the database service
        courses_data = await db_service.list_courses(page, size, topic, level, search)
        total = await db_service.count_courses(topic, level, search)
        
        # Calculate pagination metadata
        pages = (total + size - 1) // size if total > 0 else 0
        
        return PaginatedCourseResponse(
            courses=[CourseResponse(**course) for course in courses_data],
            total=total,
            page=page,
            size=size,
            pages=pages
        )
    except Exception as e:
        logger.error(f"Failed to list courses: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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
    course_update: CourseUpdate = None
):
    """Update a course."""
    try:
        # Check if course exists
        existing_course = await db_service.get_course(course_id)
        if not existing_course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        # Prepare update data
        update_data = course_update.dict(exclude_unset=True)
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