import pytest
from fastapi import status
from config import DOMEN

class TestCreateShortLink:
    """Тесты POST /shorten/"""

    def test_create_link_success(self, client, mock_service):
        """Успешное создание ссылки."""
        mock_service.create_link.return_value = {
            "full_link": "https://example.com",
            "short_link": f"{DOMEN}abc123",
        }

        response = client.post("/api/v1/shorten/", json={"link": "https://example.com"})

        mock_service.create_link.assert_called_once()
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["short_link"] == f"{DOMEN}abc123"
        mock_service.create_link.assert_called_once()

    def test_create_link_invalid_data(self, client):
        """Невалидные данные."""
        response = client.post("/api/v1/shorten/", json={"link": "invalid-url"})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_create_link_empty_body(self, client):
        """Пустой запрос."""
        response = client.post("/api/v1/shorten/", json={})

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


class TestRedirectLink:
    """Тесты GET /{code}"""

    def test_redirect_success(self, client, mock_service):
        """Успешный редирект."""
        mock_service.get_full_link.return_value = "https://example.com"

        response = client.get("/api/v1/abc123", follow_redirects=False)

        assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
        assert response.headers["location"] == "https://example.com"
        mock_service.get_full_link.assert_called_once_with("abc123")
