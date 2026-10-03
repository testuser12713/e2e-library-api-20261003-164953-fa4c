"""Returns router — Rückgabe einer offenen Ausleihe."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import require_api_key
from app.database import get_db
from app.models import Loan
from app.schemas import LoanOut

router = APIRouter(tags=["returns"])


@router.post("/loans/{loan_id}/return", response_model=LoanOut)
def return_loan(
    loan_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(require_api_key),
):
    loan = db.get(Loan, loan_id)
    if loan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ausleihe nicht gefunden",
        )
    if loan.zurueckgegeben_am is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ausleihe bereits zurückgegeben",
        )

    loan.zurueckgegeben_am = date.today()
    db.commit()
    db.refresh(loan)
    return loan
