"""Deep harvest of all Indian Kanoon judgments citing Section 10 of Indian Divorce Act, 1869.

Crawls all pages of citedby:1387951 (900+ decisions across all Indian High Courts & Supreme Court),
downloads HTML, validates substantive discussion, labels grounds & outcomes,
and saves to data/parsed/ and data/labeled/cases.jsonl.
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
logger = logging.getLogger("deep_harvest")

DATA_DIR = REPO_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PARSED_DIR = DATA_DIR / "parsed"
LABELED_FILE = DATA_DIR / "labeled" / "cases.jsonl"
URLS_FILE = DATA_DIR / "urls.txt"

STATUTE_DOC_ID = "1387951"  # Section 10 of Indian Divorce Act on Indian Kanoon

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 (LegalAcademicResearch/2.0)",
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


def crawl_citedby_pages(existing_ids: set[str], max_pages: int = 95) -> list[dict]:
    """Crawls all search pages of citedby:1387951 on Indian Kanoon."""
    candidates = []
    seen = set(existing_ids)
    consecutive_empty = 0

    logger.info(f"Starting crawl of up to {max_pages} pages for citedby:{STATUTE_DOC_ID}...")

    for page in range(max_pages):
        url = f"https://indiankanoon.org/search/?formInput=citedby:{STATUTE_DOC_ID}&pagenum={page}"
        logger.info(f"Fetching citedby page {page}: {url}")
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=14) as resp:
                if resp.status != 200:
                    logger.warning(f"Page {page} returned status {resp.status}")
                    time.sleep(3.0)
                    continue
                html = resp.read().decode("utf-8", errors="replace")

            soup = BeautifulSoup(html, "lxml")
            titles = soup.find_all(class_="result_title")
            if not titles:
                consecutive_empty += 1
                if consecutive_empty >= 2:
                    logger.info(f"Page {page} had 0 results. End of listings reached.")
                    break
                continue

            consecutive_empty = 0
            new_on_page = 0
            for t in titles:
                a = t.find("a")
                if not a or not a.get("href"):
                    continue
                m = re.search(r"/(?:doc|docfragment)/(\d+)/", a["href"])
                if not m:
                    continue
                doc_id = m.group(1)
                if doc_id == STATUTE_DOC_ID or doc_id in seen:
                    continue

                seen.add(doc_id)
                candidates.append({
                    "doc_id": doc_id,
                    "title": a.get_text(strip=True),
                    "url": f"https://indiankanoon.org/doc/{doc_id}/",
                })
                new_on_page += 1

            logger.info(f"  Page {page}: found {len(titles)} results, {new_on_page} new candidates (total new: {len(candidates)})")
            time.sleep(1.2)
        except Exception as e:
            logger.warning(f"Error fetching page {page}: {e}")
            time.sleep(3.0)

    logger.info(f"Total new unique candidate decisions discovered: {len(candidates)}")
    return candidates


def fetch_and_process_case(candidate: dict) -> dict | None:
    doc_id = candidate["doc_id"]
    url = candidate["url"]
    raw_path = RAW_DIR / f"{doc_id}.html"

    # 1. Fetch raw HTML
    html = ""
    if raw_path.exists():
        with open(raw_path, "r", encoding="utf-8") as f:
            html = f.read()
    else:
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=14) as resp:
                if resp.status == 200:
                    html = resp.read().decode("utf-8", errors="replace")
                    RAW_DIR.mkdir(parents=True, exist_ok=True)
                    with open(raw_path, "w", encoding="utf-8") as f:
                        f.write(html)
                else:
                    return None
            time.sleep(1.2)
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
        return None

    paras = [str(p.get("text", "")).strip() for p in parsed.get("paragraphs", [])]
    paras = [p for p in paras if p]
    if len(paras) < 3:
        return None

    para_objs = [{"p_id": f"p_{i}", "text": text} for i, text in enumerate(paras)]

    # 4. Save parsed JSON for reader & HF sync
    PARSED_DIR.mkdir(parents=True, exist_ok=True)
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

    logger.info(f"Retained [{doc_id}] {title[:48]} | {court} | {primary_ground} | {disposal}")
    return case_record


def run_deep_harvest(max_pages: int = 95):
    existing_ids = load_existing_doc_ids()
    logger.info(f"Starting deep harvest with {len(existing_ids)} existing cases.")

    candidates = crawl_citedby_pages(existing_ids, max_pages=max_pages)
    new_cases = []

    for idx, c in enumerate(candidates):
        res = fetch_and_process_case(c)
        if res:
            new_cases.append(res)
            # Incrementally append to cases.jsonl so nothing is lost if interrupted
            with open(LABELED_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(res, ensure_ascii=False) + "\n")
            if URLS_FILE.exists():
                with open(URLS_FILE, "a", encoding="utf-8") as f:
                    f.write(res["url"] + "\n")
        if (idx + 1) % 20 == 0:
            logger.info(f"Progress: evaluated {idx + 1}/{len(candidates)} candidates, {len(new_cases)} retained.")

    logger.info(f"Deep harvest completed: added {len(new_cases)} new substantive judgments.")
    return len(new_cases)


if __name__ == "__main__":
    pages = int(sys.argv[1]) if len(sys.argv) > 1 else 95
    count = run_deep_harvest(max_pages=pages)
    print(f"\nDeep harvest finished: {count} new cases added to corpus.")
