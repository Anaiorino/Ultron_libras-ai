from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_register():
    response = client.post(
        "/auth/register",
        json={
            "name": "Teste",
            "email": "teste@email.com",
            "password": "123456"
        }
    )

    assert response.status_code in [200, 400]


def test_login():
    response = client.post(
        "/auth/login",
        json={
            "email": "teste@email.com",
            "password": "123456"
        }
    )

    assert response.status_code == 200

    body = response.json()

    assert "access_token" in body


def test_register():

    response = client.post(
        "/auth/register",
        json={
            "name": "Teste",
            "email": "teste@email.com",
            "password": "123456"
        }
    )

    assert response.status_code in [200, 400]
    
    