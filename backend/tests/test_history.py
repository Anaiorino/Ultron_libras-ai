from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def get_auth_data():
    # registra usuário
    client.post(
        "/auth/register",
        json={
            "name": "Usuário History",
            "email": "history@test.com",
            "password": "123456"
        }
    )

    # login
    response = client.post(
        "/auth/login",
        json={
            "email": "history@test.com",
            "password": "123456"
        }
    )

    data = response.json()

    token = data["access_token"]
    user_id = data["user"]["id"]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    return headers, user_id


def test_create_history():
    headers, user_id = get_auth_data()

    response = client.post(
        "/history/",
        json={
            "user_id": user_id,
            "input_text": "oi",
            "output_text": "sinal de oi",
            "translation_type": "text_to_libras",
            "confidence": "0.95"
        },
        headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == user_id
    assert data["input_text"] == "oi"
    assert data["output_text"] == "sinal de oi"


def test_list_history():
    headers, user_id = get_auth_data()

    client.post(
        "/history/",
        json={
            "user_id": user_id,
            "input_text": "bom dia",
            "output_text": "sinal de bom dia",
            "translation_type": "text_to_libras",
            "confidence": "0.90"
        },
        headers=headers
    )

    response = client.get("/history/", headers=headers)

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_delete_history():
    headers, user_id = get_auth_data()

    create_response = client.post(
        "/history/",
        json={
            "user_id": user_id,
            "input_text": "teste",
            "output_text": "teste traduzido",
            "translation_type": "text_to_libras",
            "confidence": "0.99"
        },
        headers=headers
    )

    assert create_response.status_code == 200

    history_id = create_response.json()["id"]

    response = client.delete(
        f"/history/{history_id}",
        headers=headers
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Histórico deletado com sucesso"