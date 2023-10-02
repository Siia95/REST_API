import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from fastapi import HTTPException

from auth import HashPassword, create_user, authenticate_user, get_user_by_email, create_access_token, confirmed_email, create_email_token
from models import User
from database import SessionLocal

class TestAuth(unittest.TestCase):
    def setUp(self):
        self.mock_session = MagicMock()
        self.mock_user = User(id=1, username="testuser", email="test@example.com", hashed_password="hashedpassword")

    def test_hash_password(self):
        hasher = HashPassword()
        hashed_password = hasher.hash_password("test123")
        self.assertTrue(hashed_password)

    def test_verify_password(self):
        hasher = HashPassword()
        plain_password = "test123"
        hashed_password = hasher.hash_password(plain_password)
        result = hasher.verify_password(plain_password, hashed_password)
        self.assertTrue(result)

    @patch("auth.SessionLocal", autospec=True)
    def test_create_user(self, mock_session_local):
        mock_session_instance = MagicMock()
        mock_session_local.return_value = mock_session_instance

        user = create_user("testuser", "test@example.com", "testpassword")

        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.hashed_password)
        mock_session_instance.add.assert_called_once()
        mock_session_instance.commit.assert_called_once()
        mock_session_instance.refresh.assert_called_once()

    @patch("auth.SessionLocal", autospec=True)
    def test_authenticate_user(self, mock_session_local):
        mock_session_instance = MagicMock()
        mock_session_local.return_value = mock_session_instance
        mock_session_instance.query.return_value.filter_by.return_value.first.return_value = self.mock_user

        user = authenticate_user("test@example.com", "testpassword")

        self.assertEqual(user, self.mock_user)
        mock_session_instance.query.return_value.filter_by.assert_called_once_with(email="test@example.com")
        mock_session_instance.close.assert_called_once()

    @patch("auth.SessionLocal", autospec=True)
    def test_get_user_by_email(self, mock_session_local):
        mock_session_instance = MagicMock()
        mock_session_local.return_value = mock_session_instance
        mock_session_instance.query.return_value.filter_by.return_value.first.return_value = self.mock_user

        user = get_user_by_email("test@example.com", mock_session_instance)

        self.assertEqual(user, self.mock_user)
        mock_session_instance.query.return_value.filter_by.assert_called_once_with(email="test@example.com")

    def test_create_access_token(self):
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(minutes=30)
        token = create_access_token(data, expires_delta)
        self.assertTrue(token)

    @patch("auth.get_user_by_email", autospec=True)
    def test_confirmed_email(self, mock_get_user_by_email):
        mock_session_instance = MagicMock()
        user = User(id=1, username="testuser", email="test@example.com", hashed_password="hashedpassword", confirmed=False)
        mock_get_user_by_email.return_value = user

        confirmed_email("test@example.com", mock_session_instance)

        self.assertTrue(user.confirmed)
        mock_session_instance.commit.assert_called_once()

    def test_create_email_token(self):
        data = {"sub": "test@example.com"}
        token = create_email_token(data)
        self.assertTrue(token)

if __name__ == '__main__':
    unittest.main()
