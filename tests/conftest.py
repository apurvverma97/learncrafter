import pytest_asyncio
from httpx import AsyncClient

from app.main import app


@pytest_asyncio.fixture(scope="function")
async def client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
