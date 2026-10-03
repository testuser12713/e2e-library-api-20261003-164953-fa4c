"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import models
from app.database import engine
from app.routers import books, loans, members, overdue, returns


@asynccontextmanager
async def lifespan(app: FastAPI):
    models.Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Bibliotheksausleihe API", lifespan=lifespan)

app.include_router(books.router)
app.include_router(members.router)
app.include_router(loans.router)
app.include_router(returns.router)
app.include_router(overdue.router)


@app.get("/health")
def health():
    return {"status": "ok"}
