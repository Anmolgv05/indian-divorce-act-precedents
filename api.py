"""
Backend REST API for Section 10 Indian Divorce Act Precedent Search.
Provides endpoints for search queries, statistics, scope notices, and configuration.
"""

import os
import sys
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, Query, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Ensure repo root is on sys.path
REPO_ROOT = os.path.abspath(os.path.dirname(__file__))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from src.search import search, stats, out_of_scope_notice

app = FastAPI(
    title="Section 10 Indian Divorce Act Precedent Search API",
    description="Precedent search engine over Section 10 Indian Divorce Act case law",
    version="1.0.0"
)

# Enable CORS for local development and UI frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def prewarm_models():
    """Pre-loads search index and TF-IDF during startup."""
    try:
        from src.search import load_index, load_tfidf
        print("[Startup] Pre-warming index and TF-IDF matrices...")
        load_index()
        load_tfidf()
        print("[Startup] Index pre-warm completed successfully!")
    except Exception as e:
        print(f"[Startup Warning] Pre-warm deferred: {e}")


GROUND_CHOICES = [
    "All",
    "adultery",
    "cruelty",
    "desertion",
    "nullity_sec19",
    "mutual_consent_10A",
    "non_consummation",
    "unsound_mind",
    "conversion",
    "procedural",
    "constitutional_validity"
]

SAMPLE_QUERIES = [
    "husband alleges wife deserted him for three years without reasonable cause",
    "wife seeks divorce on ground of husband living in adultery",
    "husband treated wife with physical and mental cruelty making cohabitation impossible",
    "marriage not consummated due to respondent wilful refusal",
    "joint petition under section 10A for dissolution of marriage by mutual consent",
    "restitution of conjugal rights under section 32 without reasonable excuse",
    "petition for declaration of nullity of marriage under section 19",
    "divorce under Hindu Marriage Act section 13 cruelty",  # Out-of-scope trigger demo
]


class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query string")
    ground: Optional[str] = Field("All", description="Filter by ground, or 'All'")
    year_min: int = Field(1869, description="Minimum judgment year")
    year_max: int = Field(2026, description="Maximum judgment year")
    include_non_merits: bool = Field(False, description="Include non-merits procedural cases")
    show_duplicates: bool = Field(False, description="Show possible duplicate records")
    top_k: int = Field(5, ge=1, le=50, description="Number of results to retrieve")


def _sanitize_data(obj: Any) -> Any:
    """Recursively converts NumPy types and NaNs to standard Python types for clean JSON."""
    if isinstance(obj, dict):
        return {k: _sanitize_data(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_sanitize_data(v) for v in obj]
    elif hasattr(obj, "item"):  # numpy scalars
        return obj.item()
    return obj


def _execute_search(
    query: str,
    ground: Optional[str] = "All",
    year_min: int = 1869,
    year_max: int = 2026,
    include_non_merits: bool = False,
    show_duplicates: bool = False,
    top_k: int = 5
) -> Dict[str, Any]:
    clean_query = query.strip()
    if not clean_query:
        return {
            "query": "",
            "results": [],
            "stats": {
                "n_retrieved": 0,
                "ended": 0,
                "did_not_end": 0,
                "unclear_or_na": 0,
                "low_confidence": False,
                "out_of_scope_notice": None,
                "summary": "No query provided."
            },
            "out_of_scope_notice": None,
            "low_confidence": False,
            "top_score": 0.0
        }

    GROUND_ALIASES = {
        "all": None,
        "all grounds": None,
        "nullity (s.19)": "nullity_sec19",
        "nullity": "nullity_sec19",
        "mutual consent (s.10a)": "mutual_consent_10A",
        "mutual consent": "mutual_consent_10A",
        "non-consummation": "non_consummation",
        "unsound mind": "unsound_mind",
        "constitutional validity": "constitutional_validity",
        "restitution non-compliance": "restitution_noncompliance"
    }
    if ground:
        norm = ground.strip().lower()
        if norm in GROUND_ALIASES:
            target_ground = GROUND_ALIASES[norm]
        elif norm in ("all", "none"):
            target_ground = None
        else:
            target_ground = ground
    else:
        target_ground = None
    year_range = (int(year_min), int(year_max))

    try:
        from src.multilingual import translate_query
        effective_query, detected_lang = translate_query(clean_query)
    except Exception:
        effective_query, detected_lang = clean_query, None

    results = search(
        query=effective_query,
        top_k=int(top_k),
        ground=target_ground,
        year_range=year_range,
        include_non_merits=bool(include_non_merits),
        include_duplicates=bool(show_duplicates),
        mode="hybrid"
    )

    st = stats(results, query=effective_query)
    if detected_lang:
        st["multilingual"] = {
            "original_query": clean_query,
            "translated_query": effective_query,
            "detected_language": detected_lang,
        }
    top_sc = float(getattr(results, "top_score", (results[0]["score"] if results else 0.0)))
    low_conf = bool(st.get("low_confidence", False))
    scope_notice = st.get("out_of_scope_notice")

    # Ensure all results contain cleanly serializable primitives
    clean_results = []
    for r in results:
        card = dict(r)
        if "score" in card:
            card["score"] = float(card["score"])
        # Format "unclear" as "not determined" in display-oriented representations if needed,
        # but keep original key for frontend to format badges uniformly.
        clean_results.append(_sanitize_data(card))

    return {
        "query": clean_query,
        "effective_query": effective_query if detected_lang else None,
        "detected_language": detected_lang,
        "results": clean_results,
        "stats": _sanitize_data(st),
        "out_of_scope_notice": scope_notice,
        "low_confidence": low_conf,
        "top_score": top_sc
    }


@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "Section 10 Divorce Search API"}


