import os, tempfile
_fd, _db_path = tempfile.mkstemp(suffix=".db")
os.close(_fd)
os.environ["DATABASE_URL"] = f"sqlite:///{_db_path}"
os.environ["JWT_SECRET"] = "pytest-secret-not-for-production"
os.environ["CLIENT_ORIGIN"] = "http://testserver"
os.environ["ENVIRONMENT"] = "test"
from fastapi.testclient import TestClient
from app.database import Base, engine
from app.main import app
import pytest

@pytest.fixture()
def client():
    Base.metadata.drop_all(bind=engine); Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client: yield test_client
    Base.metadata.drop_all(bind=engine)

@pytest.fixture()
def registered_user(client):
    response = client.post("/api/auth/register", json={"name":"Test User","email":"test@example.com","password":"correct-horse-battery"})
    assert response.status_code == 201
    return response.json()

@pytest.fixture()
def auth_headers(registered_user): return {"Authorization": f"Bearer {registered_user['token']}"}
