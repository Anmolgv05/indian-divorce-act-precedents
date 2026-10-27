from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.testclient import TestClient

import src.summarize as S

R = [
    {"doc_id": 1, "title": "A vs B on 3 May, 1999", "year": 1999, "primary_ground": "cruelty", "disposal": "allowed",
     "marriage_dissolved": "yes", "passage": "The respondent treated the petitioner with persistent cruelty over several years, which amounts to legal cruelty."},
    {"doc_id": 2, "title": "C vs D", "year": 2005, "primary_ground": "cruelty", "disposal": "dismissed", "marriage_dissolved": "no", "passage": ""},
    {"doc_id": 3, "title": "E vs F", "year": 2010, "primary_ground": "procedural", "disposal": "remanded", "marriage_dissolved": "unclear",
     "non_merits": True, "passage": "x"},
]


def test_extractive_counts_and_cites():
    out = S.summarize("cruelty by husband", R)
    t = out["text"]
    assert out["mode"] == "extractive" and "3 cases" in t and "between 1999 and 2010" in t
    assert "it ended in 1 and did not in 1" in t          # non-merits case excluded from outcome stats
    assert "A vs B (1999)" in t and "[1]" in t and "persistent cruelty" in t
    assert "on 3 May" not in t                             # date stripped from title


def test_empty_and_unknown_labels_not_negative():
    assert S.summarize("q", [])["text"] == "No cases matched this search."
    out = S.summarize("q", [{"title": "X", "marriage_dissolved": "unclear", "disposal": "unclear"}])
    assert "ended" not in out["text"].split("\n\n")[0].replace("marriage ended", "")  # no 'ended in 0' claim


def test_llm_validation_rejects_bad_output():
    assert S.validate_llm("Cases agree on cruelty [1].", 3)
    assert not S.validate_llm("No citations here.", 3)
    assert not S.validate_llm("Cruelty [7].", 3)
    assert not S.validate_llm("You should file now [1].", 3)


def test_llm_used_only_when_enabled_and_valid(monkeypatch):
    monkeypatch.setenv("SUMMARY_LLM", "1"); monkeypatch.setenv("ANTHROPIC_API_KEY", "k")
    S._calls.clear()
    assert S.summarize("q", R, llm=lambda q, c: "Both cruelty cases differ on outcome [1][2].")["mode"] == "llm"
    assert S.summarize("q", R, llm=lambda q, c: "ungrounded")["mode"] == "extractive"
    def boom(q, c): raise RuntimeError("net")
    assert S.summarize("q", R, llm=boom)["mode"] == "extractive"
    monkeypatch.delenv("SUMMARY_LLM")
    assert S.summarize("q", R, llm=lambda q, c: "ok [1].")["mode"] == "extractive"


def test_route_wins_over_catch_all_mount(tmp_path):
    (tmp_path / "index.html").write_text("hi")
    app = FastAPI()
    app.mount("/", StaticFiles(directory=tmp_path, html=True), name="static")
    S.install(app)
    r = TestClient(app).post("/api/summary", json={"query": "cruelty", "results": R})
    assert r.status_code == 200 and r.json()["mode"] == "extractive"
