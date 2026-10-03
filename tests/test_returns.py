"""Tests for the loan-return endpoint (POST /loans/{loan_id}/return)."""

from datetime import date, timedelta

from fastapi.testclient import TestClient

from app import models
from app.database import get_db
from app.main import app

API_KEY = "test-api-key"


def _db_session():
    override = app.dependency_overrides[get_db]
    gen = override()
    db = next(gen)
    return db, gen


def _seed_loan() -> int:
    db, gen = _db_session()
    try:
        book = models.Book(
            titel="Testbuch",
            autor="Autor",
            isbn="1234567890",
            erscheinungsjahr=2020,
            anzahl_exemplare=3,
        )
        member = models.Member(
            name="Max Mustermann",
            email="max@example.com",
            mitglied_seit=date(2024, 1, 1),
        )
        db.add_all([book, member])
        db.flush()
        loan = models.Loan(
            book_id=book.id,
            member_id=member.id,
            ausgeliehen_am=date.today() - timedelta(days=10),
            faellig_am=date.today() + timedelta(days=4),
        )
        db.add(loan)
        db.commit()
        db.refresh(loan)
        return loan.id
    finally:
        gen.close()


def test_return_loan_sets_zurueckgegeben_am():
    loan_id = _seed_loan()

    with TestClient(app) as client:
        response = client.post(
            f"/loans/{loan_id}/return",
            headers={"X-API-Key": API_KEY},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == loan_id
    assert body["zurueckgegeben_am"] == date.today().isoformat()


def test_return_loan_twice_conflicts():
    loan_id = _seed_loan()

    with TestClient(app) as client:
        first = client.post(
            f"/loans/{loan_id}/return",
            headers={"X-API-Key": API_KEY},
        )
        assert first.status_code == 200

        second = client.post(
            f"/loans/{loan_id}/return",
            headers={"X-API-Key": API_KEY},
        )

    assert second.status_code == 409
    assert second.json() == {"detail": "Ausleihe bereits zurückgegeben"}


def test_return_unknown_loan_not_found():
    with TestClient(app) as client:
        response = client.post(
            "/loans/9999/return",
            headers={"X-API-Key": API_KEY},
        )

    assert response.status_code == 404
    assert response.json() == {"detail": "Ausleihe nicht gefunden"}


def test_return_requires_api_key():
    loan_id = _seed_loan()

    with TestClient(app) as client:
        response = client.post(f"/loans/{loan_id}/return")

    assert response.status_code == 401
    assert "detail" in response.json()


def test_return_rejects_wrong_api_key():
    loan_id = _seed_loan()

    with TestClient(app) as client:
        response = client.post(
            f"/loans/{loan_id}/return",
            headers={"X-API-Key": "falscher-key"},
        )

    assert response.status_code == 401
    assert "detail" in response.json()
