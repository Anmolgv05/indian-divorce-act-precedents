"""Grounded summaries of search results for Section 10 Divorce Search.

Two modes, both built ONLY from the cases the search returned:
  * extractive (default): composed from the labels and matched passages. No network, no model.
  * llm (optional): set SUMMARY_LLM=1 and ANTHROPIC_API_KEY. The model is told to use only the
    supplied cases and cite them as [n]. Output is validated; on any failure we fall back to extractive.

Wire into FastAPI with:  from src.summarize import install; install(app)
Endpoint: POST /api/summary  {"query": str, "results": [ ...result dicts as returned by /api/search... ]}
"""
from __future__ import annotations

import json
import os
import re
import time
import urllib.request
from collections import Counter, deque
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

MAX_CASES = 8
PASSAGE_CHARS = 700

DISPOSAL = {
    "allowed": "allowed", "dismissed": "dismissed", "confirmed": "confirmed (decree upheld)",
    "not_confirmed": "not confirmed", "partly_allowed": "partly allowed", "remanded": "sent back for fresh decision",
    "disposed_of": "disposed of", "modified": "modified", "interim": "decided on an interim point",
}
GROUND = {
    "adultery": "adultery", "cruelty": "cruelty", "desertion": "desertion", "procedural": "a procedural question",
    "nullity_sec19": "nullity (Section 19)", "mutual_consent_10A": "mutual consent (Section 10A)",
    "constitutional_validity": "constitutional validity", "non_consummation": "non-consummation",
    "unsound_mind": "unsound mind", "wife_specific": "a wife-specific ground",
}
KEYS = {
    "doc_id": ("doc_id", "id", "tid", "docId"), "title": ("title", "case_title"), "year": ("year",),
    "disposal": ("disposal", "outcome"), "ended": ("marriage_dissolved", "dissolved", "marriage_ended"),
    "ground": ("primary_ground", "ground"),
    "passage": ("passage", "text", "snippet", "best_chunk", "matched_passage", "chunk", "excerpt"),
    "non_merits": ("non_merits", "is_non_merits", "nonMerits"),
}


def _get(d: dict, field: str, default=None):
    for k in KEYS[field]:
        if k in d and d[k] not in (None, ""):
            v = d[k]
            if isinstance(v, dict) and "text" in v:
                return v["text"]
            return v
    for sub in ("labels", "meta", "case"):
        if isinstance(d.get(sub), dict):
            for k in KEYS[field]:
                if k in d[sub] and d[sub][k] not in (None, ""):
                    v = d[sub][k]
                    if isinstance(v, dict) and "text" in v:
                        return v["text"]
                    return v
    return default



def normalize(results: list[dict]) -> list[dict]:
    out = []
    for i, r in enumerate(results[:MAX_CASES], 1):
        if not isinstance(r, dict):
            continue
        title = re.sub(r"\s+on\s+\d{1,2}\s+\w+,\s*\d{4}\s*$", "", str(_get(r, "title", "Untitled case")))
        out.append({
            "n": i, "doc_id": str(_get(r, "doc_id", "")), "title": title.strip(),
            "year": _get(r, "year"), "disposal": str(_get(r, "disposal", "unclear")),
            "ended": str(_get(r, "ended", "unclear")), "ground": str(_get(r, "ground", "unclear")),
            "non_merits": bool(_get(r, "non_merits", False)),
            "passage": re.sub(r"\s+", " ", str(_get(r, "passage", ""))).strip()[:PASSAGE_CHARS],
        })
    return out


def _best_sentence(passage: str, query: str, limit: int = 200) -> str:
    sents = [s.strip() for s in re.split(r"(?<=[.;])\s+", passage) if len(s.strip()) > 40]
    if not sents:
        return ""
    q = {w for w in re.findall(r"[a-z]{4,}", query.lower())}
    best = max(sents, key=lambda s: len(q & set(re.findall(r"[a-z]{4,}", s.lower()))))
    return best if len(best) <= limit else best[: limit - 1].rsplit(" ", 1)[0] + "…"


