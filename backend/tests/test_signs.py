from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


# ==========================================
# TESTE CREATE
# ==========================================

def test_create_sign():

    response = client.post(
        "/signs/",
        json={
            "name": "oi",
            "description": "Sinal de oi",
            "video_path": "videos/oi.mp4"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "oi"


# ==========================================
# TESTE LIST
# ==========================================

def test_list_signs():

    response = client.get("/signs/")

    assert response.status_code == 200

    assert isinstance(response.json(), list)


# ==========================================
# TESTE GET BY ID
# ==========================================

def test_get_sign():

    create_response = client.post(
        "/signs/",
        json={
            "name": "sim"
        }
    )

    sign_id = create_response.json()["id"]

    response = client.get(f"/signs/{sign_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == sign_id


# ==========================================
# TESTE UPDATE
# ==========================================

def test_update_sign():

    create_response = client.post(
        "/signs/",
        json={
            "name": "nao"
        }
    )

    sign_id = create_response.json()["id"]

    response = client.put(
        f"/signs/{sign_id}",
        json={
            "name": "nao_atualizado"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "nao_atualizado"


# ==========================================
# TESTE DELETE
# ==========================================

def test_delete_sign():

    create_response = client.post(
        "/signs/",
        json={
            "name": "teste_delete"
        }
    )

    sign_id = create_response.json()["id"]

    response = client.delete(f"/signs/{sign_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Sinal deletado com sucesso"