"""Members router — CRUD endpoints for library members."""

import re
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ValidationError, field_validator
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import require_api_key
from app.database import get_db
from app.models import Member
from app.schemas import MemberCreate, MemberOut, MemberUpdate

router = APIRouter(tags=["members"])

_EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class _EmailCheck(BaseModel):
    """Pydantic v2 wrapper that validates the email format.

    The shared ``MemberCreate``/``MemberUpdate`` schemas declare ``email`` as a
    plain ``str``, so the format check lives here instead of in the schema.
    """

    email: str

    @field_validator("email")
    @classmethod
    def _validate_email(cls, value: str) -> str:
        if not _EMAIL_REGEX.fullmatch(value):
            raise ValueError("Ungültige E-Mail-Adresse")
        return value


def _check_email(email: str) -> None:
    try:
        _EmailCheck(email=email)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail="Ungültige E-Mail-Adresse") from exc


def _get_member_or_404(db: Session, member_id: int) -> Member:
    member = db.get(Member, member_id)
    if member is None:
        raise HTTPException(status_code=404, detail="Mitglied nicht gefunden")
    return member


def _email_exists(db: Session, email: str, exclude_id: int | None = None) -> bool:
    stmt = select(Member).where(Member.email == email)
    if exclude_id is not None:
        stmt = stmt.where(Member.id != exclude_id)
    return db.execute(stmt).first() is not None


@router.get("/members", response_model=list[MemberOut])
def list_members(db: Session = Depends(get_db)):
    return db.scalars(select(Member).order_by(Member.id)).all()


@router.get("/members/{member_id}", response_model=MemberOut)
def get_member(member_id: int, db: Session = Depends(get_db)):
    return _get_member_or_404(db, member_id)


@router.post("/members", status_code=201, response_model=MemberOut)
def create_member(
    member: MemberCreate,
    api_key: str = Depends(require_api_key),
    db: Session = Depends(get_db),
):
    _check_email(member.email)
    if _email_exists(db, member.email):
        raise HTTPException(status_code=409, detail="E-Mail bereits vergeben")

    new_member = Member(
        name=member.name,
        email=member.email,
        mitglied_seit=member.mitglied_seit or date.today(),
    )
    db.add(new_member)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="E-Mail bereits vergeben") from exc
    db.refresh(new_member)
    return new_member


@router.put("/members/{member_id}", response_model=MemberOut)
def update_member(
    member_id: int,
    member: MemberUpdate,
    api_key: str = Depends(require_api_key),
    db: Session = Depends(get_db),
):
    existing = _get_member_or_404(db, member_id)

    data = member.model_dump(exclude_unset=True)
    if "email" in data:
        _check_email(data["email"])
        if _email_exists(db, data["email"], exclude_id=member_id):
            raise HTTPException(status_code=409, detail="E-Mail bereits vergeben")

    for field, value in data.items():
        setattr(existing, field, value)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="E-Mail bereits vergeben") from exc
    db.refresh(existing)
    return existing


@router.delete("/members/{member_id}", status_code=204)
def delete_member(
    member_id: int,
    api_key: str = Depends(require_api_key),
    db: Session = Depends(get_db),
):
    member = _get_member_or_404(db, member_id)
    db.delete(member)
    db.commit()
