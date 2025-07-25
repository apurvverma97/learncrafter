"""
Main FastAPI application for LearnCrafter MVP.
Dependency Inversion: Depends on abstractions, not concrete implementations.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.api.routes import courses, modules, concepts, prompts
from app.models.schemas import CourseLevel, CourseTopic

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting LearnCrafter MVP application...")
    yield
    # Shutdown
    logger.info("Shutting down LearnCrafter MVP application...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Interactive Content Generator System MVP",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version
    }


# Utility endpoints
@app.get("/topics")
async def get_topics():
    """Get available course topics."""
    return {
        "topics": [
            {"value": topic.value, "label": topic.value.replace("-", " ").title()}
            for topic in CourseTopic
        ]
    }


@app.get("/levels")
async def get_levels():
    """Get available course levels."""
    return {
        "levels": [
            {"value": level.value, "label": level.value.title()}
            for level in CourseLevel
        ]
    }


# Include API routes
app.include_router(courses.router, prefix=settings.api_prefix)
app.include_router(modules.router, prefix=settings.api_prefix)
app.include_router(concepts.router, prefix=settings.api_prefix)
app.include_router(prompts.router, prefix=settings.api_prefix)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to LearnCrafter MVP",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    ) 