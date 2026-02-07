import pytest
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient
from src.services import ShortenerService
from main import app
from config import DOMEN


@pytest.fixture
def mock_service():
    service = AsyncMock(spec=ShortenerService)
    service.domen = f"{DOMEN}/api/v1"
    service.create_link = AsyncMock()
    service.get_full_link = AsyncMock()
    return service


@pytest.fixture
def client(mock_service):
    """Тестовый клиент с подменой через dependency_overrides."""
    from src.routers import get_shortener_service

    def override_get_shortener_service():
        return mock_service

    app.dependency_overrides[get_shortener_service] = override_get_shortener_service

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
