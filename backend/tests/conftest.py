import pytest
from unittest.mock import AsyncMock, patch

from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
def mock_mongodb_lifecycle():
    with (
        patch("app.main.connect_to_mongodb", new_callable=AsyncMock),
        patch("app.main.init_indexes", new_callable=AsyncMock),
        patch("app.main.verify_mongodb_read_write", new_callable=AsyncMock, return_value=True),
        patch("app.main.close_mongodb_connection", new_callable=AsyncMock),
    ):
        yield


@pytest.fixture
async def api_client(mock_mongodb_lifecycle):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
