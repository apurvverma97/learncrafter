"""
Validation service for LearnCrafter MVP.
Single Responsibility: Content validation and security only.
"""

import logging
import re
from typing import List, Tuple

from bs4 import BeautifulSoup

from app.core.config import settings
from app.models.schemas import ValidationResult

logger = logging.getLogger(__name__)


class ValidationService:
    """Service for content validation and security checks."""

    def __init__(self):
        """Initialize validation service."""
        # Only block truly dangerous patterns
        self.dangerous_js_patterns = [
            r"eval\s*\(",
            r"document\.write",
            r"window\.open",
            r"fetch\s*\(",
            r"XMLHttpRequest",
            r"localStorage",
            r"sessionStorage",
            r"indexedDB",
            r"postMessage",
            r"importScripts",
            r"Function\s*\(",
            r"constructor\s*\(",
            r"__proto__",
            r"prototype",
        ]

    def validate_content(self, content: str) -> ValidationResult:
        """
        Simplified content validation for educational content.

        Args:
            content: HTML content to validate

        Returns:
            ValidationResult with validation status and issues
        """
        errors = []
        warnings = []

        try:
            # Basic content checks
            if not content or len(content.strip()) == 0:
                errors.append("Content is empty")
                return ValidationResult(is_valid=False, errors=errors, warnings=warnings)

            # Content length check
            if len(content) > settings.max_content_length:
                errors.append(
                    "Content exceeds maximum length of " f"{settings.max_content_length} characters"
                )

            # Parse HTML to check if it's valid
            try:
                soup = BeautifulSoup(content, "html.parser")
            except Exception as e:
                errors.append(f"Invalid HTML structure: {str(e)}")
                return ValidationResult(is_valid=False, errors=errors, warnings=warnings)

            # Check for basic HTML structure
            if not soup.find("html"):
                warnings.append("Missing <html> tag")

            if not soup.find("head"):
                warnings.append("Missing <head> tag")

            if not soup.find("body"):
                warnings.append("Missing <body> tag")

            # Check for truly dangerous content only
            security_errors, security_warnings = self._validate_security(soup)
            errors.extend(security_errors)
            warnings.extend(security_warnings)

            # Check for dangerous JavaScript patterns
            js_errors, js_warnings = self._validate_javascript(soup)
            errors.extend(js_errors)
            warnings.extend(js_warnings)

            is_valid = len(errors) == 0

            return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings)

        except Exception as e:
            logger.error(f"Validation error: {e}")
            errors.append(f"Validation failed: {str(e)}")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)

    def _validate_security(self, soup: BeautifulSoup) -> Tuple[List[str], List[str]]:
        """Validate only critical security aspects."""
        errors = []
        warnings = []

        # Only block iframe, object, embed tags as they can be dangerous
        dangerous_tags = soup.find_all(["iframe", "object", "embed"])
        if dangerous_tags:
            errors.append("Dangerous tags found: " f"{[tag.name for tag in dangerous_tags]}")

        # Check for external scripts from untrusted sources
        scripts = soup.find_all("script", src=True)
        for script in scripts:
            src = script.get("src", "")
            if src and not self._is_allowed_external_resource(src):
                warnings.append(f"External script from untrusted source: {src}")

        return errors, warnings

    def _validate_javascript(self, soup: BeautifulSoup) -> Tuple[List[str], List[str]]:
        """Validate JavaScript content for dangerous patterns only."""
        errors = []
        warnings = []

        scripts = soup.find_all("script")
        for script in scripts:
            js_content = script.string or ""

            # Check for dangerous patterns
            for pattern in self.dangerous_js_patterns:
                if re.search(pattern, js_content, re.IGNORECASE):
                    errors.append(f"Dangerous JavaScript pattern detected: {pattern}")

            # Check for external scripts
            if script.get("src"):
                src = script.get("src")
                if not self._is_allowed_external_resource(src):
                    warnings.append(f"External script from untrusted source: {src}")

        return errors, warnings

    def _is_allowed_external_resource(self, url: str) -> bool:
        """Check if external resource URL is allowed."""
        if not url:
            return True

        # Allow CDN resources
        allowed_domains = [
            "cdn.jsdelivr.net",
            "unpkg.com",
            "cdnjs.cloudflare.com",
            "fonts.googleapis.com",
            "fonts.gstatic.com",
            "code.jquery.com",
            "cdn.jsdelivr.net",
        ]

        for domain in allowed_domains:
            if domain in url:
                return True

        # Allow relative URLs
        if url.startswith("/") or url.startswith("./") or url.startswith("../"):
            return True

        # Allow protocol-relative URLs
        if url.startswith("//"):
            return True

        return False

    def sanitize_content(self, content: str) -> str:
        """
        Sanitize content by removing only dangerous elements.

        Args:
            content: Raw content to sanitize

        Returns:
            Sanitized content
        """
        try:
            soup = BeautifulSoup(content, "html.parser")

            # Remove only dangerous tags
            dangerous_tags = soup.find_all(["iframe", "object", "embed"])
            for tag in dangerous_tags:
                tag.decompose()

            return str(soup)

        except Exception as e:
            logger.error(f"Sanitization error: {e}")
            return content
