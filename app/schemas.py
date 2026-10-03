"""Pydantic v2 schemas for the library API."""

from datetime import date

from pydantic import BaseModel, ConfigDict


class BookCreate(BaseModel):
    titel: str
    autor: str
    isbn: str
    erscheinungsjahr: int
    anzahl_exemplare: int


class BookUpdate(BaseModel):
    titel: str | None = None
    autor: str | None = None
    isbn: str | None = None
    erscheinungsjahr: int | None = None
    anzahl_exemplare: int | None = None


class BookOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    titel: str
    autor: str
    isbn: str
    erscheinungsjahr: int
    anzahl_exemplare: int


class MemberCreate(BaseModel):
    name: str
    email: str
    mitglied_seit: date | None = None


class MemberUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    mitglied_seit: date | None = None


class MemberOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    mitglied_seit: date


class LoanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    book_id: int
    member_id: int
    ausgeliehen_am: date
    faellig_am: date
    zurueckgegeben_am: date | None
