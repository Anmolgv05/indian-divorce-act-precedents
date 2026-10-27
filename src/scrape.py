"""
Scrape Indian Kanoon judgments for a specific shard.
Caches raw HTML in data/raw/{doc_id}.html, parses core fields,
and writes records to data/shards/shard_{N}.jsonl.
"""

import os
import re
import sys
import time
import json
import argparse
from datetime import datetime
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
        total=4,
        backoff_factor=2.0,
        status_forcelist=[429, 500, 502, 503, 504],
        raise_on_status=False
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def extract_doc_id(url: str) -> str:
    m = re.search(r"/(?:doc|docfragment)/(\d+)/", url)
    if not m:
        raise ValueError(f"Could not extract doc_id from URL: {url}")
    return m.group(1)


def parse_date_from_title(title: str) -> tuple[str, int]:
    """Extracts date string and 4-digit year from Indian Kanoon title (e.g. '... on 6 May, 1997')."""
    m = re.search(r"\bon\s+(\d{1,2}\s+[A-Za-z]+,?\s+\d{4})", title, re.IGNORECASE)
    if m:
        date_str = m.group(1).replace(",", "")
        try:
            dt = datetime.strptime(date_str, "%d %B %Y")
            return dt.strftime("%Y-%m-%d"), dt.year
        except ValueError:
            pass

    # Fallback: find any 4-digit year in 1800-2030
    year_match = re.search(r"\b(18\d{2}|19\d{2}|20\d{2})\b", title)
    if year_match:
        year = int(year_match.group(1))
        return f"{year}-01-01", year
    return "", 0


def parse_judgment_html(html: str, doc_id: str, url: str) -> dict:
    """Parses raw HTML from Indian Kanoon judgment page."""
    soup = BeautifulSoup(html, "lxml")

    # Document Title
    title_elem = soup.find(class_="doc_title") or soup.find("h2") or soup.title
    title = title_elem.get_text(strip=True) if title_elem else f"Document {doc_id}"

    # Court / Source
    court_elem = soup.find(class_="docsource_main") or soup.find(class_="doc_source")
    court = court_elem.get_text(strip=True) if court_elem else "Unknown Court"

    # Equivalent citations
    citations_elem = soup.find(class_="doc_citations")
    citations = citations_elem.get_text(strip=True) if citations_elem else ""

    # Parse date and year
    date_str, year = parse_date_from_title(title)

    # Paragraph and blockquote/pre extraction
    judgments_div = soup.find(class_="judgments") or soup.find("div", class_="maindoc") or soup
    for a in judgments_div.find_all("a"):
        a.insert_before(" ")
        a.insert_after(" ")
    paragraphs = []
    para_elements = judgments_div.find_all(["p", "blockquote", "pre", "table"])

    p_idx = 1
    for p in para_elements:
        text = re.sub(r"[ \t]+", " ", p.get_text()).strip()
        if not text:
            continue
        # Skip site headers or marketing banners if embedded in p tags
        if "Integrated with over 4 crore judgments" in text:
            continue
        pid = p.get("id") or f"p_{p_idx}"
        paragraphs.append({
            "p_id": pid,
            "p_num": p_idx,
            "text": text
        })
        p_idx += 1

    # In case there are no <p> tags, fallback to block text
    if not paragraphs:
        raw_text = judgments_div.get_text(separator="\n", strip=True)
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        for idx, line in enumerate(lines, start=1):
            paragraphs.append({
                "p_id": f"p_{idx}",
                "p_num": idx,
                "text": line
            })

    full_text = "\n\n".join(f"[{p['p_id']}] {p['text']}" for p in paragraphs)

    # Structured tags (if exposed)
    structured_tags = []
    for tag_div in soup.find_all(class_=re.compile(r"tag|premium-banner__ai-tag")):
        t_text = tag_div.get_text(strip=True)
        if t_text:
            structured_tags.append(t_text)

    return {
        "doc_id": doc_id,
        "url": url,
        "title": title,
        "court": court,
        "date": date_str,
        "year": year,
        "citations": citations,
        "paragraphs": paragraphs,
        "num_paragraphs": len(paragraphs),
        "full_text": full_text,
        "structured_tags": structured_tags
    }


