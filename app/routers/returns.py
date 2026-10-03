"""Returns router — endpoint stub to be implemented by the returns ticket."""

from fastapi import APIRouter, Depends, HTTPException

from app.auth import require_api_key
from app.schemas import LoanOut

router = APIRouter(tags=["returns"])


@router.post("/loans/{loan_id}/return", response_model=LoanOut)
def return_loan(loan_id: int, api_key: str = Depends(require_api_key)):
    raise HTTPException(status_code=501, detail="Rückgabe implementiert diesen Endpunkt")
