"""
Unit tests for the ValidationService.
"""

from unittest.mock import patch

import pytest

from app.services.validation_service import ValidationService


@pytest.fixture
def validation_service():
    """Fixture for a ValidationService instance."""
    return ValidationService()


def test_validate_content_empty(validation_service):
    """Tests that empty content is invalid."""
    result = validation_service.validate_content("")
    assert not result.is_valid
    assert "Content is empty" in result.errors


def test_validate_content_valid(validation_service):
    """Tests that valid, safe content passes validation."""
    content = "<html><head><title>Test</title></head>" "<body><p>Hello</p></body></html>"
    result = validation_service.validate_content(content)
    assert result.is_valid


def test_validate_content_length_exceeded(validation_service):
    """Tests that content exceeding the max length is invalid."""
    with patch("app.services.validation_service.settings") as mock_settings:
        mock_settings.max_content_length = 100
        long_content = "a" * 101
        result = validation_service.validate_content(long_content)
        assert not result.is_valid
        assert "Content exceeds maximum length" in result.errors[0]


def test_validate_dangerous_tags(validation_service):
    """Tests that content with dangerous tags is invalid."""
    content = "<html><body><iframe></iframe></body></html>"
    result = validation_service.validate_content(content)
    assert not result.is_valid
    assert "Dangerous tags found" in result.errors[0]


def test_validate_dangerous_js_patterns(validation_service):
    """Tests that content with dangerous JS patterns is invalid."""
    content = "<html><body><script>eval('danger');</script></body></html>"
    result = validation_service.validate_content(content)
    assert not result.is_valid
    assert "Dangerous JavaScript pattern detected" in result.errors[0]


def test_validate_untrusted_external_script(validation_service):
    """Tests that a warning is generated for untrusted external scripts."""
    content = (
        '<html><head><script src="http://evil.com/script.js">'
        "</script></head><body></body></html>"
    )
    result = validation_service.validate_content(content)
    assert "External script from untrusted source" in result.warnings[0]


def test_sanitize_content(validation_service):
    """Tests that dangerous tags are removed by the sanitize_content method."""
    content = "<html><body><p>Safe</p><iframe src='danger'>" "</iframe></body></html>"
    sanitized_content = validation_service.sanitize_content(content)
    assert "<p>Safe</p>" in sanitized_content
    assert "<iframe>" not in sanitized_content
