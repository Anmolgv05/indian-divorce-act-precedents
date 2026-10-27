"""
Tests for Section 10 Indian Divorce Act Precedent Search REST API.
"""

import pytest
from fastapi.testclient import TestClient
from api import app

client = TestClient(app)


def test_api_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"


def test_api_config():
    res = client.get("/api/config")
    assert res.status_code == 200
    data = res.json()
    assert "grounds" in data
    assert "sample_queries" in data
    assert "adultery" in data["grounds"]
    assert "cruelty" in data["grounds"]
    assert "mutual_consent_10A" in data["grounds"]


def test_api_search_post():
    payload = {
        "query": "husband alleges wife deserted him for three years without reasonable cause",
        "top_k": 3,
        "ground": "All"
    }
    res = client.post("/api/search", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "results" in data
    assert "stats" in data
    assert len(data["results"]) <= 3
    assert data["stats"]["n_retrieved"] == len(data["results"])
    assert "ended" in data["stats"]
    assert "did_not_end" in data["stats"]
    assert "unclear_or_na" in data["stats"]


def test_api_search_get():
    res = client.get("/api/search?query=wife+accuses+husband+of+adultery&top_k=2")
    assert res.status_code == 200
    data = res.json()
    assert "results" in data
    assert len(data["results"]) <= 2


def test_api_out_of_scope_notice():
    payload = {
        "query": "divorce under Hindu Marriage Act section 13 cruelty",
        "top_k": 2
    }
    res = client.post("/api/search", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["out_of_scope_notice"] is not None
    assert "Hindu Marriage Act" in data["out_of_scope_notice"]


def test_api_empty_query():
    payload = {
        "query": "   ",
        "top_k": 5
    }
    res = client.post("/api/search", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["results"] == []
    assert data["stats"]["n_retrieved"] == 0
