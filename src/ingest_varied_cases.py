"""Ingest varied Section 10 Indian Divorce Act judgments from under-represented courts and grounds.

Gathers candidate URLs, filters out duplicates, scrapes HTML, validates substantive discussion,
labels grounds & outcomes, writes to data/parsed/ and data/labeled/cases.jsonl.
"""

from __future__ import annotations

import os
import re
import sys
import time
import json
import logging
import urllib.request
import urllib.parse
from pathlib import Path
from bs4 import BeautifulSoup

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

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
logger = logging.getLogger("ingest")

DATA_DIR = REPO_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PARSED_DIR = DATA_DIR / "parsed"
LABELED_FILE = DATA_DIR / "labeled" / "cases.jsonl"
URLS_FILE = DATA_DIR / "urls.txt"

SEARCH_QUERIES = [
    # Supreme Court & High Courts with low coverage
    ("\"section 10\" \"divorce act\" doctypes:supremecourt", "Supreme Court"),
    ("\"section 10\" \"divorce act\" doctypes:delhi", "Delhi High Court"),
    ("\"section 10\" \"divorce act\" doctypes:kolkata", "Calcutta High Court"),
    ("\"section 10\" \"divorce act\" doctypes:allahabad", "Allahabad High Court"),
    ("\"section 10\" \"divorce act\" doctypes:mp", "Madhya Pradesh High Court"),
    ("\"section 10\" \"divorce act\" doctypes:gauhati", "Gauhati High Court"),
    ("\"section 10\" \"divorce act\" doctypes:patna", "Patna High Court"),
    ("\"section 10\" \"divorce act\" doctypes:rajasthan", "Rajasthan High Court"),
    ("\"section 10\" \"divorce act\" doctypes:himachal_pradesh", "Himachal Pradesh High Court"),
    ("\"section 10\" \"divorce act\" doctypes:chhattisgarh", "Chhattisgarh High Court"),
    ("\"section 10\" \"divorce act\" doctypes:jharkhand", "Jharkhand High Court"),
    ("\"section 10\" \"divorce act\" doctypes:orissa", "Orissa High Court"),
    # Grounds with lower counts in current corpus
    ("\"section 10A\" \"divorce act\" \"mutual consent\"", "Section 10A Mutual Consent"),
    ("\"section 10\" \"divorce act\" \"conversion\" Christian", "Conversion"),
    ("\"section 10\" \"divorce act\" \"unsound mind\"", "Unsound Mind"),
    ("\"section 10\" \"divorce act\" \"desertion\" \"two years\"", "Desertion"),
    ("\"section 19\" \"divorce act\" \"nullity\" Christian", "Section 19 Nullity"),
    ("\"section 10\" \"divorce act\" \"restitution of conjugal rights\"", "Restitution"),
    ("\"section 10\" \"divorce act\" \"venereal disease\"", "Venereal Disease"),
    ("\"section 10\" \"divorce act\" \"leprosy\"", "Leprosy"),
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 (CourseworkResearch/2.0)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


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


def search_kanoon_for_candidates(existing_ids: set[str], max_per_query: int = 15) -> list[dict]:
    candidates = []
    seen = set(existing_ids)

    for query_str, category in SEARCH_QUERIES:
        logger.info(f"Searching: {category} ({query_str})")
        for page in range(2):  # Pages 0 and 1
            search_url = f"https://indiankanoon.org/search/?formInput={urllib.parse.quote(query_str)}&pagenum={page}"
            try:
                req = urllib.request.Request(search_url, headers=HEADERS)
                with urllib.request.urlopen(req, timeout=12) as resp:
                    if resp.status != 200:
                        break
                    html = resp.read().decode("utf-8", errors="replace")
                
                soup = BeautifulSoup(html, "lxml")
                titles = soup.find_all(class_="result_title")
                if not titles:
                    break

                for t in titles:
                    a = t.find("a")
                    if not a or not a.get("href"):
                        continue
                    m = re.search(r"/(?:doc|docfragment)/(\d+)/", a["href"])
                    if not m:
                        continue
                    doc_id = m.group(1)
                    if doc_id in seen or doc_id == "1387951":  # Skip statute itself
                        continue

                    title_text = a.get_text(strip=True)
                    # Skip evident criminal or unrelated statutes in titles
                    if any(x in title_text.lower() for x in ["motor vehicles", "negotiable instruments", "hindu marriage act", "industrial disputes"]):
                        continue

                    seen.add(doc_id)
                    candidates.append({
                        "doc_id": doc_id,
                        "title": title_text,
                        "url": f"https://indiankanoon.org/doc/{doc_id}/",
                        "category": category,
                    })

                time.sleep(1.5)  # Polite crawling delay
            except Exception as e:
                logger.warning(f"Error querying {category} page {page}: {e}")
                time.sleep(2.0)
                break

    logger.info(f"Collected {len(candidates)} new candidate cases to evaluate.")
    return candidates


def fetch_and_process_case(candidate: dict) -> dict | None:
    doc_id = candidate["doc_id"]
    url = candidate["url"]
    raw_path = RAW_DIR / f"{doc_id}.html"

    # 1. Fetch HTML if not already cached
    html = ""
    if raw_path.exists():
        with open(raw_path, "r", encoding="utf-8") as f:
            html = f.read()
    else:
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=15) as resp:
                if resp.status == 200:
                    html = resp.read().decode("utf-8", errors="replace")
                    RAW_DIR.mkdir(parents=True, exist_ok=True)
                    with open(raw_path, "w", encoding="utf-8") as f:
                        f.write(html)
                else:
                    return None
            time.sleep(1.5)
        except Exception as e:
            logger.warning(f"Failed to fetch {doc_id}: {e}")
            return None

    if not html:
        return None

    # 2. Parse judgment structure
    parsed = parse_judgment_html(html, doc_id, url)
    full_text = " ".join(p.get("text", "") for p in parsed.get("paragraphs", []))
    parsed["full_text"] = full_text

    # 3. Apply substantive Section 10 filter
    is_subst, reason = is_substantive_sec10_case(parsed)
    if not is_subst:
        logger.info(f"Skipping {doc_id} ({candidate['title'][:40]}...): {reason}")
        return None

    paras = [str(p.get("text", "")).strip() for p in parsed.get("paragraphs", [])]
    paras = [p for p in paras if p]
    if len(paras) < 3:
        return None

    # 4. Save parsed JSON for reader & HF sync
    PARSED_DIR.mkdir(parents=True, exist_ok=True)
    para_objs = [{"p_id": f"p_{i}", "text": text} for i, text in enumerate(paras)]
    parsed_record = {
        "doc_id": doc_id,
        "url": url,
        "title": parsed.get("title", candidate["title"]),
        "court": parsed.get("court", ""),
        "date": parsed.get("date", ""),
        "year": parsed.get("year", 0),
        "citations": parsed.get("citations", ""),
        "paragraphs": para_objs,
    }
    with open(PARSED_DIR / f"{doc_id}.json", "w", encoding="utf-8") as f:
        json.dump(parsed_record, f, ensure_ascii=False, indent=2)

    # 5. Label grounds, outcomes, and rhetorical segments
    year = parsed.get("year", 0)
    title = parsed.get("title", candidate["title"])
    court = parsed.get("court", "")

    grounds_list, primary_ground, scores = label_grounds(para_objs, year=year, title=title)
    disposal = label_disposal(para_objs)
    ended, relief = label_dissolved(para_objs, ground=primary_ground)
    petitioner_gender = label_petitioner(para_objs, title=title)
    non_merits = is_non_merits(title, para_objs)
    segments = segment_paragraphs(para_objs)
    statutes = extract_statutes_cited(full_text)

    case_record = {
        "doc_id": str(doc_id),
        "url": url,
        "title": title,
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

    logger.info(f"Retained new case [{doc_id}] {title[:50]} | Court: {court} | Ground: {primary_ground} | Outcome: {disposal}")
    return case_record


def run_ingestion():
    existing_ids = load_existing_doc_ids()
    logger.info(f"Existing corpus has {len(existing_ids)} cases.")

    candidates = search_kanoon_for_candidates(existing_ids)
    new_cases = []

    for c in candidates:
        res = fetch_and_process_case(c)
        if res:
            new_cases.append(res)

    logger.info(f"Successfully processed {len(new_cases)} new substantive cases.")

    if new_cases:
        # Append to cases.jsonl
        with open(LABELED_FILE, "a", encoding="utf-8") as f:
            for case in new_cases:
                f.write(json.dumps(case, ensure_ascii=False) + "\n")
        logger.info(f"Appended {len(new_cases)} cases to {LABELED_FILE}")

        # Update urls.txt
        if URLS_FILE.exists():
            with open(URLS_FILE, "a", encoding="utf-8") as f:
                for case in new_cases:
                    f.write(case["url"] + "\n")

    return len(new_cases)


if __name__ == "__main__":
    count = run_ingestion()
    print(f"\nIngestion finished: {count} new cases added to corpus.")
