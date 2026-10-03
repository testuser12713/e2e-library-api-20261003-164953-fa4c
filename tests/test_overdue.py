"""Tests for GET /loans/overdue."""

from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from app.database import get_db
from app.main import app
from app.models import Book, Loan, Member


@pytest.fixture
def db():
    override = app.dependency_overrides[get_db]
    gen = override()
    session = next(gen)
    try:
        yield session
    finally:
        session.close()


def _book(db, isbn: str) -> Book:
    book = Book(
        titel="Testbuch",
        autor="Testautor",
        isbn=isbn,
        erscheinungsjahr=2020,
        anzahl_exemplare=3,
    )
    db.add(book)
    return book


def _member(db, email: str) -> Member:
    member = Member(
        name="Max Mustermann",
        email=email,
        mitglied_seit=date(2020, 1, 1),
    )
    db.add(member)
    return member


def _loan(db, book, member, faellig_am, zurueckgegeben_am=None) -> Loan:
    loan = Loan(
        book_id=book.id,
        member_id=member.id,
        ausgeliehen_am=faellig_am - timedelta(days=14),
        faellig_am=faellig_am,
        zurueckgegeben_am=zurueckgegeben_am,
    )
    db.add(loan)
    return loan


def test_overdue_returns_only_open_and_due_loans(db):
    book = _book(db, "978-3-16-148410-0")
    member = _member(db, "a@example.com")
    db.flush()

    today = date.today()
    overdue = _loan(db, book, member, today - timedelta(days=5))
    not_yet_due = _loan(db, book, member, today + timedelta(days=5))
    returned = _loan(
        db,
        book,
        member,
        today - timedelta(days=3),
        zurueckgegeben_am=today - timedelta(days=1),
    )
    due_today = _loan(db, book, member, today)
    db.commit()

    with TestClient(app) as client:
        response = client.get("/loans/overdue")

    assert response.status_code == 200
    ids = {loan["id"] for loan in response.json()}
    assert overdue.id in ids
    assert not_yet_due.id not in ids
    assert returned.id not in ids
    assert due_today.id not in ids


def test_overdue_sorted_ascending_by_due_date(db):
    book = _book(db, "978-3-16-148411-7")
    member = _member(db, "b@example.com")
    db.flush()

    today = date.today()
    earliest = _loan(db, book, member, today - timedelta(days=10))
    late = _loan(db, book, member, today - timedelta(days=1))
    middle = _loan(db, book, member, today - timedelta(days=5))
    db.commit()

    with TestClient(app) as client:
        response = client.get("/loans/overdue")

    assert response.status_code == 200
    assert [loan["id"] for loan in response.json()] == [earliest.id, middle.id, late.id]


def test_overdue_returns_empty_list_when_no_matches(db):
    book = _book(db, "978-3-16-148412-4")
    member = _member(db, "c@example.com")
    db.flush()

    today = date.today()
    _loan(db, book, member, today + timedelta(days=2))
    db.commit()

    with TestClient(app) as client:
        response = client.get("/loans/overdue")

    assert response.status_code == 200
    assert response.json() == []
