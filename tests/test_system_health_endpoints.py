import tracemalloc

from fastapi.testclient import TestClient

from example.main import app  # replace with the name of your FastAPI app

client = TestClient(app)


def test_health_status():
    response = client.get("/api/health/status")
    assert response.status_code == 200
    assert response.json() == {"status": "UP"}


def test_get_uptime():
    response = client.get("/api/health/uptime")
    assert response.status_code == 200
    assert "uptime" in response.json()


def test_get_heapdump():
    tracemalloc.start()  # Start tracing memory allocations
    response = client.get("/api/health/heapdump")
    tracemalloc.stop()  # Stop tracing memory allocations
    assert response.status_code == 200
    assert "heap_dump" in response.json()
