"""Collect all candidate Section 10 / Indian Divorce Act judgments from Indian Kanoon.

Gathers doc_ids across all available pages for citedby:1387951, grounds queries,
and High Court specific doctypes to build a comprehensive candidate set.
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
DATA_DIR = REPO_ROOT / "data"
CANDIDATES_FILE = DATA_DIR / "all_candidates.json"
LABELED_FILE = DATA_DIR / "labeled" / "cases.jsonl"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("collector")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 (LegalScholar/3.0)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

SEARCH_TASKS = [
    # citedby:1387951 (Section 10 of Indian Divorce Act) - 928 decisions
    ("citedby:1387951", 95, "Section 10 citedby"),
    
    # Core Divorce Act grounds across all courts
    ("\"Indian Divorce Act\" \"Section 10\"", 35, "Section 10 queries"),
    ("\"Indian Divorce Act\" \"Section 10A\"", 30, "Section 10A mutual consent"),
    ("\"Indian Divorce Act\" \"Section 19\"", 25, "Section 19 nullity"),
    ("\"Indian Divorce Act\" \"Section 22\"", 20, "Section 22 judicial separation"),
    ("\"Indian Divorce Act\" \"Section 32\"", 20, "Section 32 restitution"),
    ("\"Indian Divorce Act\" \"Section 37\"", 20, "Section 37 alimony"),
    ("\"Indian Divorce Act\" \"Section 11\"", 20, "Section 11 co-respondent"),
    ("\"Indian Divorce Act\" cruelty", 30, "Cruelty ground"),
    ("\"Indian Divorce Act\" desertion", 30, "Desertion ground"),
    ("\"Indian Divorce Act\" adultery", 30, "Adultery ground"),
    ("\"Indian Divorce Act\" \"nullity of marriage\"", 20, "Nullity ground"),
    ("\"Divorce Act, 1869\" dissolution", 30, "Divorce Act 1869 dissolution"),
    ("\"Divorce Act\" \"Christian Marriage\"", 25, "Christian Marriage disputes"),
    
    # Individual High Courts & Supreme Court
    ("\"Indian Divorce Act\" doctypes:kerala", 25, "Kerala HC"),
    ("\"Indian Divorce Act\" doctypes:madras", 25, "Madras HC"),
    ("\"Indian Divorce Act\" doctypes:bombay", 25, "Bombay HC"),
    ("\"Indian Divorce Act\" doctypes:delhi", 25, "Delhi HC"),
    ("\"Indian Divorce Act\" doctypes:kolkata", 25, "Calcutta HC"),
    ("\"Indian Divorce Act\" doctypes:allahabad", 25, "Allahabad HC"),
    ("\"Indian Divorce Act\" doctypes:karnataka", 25, "Karnataka HC"),
    ("\"Indian Divorce Act\" doctypes:supremecourt", 25, "Supreme Court"),
    ("\"Indian Divorce Act\" doctypes:jharkhand", 20, "Jharkhand HC"),
    ("\"Indian Divorce Act\" doctypes:orissa", 20, "Orissa HC"),
    ("\"Indian Divorce Act\" doctypes:rajasthan", 20, "Rajasthan HC"),
    ("\"Indian Divorce Act\" doctypes:punjab-haryana", 20, "Punjab & Haryana HC"),
    ("\"Indian Divorce Act\" doctypes:gauhati", 20, "Gauhati HC"),
    ("\"Indian Divorce Act\" doctypes:patna", 20, "Patna HC"),
    ("\"Indian Divorce Act\" doctypes:himachal_pradesh", 20, "Himachal Pradesh HC"),
    ("\"Indian Divorce Act\" doctypes:mp", 20, "Madhya Pradesh HC"),
    ("\"Indian Divorce Act\" doctypes:andhra", 20, "Andhra HC"),
    ("\"Indian Divorce Act\" doctypes:telangana", 20, "Telangana HC"),
    ("\"Indian Divorce Act\" doctypes:gujarat", 20, "Gujarat HC"),
    ("\"Indian Divorce Act\" doctypes:chhattisgarh", 20, "Chhattisgarh HC"),
    ("\"Indian Divorce Act\" doctypes:uttaranchal", 15, "Uttarakhand HC"),
    ("\"Indian Divorce Act\" doctypes:jammu", 15, "J&K HC"),
]


def load_existing_ids() -> set[str]:
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


def collect_all_candidates():
    existing_ids = load_existing_ids()
    logger.info(f"Existing corpus contains {len(existing_ids)} cases.")

    candidates: dict[str, dict] = {}
    if CANDIDATES_FILE.exists():
        try:
            with open(CANDIDATES_FILE, "r", encoding="utf-8") as f:
                candidates = json.load(f)
            logger.info(f"Loaded {len(candidates)} previously collected candidates from disk.")
        except Exception:
            candidates = {}

    total_new = 0

    for query_str, max_pages, label in SEARCH_TASKS:
        logger.info(f"=== Searching: {label} [{query_str}] up to {max_pages} pages ===")
        consecutive_empty = 0
        for page in range(max_pages):
            url = f"https://indiankanoon.org/search/?formInput={urllib.parse.quote(query_str)}&pagenum={page}"
            try:
                req = urllib.request.Request(url, headers=HEADERS)
                with urllib.request.urlopen(req, timeout=12) as resp:
                    if resp.status != 200:
                        logger.warning(f"  Page {page} returned status {resp.status}")
                        time.sleep(2.0)
                        continue
                    html = resp.read().decode("utf-8", errors="replace")

                soup = BeautifulSoup(html, "lxml")
                titles = soup.find_all(class_="result_title")
                if not titles:
                    consecutive_empty += 1
                    if consecutive_empty >= 2:
                        logger.info(f"  Reached end of listings at page {page}.")
                        break
                    continue

                consecutive_empty = 0
                page_added = 0
                for t in titles:
                    a_tag = t.find("a")
                    if not a_tag or not a_tag.get("href"):
                        continue
                    href = a_tag["href"]
                    m = re.search(r"/doc(?:fragment)?/(\d+)/", href)
                    if not m:
                        continue
                    doc_id = m.group(1)

                    # Skip known statutes or already retained cases
                    if doc_id in existing_ids:
                        continue

                    title_text = a_tag.get_text(" ", strip=True)
                    # Skip acts / sections / law commission reports
                    if any(x in title_text.lower() for x in ["law commission", "in the parsi", "in the special marriage", "rules, 20", "act, 20"]):
                        continue

                    if doc_id not in candidates:
                        candidates[doc_id] = {
                            "doc_id": doc_id,
                            "title": title_text,
                            "url": f"https://indiankanoon.org/doc/{doc_id}/",
                            "source_query": query_str,
                            "query_label": label,
                        }
                        page_added += 1
                        total_new += 1

                time.sleep(0.5)

            except Exception as e:
                logger.warning(f"  Error fetching page {page} for '{label}': {e}")
                time.sleep(2.0)

        logger.info(f"  Finished {label}. Total candidate pool now: {len(candidates)} (new: {total_new})")
        # Save snapshot periodically
        with open(CANDIDATES_FILE, "w", encoding="utf-8") as f:
            json.dump(candidates, f, ensure_ascii=False, indent=2)

    logger.info(f"\n==========================================")
    logger.info(f"COLLECTION COMPLETE: {len(candidates)} unique new candidates ready to ingest!")
    logger.info(f"==========================================")
    return candidates


if __name__ == "__main__":
    collect_all_candidates()
