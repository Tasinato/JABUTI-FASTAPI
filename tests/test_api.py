from uuid import uuid4

import pytest

USER = {"nome": "Ana", "email": "ana@example.com", "idade": 30}


@pytest.mark.parametrize(
    "method,path",
    [
        ("get", "/usuarios/"),
        ("post", "/usuarios/"),
        ("get", f"/usuarios/{uuid4()}"),
        ("put", f"/usuarios/{uuid4()}"),
        ("delete", f"/usuarios/{uuid4()}"),
    ],
)
@pytest.mark.parametrize("key", [None, "incorrect"])
def test_authentication(client, method, path, key):
    client.headers.pop("X-API-Key")
    headers = {"X-API-Key": key} if key else {}
    assert client.request(method, path, headers=headers, json=USER).status_code == 401


def test_crud_and_conflicts(client):
    created = client.post("/usuarios/", json=USER)
    assert created.status_code == 201
    user_id = created.json()["id"]
    assert client.get(f"/usuarios/{user_id}").json() == created.json()
    assert client.post("/usuarios/", json=USER).status_code == 409
    second = client.post("/usuarios/", json={**USER, "email": "other@example.com"}).json()
    assert client.put(f"/usuarios/{second['id']}", json={"email": USER["email"]}).status_code == 409
    updated = client.put(f"/usuarios/{user_id}", json={"nome": " Maria "})
    assert updated.status_code == 200
    assert updated.json()["nome"] == "Maria"
    assert updated.json()["idade"] == 30
    listing = client.get("/usuarios/?limit=1&sort=-nome").json()
    assert listing["total_count"] == 2
    assert listing["has_next"] is True
    assert listing["items"][0]["nome"] == "Maria"
    assert client.delete(f"/usuarios/{user_id}").status_code == 204
    assert client.get(f"/usuarios/{user_id}").status_code == 404
    assert client.put(f"/usuarios/{user_id}", json={"idade": 1}).status_code == 404
    assert client.delete(f"/usuarios/{user_id}").status_code == 404


@pytest.mark.parametrize(
    "changes",
    [
        {"nome": " "},
        {"nome": "a" * 101},
        {"email": "invalid"},
        {"idade": -1},
        {"idade": True},
        {"idade": "20"},
        {"extra": 1},
        {"nome": None},
        {"idade": None},
        {"email": None},
    ],
)
def test_create_validation(client, changes):
    assert client.post("/usuarios/", json={**USER, **changes}).status_code == 422


@pytest.mark.parametrize("field", ["nome", "email", "idade"])
def test_update_rejects_null(client, field):
    user_id = client.post("/usuarios/", json=USER).json()["id"]
    assert client.put(f"/usuarios/{user_id}", json={field: None}).status_code == 422
    assert client.get(f"/usuarios/{user_id}").json()[field] == USER[field]


@pytest.mark.parametrize(
    "query,status",
    [
        ("limit=0", 422),
        ("limit=101", 422),
        ("offset=-1", 422),
        ("sort=password", 400),
    ],
)
def test_list_validation(client, query, status):
    assert client.get(f"/usuarios/?{query}").status_code == status


def test_health(client):
    client.headers.pop("X-API-Key")
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["database"] == "ok"
    assert response.json()["redis"] == "disabled"


def test_invalid_uuid(client):
    assert client.get("/usuarios/not-a-uuid").status_code == 422


def test_cache_invalidation_on_writes(client, monkeypatch):
    import src.controllers.user_controller as controller

    cached = {}

    async def get(key):
        return cached.get(key)

    async def set_value(key, value, ttl):
        cached[key] = value

    async def delete(key):
        cached.pop(key, None)

    async def delete_prefix(prefix):
        for key in list(cached):
            if key.startswith(prefix):
                del cached[key]

    monkeypatch.setattr(controller, "cache_get", get)
    monkeypatch.setattr(controller, "cache_set", set_value)
    monkeypatch.setattr(controller, "cache_delete", delete)
    monkeypatch.setattr(controller, "cache_delete_prefix", delete_prefix)
    assert client.get("/usuarios/").json()["total_count"] == 0
    user = client.post("/usuarios/", json=USER).json()
    assert client.get("/usuarios/").json()["total_count"] == 1
    client.put(f"/usuarios/{user['id']}", json={"nome": "Maria"})
    assert client.get(f"/usuarios/{user['id']}").json()["nome"] == "Maria"
    assert client.get("/usuarios/").json()["items"][0]["nome"] == "Maria"
    client.delete(f"/usuarios/{user['id']}")
    assert client.get(f"/usuarios/{user['id']}").status_code == 404
    assert client.get("/usuarios/").json()["total_count"] == 0
