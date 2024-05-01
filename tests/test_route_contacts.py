from unittest.mock import patch, MagicMock, AsyncMock

import pytest

from src.config import messages
from src.database.models import User
from src.services.auth import auth_service

contact_data = {"first_name": "Vanya",
                "last_name": "Petrov",
                "email": "petrov@example.com",
                "phone_number": "123456789",
                "born_date": "2023-01-01",
                "description": "string",
                "user_id": 1
                }
user_data = {"username": "peter", "email": "peter@gmail.com", "password": "12345678"}


@pytest.fixture()
def token(client, session, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    client.post("/api/auth/signup", json=user_data)
    current_user: User = session.query(User).filter(User.email == user_data.get('email')).first()
    current_user.confirmed = True
    session.commit()
    response = client.post(
        "/api/auth/login",
        data={"username": user_data.get('email'), "password": user_data.get('password')},
    )
    data = response.json()
    return data["access_token"]


def test_create_contact(client, token, monkeypatch):
    with patch.object(auth_service, 'r') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post(
            "/api/contacts/",
            json=contact_data,
            headers=headers
        )
        assert response.status_code == 201, response.text
        data = response.json()
        assert data["first_name"] == contact_data.get("first_name")
        assert "id" in data


def test_read_contacts(client, token, monkeypatch):
    with patch.object(auth_service, 'r') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        response = client.get(
            "/api/contacts/",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert isinstance(data, list)
        assert data[0]["first_name"] == contact_data.get("first_name")
        assert "id" in data[0]


def test_read_contact_existing(client, token, monkeypatch):
    with patch.object(auth_service, 'r') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        response = client.get(f"/api/contacts/1",
                              headers={"Authorization": f"Bearer {token}"}
                              )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["first_name"] == contact_data.get("first_name")
        assert "id" in data


def test_read_contact_not_found(client, token, monkeypatch):
    with patch.object(auth_service, 'r') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        response = client.get(
            "/api/contacts/2",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == messages.CONTACT_NOT_FOUND


def test_update_contact_existing(client, token, monkeypatch):
    with patch.object(auth_service, 'r') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        response = client.put(f"/api/contacts/1",
                              json={"first_name": contact_data.get("first_name"),
                                    "last_name": contact_data.get("last_name"),
                                    "email": contact_data.get("email"),
                                    "phone_number": contact_data.get("phone_number"),
                                    "born_date": contact_data.get("born_date"),
                                    "description": contact_data.get("description")},
                              headers={"Authorization": f"Bearer {token}"}
                              )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["first_name"] == contact_data.get("first_name")
        assert data["last_name"] == contact_data.get("last_name")
        assert data["email"] == contact_data.get("email")
        assert data["phone_number"] == contact_data.get("phone_number")
        assert data["born_date"] == contact_data.get("born_date")
        assert data["description"] == contact_data.get("description")
        assert "id" in data


def test_update_contact_not_found(client, token, monkeypatch):
    with patch.object(auth_service, 'r') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        response = client.put(
            "/api/contacts/2",
            json={"first_name": contact_data.get("first_name"),
                  "last_name": contact_data.get("last_name"),
                  "email": contact_data.get("email"),
                  "phone_number": contact_data.get("phone_number"),
                  "born_date": contact_data.get("born_date"),
                  "description": contact_data.get("description")},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == messages.CONTACT_NOT_FOUND


def test_delete_contact_existing(client, token, monkeypatch):
    with patch.object(auth_service, 'r') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        response = client.delete(f"/api/contacts/1",
                                 headers={"Authorization": f"Bearer {token}"}
                                 )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["first_name"] == contact_data.get("first_name")
        assert data["last_name"] == contact_data.get("last_name")
        assert "id" in data


def test_repeat_delete_contact(client, token, monkeypatch):
    with patch.object(auth_service, 'r') as redis_mock:
        redis_mock.get.return_value = None
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        with patch.object(auth_service, 'r') as r_mock:
            r_mock.get.return_value = None
            response = client.delete(
                "/api/contacts/1",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code == 404, response.text
            data = response.json()
            assert data["detail"] == messages.CONTACT_NOT_FOUND