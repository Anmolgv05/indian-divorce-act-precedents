"""High-throughput multi-worker ingest engine for all collected Divorce Act judgments.

Fetches HTML, validates matrimonial discussion, segments paragraphs,
labels statutory grounds and judicial outcomes, and appends to cases.jsonl.
"""

from __future__ import annotations

import os
import re
import sys
import time
import json
import logging
import threading
import urllib.request
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

from src.scrape import parse_judgment_html
from src.parse_clean import is_substantive_sec10_case
from src.labels import (
    label_grounds,
    label_disposal,
    label_dissolved,
    label_petitioner,
    is_non_merits,
    segment_paragraphs,
    clean_tail,
)
from src.segment_label import extract_statutes_cited

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("massive_ingest")

DATA_DIR = REPO_ROOT / "data"
PARSED_DIR = DATA_DIR / "parsed"
LABELED_FILE = DATA_DIR / "labeled" / "cases.jsonl"
CANDIDATES_FILE = DATA_DIR / "all_candidates.json"

PARSED_DIR.mkdir(parents=True, exist_ok=True)
LABELED_FILE.parent.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 (NationalJudicialCorpus/3.0)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

FILE_LOCK = threading.Lock()


def load_existing_doc_ids() -> set[str]:
    existing = set()
    if LABELED_FILE.exists():
        with open(LABELED_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        c = json.loads(line)
                        existing.add(str(c["doc_id"]))
                    except Exception:
                        pass
    return existing


def is_matrimonial_case(title: str, text: str) -> bool:
    """Checks if the document discusses matrimonial / divorce proceedings."""
    lower_title = title.lower()
    # Reject acts, rules, and law commission reports
    if any(x in lower_title for x in ["in the parsi", "in the special marriage", "law commission", "rules, 20", "act, 20", "amendment act"]):
        return False
    
    lower_text = text.lower()
    # Must mention Divorce Act or matrimonial relief
    has_act = ("divorce act" in lower_text or "divorce" in lower_text or "marriage" in lower_text or "matrimonial" in lower_text)
    has_parties = ("appellant" in lower_text or "respondent" in lower_text or "petitioner" in lower_text or "husband" in lower_text or "wife" in lower_text)
    return has_act and has_parties


def process_single_candidate(candidate: dict) -> dict | None:
    doc_id = str(candidate["doc_id"])
    url = candidate["url"]
    title = candidate["title"]

    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=14) as resp:
            if resp.status != 200:
                return None
            html = resp.read().decode("utf-8", errors="replace")

        parsed = parse_judgment_html(html, doc_id=doc_id, url=url)
        full_text = parsed.get("full_text") or parsed.get("text", "")
        if len(full_text.split()) < 60:
            return None

        # Check court and title
        court = parsed.get("court", "Unknown Court")
        if any(x in court for x in ["Act", "Section", "Tribunal"]):
            return None

        # Validate matrimonial context
        if not is_matrimonial_case(parsed.get("title", title), full_text):
            return None

        # Validate substantive discussion
        is_subst, reason = is_substantive_sec10_case(parsed)
        # Even if not purely Section 10, if it discusses matrimonial dissolution / nullity under Divorce Act, retain
        lower = full_text.lower()
        if not is_subst and ("divorce act" in lower and any(g in lower for g in ["cruelty", "desertion", "adultery", "mutual consent", "nullity", "judicial separation", "restitution"])):
            is_subst = True

        if not is_subst:
            return None

        paras = parsed.get("paragraphs", [])
        if paras and isinstance(paras[0], dict):
            para_objs = paras
        else:
            para_objs = [{"p_id": f"p_{i+1}", "text": str(p)} for i, p in enumerate(paras)]
        if not para_objs:
            para_objs = [{"p_id": "p_1", "text": full_text}]

        raw_year = parsed.get("year")
        try:
            year = int(raw_year) if raw_year else None
        except Exception:
            year = None

        grounds_list, primary_ground, _ = label_grounds(para_objs, year=year, title=parsed.get("title", title))
        disposal = label_disposal(para_objs)
        ended, relief = label_dissolved(para_objs, ground=primary_ground)
        petitioner_gender = label_petitioner(para_objs)
        non_merits = is_non_merits(parsed.get("title", title), para_objs)
        segments = segment_paragraphs(para_objs)
        statutes = extract_statutes_cited(full_text)

        case_record = {
            "doc_id": doc_id,
            "url": url,
            "title": parsed.get("title", title),
            "court": court,
            "date": parsed.get("date", ""),
            "year": year,
            "citations": parsed.get("citations", ""),
            "grounds": grounds_list,
            "primary_ground": primary_ground,
            "disposal": disposal,
            "marriage_dissolved": ended,
            "relief": relief,
            "non_merits": non_merits,
            "possible_duplicate_of": None,
            "petitioner_gender": petitioner_gender,
            "statutes_cited": statutes,
            "precedents_cited": [],
            "segments": segments,
            "judgment_tail": clean_tail(para_objs, min_chars=450),
            "label_source": {
                "grounds": "rule",
                "disposal": "rule",
                "marriage_dissolved": "rule",
                "relief": "rule",
                "petitioner": "rule",
            },
        }

        # Write parsed individual JSON
        parsed_out = PARSED_DIR / f"{doc_id}.json"
        with open(parsed_out, "w", encoding="utf-8") as f:
            json.dump({**parsed, "doc_id": doc_id, "url": url}, f, ensure_ascii=False)

        cleaned_record = {
            "doc_id": str(doc_id),
            "title": parsed.get("title", title),
            "court": court,
            "date": parsed.get("date", ""),
            "year": year,
            "citations": parsed.get("citations", ""),
            "url": url,
            "paragraphs": para_objs,
            "num_paragraphs": len(para_objs),
            "full_text": full_text,
            "structured_tags": parsed.get("structured_tags", []),
            "possible_duplicate_of": None,
        }

        # Thread-safe append to cases.jsonl and cleaned_cases.jsonl
        with FILE_LOCK:
            with open(LABELED_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(case_record, ensure_ascii=False) + "\n")
            with open(DATA_DIR / "parsed" / "cleaned_cases.jsonl", "a", encoding="utf-8") as f:
                f.write(json.dumps(cleaned_record, ensure_ascii=False) + "\n")

        logger.info(f"Retained [{doc_id}] {parsed.get('title', title)[:45]} | {court} | {primary_ground} | {disposal}")
        return case_record

    except Exception as e:
        logger.debug(f"Error processing {doc_id}: {e}")
        return None


