from httpx import AsyncClient
import pytest
from main import app  # Import your FastAPI app

@pytest.mark.anyio
async def test_root():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert response.headers["location"] == "/static/index.html"
