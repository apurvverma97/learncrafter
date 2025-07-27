"""
Unit tests for the CoursePublishingAgent.
"""

import json
from unittest.mock import AsyncMock

import pytest

from app.agents.course_publisher import CoursePublishingAgent
from app.models.schemas import (
    ConceptPlan,
    CourseLevel,
    CoursePublishJobRequest,
    CourseTopic,
    ModulePlan,
)


@pytest.fixture
def mock_course_service():
    """Fixture for a mocked CourseService."""
    return AsyncMock()


@pytest.fixture
def mock_db_service():
    """Fixture for a mocked DatabaseService."""
    return AsyncMock()


@pytest.mark.asyncio
async def test_publish_course_fully_automated(mock_course_service, mock_db_service):
    """
    Tests the fully automated course creation workflow.

    It should call the LLM for course, module, and concept plans
    and then save them.
    """
    # Arrange
    agent = CoursePublishingAgent(course_service=mock_course_service, db_service=mock_db_service)
    job_request = CoursePublishJobRequest(topic=CourseTopic.PROGRAMMING, level=CourseLevel.BEGINNER)

    mock_course_service.generate_content.side_effect = [
        json.dumps(
            {
                "course_title": "Intro to Python",
                "course_description": "A beginner course.",
                "module_plans": [{"module_title": "Basics", "module_description": "The basics."}],
            }
        ),
        json.dumps(
            {
                "concepts": [
                    {
                        "concept_title": "Variables",
                        "concept_description": "Storing data.",
                        "learning_objectives": [],
                        "prerequisites": [],
                    }
                ]
            }
        ),
        "<html><body>Generated content for Variables</body></html>",  # Content for concept
    ]
    mock_db_service.create_course.return_value = "course_123"
    mock_db_service.create_module.return_value = "module_123"
    mock_db_service.get_module.return_value = {"title": "Basics", "description": "The basics."}

    # Act - Pass delay=0 for testing
    await agent.publish_course(job_request, llm_delay_seconds=0.0)

    # Assert - Now expecting 3 calls: course planning, concept planning, and concept content
    # generation
    assert mock_course_service.generate_content.call_count == 3
    mock_db_service.create_course.assert_called_once()
    mock_db_service.create_module.assert_called_once()
    mock_db_service.create_concept.assert_called_once()


@pytest.mark.asyncio
async def test_publish_course_fully_manual(mock_course_service, mock_db_service):
    """
    Tests the fully manual course creation workflow.

    It should call the LLM only for concept content generation.
    """
    # Arrange
    agent = CoursePublishingAgent(course_service=mock_course_service, db_service=mock_db_service)
    job_request = CoursePublishJobRequest(
        topic=CourseTopic.PROGRAMMING,
        level=CourseLevel.INTERMEDIATE,
        course_title="Advanced Python",
        course_description="An advanced course.",
        modules=[
            ModulePlan(
                title="Decorators",
                description="All about decorators.",
                concepts=[
                    ConceptPlan(
                        title="Simple Decorators",
                        description="A first look.",
                    )
                ],
            )
        ],
    )

    mock_course_service.generate_content.return_value = (
        "<html><body>Generated content for Simple Decorators</body></html>"
    )
    mock_db_service.create_course.return_value = "course_123"
    mock_db_service.create_module.return_value = "module_123"
    mock_db_service.get_module.return_value = {
        "title": "Decorators",
        "description": "All about decorators.",
    }

    # Act - Pass delay=0 for testing
    await agent.publish_course(job_request, llm_delay_seconds=0.0)

    # Assert - Should call LLM once for concept content generation
    mock_course_service.generate_content.assert_called_once()
    mock_db_service.create_course.assert_called_once()
    mock_db_service.create_module.assert_called_once()
    mock_db_service.create_concept.assert_called_once()


@pytest.mark.asyncio
async def test_publish_course_hybrid_manual_modules(mock_course_service, mock_db_service):
    """
    Tests a hybrid workflow where modules are provided manually.

    Concepts are generated.
    """
    # Arrange
    agent = CoursePublishingAgent(course_service=mock_course_service, db_service=mock_db_service)
    job_request = CoursePublishJobRequest(
        topic=CourseTopic.DATA_SCIENCE,
        level=CourseLevel.ADVANCED,
        course_title="Data Science with Python",
        course_description="A complete guide.",
        modules=[ModulePlan(title="Pandas", description="Data manipulation with Pandas.")],
    )
    mock_course_service.generate_content.side_effect = [
        json.dumps(
            {
                "concepts": [
                    {"concept_title": "DataFrames", "concept_description": "Core of Pandas."}
                ]
            }
        ),
        "<html><body>Generated content for DataFrames</body></html>",  # Content for concept
    ]
    mock_db_service.create_course.return_value = "course_789"
    mock_db_service.create_module.return_value = "module_789"
    mock_db_service.get_module.return_value = {
        "title": "Pandas",
        "description": "Data manipulation with Pandas.",
    }

    # Act
    await agent.publish_course(job_request, llm_delay_seconds=0.0)

    # Assert - Now expecting 2 calls: concept planning and concept content generation
    assert mock_course_service.generate_content.call_count == 2
    mock_db_service.create_course.assert_called_once()
    mock_db_service.create_module.assert_called_once_with(
        {
            "course_id": "course_789",
            "title": "Pandas",
            "description": "Data manipulation with Pandas.",
            "order_index": 1,
        }
    )
    mock_db_service.create_concept.assert_called_once()