@app.get("/api/config")
def get_config():
    return {
        "grounds": GROUND_CHOICES,
        "sample_queries": SAMPLE_QUERIES,
        "year_min_default": 1869,
        "year_max_default": 2026,
        "default_top_k": 5,
        "scope_notice": "Only Indian Divorce Act (Christian marriages) judgments. Similar past cases, not predictions, not legal advice."
    }


@app.get("/api/stats")
def get_corpus_stats():
    import json
    with open(os.path.join(REPO_ROOT, "data/labeled/cases.jsonl")) as f:
        cases = [json.loads(line) for line in f]
    ground_counts = {}
    years = [c.get("year") for c in cases if c.get("year")]
    for c in cases:
        g = c.get("primary_ground", "unclear")
        ground_counts[g] = ground_counts.get(g, 0) + 1
    return {
        "total_cases": len(cases),
        "year_range": [min(years) if years else 1869, max(years) if years else 2026],
        "grounds": ground_counts,
    }



@app.post("/api/search")
def search_post(payload: SearchRequest):
    return _execute_search(
        query=payload.query,
        ground=payload.ground,
        year_min=payload.year_min,
        year_max=payload.year_max,
        include_non_merits=payload.include_non_merits,
        show_duplicates=payload.show_duplicates,
        top_k=payload.top_k
    )


@app.get("/api/search")
def search_get(
    query: str = Query(..., description="Search query string"),
    ground: Optional[str] = Query("All", description="Filter by ground, or 'All'"),
    year_min: int = Query(1869, description="Minimum judgment year"),
    year_max: int = Query(2026, description="Maximum judgment year"),
    include_non_merits: bool = Query(False, description="Include non-merits procedural cases"),
    show_duplicates: bool = Query(False, description="Show possible duplicate records"),
    top_k: int = Query(5, ge=1, le=50, description="Number of results to retrieve")
):
    return _execute_search(
        query=query,
        ground=ground,
        year_min=year_min,
        year_max=year_max,
        include_non_merits=include_non_merits,
        show_duplicates=show_duplicates,
        top_k=top_k
    )


try:
    from src.reader_api import router as reader_router
except ImportError:
    from reader_api import router as reader_router
app.include_router(reader_router)

from src.summarize import install as _install_summary
_install_summary(app)

from src.explorer import install as _install_explorer
_install_explorer(app)

# Mount static assets if frontend production build exists
dist_dir = os.path.join(REPO_ROOT, "frontend", "dist")
if os.path.exists(dist_dir):
    app.mount("/", StaticFiles(directory=dist_dir, html=True), name="static_frontend")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run("api:app", host="0.0.0.0", port=port)
