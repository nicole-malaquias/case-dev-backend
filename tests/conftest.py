import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.app import app
from app.database import get_session
from app.models import Base
from app.settings import Settings


@pytest.fixture
def session():
    engine = create_engine(Settings().DATABASE_URL)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(engine)
    with Session() as session:
        yield session
        session.rollback()

    Base.metadata.drop_all(engine)


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()