def scrape_shard(
    shard_id: int,
    shard_file: str,
    raw_dir: str,
    output_jsonl: str,
    failures_file: str,
    delay: float = 2.0,
    user_agent: str = "CourseworkResearch/1.0",
    limit: int = None
) -> int:
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(os.path.dirname(output_jsonl), exist_ok=True)
    os.makedirs(os.path.dirname(failures_file), exist_ok=True)

    if not os.path.exists(shard_file):
        raise FileNotFoundError(f"Shard file not found: {shard_file}. Run collect_urls.py first.")

    with open(shard_file, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]

    if limit:
        urls = urls[:limit]

    print(f"Scraping Shard {shard_id}: {len(urls)} URLs from {shard_file}")
    session = get_session(user_agent)

    # Track already processed doc_ids in this shard's JSONL
    processed_ids = set()
    if os.path.exists(output_jsonl):
        with open(output_jsonl, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        record = json.loads(line)
                        processed_ids.add(record["doc_id"])
                    except json.JSONDecodeError:
                        pass
        print(f"Resuming: found {len(processed_ids)} already scraped records in {output_jsonl}")

    success_count = len(processed_ids)

    with open(output_jsonl, "a", encoding="utf-8") as out_f, \
         open(failures_file, "a", encoding="utf-8") as err_f:

        for idx, url in enumerate(urls, start=1):
            try:
                doc_id = extract_doc_id(url)
            except Exception as e:
                err_f.write(f"{datetime.utcnow().isoformat()}\t{url}\t{e}\n")
                continue

            if doc_id in processed_ids:
                continue

            cache_path = os.path.join(raw_dir, f"{doc_id}.html")
            html = ""

            # 1. Read from disk cache if already cached
            if os.path.exists(cache_path):
                with open(cache_path, "r", encoding="utf-8", errors="replace") as cf:
                    html = cf.read()
            else:
                # 2. Fetch from network
                print(f"[{idx}/{len(urls)}] Fetching doc {doc_id} -> {url}")
                try:
                    resp = session.get(url, timeout=15)
                    if resp.status_code == 200:
                        html = resp.text
                        with open(cache_path, "w", encoding="utf-8") as cf:
                            cf.write(html)
                    else:
                        msg = f"HTTP {resp.status_code}"
                        print(f"  Error fetching {doc_id}: {msg}")
                        err_f.write(f"{datetime.utcnow().isoformat()}\t{doc_id}\t{url}\t{msg}\n")
                        err_f.flush()
                        time.sleep(delay)
                        continue
                except Exception as e:
                    print(f"  Exception fetching {doc_id}: {e}")
                    err_f.write(f"{datetime.utcnow().isoformat()}\t{doc_id}\t{url}\t{e}\n")
                    err_f.flush()
                    time.sleep(delay)
                    continue

                time.sleep(delay)

            # 3. Parse and extract
            try:
                record = parse_judgment_html(html, doc_id=doc_id, url=url)
                out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
                out_f.flush()
                processed_ids.add(doc_id)
                success_count += 1
            except Exception as e:
                print(f"  Error parsing {doc_id}: {e}")
                err_f.write(f"{datetime.utcnow().isoformat()}\t{doc_id}\t{url}\tParseError: {e}\n")
                err_f.flush()

    print(f"Shard {shard_id} finished. Total records in {output_jsonl}: {success_count}")
    return success_count


def main():
    parser = argparse.ArgumentParser(description="Scrape Section 10 Indian Kanoon judgments for a shard.")
    parser.add_argument("--shard", type=int, default=0, help="Shard index (0, 1, 2, ...)")
    parser.add_argument("--shard-file", type=str, default=None, help="Path to shard URLs file")
    parser.add_argument("--all", action="store_true", help="Scrape all shards sequentially")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of documents to scrape")
    parser.add_argument("--delay", type=float, default=None, help="Polite delay between requests in seconds")
    args = parser.parse_args()

    cfg = load_config()
    scraping_cfg = cfg.get("scraping", {})
    paths_cfg = cfg.get("paths", {})

    raw_dir = paths_cfg.get("raw_dir", "data/raw")
    shards_dir = paths_cfg.get("shards_dir", "data/shards")
    failures_file = paths_cfg.get("scrape_failures", "reports/scrape_failures.txt")
    delay = args.delay if args.delay is not None else scraping_cfg.get("delay_seconds", 2.0)
    user_agent = scraping_cfg.get("user_agent", "CourseworkResearch/1.0")
    shard_count = scraping_cfg.get("shard_count", 3)

    if args.all:
        total_scraped = 0
        for s in range(shard_count):
            s_file = os.path.join(shards_dir, f"shard_{s}_urls.txt")
            out_jsonl = os.path.join(shards_dir, f"shard_{s}.jsonl")
            count = scrape_shard(
                shard_id=s,
                shard_file=s_file,
                raw_dir=raw_dir,
                output_jsonl=out_jsonl,
                failures_file=failures_file,
                delay=delay,
                user_agent=user_agent,
                limit=args.limit
            )
            total_scraped += count
        print(f"\nAll {shard_count} shards scraped. Total documents scraped: {total_scraped}")
    else:
        shard_id = args.shard
        s_file = args.shard_file or os.path.join(shards_dir, f"shard_{shard_id}_urls.txt")
        out_jsonl = os.path.join(shards_dir, f"shard_{shard_id}.jsonl")
        scrape_shard(
            shard_id=shard_id,
            shard_file=s_file,
            raw_dir=raw_dir,
            output_jsonl=out_jsonl,
            failures_file=failures_file,
            delay=delay,
            user_agent=user_agent,
            limit=args.limit
        )


if __name__ == "__main__":
    main()
