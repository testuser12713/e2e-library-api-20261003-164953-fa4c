"""Books router — endpoint stubs to be implemented by the books ticket."""

from fastapi import APIRouter, Depends, HTTPException, Query

from app.auth import require_api_key
from app.schemas import BookCreate, BookOut, BookUpdate

router = APIRouter(tags=["books"])


@router.get("/books")
def list_books(
    q: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    raise HTTPException(status_code=501, detail="Bücher-CRUD implementiert diesen Endpunkt")


@router.get("/books/{book_id}", response_model=BookOut)
def get_book(book_id: int):
    raise HTTPException(status_code=501, detail="Bücher-CRUD implementiert diesen Endpunkt")


@router.post("/books", status_code=201, response_model=BookOut)
def create_book(book: BookCreate, api_key: str = Depends(require_api_key)):
    raise HTTPException(status_code=501, detail="Bücher-CRUD implementiert diesen Endpunkt")


@router.put("/books/{book_id}", response_model=BookOut)
def update_book(book_id: int, book: BookUpdate, api_key: str = Depends(require_api_key)):
    raise HTTPException(status_code=501, detail="Bücher-CRUD implementiert diesen Endpunkt")


@router.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int, api_key: str = Depends(require_api_key)):
    raise HTTPException(status_code=501, detail="Bücher-CRUD implementiert diesen Endpunkt")
