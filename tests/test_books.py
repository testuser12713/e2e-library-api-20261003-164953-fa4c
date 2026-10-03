"""Tests for the books CRUD, search and pagination endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

API_KEY = "test-api-key"
HEADERS = {"X-API-Key": API_KEY}


@pytest.fixture
def client():
    return TestClient(app)


def make_book(**overrides):
    payload = {
        "titel": "Der Steppenwolf",
        "autor": "Hermann Hesse",
        "isbn": "978-3-518-36630-8",
        "erscheinungsjahr": 1927,
        "anzahl_exemplare": 3,
    }
    payload.update(overrides)
    return payload


def test_create_and_get_book(client):
    payload = make_book()
    resp = client.post("/books", json=payload, headers=HEADERS)
    assert resp.status_code == 201
    created = resp.json()
    assert created["id"] is not None
    assert created["titel"] == payload["titel"]

    resp = client.get(f"/books/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["isbn"] == payload["isbn"]


def test_create_duplicate_isbn_conflict(client):
    assert client.post("/books", json=make_book(), headers=HEADERS).status_code == 201
    resp = client.post("/books", json=make_book(), headers=HEADERS)
    assert resp.status_code == 409
    assert resp.json()["detail"]


def test_search_by_title_and_author_case_insensitive(client):
    for payload in (
        make_book(titel="Die Verwandlung", autor="Kafka", isbn="isbn-1"),
        make_book(titel="Der Prozess", autor="Kafka", isbn="isbn-2"),
        make_book(titel="Faust", autor="Goethe", isbn="isbn-3"),
    ):
        assert client.post("/books", json=payload, headers=HEADERS).status_code == 201

    resp = client.get("/books", params={"q": "kafka"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    assert {item["autor"] for item in data["items"]} == {"Kafka"}

    resp = client.get("/books", params={"q": "VERWANDLUNG"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["titel"] == "Die Verwandlung"


def test_pagination_total_limit_offset(client):
    for i in range(5):
        payload = make_book(titel=f"Buch {i}", isbn=f"isbn-{i}")
        assert client.post("/books", json=payload, headers=HEADERS).status_code == 201

    resp = client.get("/books", params={"limit": 2, "offset": 0})
    data = resp.json()
    assert data["total"] == 5
    assert data["limit"] == 2
    assert data["offset"] == 0
    assert len(data["items"]) == 2

    resp = client.get("/books", params={"limit": 2, "offset": 2})
    data = resp.json()
    assert data["total"] == 5
    assert data["offset"] == 2
    assert len(data["items"]) == 2


def test_list_defaults(client):
    assert client.post("/books", json=make_book(), headers=HEADERS).status_code == 201
    data = client.get("/books").json()
    assert data["limit"] == 20
    assert data["offset"] == 0
    assert data["total"] == 1
    assert len(data["items"]) == 1


def test_get_book_not_found(client):
    resp = client.get("/books/999")
    assert resp.status_code == 404
    assert resp.json()["detail"]


def test_update_book(client):
    created = client.post("/books", json=make_book(), headers=HEADERS).json()
    resp = client.put(f"/books/{created['id']}", json={"titel": "Neu"}, headers=HEADERS)
    assert resp.status_code == 200
    assert resp.json()["titel"] == "Neu"
    assert resp.json()["autor"] == created["autor"]


def test_update_book_not_found(client):
    resp = client.put("/books/999", json={"titel": "Neu"}, headers=HEADERS)
    assert resp.status_code == 404
    assert resp.json()["detail"]


def test_update_isbn_conflict(client):
    b1 = client.post("/books", json=make_book(isbn="aaa"), headers=HEADERS).json()
    b2 = client.post("/books", json=make_book(isbn="bbb"), headers=HEADERS).json()
    resp = client.put(f"/books/{b2['id']}", json={"isbn": "aaa"}, headers=HEADERS)
    assert resp.status_code == 409
    assert b1["id"] != b2["id"]


def test_delete_book(client):
    created = client.post("/books", json=make_book(), headers=HEADERS).json()
    assert client.delete(f"/books/{created['id']}", headers=HEADERS).status_code == 204
    assert client.get(f"/books/{created['id']}").status_code == 404


def test_delete_book_not_found(client):
    assert client.delete("/books/999", headers=HEADERS).status_code == 404


def test_write_endpoints_require_api_key(client):
    assert client.post("/books", json=make_book()).status_code == 401
    assert (
        client.post("/books", json=make_book(), headers={"X-API-Key": "wrong"}).status_code == 401
    )
    assert client.put("/books/1", json={"titel": "Neu"}).status_code == 401
    assert client.delete("/books/1").status_code == 401
