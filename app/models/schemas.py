"""
Data schemas for LearnCrafter MVP.
Single Responsibility: Data validation and serialization only.
"""
from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field, validator


class CourseLevel(str, Enum):
    """Course difficulty levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class CourseTopic(str, Enum):
    """Available course topics."""
    COMPUTER_SCIENCE = "computer-science"
    MATHEMATICS = "mathematics"
    PHYSICS = "physics"
    CHEMISTRY = "chemistry"
    BIOLOGY = "biology"
    PROGRAMMING = "programming"
    DATA_SCIENCE = "data-science"
    MACHINE_LEARNING = "machine-learning"


class Status(str, Enum):
    """Entity status values."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"


# Base Models
class BaseSchema(BaseModel):
    """Base schema with common configurations."""
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Course Models
class CourseCreate(BaseSchema):
    """Schema for creating a course."""
    title: str = Field(..., min_length=1, max_length=255, description="Course title")
    description: Optional[str] = Field(None, max_length=1000, description="Course description")
    topic: CourseTopic = Field(..., description="Course topic")
    level: CourseLevel = Field(default=CourseLevel.BEGINNER, description="Course difficulty level")


class CourseUpdate(BaseSchema):
    """Schema for updating a course."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    topic: Optional[CourseTopic] = None
    level: Optional[CourseLevel] = None


class CourseResponse(BaseSchema):
    """Schema for course responses."""
    id: str = Field(..., description="Course UUID")
    title: str
    description: Optional[str]
    topic: CourseTopic
    level: CourseLevel
    status: Status
    created_at: datetime
    updated_at: datetime


# Module Models
class ModuleCreate(BaseSchema):
    """Schema for creating a module."""
    course_id: str = Field(..., description="Course ID this module belongs to")
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    order_index: int = Field(..., ge=1, description="Module order in course")


class ModuleUpdate(BaseSchema):
    """Schema for updating a module."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    order_index: Optional[int] = Field(None, ge=1)


class ModuleResponse(BaseSchema):
    """Schema for module responses."""
    id: str
    course_id: str
    title: str
    description: Optional[str]
    order_index: int
    status: Status
    created_at: datetime
    updated_at: datetime


# Concept Models
class ConceptCreate(BaseSchema):
    """Schema for creating a concept."""
    module_id: str = Field(..., description="Module ID this concept belongs to")
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    order_index: int = Field(..., ge=1)
    learning_objectives: Optional[List[str]] = Field(default=[], max_items=10)
    prerequisites: Optional[List[str]] = Field(default=[], max_items=10)

    @validator('learning_objectives', 'prerequisites')
    def validate_array_items(cls, v):
        if v is None:
            return []
        for item in v:
            if not item or len(item.strip()) == 0:
                raise ValueError("Array items cannot be empty")
            if len(item) > 100:
                raise ValueError("Array items cannot exceed 100 characters")
        return v


class ConceptUpdate(BaseSchema):
    """Schema for updating a concept."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    order_index: Optional[int] = Field(None, ge=1)
    learning_objectives: Optional[List[str]] = Field(None, max_items=10)
    prerequisites: Optional[List[str]] = Field(None, max_items=10)


class ConceptResponse(BaseSchema):
    """Schema for concept responses."""
    id: str
    module_id: str
    title: str
    description: Optional[str]
    content: str
    order_index: int
    learning_objectives: List[str]
    prerequisites: List[str]
    status: Status
    created_at: datetime
    updated_at: datetime


# Generation Models
class ConceptGenerationRequest(BaseSchema):
    """Schema for concept generation requests."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    learning_objectives: Optional[List[str]] = Field(default=[], max_items=10)
    prerequisites: Optional[List[str]] = Field(default=[], max_items=10)
    module_context: Optional[str] = Field(None, max_length=500)


class ValidationResult(BaseSchema):
    """Schema for content validation results."""
    is_valid: bool
    errors: List[str] = Field(default=[])
    warnings: List[str] = Field(default=[])


class GenerationResponse(BaseSchema):
    """Schema for generation responses."""
    concept_id: str
    content: str
    validation: ValidationResult


# Nested Response Models
class ModuleWithConcepts(BaseSchema):
    """Schema for module with nested concepts."""
    id: str
    title: str
    description: Optional[str]
    order_index: int
    status: Status
    concepts: List[ConceptResponse]
    created_at: datetime
    updated_at: datetime


class CourseWithModules(BaseSchema):
    """Schema for course with nested modules and concepts."""
    id: str
    title: str
    description: Optional[str]
    topic: CourseTopic
    level: CourseLevel
    status: Status
    modules: List[ModuleWithConcepts]
    created_at: datetime
    updated_at: datetime


# Pagination Models
class PaginationParams(BaseSchema):
    """Schema for pagination parameters."""
    page: int = Field(default=1, ge=1, description="Page number")
    size: int = Field(default=20, ge=1, le=100, description="Page size")


class PaginatedCourseResponse(BaseSchema):
    """Schema for paginated course responses."""
    courses: List[CourseResponse]
    total: int
    page: int
    size: int
    pages: int 