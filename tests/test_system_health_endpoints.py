# -*- coding: utf-8 -*-
import tracemalloc
from unittest.mock import patch

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
    # Check that the uptime dictionary has the expected keys
    assert set(response.json()["uptime"].keys()) == {
        "Days",
        "Hours",
        "Minutes",
        "Seconds",
    }


def test_get_heapdump():
    tracemalloc.start()  # Start tracing memory allocations
    response = client.get("/api/health/heapdump")
    tracemalloc.stop()  # Stop tracing memory allocations
    assert response.status_code == 200
    assert "heap_dump" in response.json()
    # Check that each item in the heap dump has the expected keys
    for item in response.json()["heap_dump"]:
        assert set(item.keys()) == {"filename", "lineno", "size", "count"}


@patch("tracemalloc.stop")  # , side_effect=TracemallocNotStartedError())
def test_get_heapdump_tracemalloc_error(mock_start):
    response = client.get("/api/health/heapdump")
    assert response.status_code == 500
    assert "detail" in response.json()
