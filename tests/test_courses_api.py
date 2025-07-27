import uuid
from datetime import datetime

import pytest
from httpx import AsyncClient

from app.models.schemas import CourseLevel, CourseTopic


@pytest.mark.asyncio
async def test_create_course(client: AsyncClient, mocker):
    mocker.patch(
        "app.services.database.DatabaseService.create_course",
        return_value=str(uuid.uuid4()),
    )
    mocker.patch(
        "app.services.database.DatabaseService.get_course",
        return_value={
            "id": str(uuid.uuid4()),
            "title": "Test Course",
            "description": "A test course.",
            "topic": "programming",
            "level": "beginner",
            "status": "draft",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        },
    )
    response = await client.post(
        "/api/v1/courses/",
        json={
            "title": "Test Course",
            "description": "A test course.",
            "topic": "programming",
            "level": "beginner",
        },
    )
    assert response.status_code == 201
    assert "id" in response.json()


@pytest.mark.asyncio
async def test_get_course(client: AsyncClient, mocker):
    mocker.patch(
        "app.services.database.DatabaseService.get_course",
        return_value={
            "id": str(uuid.uuid4()),
            "title": "Test Course",
            "description": "A test course.",
            "topic": "programming",
            "level": "beginner",
            "status": "draft",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        },
    )
    response = await client.get(f"/api/v1/courses/{uuid.uuid4()}")
    assert response.status_code == 200
    assert response.json()["title"] == "Test Course"


@pytest.mark.asyncio
async def test_list_courses(client: AsyncClient, mocker):
    mocker.patch(
        "app.services.database.DatabaseService.list_courses",
        return_value=[
            {
                "id": str(uuid.uuid4()),
                "title": "Test Course",
                "description": "A test course.",
                "topic": "programming",
                "level": "beginner",
                "status": "draft",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            }
        ],
    )
    mocker.patch("app.services.database.DatabaseService.count_courses", return_value=1)
    response = await client.get("/api/v1/courses/")
    assert response.status_code == 200
    assert "data" in response.json()
    assert len(response.json()["data"]) > 0


@pytest.mark.asyncio
async def test_publish_course_job(client: AsyncClient, mocker):
    mocker.patch(
        "app.agents.course_publisher.CoursePublishingAgent.publish_course",
        return_value=None,
    )
    response = await client.post(
        "/api/v1/courses/publishJob",
        json={
            "topic": CourseTopic.PROGRAMMING.value,
            "level": CourseLevel.BEGINNER.value,
        },
    )
    assert response.status_code == 202
    assert "job_id" in response.json()
