"""Overdue router — lists open, already-due loans."""

from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Loan
from app.schemas import LoanOut

router = APIRouter(tags=["overdue"])


@router.get("/loans/overdue", response_model=list[LoanOut])
def list_overdue(db: Session = Depends(get_db)):
    today = date.today()
    stmt = (
        select(Loan)
        .where(Loan.zurueckgegeben_am.is_(None), Loan.faellig_am < today)
        .order_by(Loan.faellig_am.asc())
    )
    return db.scalars(stmt).all()
