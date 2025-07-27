import uuid
from datetime import datetime

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_module(client: AsyncClient, mocker):
    mocker.patch(
        "app.services.database.DatabaseService.create_module",
        return_value=str(uuid.uuid4()),
    )
    mocker.patch(
        "app.services.database.DatabaseService.get_module",
        return_value={
            "id": str(uuid.uuid4()),
            "course_id": str(uuid.uuid4()),
            "title": "Test Module",
            "description": "A test module.",
            "order_index": 1,
            "status": "draft",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        },
    )
    response = await client.post(
        "/api/v1/modules/",
        json={
            "course_id": str(uuid.uuid4()),
            "title": "Test Module",
            "description": "A test module.",
            "order_index": 1,
        },
    )
    assert response.status_code == 201
    assert "id" in response.json()


@pytest.mark.asyncio
async def test_get_module(client: AsyncClient, mocker):
    mocker.patch(
        "app.services.database.DatabaseService.get_module",
        return_value={
            "id": str(uuid.uuid4()),
            "course_id": str(uuid.uuid4()),
            "title": "Test Module",
            "description": "A test module.",
            "order_index": 1,
            "status": "draft",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        },
    )
    response = await client.get(f"/api/v1/modules/{uuid.uuid4()}")
    assert response.status_code == 200
    assert response.json()["title"] == "Test Module"
