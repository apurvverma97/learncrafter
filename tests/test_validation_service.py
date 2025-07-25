"""
Tests for ValidationService.
Demonstrates testing approach following SOLID principles.
"""
import pytest
from app.services.validation_service import ValidationService
from app.models.schemas import ValidationResult


class TestValidationService:
    """Test cases for ValidationService."""
    
    @pytest.fixture
    def validation_service(self):
        """Create ValidationService instance for testing."""
        return ValidationService()
    
    def test_validate_empty_content(self, validation_service):
        """Test validation of empty content."""
        result = validation_service.validate_content("")
        assert not result.is_valid
        assert "Content is empty" in result.errors
    
    def test_validate_valid_html(self, validation_service):
        """Test validation of valid HTML content."""
        valid_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test</title>
        </head>
        <body>
            <h1>Hello World</h1>
            <p>This is a test.</p>
        </body>
        </html>
        """
        result = validation_service.validate_content(valid_html)
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_validate_dangerous_tags(self, validation_service):
        """Test validation rejects dangerous HTML tags."""
        dangerous_html = """
        <html>
        <body>
            <iframe src="malicious.com"></iframe>
            <object data="bad.com"></object>
        </body>
        </html>
        """
        result = validation_service.validate_content(dangerous_html)
        assert not result.is_valid
        assert "Dangerous tags found" in result.errors[0]
    
    def test_validate_dangerous_javascript(self, validation_service):
        """Test validation rejects dangerous JavaScript."""
        dangerous_js = """
        <html>
        <body>
            <script>
                eval("alert('dangerous')");
                document.write("bad");
            </script>
        </body>
        </html>
        """
        result = validation_service.validate_content(dangerous_js)
        assert not result.is_valid
        assert any("Dangerous JavaScript pattern" in error for error in result.errors)
    
    def test_validate_external_resources(self, validation_service):
        """Test validation of external resources."""
        external_resources = """
        <html>
        <head>
            <script src="https://malicious.com/script.js"></script>
            <link rel="stylesheet" href="https://bad.com/style.css">
        </head>
        <body>
            <img src="https://evil.com/image.jpg">
        </body>
        </html>
        """
        result = validation_service.validate_content(external_resources)
        assert not result.is_valid
        assert any("Disallowed external" in error for error in result.errors)
    
    def test_validate_allowed_cdn_resources(self, validation_service):
        """Test validation allows CDN resources."""
        cdn_resources = """
        <html>
        <head>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <link href="https://fonts.googleapis.com/css2?family=Roboto" rel="stylesheet">
        </head>
        <body>
            <h1>Test</h1>
        </body>
        </html>
        """
        result = validation_service.validate_content(cdn_resources)
        assert result.is_valid
        assert len(result.errors) == 0
    
    def test_sanitize_content(self, validation_service):
        """Test content sanitization."""
        dangerous_content = """
        <html>
        <body>
            <iframe src="malicious.com"></iframe>
            <script>eval("bad");</script>
            <a href="javascript:alert('xss')">Click me</a>
        </body>
        </html>
        """
        sanitized = validation_service.sanitize_content(dangerous_content)
        
        # Check that dangerous elements are removed
        assert "<iframe" not in sanitized
        assert "javascript:alert" not in sanitized
        
        # Check that safe elements remain
        assert "<html>" in sanitized
        assert "<body>" in sanitized
        assert "<a" in sanitized
    
    def test_validate_content_length(self, validation_service):
        """Test content length validation."""
        # Create content exceeding max length
        long_content = "<html><body>" + "x" * 60000 + "</body></html>"
        result = validation_service.validate_content(long_content)
        assert not result.is_valid
        assert "exceeds maximum length" in result.errors[0]
    
    def test_validate_css_dangerous_patterns(self, validation_service):
        """Test validation of dangerous CSS patterns."""
        dangerous_css = """
        <html>
        <head>
            <style>
                body { behavior: url(malicious.htc); }
                div { background: expression(alert('xss')); }
            </style>
        </head>
        <body>
            <div>Test</div>
        </body>
        </html>
        """
        result = validation_service.validate_content(dangerous_css)
        assert not result.is_valid
        assert any("Dangerous CSS pattern" in error for error in result.errors)
    
    def test_validate_inline_event_handlers(self, validation_service):
        """Test validation of inline event handlers."""
        inline_events = """
        <html>
        <body>
            <button onclick="alert('test')">Click</button>
            <div onmouseover="console.log('test')">Hover</div>
        </body>
        </html>
        """
        result = validation_service.validate_content(inline_events)
        # Should generate warnings but not errors
        assert result.is_valid
        assert any("Inline event handlers" in warning for warning in result.warnings) 