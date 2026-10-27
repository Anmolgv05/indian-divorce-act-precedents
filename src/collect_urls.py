"""
Collect candidate judgment URLs citing Section 10 of Indian Divorce Act, 1869 from Indian Kanoon.
Splits collected URLs into shards for parallel scraping.
"""

import os
import re
import sys
import time
import yaml
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup


def load_config(config_path: str = "config.yaml") -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_session(user_agent: str) -> requests.Session:
    session = requests.Session()
    session.headers.update({
        "User-Agent": user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    })
    retries = Retry(
        total=5,
        backoff_factor=2.0,
        status_forcelist=[429, 500, 502, 503, 504],
        raise_on_status=False
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def extract_doc_ids_from_search(html: str) -> list[tuple[str, str]]:
    """Extracts (doc_id, title) tuples from search result HTML."""
    soup = BeautifulSoup(html, "lxml")
    results = []
    titles = soup.find_all(class_="result_title")
    for t in titles:
        a = t.find("a")
        if not a or not a.get("href"):
            continue
        href = a["href"]
        match = re.search(r"/(?:doc|docfragment)/(\d+)/", href)
        if match:
            doc_id = match.group(1)
            title = t.get_text(strip=True)
            results.append((doc_id, title))
    return results


def collect_urls(target_count: int = 200, statute_doc_id: str = "1387951") -> list[str]:
    cfg = load_config()
    scraping_cfg = cfg.get("scraping", {})
    paths_cfg = cfg.get("paths", {})
    urls_file = paths_cfg.get("urls_file", "data/urls.txt")

    delay = scraping_cfg.get("delay_seconds", 2.0)
    user_agent = scraping_cfg.get("user_agent", "CourseworkResearch/1.0")

    session = get_session(user_agent)

    # Resume from existing urls.txt if present
    seen_ids = set()
    collected_urls = []
    if os.path.exists(urls_file):
        with open(urls_file, "r", encoding="utf-8") as f:
            for line in f:
                u = line.strip()
                if u:
                    m = re.search(r"/doc/(\d+)/", u)
                    if m:
                        seen_ids.add(m.group(1))
                    collected_urls.append(u)
        print(f"Loaded {len(collected_urls)} existing URLs from {urls_file}")

    page = len(collected_urls) // 10
    max_pages = 60

    print(f"Targeting {target_count} unique candidate judgments citing Section 10...")
    print(f"Query: citedby:{statute_doc_id} starting at page {page} with {delay}s polite delay")

    while len(collected_urls) < target_count and page < max_pages:
        search_url = f"https://indiankanoon.org/search/?formInput=citedby:{statute_doc_id}&pagenum={page}"
        print(f"Fetching search page {page}: {search_url}")
        
        try:
            resp = session.get(search_url, timeout=15)
            if resp.status_code != 200:
                print(f"Page {page} returned status {resp.status_code}. Waiting 5s...")
                time.sleep(5)
                continue
            html = resp.text
        except Exception as e:
            print(f"Connection error on page {page}: {e}. Waiting 5s and continuing...")
            time.sleep(5)
            page += 1
            continue

        doc_items = extract_doc_ids_from_search(html)
        if not doc_items:
            print(f"No results found on page {page}. Reached end of listing.")
            break

        new_on_page = 0
        for doc_id, title in doc_items:
            if doc_id == statute_doc_id:
                continue
            if doc_id not in seen_ids:
                seen_ids.add(doc_id)
                full_url = f"https://indiankanoon.org/doc/{doc_id}/"
                collected_urls.append(full_url)
                new_on_page += 1
                if len(collected_urls) >= target_count:
                    break

        print(f"  Page {page} yielded {new_on_page} new URLs. Total collected so far: {len(collected_urls)}")
        page += 1
        time.sleep(delay)

    return collected_urls


def split_into_shards(urls: list[str], shard_count: int, shards_dir: str) -> list[str]:
    """Splits URLs into shard_count files using index % shard_count (no overlaps)."""
    os.makedirs(shards_dir, exist_ok=True)
    shard_files = []
    
    for shard_idx in range(shard_count):
        shard_urls = [url for idx, url in enumerate(urls) if idx % shard_count == shard_idx]
        shard_path = os.path.join(shards_dir, f"shard_{shard_idx}_urls.txt")
        with open(shard_path, "w", encoding="utf-8") as f:
            for u in shard_urls:
                f.write(u + "\n")
        shard_files.append(shard_path)
        print(f"Shard {shard_idx}: wrote {len(shard_urls)} URLs to {shard_path}")

    # Integrity verification
    all_sharded = set()
    for shard_idx, path in enumerate(shard_files):
        with open(path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        overlap = all_sharded.intersection(lines)
        if overlap:
            raise ValueError(f"Integrity check failed: Shard {shard_idx} has {len(overlap)} overlapping URLs!")
        all_sharded.update(lines)

    assert len(all_sharded) == len(urls), f"Mismatch in sharded count: {len(all_sharded)} vs {len(urls)}"
    print("Shard integrity check passed: 0 overlaps, total count matches exactly.")
    return shard_files


def main():
    cfg = load_config()
    paths_cfg = cfg.get("paths", {})
    scraping_cfg = cfg.get("scraping", {})
    
    urls_file = paths_cfg.get("urls_file", "data/urls.txt")
    shards_dir = paths_cfg.get("shards_dir", "data/shards")
    shard_count = scraping_cfg.get("shard_count", 3)

    target_count = 180  # in the 150-250 candidate range
    urls = collect_urls(target_count=target_count)

    os.makedirs(os.path.dirname(urls_file), exist_ok=True)
    with open(urls_file, "w", encoding="utf-8") as f:
        for u in urls:
            f.write(u + "\n")

    print(f"\nSaved {len(urls)} unique candidate URLs to {urls_file}")
    
    print("\nSplitting into shards...")
    split_into_shards(urls, shard_count=shard_count, shards_dir=shards_dir)
    print("\nTask 1 URL collection complete.")


if __name__ == "__main__":
    main()
