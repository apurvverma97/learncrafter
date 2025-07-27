"""
Unit tests for the DatabaseService.
"""

from unittest.mock import Mock

import pytest

from app.services.database import DatabaseService


@pytest.fixture
def mock_dao():
    """Fixture for a mocked SupabaseDAO."""
    return Mock()


@pytest.mark.asyncio
async def test_create_course(mock_dao):
    """Tests the create_course method."""
    # Arrange
    db_service = DatabaseService(dao=mock_dao)
    course_data = {"title": "Test Course", "description": "A test course."}
    mock_dao.insert.return_value = {"id": "123"}

    # Act
    course_id = await db_service.create_course(course_data)

    # Assert
    mock_dao.insert.assert_called_once_with("courses", course_data)
    assert course_id == "123"
