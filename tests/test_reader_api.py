import json
import sys
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import reader_api  # noqa: E402


@pytest.fixture()
def client(tmp_path, monkeypatch):
    parsed = tmp_path / "parsed"
    parsed.mkdir()
    (parsed / "111.json").write_text(json.dumps({
        "title": "A vs B on 1 May, 2001", "court": "Madras High Court", "year": 2001,
        "paragraphs": [{"text": "First para."}, {"text": "  "}, {"text": "Second para."}],
    }), encoding="utf-8")
    (parsed / "222.json").write_text(json.dumps({"title": "Dropped", "paragraphs": [{"text": "x"}]}), encoding="utf-8")
    labeled = tmp_path / "cases.jsonl"
    labeled.write_text(json.dumps({"doc_id": 111}) + "\n" + json.dumps({"doc_id": 333}) + "\n", encoding="utf-8")
    monkeypatch.setattr(reader_api, "PARSED", parsed)
    monkeypatch.setattr(reader_api, "LABELED", labeled)
    reader_api._retained_ids.cache_clear()
    app = FastAPI()
    app.include_router(reader_api.router)
    return TestClient(app)


def test_off_by_default(client, monkeypatch):
    monkeypatch.delenv("FULLTEXT", raising=False)
    assert client.get("/api/reader/status").json() == {"enabled": False}
    assert client.get("/api/cases/111/text").status_code == 404


def test_serves_retained_case_when_on(client, monkeypatch):
    monkeypatch.setenv("FULLTEXT", "1")
    assert client.get("/api/reader/status").json() == {"enabled": True}
    r = client.get("/api/cases/111/text")
    assert r.status_code == 200
    d = r.json()
    assert d["paragraphs"] == ["First para.", "Second para."]
    assert d["source_url"].endswith("/111/")


def test_refuses_dropped_case_and_bad_ids(client, monkeypatch):
    monkeypatch.setenv("FULLTEXT", "1")
    assert client.get("/api/cases/222/text").status_code == 404   # parsed but not retained
    assert client.get("/api/cases/333/text").status_code == 404   # retained but no parsed file
    assert client.get("/api/cases/..%2Fsecret/text").status_code in (400, 404)
    assert client.get("/api/cases/abc/text").status_code == 400
