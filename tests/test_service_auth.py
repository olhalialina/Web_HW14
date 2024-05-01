from unittest.mock import patch, Mock
from fastapi import HTTPException
from jwt import PyJWTError
from sqlalchemy.orm import Session

import pytest

from src.config import messages
from src.services.auth import Auth


@pytest.mark.asyncio
async def test_get_current_user_valid_token():
    # Mocking dependencies
    token = "valid_token"
    db = Mock(spec=Session)
    auth_instance = Auth()
    auth_instance.r = Mock()
    auth_instance.SECRET_KEY = "test_secret_key"
    auth_instance.ALGORITHM = "test_algorithm"

    # Mocking jwt.decode
    with patch("src.services.auth.jwt.decode") as mock_jwt_decode:
        mock_jwt_decode.return_value = {"scope": "access_token", "sub": "test@example.com"}
        auth_instance.r.get.return_value = None
        user_data = {"id": 1, "email": "test@example.com"}
        with patch("src.services.auth.repository_users.get_user_by_email") as mock_get_user_by_email:
            mock_get_user_by_email.return_value = user_data
            user = await auth_instance.get_current_user(token, db)
            assert user == user_data


@pytest.mark.asyncio
async def test_get_current_user_invalid_token():
    # Mocking dependencies
    token = "valid_token"
    db = Mock(spec=Session)
    auth_instance = Auth()
    auth_instance.r = Mock()
    auth_instance.SECRET_KEY = "test_secret_key"
    auth_instance.ALGORITHM = "test_algorithm"

    # Mocking jwt.decode to raise JWTError
    with patch("src.services.auth.jwt.decode") as mock_jwt_decode:
        mock_jwt_decode.side_effect = PyJWTError(messages.INVALID_TOKEN)

        with pytest.raises(PyJWTError) as exc_info:
            await auth_instance.get_current_user(token, db)

        assert messages.INVALID_TOKEN in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_current_user_invalid_scope():
    # Mocking dependencies
    token = "valid_token"
    db = Mock(spec=Session)
    auth_instance = Auth()
    auth_instance.r = Mock()
    auth_instance.SECRET_KEY = "test_secret_key"
    auth_instance.ALGORITHM = "test_algorithm"

    # Mocking jwt.decode
    with patch("src.services.auth.jwt.decode") as mock_jwt_decode:
        mock_jwt_decode.return_value = {"scope": "invalid_scope", "sub": "test@example.com"}

        # Call the function and expect an HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await auth_instance.get_current_user(token, db)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == messages.NOT_VALIDATE