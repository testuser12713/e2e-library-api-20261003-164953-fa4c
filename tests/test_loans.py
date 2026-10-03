"""Tests for creating loans with their business rules."""

from datetime import date, timedelta

from fastapi.testclient import TestClient

from app.main import app
from app.models import Book, Loan, Member
from tests.conftest import TestingSessionLocal

API_KEY = "test-api-key"
HEADERS = {"X-API-Key": API_KEY}

_counter = 0


def _next_id() -> int:
    global _counter
    _counter += 1
    return _counter


def _create_book(anzahl_exemplare: int = 1) -> int:
    with TestingSessionLocal() as db:
        book = Book(
            titel="Titel",
            autor="Autor",
            isbn=f"isbn-{_next_id()}",
            erscheinungsjahr=2020,
            anzahl_exemplare=anzahl_exemplare,
        )
        db.add(book)
        db.commit()
        db.refresh(book)
        return book.id


def _create_member() -> int:
    with TestingSessionLocal() as db:
        member = Member(
            name="Max Mustermann",
            email=f"max{_next_id()}@example.com",
            mitglied_seit=date.today(),
        )
        db.add(member)
        db.commit()
        db.refresh(member)
        return member.id


def _create_open_loan(book_id: int, member_id: int) -> int:
    with TestingSessionLocal() as db:
        loan = Loan(
            book_id=book_id,
            member_id=member_id,
            ausgeliehen_am=date.today(),
            faellig_am=date.today() + timedelta(days=14),
            zurueckgegeben_am=None,
        )
        db.add(loan)
        db.commit()
        db.refresh(loan)
        return loan.id


def _post_loan(client, book_id, member_id, headers=None):
    return client.post(
        "/loans",
        json={"book_id": book_id, "member_id": member_id},
        headers=headers if headers is not None else HEADERS,
    )


def test_create_loan_returns_201_with_full_loan():
    book_id = _create_book(anzahl_exemplare=1)
    member_id = _create_member()

    with TestClient(app) as client:
        response = _post_loan(client, book_id, member_id)

    assert response.status_code == 201
    data = response.json()
    assert data["book_id"] == book_id
    assert data["member_id"] == member_id
    assert data["ausgeliehen_am"] is not None
    assert data["faellig_am"] is not None
    assert data["zurueckgegeben_am"] is None


def test_loan_due_date_is_exactly_14_days_after():
    book_id = _create_book(anzahl_exemplare=1)
    member_id = _create_member()

    with TestClient(app) as client:
        response = _post_loan(client, book_id, member_id)

    assert response.status_code == 201
    data = response.json()
    ausgeliehen = date.fromisoformat(data["ausgeliehen_am"])
    faellig = date.fromisoformat(data["faellig_am"])
    assert ausgeliehen == date.today()
    assert faellig - ausgeliehen == timedelta(days=14)


def test_fourth_open_loan_is_rejected_with_409():
    member_id = _create_member()
    for _ in range(3):
        _create_open_loan(_create_book(anzahl_exemplare=1), member_id)
    new_book_id = _create_book(anzahl_exemplare=1)

    with TestClient(app) as client:
        response = _post_loan(client, new_book_id, member_id)

    assert response.status_code == 409
    assert response.json() == {"detail": "Mitglied hat bereits drei offene Ausleihen"}


def test_fully_lent_book_is_rejected_with_409():
    book_id = _create_book(anzahl_exemplare=1)
    first_member_id = _create_member()
    second_member_id = _create_member()
    _create_open_loan(book_id, first_member_id)

    with TestClient(app) as client:
        response = _post_loan(client, book_id, second_member_id)

    assert response.status_code == 409
    assert response.json() == {"detail": "Kein freies Exemplar verfügbar"}


def test_unknown_book_id_returns_404():
    member_id = _create_member()

    with TestClient(app) as client:
        response = _post_loan(client, 999999, member_id)

    assert response.status_code == 404
    assert response.json() == {"detail": "Buch nicht gefunden"}


def test_unknown_member_id_returns_404():
    book_id = _create_book(anzahl_exemplare=1)

    with TestClient(app) as client:
        response = _post_loan(client, book_id, 999999)

    assert response.status_code == 404
    assert response.json() == {"detail": "Mitglied nicht gefunden"}


def test_wrong_api_key_returns_401():
    book_id = _create_book(anzahl_exemplare=1)
    member_id = _create_member()

    with TestClient(app) as client:
        response = _post_loan(client, book_id, member_id, headers={"X-API-Key": "wrong-key"})

    assert response.status_code == 401
