from fastapi.testclient import TestClient
from src.app.main import app

client = TestClient(app)

# Override dependencies to speed up tests and avoid external calls
from src.app.deps import local_index

def _empty_index():
    """Return an empty index so that /ask does not call external services."""
    return {}

app.dependency_overrides[local_index] = _empty_index


# New endpoint tests

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_stats():
    response = client.get("/stats")
    assert response.status_code == 200
    data = response.json()
    # With the empty index override we expect zeros but simply assert keys exist
    assert "files" in data and "chunks" in data
    assert isinstance(data["files"], int)
    assert isinstance(data["chunks"], int)


def test_ask_empty_query():
    response = client.post("/ask", json={"query": ""})
    assert response.status_code == 400


def test_ask_no_results():
    response = client.post("/ask", json={"query": "alguma pergunta que nao existe"})
    assert response.status_code == 200
    payload = response.json()
    assert "answer" in payload
    assert "sources" in payload
    assert isinstance(payload["sources"], list)
