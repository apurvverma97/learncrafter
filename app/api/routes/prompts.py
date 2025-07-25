"""
Prompt management API routes for LearnCrafter MVP.
Single Responsibility: Prompt management endpoints only.
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.services.prompt_service import PromptService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/prompts", tags=["prompts"])

# Initialize prompt service
prompt_service = PromptService()


@router.get("/")
async def list_prompts() -> Dict[str, Any]:
    """List all available prompts and their configurations."""
    try:
        prompts = prompt_service.list_available_prompts()
        return {
            "prompts": prompts,
            "total": len(prompts)
        }
    except Exception as e:
        logger.error(f"Failed to list prompts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{prompt_id}")
async def get_prompt_info(prompt_id: str) -> Dict[str, Any]:
    """Get information about a specific prompt."""
    try:
        prompts = prompt_service.list_available_prompts()
        if prompt_id not in prompts:
            raise HTTPException(status_code=404, detail="Prompt not found")
        
        return {
            "prompt_id": prompt_id,
            "info": prompts[prompt_id]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get prompt info for {prompt_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reload")
async def reload_prompts() -> Dict[str, str]:
    """Reload prompt configuration from files."""
    try:
        success = prompt_service.reload_config()
        if success:
            return {"message": "Prompt configuration reloaded successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to reload prompt configuration")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to reload prompts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test/{prompt_id}")
async def test_prompt(prompt_id: str, variables: Dict[str, Any]) -> Dict[str, Any]:
    """Test a prompt with provided variables."""
    try:
        prompt = prompt_service.get_prompt(prompt_id, variables)
        if not prompt:
            raise HTTPException(status_code=404, detail="Prompt not found or failed to load")
        
        return {
            "prompt_id": prompt_id,
            "variables": variables,
            "formatted_prompt": prompt,
            "length": len(prompt)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to test prompt {prompt_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 