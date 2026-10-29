"""Parallel AI Client & Query Decomposition / Fallback Research Module.

Provides integration with Parallel AI (https://api.parallel.ai):
1. Query Decomposition: Breaks down complex legal scenarios for the local SLM (vector & TF-IDF search).
2. Low-Confidence Fallback: Deep web-grounded precedent research when local database response is poor.
3. Web Precedent Search: Citation-aware case discovery via Parallel AI Search API.
"""

from __future__ import annotations

import json
import logging
import os
import re
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional

logger = logging.getLogger("parallel_ai")

# Default API key provided for the project
DEFAULT_PARALLEL_API_KEY = "pcUARAJNAwKMEPfAnZyoMRJH_Xp277A1Hmjd7XDn"
API_BASE_URL = "https://api.parallel.ai/v1"


def get_api_key() -> str:
    """Returns the active Parallel AI API key."""
    return os.environ.get("PARALLEL_API_KEY", DEFAULT_PARALLEL_API_KEY).strip()


def decompose_query(query: str, timeout: int = 25) -> Dict[str, Any]:
    """Uses Parallel AI LLM to decompose a complex/conversational user query

    into statutory grounds, legal facts, relevant sections, and targeted SLM
    search queries.
    """
    api_key = get_api_key()
    if not api_key:
        return _heuristic_decomposition(query)

    prompt = (
        "You are an expert Indian matrimonial legal analyst assisting a legal search engine for Section 10 "
        "of the Indian Divorce Act, 1869 (Christian matrimonial law).\n"
        f"User Query / Scenario: \"{query}\"\n\n"
        "Decompose this scenario for a local Small Language Model (SLM / TF-IDF + sentence embedding search index).\n"
        "Return ONLY a valid JSON object (no markdown, no backticks, no prose outside JSON) with exactly these keys:\n"
        "{\n"
        '  "grounds": ["list of recognized statutory grounds, e.g. adultery, cruelty, desertion, non_consummation, unsound_mind, mutual_consent_10A, nullity_sec19"],\n'
        '  "statutory_sections": ["list of relevant sections under Indian Divorce Act, 1869, e.g. Section 10, Section 11 (co-respondent), Section 14 (condonation), Section 19, etc."],\n'
        '  "key_facts": ["concise list of factual claims extracted from query"],\n'
        '  "slm_search_queries": ["2 to 3 short keyword search phrases optimized for legal vector/TF-IDF retrieval"]\n'
        "}"
    )

    payload = {
        "model": "parallel",
        "input": prompt,
        "temperature": 0.15,
    }

    try:
        req = urllib.request.Request(
            f"{API_BASE_URL}/responses",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        text = ""
        output_items = data.get("output", [])
        for item in output_items:
            if item.get("type") == "message":
                for content in item.get("content", []):
                    if content.get("type") == "output_text":
                        text += content.get("text", "")

        # Extract JSON from potential markdown wrapping
        json_match = re.search(r"\{[\s\S]*\}", text)
        if json_match:
            parsed = json.loads(json_match.group(0))
            return {
                "ok": True,
                "source": "parallel_ai",
                "grounds": parsed.get("grounds", []),
                "statutory_sections": parsed.get("statutory_sections", []),
                "key_facts": parsed.get("key_facts", []),
                "slm_search_queries": parsed.get(
                    "slm_search_queries", [query]
                ),
                "raw_text": text,
            }
    except Exception as e:
        logger.warning(
            f"Parallel AI query decomposition failed or timed out: {e}"
        )

    return _heuristic_decomposition(query)


def _heuristic_decomposition(query: str) -> Dict[str, Any]:
    """Fallback query decomposition when API is unavailable."""
    from src.search import detect_query_grounds
    grounds = detect_query_grounds(query)
    sections = ["Section 10"]
    if "mutual_consent_10A" in grounds:
        sections.append("Section 10A")
    if "nullity_sec19" in grounds:
        sections.append("Section 19")
    if "condon" in query.lower():
        sections.append("Section 14")
    if "co-respondent" in query.lower() or "adulterer" in query.lower():
        sections.append("Section 11")

    return {
        "ok": True,
        "source": "heuristic_fallback",
        "grounds": grounds or ["unclear"],
        "statutory_sections": list(dict.fromkeys(sections)),
        "key_facts": [query],
        "slm_search_queries": [query],
        "raw_text": None,
    }


def fallback_precedent_research(
    query: str,
    top_score: float = 0.0,
    local_cases: Optional[List[Dict[str, Any]]] = None,
    timeout: int = 75,
) -> Dict[str, Any]:
    """Triggered when local SLM search produces a 'very bad' or low-confidence response
    (e.g. top_score < threshold or out-of-scope).
    Calls Parallel AI to perform web-grounded legal research over High Court / Supreme Court precedents
    and synthesize an authoritative legal answer with verified citations.
    """
    api_key = get_api_key()
    if not api_key:
        return {
            "ok": False,
            "error": "No Parallel AI API key configured",
            "fallback_used": False,
        }

    from src.search import detect_query_grounds
    detected_grounds = detect_query_grounds(query)

    case_context = ""
    if local_cases:
        matching_local = [
            c for c in local_cases
            if not detected_grounds or c.get("primary_ground") in detected_grounds or any(g in detected_grounds for g in c.get("grounds", []))
        ]
        if matching_local:
            case_context = "\nCorpus precedents on point:\n" + "\n".join(
                f"- {c.get('title', 'Unknown')} ({c.get('year', '')}): {c.get('primary_ground', '')}, outcome: {c.get('disposal', '')}"
                for c in matching_local[:3]
            )

    prompt = (
        f"You are an authoritative Indian legal precedent researcher specializing in the Indian Divorce Act, 1869 (Christian matrimonial law).\n"
        f"User Query / Factual Scenario: \"{query}\"\n{case_context}\n\n"
        f"Provide a concise, strictly grounded precedent assessment:\n"
        f"1. Applicable Statutory Provision & Grounds: State the exact applicable sub-clause of Section 10 (or relevant section like 10A, 19, etc.) of the Indian Divorce Act, 1869, and whether relief can be granted on these facts.\n"
        f"2. Leading Reported Precedents: Cite 2 to 3 real, reported High Court or Supreme Court precedents directly on point (by case name and year), explaining the core ratio decidendi.\n"
        f"3. Evidentiary Standard & Essential Legal Ingredients: State the specific burden of proof and statutory requirements necessary to establish this specific ground (do NOT discuss irrelevant fault grounds like desertion or adultery unless directly raised by the query).\n"
        f"Keep the answer concise, objective, authoritative, lawyer-grade, and strictly bound to the applicable ground."
    )

    payload = {
        "model": "parallel",
        "input": prompt,
        "temperature": 0.15,
    }

    try:
        req = urllib.request.Request(
            f"{API_BASE_URL}/responses",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        text = ""
        citations = []
        output_items = data.get("output", [])
        for item in output_items:
            if item.get("type") == "message":
                for content in item.get("content", []):
                    if content.get("type") == "output_text":
                        text += content.get("text", "")
                        for annot in content.get("annotations", []):
                            if annot.get("type") == "url_citation":
                                citations.append({
                                    "title": annot.get("title", ""),
                                    "url": annot.get("url", ""),
                                })

        return {
            "ok": True,
            "fallback_used": True,
            "source": "parallel_ai_deep_research",
            "research_synthesis": text.strip(),
            "citations": citations,
            "query": query,
            "local_top_score": top_score,
        }
    except Exception as e:
        logger.error(f"Parallel AI fallback research call failed: {e}")
        return {
            "ok": False,
            "fallback_used": False,
            "error": str(e),
            "query": query,
        }


def search_web_precedents(
    query: str,
    search_queries: Optional[List[str]] = None,
    timeout: int = 15,
) -> List[Dict[str, Any]]:
    """Calls Parallel AI Search API directly to retrieve live Indian Kanoon

    and High Court case law citations with excerpts.
    """
    api_key = get_api_key()
    if not api_key:
        return []

    queries = search_queries or [
        f"Section 10 Indian Divorce Act {query}",
        f"{query} Indian Kanoon High Court judgment",
    ]

    payload = {
        "objective": f"Find relevant High Court and Supreme Court precedents under Indian Divorce Act for: {query}",
        "search_queries": queries[:3],
    }

    try:
        req = urllib.request.Request(
            f"{API_BASE_URL}/search",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "x-api-key": api_key,
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        results = []
        for r in data.get("results", []):
            results.append({
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "publish_date": r.get("publish_date"),
                "excerpts": r.get("excerpts", []),
            })
        return results
    except Exception as e:
        logger.warning(f"Parallel AI search failed: {e}")
        return []
