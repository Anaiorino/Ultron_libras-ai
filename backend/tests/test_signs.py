from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def get_auth_headers():
    # registra usuário
    client.post(
        "/auth/register",
        json={
            "name": "Usuário Signs",
            "email": "signs@test.com",
            "password": "123456"
        }
    )

    # faz login
    response = client.post(
        "/auth/login",
        json={
            "email": "signs@test.com",
            "password": "123456"
        }
    )

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }


def test_create_sign():
    headers = get_auth_headers()

    response = client.post(
        "/signs/",
        json={
            "name": "Oi",
            "description": "Sinal de saudação",
            "video_path": "videos/oi.mp4"
        },
        headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Oi"
    assert data["description"] == "Sinal de saudação"
    assert data["video_path"] == "videos/oi.mp4"


def test_list_signs():
    headers = get_auth_headers()

    # cria um sinal antes
    client.post(
        "/signs/",
        json={
            "name": "Bom dia",
            "description": "Cumprimento",
            "video_path": "videos/bom_dia.mp4"
        },
        headers=headers
    )

    response = client.get("/signs/", headers=headers)

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_sign():
    headers = get_auth_headers()

    create_response = client.post(
        "/signs/",
        json={
            "name": "Tudo bem",
            "description": "Sinal de cumprimento",
            "video_path": "videos/tudo_bem.mp4"
        },
        headers=headers
    )

    assert create_response.status_code == 200

    sign_id = create_response.json()["id"]

    response = client.get(f"/signs/{sign_id}", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sign_id
    assert data["name"] == "Tudo bem"


def test_update_sign():
    headers = get_auth_headers()

    create_response = client.post(
        "/signs/",
        json={
            "name": "Casa",
            "description": "Descrição antiga",
            "video_path": "videos/casa.mp4"
        },
        headers=headers
    )

    assert create_response.status_code == 200

    sign_id = create_response.json()["id"]

    response = client.put(
        f"/signs/{sign_id}",
        json={
            "name": "Casa Atualizada",
            "description": "Nova descrição",
            "video_path": "videos/casa_nova.mp4"
        },
        headers=headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Casa Atualizada"
    assert data["description"] == "Nova descrição"
    assert data["video_path"] == "videos/casa_nova.mp4"


def test_delete_sign():
    headers = get_auth_headers()

    create_response = client.post(
        "/signs/",
        json={
            "name": "Apagar",
            "description": "Sinal para deletar",
            "video_path": "videos/apagar.mp4"
        },
        headers=headers
    )

    assert create_response.status_code == 200

    sign_id = create_response.json()["id"]

    response = client.delete(
        f"/signs/{sign_id}",
        headers=headers
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Sinal deletado com sucesso"