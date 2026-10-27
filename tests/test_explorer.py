import json

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path, monkeypatch):
    (tmp_path / "labeled").mkdir(); (tmp_path / "parsed").mkdir()
    rows = [
        {"doc_id": 1, "title": "Ruth vs Dr. M. Danial on 29 November, 1993", "year": 1993, "court": "Madras High Court",
         "primary_ground": "adultery", "disposal": "remanded", "marriage_dissolved": "unclear", "relief": "unclear", "non_merits": False},
        {"doc_id": 2, "title": "A vs B on 3 May, 1999", "year": 1999, "court": "Kerala High Court",
         "primary_ground": "cruelty", "disposal": "allowed", "marriage_dissolved": "yes", "relief": "dissolution", "non_merits": False},
        {"doc_id": 3, "title": "Transfer petition C vs D", "year": 2017, "court": "Kerala High Court",
         "primary_ground": "procedural", "disposal": "allowed", "marriage_dissolved": "unclear", "relief": "none", "non_merits": True},
        {"doc_id": 4, "title": "No year case", "court": "", "primary_ground": "cruelty"},
    ]
    (tmp_path / "labeled" / "cases.jsonl").write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
    long_tail = "word " * 300 + "The appeal is allowed and the decree is set aside."
    (tmp_path / "parsed" / "cleaned_cases.jsonl").write_text(
        json.dumps({"doc_id": 2, "paragraphs": [{"text": "Intro."}, {"text": long_tail}]}), encoding="utf-8")
    import src.explorer as E
    monkeypatch.setattr(E, "DATA", tmp_path)
    E._cases.cache_clear(); E._paras.cache_clear()
    app = FastAPI(); E.install(app)
    return TestClient(app)


def test_list_default_sorted_newest_first_and_facets(client):
    d = client.get("/api/cases").json()
    assert d["total"] == 4 and [c["doc_id"] for c in d["items"]][:3] == ["3", "2", "1"]
    assert d["facets"]["ground"]["cruelty"] == 2 and d["facets"]["year_min"] == 1993 and d["facets"]["year_max"] == 2017


def test_filters_combine(client):
    assert client.get("/api/cases?ground=cruelty&ended=yes").json()["total"] == 1
    assert client.get("/api/cases?court=Kerala High Court&include_non_merits=false").json()["total"] == 1
    assert client.get("/api/cases?year_min=1995&year_max=2000").json()["total"] == 1
    assert [c["doc_id"] for c in client.get("/api/cases?q=ruth").json()["items"]] == ["1"]
    assert [c["doc_id"] for c in client.get("/api/cases?q=4").json()["items"]] == ["4"]   # doc id match


def test_paging_and_validation(client):
    d = client.get("/api/cases?page_size=2&page=2").json()
    assert d["pages"] == 2 and len(d["items"]) == 2
    assert client.get("/api/cases?page_size=500").status_code == 422
    assert client.get("/api/cases?sort=bogus").status_code == 422


def test_detail_has_short_excerpt_only(client):
    d = client.get("/api/cases/2").json()
    assert d["url"].endswith("/doc/2/") and d["excerpt"].endswith("decree is set aside.") and len(d["excerpt"]) < 520
    assert client.get("/api/cases/1").json()["excerpt"] == ""
    assert client.get("/api/cases/999").status_code == 404
