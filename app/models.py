"""SQLAlchemy ORM models for books, members and loans."""

from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    titel: Mapped[str] = mapped_column(String(200))
    autor: Mapped[str] = mapped_column(String(200))
    isbn: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    erscheinungsjahr: Mapped[int] = mapped_column(Integer)
    anzahl_exemplare: Mapped[int] = mapped_column(Integer)


class Member(Base):
    __tablename__ = "members"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    mitglied_seit: Mapped[date] = mapped_column(Date)


class Loan(Base):
    __tablename__ = "loans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"))
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"))
    ausgeliehen_am: Mapped[date] = mapped_column(Date)
    faellig_am: Mapped[date] = mapped_column(Date)
    zurueckgegeben_am: Mapped[date | None] = mapped_column(Date, nullable=True)
