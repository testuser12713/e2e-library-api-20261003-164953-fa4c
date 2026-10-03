"""Tests for the health endpoint and the OpenAPI route registration."""

from fastapi.testclient import TestClient

from app.main import app


def test_health_returns_ok():
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_openapi_documents_all_endpoints():
    with TestClient(app) as client:
        openapi = client.get("/openapi.json").json()

    paths = set(openapi["paths"])
    expected = {
        "/health",
        "/books",
        "/books/{book_id}",
        "/members",
        "/members/{member_id}",
        "/loans",
        "/loans/{loan_id}/return",
        "/loans/overdue",
    }
    missing = expected - paths
    assert not missing, f"nicht dokumentierte Endpunkte: {sorted(missing)}"
