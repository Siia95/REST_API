import json
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_register_user():
    # Тест на успішну реєстрацію користувача
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword"
    }
    response = client.post("/register/", json=user_data)
    assert response.status_code == 201
    assert response.json()["username"] == user_data["username"]
    assert response.json()["email"] == user_data["email"]

    # Тест на спробу реєстрації користувача з вже існуючим email
    response = client.post("/register/", json=user_data)
    assert response.status_code == 409
    assert "User already registered" in response.text
