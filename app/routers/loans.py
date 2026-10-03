"""Loans router — create a loan with its business rules."""

from datetime import date, timedelta

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import require_api_key
from app.database import get_db
from app.models import Book, Loan, Member
from app.schemas import LoanOut

router = APIRouter(tags=["loans"])


@router.post("/loans", status_code=201, response_model=LoanOut)
def create_loan(
    book_id: int = Body(...),
    member_id: int = Body(...),
    db: Session = Depends(get_db),
    api_key: str = Depends(require_api_key),
):
    member = db.get(Member, member_id)
    if member is None:
        raise HTTPException(status_code=404, detail="Mitglied nicht gefunden")

    book = db.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Buch nicht gefunden")

    open_loans_member = (
        db.query(func.count(Loan.id))
        .filter(Loan.member_id == member_id, Loan.zurueckgegeben_am.is_(None))
        .scalar()
    )
    if open_loans_member >= 3:
        raise HTTPException(
            status_code=409,
            detail="Mitglied hat bereits drei offene Ausleihen",
        )

    open_loans_book = (
        db.query(func.count(Loan.id))
        .filter(Loan.book_id == book_id, Loan.zurueckgegeben_am.is_(None))
        .scalar()
    )
    if open_loans_book >= book.anzahl_exemplare:
        raise HTTPException(
            status_code=409,
            detail="Kein freies Exemplar verfügbar",
        )

    today = date.today()
    loan = Loan(
        book_id=book_id,
        member_id=member_id,
        ausgeliehen_am=today,
        faellig_am=today + timedelta(days=14),
        zurueckgegeben_am=None,
    )
    db.add(loan)
    db.commit()
    db.refresh(loan)
    return loan
