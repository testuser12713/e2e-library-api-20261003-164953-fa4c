"""Members router — endpoint stubs to be implemented by the members ticket."""

from fastapi import APIRouter, Depends, HTTPException

from app.auth import require_api_key
from app.schemas import MemberCreate, MemberOut, MemberUpdate

router = APIRouter(tags=["members"])


@router.get("/members", response_model=list[MemberOut])
def list_members():
    raise HTTPException(status_code=501, detail="Mitglieder-CRUD implementiert diesen Endpunkt")


@router.get("/members/{member_id}", response_model=MemberOut)
def get_member(member_id: int):
    raise HTTPException(status_code=501, detail="Mitglieder-CRUD implementiert diesen Endpunkt")


@router.post("/members", status_code=201, response_model=MemberOut)
def create_member(member: MemberCreate, api_key: str = Depends(require_api_key)):
    raise HTTPException(status_code=501, detail="Mitglieder-CRUD implementiert diesen Endpunkt")


@router.put("/members/{member_id}", response_model=MemberOut)
def update_member(member_id: int, member: MemberUpdate, api_key: str = Depends(require_api_key)):
    raise HTTPException(status_code=501, detail="Mitglieder-CRUD implementiert diesen Endpunkt")


@router.delete("/members/{member_id}", status_code=204)
def delete_member(member_id: int, api_key: str = Depends(require_api_key)):
    raise HTTPException(status_code=501, detail="Mitglieder-CRUD implementiert diesen Endpunkt")
