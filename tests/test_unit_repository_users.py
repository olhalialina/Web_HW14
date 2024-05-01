import unittest
from unittest.mock import MagicMock
from libgravatar import Gravatar
from sqlalchemy.orm import Session
from src.database.models import User
from src.schemas import UserModel
from src.repository.users import (
    get_user_by_email,
    create_user,
    update_token,
    confirmed_email,
    update_avatar,
)


class TestUserFunctions(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)

    async def test_get_user_by_email(self):
        user = User(id=1, email="test@example.com")
        self.session.query().filter().first.return_value = user
        result = await get_user_by_email(email="test@example.com", db=self.session)
        self.assertEqual(result, user)

    async def test_get_user_by_email_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_user_by_email(email="nonexistent@example.com", db=self.session)
        self.assertIsNone(result)

    async def test_create_user(self):
        user_data = UserModel(
            username="testuser",
            email="test@example.com",
            password="password123",
        )
        gravatar_mock = MagicMock(spec=Gravatar)
        gravatar_mock.get_image.return_value = "https://www.gravatar.com/avatar/55502f40dc8b7c769880b10874abc9d0"
        with unittest.mock.patch('libgravatar.Gravatar', return_value=gravatar_mock):
            new_user = User(**user_data.dict(), avatar="http://example.com/avatar.jpg")
            self.session.add(new_user)
            self.session.commit.return_value = None
            self.session.refresh(new_user)
            result = await create_user(body=user_data, db=self.session)
            self.assertEqual(result.username, new_user.username)
            self.assertEqual(result.email, new_user.email)
            self.assertEqual(result.password, new_user.password)
            self.assertEqual(result.avatar, "https://www.gravatar.com/avatar/55502f40dc8b7c769880b10874abc9d0")

    async def test_create_user_with_gravatar_error(self):
        user_data = UserModel(
            username="testuser",
            email="test@example.com",
            password="password123",
        )
        gravatar_mock = MagicMock(spec=Gravatar)
        gravatar_mock.get_image.side_effect = Exception("Gravatar error")
        with unittest.mock.patch('libgravatar.Gravatar', return_value=gravatar_mock):
            new_user = User(**user_data.dict(), avatar=None)
            self.session.add(new_user)
            self.session.commit.return_value = None
            self.session.refresh(new_user)
            result = await create_user(body=user_data, db=self.session)
            self.assertEqual(result.username, new_user.username)
            self.assertEqual(result.email, new_user.email)
            self.assertEqual(result.password, new_user.password)
            self.assertEqual(result.avatar, "https://www.gravatar.com/avatar/55502f40dc8b7c769880b10874abc9d0")

    async def test_update_token(self):
        user = User(id=1, username="testuser", email="test@example.com", password="password123")
        self.session.commit.return_value = None
        update_token_value = "new_token"
        user.refresh_token = update_token_value
        result = await update_token(user=user, token=update_token_value, db=self.session)
        self.assertIsNone(result)
        self.assertEqual(user.refresh_token, update_token_value)

    async def test_confirmed_email(self):
        user = User(id=1, username="testuser", email="test@example.com", password="password123")
        user.confirmed = True
        self.session.commit.return_value = None
        result = await confirmed_email(email="test@example.com", db=self.session)
        self.assertIsNone(result)
        self.assertTrue(user.confirmed)

    async def test_update_avatar(self):
        email = "test@example.com"
        new_avatar_url = "http://example.com/new_avatar.jpg"
        user = User(id=1, username="testuser", email=email, password="password123")
        session_mock = MagicMock(spec=Session)
        session_mock.query().filter().first.return_value = user
        updated_user = await update_avatar(email=email, url=new_avatar_url, db=session_mock)
        self.assertEqual(updated_user.avatar, new_avatar_url)
        session_mock.commit.assert_called_once()


if __name__ == '__main__':
    unittest.main()