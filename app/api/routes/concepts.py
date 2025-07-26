"""
Concept API routes for LearnCrafter MVP.
Single Responsibility: Concept management and content generation endpoints only.
"""
from fastapi import APIRouter, HTTPException, Path
from typing import List
from app.models.schemas import (
    ConceptCreate, ConceptUpdate, ConceptResponse, ConceptGenerationRequest,
    GenerationResponse, ValidationResult
)
from app.services.database import db_service
from app.services.llm_service import LLMService
from app.services.prompt_service import PromptService
from app.services.validation_service import ValidationService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/concepts", tags=["concepts"])

# Initialize services
llm_service = LLMService()
prompt_service = PromptService()
validation_service = ValidationService()


@router.post("/", response_model=ConceptResponse, status_code=201)
async def create_concept(concept: ConceptCreate):
    """Create a new concept with auto-generated content."""
    try:
        # Generate content using LLM
        prompt = prompt_service.generate_concept_prompt(concept)
        content = await llm_service.generate_content(prompt)
        
        # Skip validation for now - just log warnings if any
        validation_result = validation_service.validate_content(content)
        if not validation_result.is_valid:
            logger.warning(f"Content validation warnings: {validation_result.errors}")
        if validation_result.warnings:
            logger.warning(f"Content validation warnings: {validation_result.warnings}")
        
        # Prepare concept data
        concept_data = concept.dict()
        concept_data['content'] = content
        
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
    concept_update: ConceptUpdate = None
):
    """Update a concept (metadata only, not content)."""
    try:
        # Check if concept exists
        existing_concept = await db_service.get_concept(concept_id)
        if not existing_concept:
            raise HTTPException(status_code=404, detail="Concept not found")
        
        # Prepare update data (exclude content)
        update_data = concept_update.dict(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="No update data provided")
        
        # Remove content from update data (content updates use regenerate endpoint)
        update_data.pop('content', None)
        
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
async def generate_concept_content(generation_request: ConceptGenerationRequest):
    """Generate content for a concept without storing it."""
    try:
        # Generate prompt
        prompt = prompt_service.generate_concept_prompt(generation_request)
        
        # Generate content
        content = await llm_service.generate_content(prompt)
        
        # Validate content
        validation_result = validation_service.validate_content(content)
        
        return GenerationResponse(
            concept_id="",  # Not stored
            content=content,
            validation=validation_result
        )
    except Exception as e:
        logger.error(f"Failed to generate concept content: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{concept_id}/regenerate", response_model=ConceptResponse)
async def regenerate_concept_content(
    concept_id: str = Path(..., description="Concept ID"),
    feedback: str = None
):
    """Regenerate content for an existing concept."""
    try:
        # Get existing concept
        existing_concept = await db_service.get_concept(concept_id)
        if not existing_concept:
            raise HTTPException(status_code=404, detail="Concept not found")
        
        # Generate regeneration prompt
        prompt = prompt_service.generate_regeneration_prompt(
            existing_concept['title'],
            existing_concept['content'],
            feedback
        )
        
        # Generate new content
        new_content = await llm_service.generate_content(prompt)
        
        # Skip validation for now - just log warnings if any
        validation_result = validation_service.validate_content(new_content)
        if not validation_result.is_valid:
            logger.warning(f"Content validation warnings: {validation_result.errors}")
        if validation_result.warnings:
            logger.warning(f"Content validation warnings: {validation_result.warnings}")
        
        # Update concept with new content
        update_data = {'content': new_content}
        success = await db_service.update_concept(concept_id, update_data)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update concept content")
        
        # Return updated concept
        updated_concept = await db_service.get_concept(concept_id)
        return ConceptResponse(**updated_concept)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to regenerate concept content {concept_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{concept_id}/validate", response_model=ValidationResult)
async def validate_concept_content(concept_id: str = Path(..., description="Concept ID")):
    """Validate content of an existing concept."""
    try:
        # Get concept
        concept = await db_service.get_concept(concept_id)
        if not concept:
            raise HTTPException(status_code=404, detail="Concept not found")
        
        # Validate content
        validation_result = validation_service.validate_content(concept['content'])
        
        return validation_result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to validate concept content {concept_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 