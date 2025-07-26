"""
Module API routes for LearnCrafter MVP.
Single Responsibility: Module management endpoints only.
"""
from fastapi import APIRouter, HTTPException, Path
from typing import List
from app.models.schemas import (
    ModuleCreate, ModuleUpdate, ModuleResponse, ModuleWithConcepts
)
from app.services.database import db_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/modules", tags=["modules"])


@router.post("/", response_model=ModuleResponse, status_code=201)
async def create_module(module: ModuleCreate):
    """Create a new module."""
    try:
        module_data = module.dict()
        module_id = await db_service.create_module(module_data)
        module_data = await db_service.get_module(module_id)
        return ModuleResponse(**module_data)
    except Exception as e:
        logger.error(f"Failed to create module: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{module_id}", response_model=ModuleResponse)
async def get_module(module_id: str = Path(..., description="Module ID")):
    """Get a specific module by ID."""
    try:
        module = await db_service.get_module(module_id)
        if not module:
            raise HTTPException(status_code=404, detail="Module not found")
        logger.info(f"Module from DB: {module}")
        return ModuleResponse(**module)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get module {module_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{module_id}/concepts", response_model=ModuleWithConcepts)
async def get_module_with_concepts(module_id: str = Path(..., description="Module ID")):
    """Get module with all its concepts."""
    try:
        # Get module
        module = await db_service.get_module(module_id)
        if not module:
            raise HTTPException(status_code=404, detail="Module not found")
        logger.info(f"Module from DB: {module}")
        
        # Get concepts for this module
        from app.models.schemas import ConceptResponse
        concepts = await db_service.get_concepts_by_module(module_id)
        logger.info(f"Concepts for module {module_id} from DB: {concepts}")
        concept_responses = [ConceptResponse(**concept) for concept in concepts]
        
        # Create module with concepts response
        module['concepts'] = concepts
        return ModuleWithConcepts(**module)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get module with concepts {module_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{module_id}", response_model=ModuleResponse)
async def update_module(
    module_id: str = Path(..., description="Module ID"),
    module_update: ModuleUpdate = None
):
    """Update a module."""
    try:
        # Check if module exists
        existing_module = await db_service.get_module(module_id)
        if not existing_module:
            raise HTTPException(status_code=404, detail="Module not found")
        
        # Prepare update data
        update_data = module_update.dict(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="No update data provided")
        
        # Update module
        success = await db_service.update_module(module_id, update_data)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update module")
        
        # Return updated module
        updated_module = await db_service.get_module(module_id)
        return ModuleResponse(**updated_module)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update module {module_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{module_id}")
async def delete_module(module_id: str = Path(..., description="Module ID")):
    """Delete a module (cascades to concepts)."""
    try:
        # Check if module exists
        existing_module = await db_service.get_module(module_id)
        if not existing_module:
            raise HTTPException(status_code=404, detail="Module not found")
        
        # Delete module
        success = await db_service.delete_module(module_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete module")
        
        return {"message": "Module deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete module {module_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 