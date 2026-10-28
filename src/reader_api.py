"""Full-text endpoint for the case reader.

Switched OFF by default. Set the environment variable FULLTEXT=1 to serve judgment text.
Only cases in the retained corpus (data/labeled/cases.jsonl) can be read, one at a time;
there is deliberately no bulk endpoint.
"""
from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, HTTPException

router = APIRouter()

ROOT = Path(__file__).resolve().parent.parent
PARSED = ROOT / "data" / "parsed"
LABELED = ROOT / "data" / "labeled" / "cases.jsonl"


def fulltext_enabled() -> bool:
    return os.environ.get("FULLTEXT", "0").strip() == "1"


@lru_cache(maxsize=1)
def _retained_ids() -> frozenset:
    ids = set()
    if LABELED.exists():
        with open(LABELED, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    ids.add(str(json.loads(line)["doc_id"]))
    return frozenset(ids)


try:
    from src.hf_sync import fetch_case_from_hf, get_case_hf_url
except ImportError:
    try:
        from hf_sync import fetch_case_from_hf, get_case_hf_url
    except ImportError:
        def fetch_case_from_hf(doc_id: str): return None
        def get_case_hf_url(doc_id: str): return f"https://huggingface.co/datasets/AnmolGV/section10-divorce-corpus/blob/main/parsed/{doc_id}.json"


@router.get("/api/reader/status")
def reader_status():
    return {"enabled": fulltext_enabled()}


@router.get("/api/cases/{doc_id}/text")
def case_text(doc_id: str):
    if not fulltext_enabled():
        raise HTTPException(status_code=404, detail="Full-text reading is switched off on this server.")
    if not doc_id.isdigit():
        raise HTTPException(status_code=400, detail="Invalid case id.")
    if doc_id not in _retained_ids():
        raise HTTPException(status_code=404, detail="Case not found in this database.")

    path = PARSED / f"{doc_id}.json"
    data = None
    source = "local"

    if path.exists():
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = None

    if not data:
        # Fall back to Hugging Face
        data = fetch_case_from_hf(doc_id, cache_locally=True)
        if data:
            source = "huggingface"

    if not data:
        raise HTTPException(status_code=404, detail="Full text is not available for this case.")

    paras = [str(p.get("text", "")).strip() for p in data.get("paragraphs", [])]
    paras = [p for p in paras if p]
    return {
        "doc_id": doc_id,
        "title": data.get("title") or "Untitled",
        "court": data.get("court") or "",
        "year": data.get("year"),
        "source_url": f"https://indiankanoon.org/doc/{doc_id}/",
        "hf_url": get_case_hf_url(doc_id),
        "source": source,
        "paragraphs": paras,
    }
