#!/usr/bin/env python3
"""
LearnCrafter MVP Setup Script
Helps configure the environment and test the application.
"""

from setuptools import find_packages, setup

setup(
    name="learncrafter",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "pydantic",
        "pydantic-settings",
        "google-generativeai",
        "anthropic",
        "supabase",
        "python-dotenv",
        "jinja2",
        "beautifulsoup4",
        "lxml",
        "pytest",
        "httpx>=0.24.0,<0.25.0",
    ],
    entry_points={
        "console_scripts": [
            "learncrafter=app.main:main",
        ],
    },
)
