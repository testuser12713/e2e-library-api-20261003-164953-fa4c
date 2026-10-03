"""Books router — CRUD and search with pagination."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.auth import require_api_key
from app.database import get_db
from app.models import Book
from app.schemas import BookCreate, BookOut, BookUpdate

router = APIRouter(tags=["books"])


@router.get("/books")
def list_books(
    q: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    filters = []
    if q:
        pattern = f"%{q}%"
        filters.append(or_(Book.titel.ilike(pattern), Book.autor.ilike(pattern)))

    count_stmt = select(func.count()).select_from(Book)
    if filters:
        count_stmt = count_stmt.where(*filters)
    total = db.scalar(count_stmt) or 0

    stmt = select(Book)
    if filters:
        stmt = stmt.where(*filters)
    items = db.scalars(stmt.order_by(Book.id).offset(offset).limit(limit)).all()

    return {
        "items": [BookOut.model_validate(item) for item in items],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/books/{book_id}", response_model=BookOut)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Buch nicht gefunden")
    return book


@router.post("/books", status_code=201, response_model=BookOut)
def create_book(
    book: BookCreate,
    api_key: str = Depends(require_api_key),
    db: Session = Depends(get_db),
):
    if db.scalar(select(Book).where(Book.isbn == book.isbn)) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="ISBN existiert bereits")

    new_book = Book(**book.model_dump())
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book


@router.put("/books/{book_id}", response_model=BookOut)
def update_book(
    book_id: int,
    book: BookUpdate,
    api_key: str = Depends(require_api_key),
    db: Session = Depends(get_db),
):
    db_book = db.get(Book, book_id)
    if db_book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Buch nicht gefunden")

    data = book.model_dump(exclude_unset=True)
    if "isbn" in data and data["isbn"] != db_book.isbn:
        conflict = db.scalar(select(Book).where(Book.isbn == data["isbn"], Book.id != book_id))
        if conflict is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="ISBN existiert bereits"
            )

    for field, value in data.items():
        setattr(db_book, field, value)

    db.commit()
    db.refresh(db_book)
    return db_book


@router.delete("/books/{book_id}", status_code=204)
def delete_book(
    book_id: int,
    api_key: str = Depends(require_api_key),
    db: Session = Depends(get_db),
):
    book = db.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Buch nicht gefunden")

    db.delete(book)
    db.commit()
