"""
Unit tests for the PromptService.
"""

from unittest.mock import AsyncMock, patch

import pytest

from app.services.prompt_service import PromptService


@pytest.fixture
def mock_db_service():
    """Fixture for a mocked DatabaseService."""
    db_service = AsyncMock()
    db_service.get_prompt.return_value = {"template": "Hello, {name}!"}
    return db_service


@pytest.mark.asyncio
async def test_get_prompt_template(mock_db_service):
    """
    Tests that the get_prompt_template method fetches a template from the db.
    """
    # Arrange
    with patch("app.services.prompt_service.db_service", mock_db_service):
        prompt_service = PromptService()

        # Act
        template = await prompt_service.get_prompt_template("test_prompt")

        # Assert
        mock_db_service.get_prompt.assert_called_once_with("test_prompt")
        assert template == "Hello, {name}!"


def test_format_prompt():
    """Tests the _format_prompt method."""
    # Arrange
    prompt_service = PromptService()
    template = "This is a {adjective} test for {user}."
    variables = {"adjective": "simple", "user": "pytest"}

    # Act
    formatted_prompt = prompt_service._format_prompt(template, variables)

    # Assert
    assert formatted_prompt == "This is a simple test for pytest."


@pytest.mark.asyncio
async def test_get_prompt(mock_db_service):
    """Tests the main get_prompt method."""
    # Arrange
    with patch("app.services.prompt_service.db_service", mock_db_service):
        prompt_service = PromptService()
        variables = {"name": "World"}

        # Act
        prompt = await prompt_service.get_prompt("test_prompt", variables)

        # Assert
        assert prompt == "Hello, World!"
