import pytest
from fastapi.testclient import TestClient
from app.main import app

# Fixtures to add:
#   - test DB session (SQLite in-memory or separate test Postgres)
#   - authenticated TestClient (with pre-generated JWT)
#   - sample user, sample ticket

@pytest.fixture
def client():
    return TestClient(app)