def _join(items: list[str]) -> str:
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def extractive_summary(query: str, cases: list[dict]) -> str:
    if not cases:
        return "No cases matched this search."
    n = len(cases)
    merits = [c for c in cases if not c["non_merits"]]
    years = [int(c["year"]) for c in cases if str(c["year"]).isdigit()]
    parts = []
    span = f", decided between {min(years)} and {max(years)}" if years else ""
    parts.append(f"This search returned {n} case{'s' if n != 1 else ''}{span}.")
    gs = Counter(c["ground"] for c in merits if c["ground"] in GROUND)
    if gs:
        top = [f"{GROUND[g]} ({k})" for g, k in gs.most_common(3)]
        parts.append(f"The main ground in the cases that decide the merits was {_join(top)}.")
    ds = Counter(c["disposal"] for c in merits if c["disposal"] in DISPOSAL)
    if ds:
        top = [f"{k} {DISPOSAL[d]}" for d, k in ds.most_common(3)]
        parts.append(f"Outcomes recorded: {_join(top)}.")
    known = [c for c in merits if c["ended"] in ("yes", "no")]
    if known:
        yes = sum(c["ended"] == "yes" for c in known)
        parts.append(f"In {len(known)} of these the court's order on whether the marriage ended could be read: it ended in {yes} and did not in {len(known) - yes}.")
    lines = []
    for c in cases[:3]:
        bits = []
        if c["ground"] in GROUND:
            bits.append(f"about {GROUND[c['ground']]}")
        if c["disposal"] in DISPOSAL:
            bits.append(DISPOSAL[c["disposal"]])
        if c["ended"] == "yes":
            bits.append("marriage ended")
        elif c["ended"] == "no":
            bits.append("marriage not ended")
        label = f"; {', '.join(bits)}" if bits else ""
        sent = _best_sentence(c["passage"], query)
        quote = f" It says: “{sent}”" if sent else ""
        yr = f" ({c['year']})" if c["year"] else ""
        lines.append(f"The closest match is {c['title']}{yr}{label} [{c['n']}].{quote}" if c is cases[0]
                     else f"Also relevant: {c['title']}{yr}{label} [{c['n']}].{quote}")
    return " ".join(parts) + "\n\n" + "\n\n".join(lines)


SYSTEM = (
    "You summarise search results from a database of Indian court judgments on Section 10 of the Indian Divorce Act, 1869. "
    "Use ONLY the numbered cases supplied. Never add facts, case names, numbers or law that are not in them. "
    "Write 120 to 180 words of plain prose in two short paragraphs. End every sentence that states a fact with the case number "
    "in square brackets, like [2]. Say what the cases have in common and where they differ. Do not predict outcomes, do not "
    "give a success rate and do not advise the reader. If the cases do not clearly answer the query, say so. "
    "Labels marked 'unclear' are unknown, not negative."
)


def _llm_call(query: str, cases: list[dict]) -> str:
    payload = {
        "model": os.environ.get("SUMMARY_MODEL", "claude-sonnet-5-5"), "max_tokens": 500, "system": SYSTEM,
        "messages": [{"role": "user", "content": "Query: " + query + "\n\nCases (JSON):\n" + json.dumps(cases, ensure_ascii=False)}],
    }
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages", data=json.dumps(payload).encode(),
        headers={"content-type": "application/json", "x-api-key": os.environ["ANTHROPIC_API_KEY"],
                 "anthropic-version": "2023-06-01"})
    with urllib.request.urlopen(req, timeout=25) as r:
        data = json.loads(r.read())
    return "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text").strip()


def validate_llm(text: str, n_cases: int) -> bool:
    cites = [int(x) for x in re.findall(r"\[(\d+)\]", text)]
    if not text or len(text) > 1800 or not cites or any(c < 1 or c > n_cases for c in cites):
        return False
    return not re.search(r"\b(you should|you will win|chances? of|likely to succeed|success rate)\b", text, re.I)


_calls: deque[float] = deque()


def _allow_llm(limit: int = 20, window: int = 60) -> bool:
    now = time.time()
    while _calls and now - _calls[0] > window:
        _calls.popleft()
    if len(_calls) >= limit:
        return False
    _calls.append(now)
    return True


def summarize(query: str, results: list[dict], llm=_llm_call) -> dict[str, Any]:
    cases = normalize(results)
    mode, text = "extractive", extractive_summary(query, cases)
    if cases and os.environ.get("SUMMARY_LLM") == "1" and os.environ.get("ANTHROPIC_API_KEY") and _allow_llm():
        try:
            cand = llm(query, cases)
            if validate_llm(cand, len(cases)):
                mode, text = "llm", cand
        except Exception:
            pass
    return {"mode": mode, "text": text, "n_cases": len(cases),
            "caveat": "Built only from the cases shown. Not a success rate and not legal advice."}


class SummaryRequest(BaseModel):
    query: str = Field(max_length=500)
    results: list[dict] = Field(default_factory=list, max_length=50)


router = APIRouter()


@router.post("/api/summary")
def api_summary(req: SummaryRequest):
    return summarize(req.query, req.results)


def install(app) -> None:
    """Include the router and move it ahead of any catch-all static mount."""
    before = len(app.router.routes)
    app.include_router(router)
    new = app.router.routes[before:]
    del app.router.routes[before:]
    app.router.routes[0:0] = new
