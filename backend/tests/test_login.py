from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_login():
    # cria usuário antes
    client.post(
        "/auth/register",
        json={
            "name": "Teste Login",
            "email": "login_teste@email.com",
            "password": "123456"
        }
    )

    # tenta logar
    response = client.post(
        "/auth/login",
        json={
            "email": "login_teste@email.com",
            "password": "123456"
        }
    )

    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "login_teste@email.com"