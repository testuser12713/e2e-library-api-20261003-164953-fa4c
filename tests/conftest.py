"""Shared pytest fixtures: isolated in-memory test database.

The development database is never touched: ``DATABASE_URL`` is pointed at an
in-memory SQLite before the app is imported, and ``get_db`` is overridden with a
session bound to a dedicated ``StaticPool`` engine whose tables are recreated
before every test.
"""

import os

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["API_KEY"] = "test-api-key"

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models
from app.database import get_db
from app.main import app

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def _database():
    models.Base.metadata.drop_all(bind=engine)
    models.Base.metadata.create_all(bind=engine)
    yield
    models.Base.metadata.drop_all(bind=engine)
