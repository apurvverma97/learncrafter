"""
Prompt management API routes for LearnCrafter MVP.
"""

import logging
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Path

from app.models.schemas import PromptCreate, PromptResponse, PromptUpdate
from app.services.database import DatabaseService, db_service, get_db_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/prompts", tags=["prompts"])


@router.post("/", response_model=PromptResponse, status_code=201)
async def create_prompt(
    prompt: PromptCreate, db: Annotated[DatabaseService, Depends(get_db_service)]
):
    """Create a new prompt."""
    try:
        existing_prompt = await db.get_prompt(prompt.prompt_id)
        if existing_prompt:
            raise HTTPException(status_code=409, detail="Prompt already exists")
        prompt_data = prompt.model_dump()
        new_prompt = await db.create_prompt(prompt_data)
        return PromptResponse(**new_prompt)
    except Exception as e:
        logger.error(f"Failed to create prompt: {e}")
        raise HTTPException(status_code=500, detail="Failed to create prompt")


@router.get("/", response_model=List[PromptResponse])
async def list_prompts():
    """List all available prompts from the database."""
    try:
        prompts = await db_service.list_prompts()
        return [PromptResponse(**p) for p in prompts]
    except Exception as e:
        logger.error(f"Failed to list prompts: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve prompts.")


@router.get("/{prompt_id}", response_model=PromptResponse)
async def get_prompt(
    prompt_id: str = Path(..., description="The string ID of the prompt to retrieve")
):
    """Get a specific prompt by its string ID."""
    try:
        prompt = await db_service.get_prompt(prompt_id)
        if not prompt:
            raise HTTPException(status_code=404, detail="Prompt not found")
        return PromptResponse(**prompt)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get prompt {prompt_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve prompt {prompt_id}.",
        )


@router.put("/{prompt_id}", response_model=PromptResponse)
async def update_prompt(
    prompt_update: PromptUpdate,
    prompt_id: str = Path(..., description="The string ID of the prompt to update"),
):
    """Update an existing prompt."""
    try:
        update_data = prompt_update.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="No update data provided")

        success = await db_service.update_prompt(prompt_id, update_data)
        if not success:
            raise HTTPException(status_code=404, detail="Prompt not found or failed to update")

        updated_prompt = await db_service.get_prompt(prompt_id)
        return PromptResponse(**updated_prompt)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update prompt {prompt_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update prompt {prompt_id}.")


@router.delete("/{prompt_id}", status_code=204)
async def delete_prompt(
    prompt_id: str = Path(..., description="The string ID of the prompt to delete")
):
    """Delete a prompt from the database."""
    try:
        success = await db_service.delete_prompt(prompt_id)
        if not success:
            raise HTTPException(status_code=404, detail="Prompt not found")
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete prompt {prompt_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete prompt {prompt_id}.")
