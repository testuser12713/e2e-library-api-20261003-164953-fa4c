"""Loans router — endpoint stubs to be implemented by the loans ticket."""

from fastapi import APIRouter, Body, Depends, HTTPException

from app.auth import require_api_key
from app.schemas import LoanOut

router = APIRouter(tags=["loans"])


@router.post("/loans", status_code=201, response_model=LoanOut)
def create_loan(
    book_id: int = Body(...),
    member_id: int = Body(...),
    api_key: str = Depends(require_api_key),
):
    raise HTTPException(status_code=501, detail="Ausleihe-Anlegen implementiert diesen Endpunkt")
