"""Overdue router — endpoint stub to be implemented by the overdue ticket."""

from fastapi import APIRouter, HTTPException

from app.schemas import LoanOut

router = APIRouter(tags=["overdue"])


@router.get("/loans/overdue", response_model=list[LoanOut])
def list_overdue():
    raise HTTPException(
        status_code=501, detail="Überfällige-Ausleihen implementiert diesen Endpunkt"
    )
