"""
Configuration management for LearnCrafter MVP.
Single Responsibility: Application configuration only.
"""

from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Application
    app_name: str = "LearnCrafter MVP"
    app_version: str = "1.0.0"
    debug: bool = False

    # API
    api_prefix: str = "/api/v1"
    cors_origins: List[str] = ["*"]

    # Database (Supabase)
    supabase_url: str
    supabase_key: str

    # LLM Provider
    llm_provider: str = "gemini"  # "openai" or "gemini"
    llm_delay_seconds: float = 45.0  # Delay between LLM calls for rate limiting

    # LLM (Google Gemini)
    gemini_api_key: str
    gemini_model: str = "gemini-1.5-flash"
    gemini_max_tokens: int = 4000
    gemini_temperature: float = 0.7

    # LLM (OpenAI)
    openai_api_key: str = "sk-proj-..."
    openai_model: str = "gpt-4"
    openai_max_tokens: int = 4000
    openai_temperature: float = 0.7

    # Content Validation
    max_content_length: int = 50000
    allowed_html_tags: List[str] = [
        # Basic structure
        "html",
        "head",
        "body",
        "title",
        "meta",
        "link",
        # Content elements
        "div",
        "p",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "span",
        "strong",
        "em",
        "code",
        "pre",
        "br",
        "hr",
        # Lists
        "ul",
        "ol",
        "li",
        "dl",
        "dt",
        "dd",
        # Interactive elements
        "button",
        "input",
        "label",
        "select",
        "option",
        "textarea",
        "form",
        "fieldset",
        "legend",
        # Media and canvas
        "canvas",
        "img",
        "video",
        "audio",
        # Scripts and styles
        "script",
        "style",
        # Semantic elements
        "header",
        "footer",
        "nav",
        "main",
        "section",
        "article",
        "aside",
        "figure",
        "figcaption",
        "details",
        "summary",
        # Tables
        "table",
        "thead",
        "tbody",
        "tfoot",
        "tr",
        "td",
        "th",
        # Links
        "a",
    ]

    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100

    class Config:
        env_file = ".env"
        case_sensitive = False
        env_prefix = ""


# Global settings instance
settings = Settings()
