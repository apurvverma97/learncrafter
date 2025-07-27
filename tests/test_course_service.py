"""
Unit tests for the CourseService.
"""

from unittest.mock import AsyncMock, patch

import pytest

from app.services.course_service import (
    CourseService,
    GeminiProvider,
    OpenAIProvider,
)


@pytest.fixture
def mock_openai_provider():
    """Fixture for a mocked OpenAIProvider."""
    return AsyncMock(spec=OpenAIProvider)


@pytest.fixture
def mock_gemini_provider():
    """Fixture for a mocked GeminiProvider."""
    return AsyncMock(spec=GeminiProvider)


@patch("app.services.course_service.settings")
def test_course_service_initialization_openai(mock_settings, mock_openai_provider):
    """Tests that CourseService initializes the correct provider (OpenAI)."""
    # Arrange
    mock_settings.llm_provider = "openai"
    with patch(
        "app.services.course_service.OpenAIProvider",
        return_value=mock_openai_provider,
    ) as mock_provider_class:
        # Act
        service = CourseService()
        # Assert
        mock_provider_class.assert_called_once()
        assert service.provider == mock_openai_provider


@patch("app.services.course_service.settings")
def test_course_service_initialization_gemini(mock_settings, mock_gemini_provider):
    """Tests that CourseService initializes the correct provider (Gemini)."""
    # Arrange
    mock_settings.llm_provider = "gemini"
    with patch(
        "app.services.course_service.GeminiProvider",
        return_value=mock_gemini_provider,
    ) as mock_provider_class:
        # Act
        service = CourseService()
        # Assert
        mock_provider_class.assert_called_once()
        assert service.provider == mock_gemini_provider


@pytest.mark.asyncio
async def test_generate_content(mock_openai_provider):
    """Tests the generate_content method."""
    # Arrange
    with patch("app.services.course_service.settings") as mock_settings:
        mock_settings.llm_provider = "openai"
        with patch(
            "app.services.course_service.OpenAIProvider",
            return_value=mock_openai_provider,
        ):
            service = CourseService()
            prompt = "Test prompt"
            expected_content = "Test content"
            mock_openai_provider.generate_content.return_value = expected_content

            # Act
            content = await service.generate_content(prompt)

            # Assert
            mock_openai_provider.generate_content.assert_called_once_with(prompt)
            assert content == expected_content
