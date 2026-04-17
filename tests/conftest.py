# tests/conftest.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app

# Test database setup

TEST_DATABASE_URL = "sqlite:///:memory"  # Use a separate SQLite database for testing, :memory: creates a new database in RAM for each test run, ensuring isolation and preventing interference with the production database

test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="function")   # runs once per test function, ensuring that each test gets a fresh database setup

def db_Session():
    Base.metadata.create_all(bind=test_engine)  # Create the database tables before each test
    db = TestSessionLocal()  # Create a new database session for the test
    try:
        yield db  # Yield the database session to the test function
    finally:
        db.close()  # Close the database session after the test is done
        Base.metadata.drop_all(bind=test_engine)  # Drop the database tables after each test to ensure a clean state for the next test

@pytest.fixture(scope="function")
def client(db_Session):
    # Override the get_db dependency to use the test database session
    def override_get_db():
        try:
            yield db_Session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db  # Override the get_db dependency in the FastAPI app to use the test database session, allowing the API routes to interact with the test database during testing
    with TestClient(app) as c:  # Create a TestClient instance for making requests to the FastAPI app during testing, which will use the overridden get_db dependency to interact with the test database
        yield c  # Yield the TestClient instance to the test functions for making API requests
        app.dependency_overrides.clear()  # Clear the dependency overrides after the test is done to ensure that subsequent tests are not affected by the overrides, maintaining isolation between tests
        