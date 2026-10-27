"""Read-only case explorer API for Section 10 Divorce Search.

GET /api/cases            filtered, sorted, paged list + facet counts
GET /api/cases/{doc_id}   one case with a short excerpt from the end of the judgment

Reads data/labeled/cases.jsonl (labels) and data/parsed/cleaned_cases.jsonl (excerpt only).
Never returns full judgment text. Install with:  from src.explorer import install; install(app)
"""
from __future__ import annotations

import json
import os
import re
from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

DATA = Path(os.environ.get("S10_DATA", Path(__file__).resolve().parent.parent / "data"))
EXCERPT_CHARS = 450
router = APIRouter()


def _read_jsonl(path: Path):
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def _year(c: dict) -> Optional[int]:
    try:
        y = int(c.get("year"))
        return y if 1800 < y < 2100 else None
    except (TypeError, ValueError):
        return None


@lru_cache(maxsize=1)
def _cases() -> list[dict]:
    out = []
    for c in _read_jsonl(DATA / "labeled" / "cases.jsonl"):
        did = str(c.get("doc_id", ""))
        out.append({
            "doc_id": did, "title": str(c.get("title") or "Untitled case").strip(), "year": _year(c),
            "court": str(c.get("court") or "").strip(), "ground": str(c.get("primary_ground") or "unclear"),
            "disposal": str(c.get("disposal") or "unclear"), "ended": str(c.get("marriage_dissolved") or "unclear"),
            "relief": str(c.get("relief") or "unclear"), "non_merits": bool(c.get("non_merits", False)),
            "url": f"https://indiankanoon.org/doc/{did}/",
        })
    return out


@lru_cache(maxsize=1)
def _paras() -> dict[str, list]:
    return {str(c.get("doc_id")): c.get("paragraphs", []) for c in _read_jsonl(DATA / "parsed" / "cleaned_cases.jsonl")}


def _excerpt(doc_id: str) -> str:
    paras = _paras().get(doc_id, [])
    if not paras:
        path = DATA / "parsed" / f"{doc_id}.json"
        if path.exists():
            try:
                with path.open(encoding="utf-8") as f:
                    d = json.load(f)
                    paras = d.get("paragraphs", [])
            except Exception:
                pass
    if not paras:
        return ""
    try:
        from src.labels import clean_tail  # the same tail the labelling rules read
        text = clean_tail(paras)
    except Exception:
        text = " ".join(p.get("text", "") if isinstance(p, dict) else str(p) for p in paras)
    text = re.sub(r"\s+", " ", text).strip()
    return ("…" + text[-EXCERPT_CHARS:].split(" ", 1)[-1]) if len(text) > EXCERPT_CHARS else text


def _facets(cases: list[dict]) -> dict:
    f = lambda k: dict(sorted(Counter(c[k] for c in cases if c[k]).items(), key=lambda kv: (-kv[1], kv[0])))
    ys = [c["year"] for c in cases if c["year"]]
    return {"ground": f("ground"), "disposal": f("disposal"), "ended": f("ended"), "court": f("court"),
            "year_min": min(ys) if ys else None, "year_max": max(ys) if ys else None, "total": len(cases)}


@router.get("/api/cases")
def list_cases(q: str = Query("", max_length=200), ground: str = "", disposal: str = "", ended: str = "",
               court: str = "", year_min: Optional[int] = None, year_max: Optional[int] = None,
               include_non_merits: bool = True, sort: str = Query("year_desc", pattern="^(year_desc|year_asc|title)$"),
               page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=50)):
    items = _cases()
    ql = q.strip().lower()
    sel = [c for c in items
           if (not ql or ql in c["title"].lower() or ql == c["doc_id"])
           and (not ground or c["ground"] == ground) and (not disposal or c["disposal"] == disposal)
           and (not ended or c["ended"] == ended) and (not court or c["court"] == court)
           and (year_min is None or (c["year"] or 0) >= year_min) and (year_max is None or (c["year"] or 9999) <= year_max)
           and (include_non_merits or not c["non_merits"])]
    if sort == "title":
        sel.sort(key=lambda c: c["title"].lower())
    else:
        sel.sort(key=lambda c: (c["year"] or 0, c["title"].lower()), reverse=(sort == "year_desc"))
    total = len(sel)
    start = (page - 1) * page_size
    return {"total": total, "page": page, "page_size": page_size, "pages": max(1, -(-total // page_size)),
            "items": sel[start:start + page_size], "facets": _facets(items)}


@router.get("/api/cases/{doc_id}")
def get_case(doc_id: str):
    for c in _cases():
        if c["doc_id"] == doc_id:
            return {**c, "excerpt": _excerpt(doc_id)}
    raise HTTPException(status_code=404, detail="Case not found")


def install(app) -> None:
    """Include the router ahead of any catch-all static mount."""
    before = len(app.router.routes)
    app.include_router(router)
    new = app.router.routes[before:]
    del app.router.routes[before:]
    app.router.routes[0:0] = new
