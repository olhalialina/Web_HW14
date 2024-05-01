from unittest.mock import MagicMock, patch
from starlette.testclient import TestClient
from sqlalchemy.orm import Session
import main

client = TestClient(main.app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, world!"}


def test_process_time_header():
    response = client.get("/")
    assert "My-Process-Time" in response.headers