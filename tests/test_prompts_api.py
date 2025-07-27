import uuid
from datetime import datetime

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_prompt(client: AsyncClient, mocker):
    mocker.patch("app.services.database.DatabaseService.get_prompt", return_value=None)
    mocker.patch(
        "app.services.database.DatabaseService.create_prompt",
        return_value={
            "id": str(uuid.uuid4()),
            "prompt_id": "test-prompt",
            "name": "Test Prompt",
            "description": "A test prompt.",
            "template": "Test template",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        },
    )
    response = await client.post(
        "/api/v1/prompts/",
        json={
            "prompt_id": "test-prompt",
            "name": "Test Prompt",
            "description": "A test prompt.",
            "template": "Test template",
        },
    )
    assert response.status_code == 201
    assert "id" in response.json()


@pytest.mark.asyncio
async def test_get_prompt(client: AsyncClient, mocker):
    mocker.patch(
        "app.services.database.DatabaseService.get_prompt",
        return_value={
            "id": str(uuid.uuid4()),
            "prompt_id": "test-prompt",
            "name": "Test Prompt",
            "description": "A test prompt.",
            "template": "Test template",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        },
    )
    response = await client.get("/api/v1/prompts/test-prompt")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Prompt"


@pytest.mark.asyncio
async def test_list_prompts(client: AsyncClient, mocker):
    mocker.patch(
        "app.services.database.DatabaseService.list_prompts",
        return_value=[
            {
                "id": str(uuid.uuid4()),
                "prompt_id": "test-prompt",
                "name": "Test Prompt",
                "description": "A test prompt.",
                "template": "Test template",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            }
        ],
    )
    response = await client.get("/api/v1/prompts/")
    assert response.status_code == 200
    assert len(response.json()) > 0
