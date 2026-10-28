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
    q_lower = query.lower()
    grounds = []
    if any(w in q_lower for w in ["adultery", "affair", "paramour"]):
        grounds.append("adultery")
    if any(w in q_lower for w in ["cruelty", "torture", "beating", "abusive", "harass"]):
        grounds.append("cruelty")
    if any(w in q_lower for w in ["desert", "left", "abandoned", "separate"]):
        grounds.append("desertion")
    if any(w in q_lower for w in ["consummat", "impoten", "erectile"]):
        grounds.append("non_consummation")
    if any(w in q_lower for w in ["mutual", "consent", "10a"]):
        grounds.append("mutual_consent_10A")
    if any(w in q_lower for w in ["nullity", "null", "void", "fraud"]):
        grounds.append("nullity_sec19")

    sections = ["Section 10"]
    if "condon" in q_lower:
        sections.append("Section 14")
    if "co-respondent" in q_lower or "adulterer" in q_lower:
        sections.append("Section 11")

    return {
        "ok": True,
        "source": "heuristic_fallback",
        "grounds": grounds or ["unclear"],
        "statutory_sections": sections,
        "key_facts": [query],
        "slm_search_queries": [query],
        "raw_text": None,
    }


def fallback_precedent_research(
    query: str,
    top_score: float = 0.0,
    local_cases: Optional[List[Dict[str, Any]]] = None,
    timeout: int = 35,
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

    case_context = ""
    if local_cases:
        case_context = "\nLocal database returned weak matches:\n" + "\n".join(
            f"- {c.get('title', 'Unknown')} ({c.get('year', '')}): {c.get('disposal', '')}, score: {c.get('score', 0)}"
            for c in local_cases[:3]
        )

    prompt = (
        f"A user queried an Indian Christian Divorce law precedent search engine (Section 10 of Indian Divorce Act, 1869):\n"
        f"Query: \"{query}\"\n"
        f"Retrieval confidence was very low (top match score: {top_score:.3f}).{case_context}\n\n"
        f"Please provide an authoritative, citation-grounded precedent research answer:\n"
        f"1. State the exact legal position under Section 10 of the Indian Divorce Act, 1869 (and relevant High Court / Supreme Court interpretations).\n"
        f"2. Cite 2 to 3 leading reported High Court or Supreme Court precedents by name and year, explaining the ratio decidendi.\n"
        f"3. Highlight critical statutory bars or evidentiary rules (e.g., standard of proof, condonation under s.14, co-respondent joinder under s.11, two-year desertion threshold).\n"
        f"Keep the tone objective, structured, and lawyer-grade."
    )

    payload = {
        "model": "parallel",
        "input": prompt,
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
