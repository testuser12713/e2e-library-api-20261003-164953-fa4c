"""Tests for the members CRUD endpoints."""

from datetime import date

import pytest
from fastapi.testclient import TestClient

from app.main import app

API_KEY = "test-api-key"


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def _headers():
    return {"X-API-Key": API_KEY}


def _create(client, name="Anna Schmidt", email="anna@example.com", **extra):
    payload = {"name": name, "email": email, **extra}
    return client.post("/members", json=payload, headers=_headers())


def test_create_member_defaults_mitglied_seit_to_today(client):
    response = _create(client)

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Anna Schmidt"
    assert body["email"] == "anna@example.com"
    assert body["mitglied_seit"] == date.today().isoformat()
    assert isinstance(body["id"], int)


def test_create_member_respects_explicit_mitglied_seit(client):
    response = _create(client, mitglied_seit="2020-01-15")

    assert response.status_code == 201
    assert response.json()["mitglied_seit"] == "2020-01-15"


def test_get_member_returns_created_member(client):
    created = _create(client)
    member_id = created.json()["id"]

    response = client.get(f"/members/{member_id}")

    assert response.status_code == 200
    assert response.json() == created.json()


def test_get_member_not_found_returns_404(client):
    response = client.get("/members/9999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Mitglied nicht gefunden"}


def test_list_members_returns_all(client):
    _create(client, name="Erste", email="erste@example.com")
    _create(client, name="Zweite", email="zweite@example.com")

    response = client.get("/members")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    assert {m["email"] for m in body} == {"erste@example.com", "zweite@example.com"}


def test_create_duplicate_email_returns_409(client):
    first = _create(client)
    assert first.status_code == 201

    second = _create(client, name="Andere Person")

    assert second.status_code == 409
    assert second.json() == {"detail": "E-Mail bereits vergeben"}


def test_create_invalid_email_returns_422(client):
    response = _create(client, email="nicht-eine-email")

    assert response.status_code == 422
    assert response.json() == {"detail": "Ungültige E-Mail-Adresse"}


def test_update_member_changes_fields(client):
    created = _create(client)
    member_id = created.json()["id"]

    response = client.put(
        f"/members/{member_id}",
        json={"name": "Anna Muster"},
        headers=_headers(),
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Anna Muster"
    assert response.json()["email"] == "anna@example.com"


def test_update_member_email_conflict_returns_409(client):
    _create(client, name="Erste", email="erste@example.com")
    second = _create(client, name="Zweite", email="zweite@example.com")
    second_id = second.json()["id"]

    response = client.put(
        f"/members/{second_id}",
        json={"email": "erste@example.com"},
        headers=_headers(),
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "E-Mail bereits vergeben"}


def test_update_member_invalid_email_returns_422(client):
    created = _create(client)
    member_id = created.json()["id"]

    response = client.put(
        f"/members/{member_id}",
        json={"email": "keine-email"},
        headers=_headers(),
    )

    assert response.status_code == 422


def test_update_member_not_found_returns_404(client):
    response = client.put(
        "/members/9999",
        json={"name": "Niemand"},
        headers=_headers(),
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Mitglied nicht gefunden"}


def test_delete_member_returns_204_and_removes(client):
    created = _create(client)
    member_id = created.json()["id"]

    response = client.delete(f"/members/{member_id}", headers=_headers())

    assert response.status_code == 204
    assert client.get(f"/members/{member_id}").status_code == 404


def test_delete_member_not_found_returns_404(client):
    response = client.delete("/members/9999", headers=_headers())

    assert response.status_code == 404
    assert response.json() == {"detail": "Mitglied nicht gefunden"}


def test_create_without_api_key_returns_401(client):
    response = client.post(
        "/members",
        json={"name": "Ohne Key", "email": "ohne@example.com"},
    )

    assert response.status_code == 401


def test_create_with_wrong_api_key_returns_401(client):
    response = client.post(
        "/members",
        json={"name": "Falscher Key", "email": "falsch@example.com"},
        headers={"X-API-Key": "falscher-key"},
    )

    assert response.status_code == 401


def test_update_without_api_key_returns_401(client):
    response = client.put(
        "/members/1",
        json={"name": "Ohne Key"},
    )

    assert response.status_code == 401


def test_delete_without_api_key_returns_401(client):
    response = client.delete("/members/1")

    assert response.status_code == 401
