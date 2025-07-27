import uuid
from datetime import datetime

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_concept(client: AsyncClient, mocker):
    mocker.patch(
        "app.services.database.DatabaseService.create_concept",
        return_value=str(uuid.uuid4()),
    )
    mocker.patch(
        "app.services.prompt_service.PromptService.generate_concept_prompt",
        return_value="Test prompt",
    )
    mocker.patch(
        "app.services.course_service.CourseService.generate_content",
        return_value="Test content",
    )
    mocker.patch(
        "app.services.database.DatabaseService.get_concept",
        return_value={
            "id": str(uuid.uuid4()),
            "module_id": str(uuid.uuid4()),
            "title": "Test Concept",
            "description": "A test concept.",
            "order_index": 1,
            "content": "Test content",
            "status": "draft",
            "learning_objectives": [],
            "prerequisites": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        },
    )
    response = await client.post(
        "/api/v1/concepts/",
        json={
            "module_id": str(uuid.uuid4()),
            "title": "Test Concept",
            "description": "A test concept.",
            "order_index": 1,
            "learning_objectives": [],
            "prerequisites": [],
        },
    )
    assert response.status_code == 201
    assert "id" in response.json()


@pytest.mark.asyncio
async def test_get_concept(client: AsyncClient, mocker):
    mocker.patch(
        "app.services.database.DatabaseService.get_concept",
        return_value={
            "id": str(uuid.uuid4()),
            "module_id": str(uuid.uuid4()),
            "title": "Test Concept",
            "description": "A test concept.",
            "order_index": 1,
            "content": "Test content",
            "status": "draft",
            "learning_objectives": [],
            "prerequisites": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        },
    )
    response = await client.get(f"/api/v1/concepts/{uuid.uuid4()}")
    assert response.status_code == 200
    assert response.json()["title"] == "Test Concept"
