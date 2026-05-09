"""Pytest fixtures shared by all backend tests."""

from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import create_app


@pytest.fixture()
def engine():
    eng = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    Base.metadata.create_all(eng)
    try:
        yield eng
    finally:
        Base.metadata.drop_all(eng)
        eng.dispose()


@pytest.fixture()
def db_session(engine) -> Generator[Session, None, None]:
    factory = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)
    session = factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(engine) -> Generator[TestClient, None, None]:
    factory = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)

    def override_get_db() -> Generator[Session, None, None]:
        db = factory()
        try:
            yield db
        finally:
            db.close()

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db
    # Bypass startup init_db (already created tables on the in-memory engine).
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