def run_massive_ingest(max_workers: int = 4):
    existing_ids = load_existing_doc_ids()
    logger.info(f"Existing corpus size: {len(existing_ids)} cases.")

    if not CANDIDATES_FILE.exists():
        logger.error(f"Candidates file {CANDIDATES_FILE} does not exist yet. Run collector first.")
        return 0

    candidates = {}
    for _ in range(5):
        try:
            with open(CANDIDATES_FILE, "r", encoding="utf-8") as f:
                candidates = json.load(f)
            break
        except Exception:
            time.sleep(0.5)

    # Filter to un-ingested candidates
    to_process = [c for c in candidates.values() if str(c["doc_id"]) not in existing_ids]
    logger.info(f"Found {len(to_process)} un-ingested candidate judgments to process.")

    retained_count = 0
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_single_candidate, c): c["doc_id"] for c in to_process}
        for idx, fut in enumerate(as_completed(futures)):
            res = fut.result()
            if res:
                retained_count += 1
            if (idx + 1) % 25 == 0:
                logger.info(f"Progress: Evaluated {idx + 1}/{len(to_process)} candidates, {retained_count} newly retained.")

    total_now = len(load_existing_doc_ids())
    logger.info(f"Finished massive ingestion: Added {retained_count} cases. Total corpus now: {total_now} judgments.")
    return retained_count


if __name__ == "__main__":
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    run_massive_ingest(max_workers=workers)
