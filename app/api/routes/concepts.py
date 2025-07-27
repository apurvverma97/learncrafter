"""
Concept API routes for LearnCrafter MVP.
Single Responsibility: Concept management and content generation endpoints only.
"""

import logging
from typing import Dict, List

from fastapi import APIRouter, HTTPException, Path

from app.models.schemas import (
    ConceptCreate,
    ConceptGenerationRequest,
    ConceptResponse,
    ConceptUpdate,
    GenerationResponse,
    ValidationResult,
)
from app.services.course_service import CourseService
from app.services.database import db_service
from app.services.prompt_service import PromptService
from app.services.validation_service import ValidationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/concepts", tags=["concepts"])

# Initialize services
course_service = CourseService()
prompt_service = PromptService()
validation_service = ValidationService()


@router.post("/", response_model=ConceptResponse, status_code=201)
async def create_concept(concept: ConceptCreate, workflow_step: str = "concept_generation"):
    """Create a new concept with auto-generated content."""
    try:
        # Generate content using CourseService with workflow step
        prompt = await prompt_service.generate_concept_prompt(concept, workflow_step=workflow_step)
        content = await course_service.generate_content(prompt)

        # Skip validation for now - just log warnings if any
        validation_result = validation_service.validate_content(content)
        if not validation_result.is_valid:
            logger.warning("Content validation warnings: " f"{validation_result.errors}")
        if validation_result.warnings:
            logger.warning("Content validation warnings: " f"{validation_result.warnings}")

        # Prepare concept data
        concept_data = concept.model_dump()
        concept_data["content"] = content

        # Store concept
        concept_id = await db_service.create_concept(concept_data)
        concept_data = await db_service.get_concept(concept_id)

        return ConceptResponse(**concept_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create concept: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{concept_id}", response_model=ConceptResponse)
async def get_concept(concept_id: str = Path(..., description="Concept ID")):
    """Get a specific concept by ID."""
    try:
        concept = await db_service.get_concept(concept_id)
        if not concept:
            raise HTTPException(status_code=404, detail="Concept not found")
        logger.info(f"Concept from DB: {concept}")
        return ConceptResponse(**concept)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get concept {concept_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{concept_id}", response_model=ConceptResponse)
async def update_concept(
    concept_id: str = Path(..., description="Concept ID"),
    concept_update: ConceptUpdate = None,
):
    """Update a concept (metadata only, not content)."""
    try:
        # Check if concept exists
        existing_concept = await db_service.get_concept(concept_id)
        if not existing_concept:
            raise HTTPException(status_code=404, detail="Concept not found")

        # Prepare update data (exclude content)
        update_data = concept_update.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="No update data provided")

        # Remove content from update data
        update_data.pop("content", None)

        # Update concept
        success = await db_service.update_concept(concept_id, update_data)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update concept")

        # Return updated concept
        updated_concept = await db_service.get_concept(concept_id)
        return ConceptResponse(**updated_concept)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update concept {concept_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{concept_id}")
async def delete_concept(concept_id: str = Path(..., description="Concept ID")):
    """Delete a concept."""
    try:
        # Check if concept exists
        existing_concept = await db_service.get_concept(concept_id)
        if not existing_concept:
            raise HTTPException(status_code=404, detail="Concept not found")

        # Delete concept
        success = await db_service.delete_concept(concept_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete concept")

        return {"message": "Concept deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete concept {concept_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate", response_model=GenerationResponse)
async def generate_concept_content(
    generation_request: ConceptGenerationRequest,
    workflow_step: str = "concept_generation",
):
    """Generate content for a concept without storing it."""
    try:
        # Generate prompt with workflow step
        prompt = await prompt_service.generate_concept_prompt(
            generation_request, workflow_step=workflow_step
        )

        # Generate content
        content = await course_service.generate_content(prompt)

        # Validate content
        validation_result = validation_service.validate_content(content)

        return GenerationResponse(
            concept_id="",  # Not stored
            content=content,
            validation=validation_result,
        )
    except Exception as e:
        logger.error(f"Failed to generate concept content: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{concept_id}/regenerate", response_model=ConceptResponse)
async def regenerate_concept_content(
    concept_id: str = Path(..., description="Concept ID"),
    feedback: str = None,
    workflow_step: str = "concept_regeneration",
):
    """Regenerate content for an existing concept."""
    try:
        # Get existing concept
        existing_concept = await db_service.get_concept(concept_id)
        if not existing_concept:
            raise HTTPException(status_code=404, detail="Concept not found")

        # Generate regeneration prompt with workflow step
        prompt = await prompt_service.generate_regeneration_prompt(
            existing_concept["title"],
            existing_concept["content"],
            feedback,
            workflow_step=workflow_step,
        )

        # Generate new content
        new_content = await course_service.generate_content(prompt)

        # Skip validation for now - just log warnings if any
        validation_result = validation_service.validate_content(new_content)
        if not validation_result.is_valid:
            logger.warning("Content validation warnings: " f"{validation_result.errors}")
        if validation_result.warnings:
            logger.warning("Content validation warnings: " f"{validation_result.warnings}")

        # Update concept with new content
        update_data = {"content": new_content}
        success = await db_service.update_concept(concept_id, update_data)
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to update concept content",
            )

        # Return updated concept
        updated_concept = await db_service.get_concept(concept_id)
        return ConceptResponse(**updated_concept)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to regenerate concept content {concept_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{concept_id}/validate", response_model=ValidationResult)
async def validate_concept_content(
    concept_id: str = Path(..., description="Concept ID"),
    workflow_step: str = "content_validation",
):
    """Validate HTML content of an existing concept."""
    try:
        # Get existing concept
        existing_concept = await db_service.get_concept(concept_id)
        if not existing_concept:
            raise HTTPException(status_code=404, detail="Concept not found")

        # Validate content
        validation_result = validation_service.validate_content(existing_concept["content"])

        # Generate validation prompt with workflow step
        prompt = await prompt_service.generate_validation_prompt(
            existing_concept["content"], workflow_step=workflow_step
        )

        # Generate validation feedback using LLM
        validation_feedback = await course_service.generate_content(prompt)

        # Add LLM feedback to validation result
        validation_result.llm_feedback = validation_feedback

        return validation_result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to validate concept content {concept_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/prompts/valid-ids", response_model=List[str])
async def get_valid_prompt_ids():
    """Get list of valid prompt IDs from the database."""
    try:
        valid_prompt_ids = await prompt_service.get_valid_prompt_ids()
        return valid_prompt_ids
    except Exception as e:
        logger.error(f"Failed to get valid prompt IDs: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch valid prompt IDs")


@router.get("/prompts/workflow-steps", response_model=Dict[str, str])
async def get_workflow_step_mapping():
    """Get mapping of workflow steps to prompt IDs."""
    try:
        return {
            "concept_regeneration": "concept_regeneration",
            "content_validation": "content_validation",
            "concept_generation": "concept_generation",
        }
    except Exception as e:
        logger.error(f"Failed to get workflow step mapping: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch workflow step mapping")
