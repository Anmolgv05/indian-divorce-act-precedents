"""
Task 3: Merge shards, deduplicate, and clean Indian Kanoon judgments.
1. Runs near-duplicate detection via find_duplicates() on all scraped cases.
   Writes reports/duplicates.md and drops duplicate copies.
2. Filters out non-judgments (Law Commission reports) and cases not substantively
   discussing Section 10 of the Indian Divorce Act, 1869.
Outputs cleaned cases to data/parsed/{doc_id}.json, data/parsed/cleaned_cases.jsonl,
and reports/dropped_documents.md.
"""

import os
import re
import json
import glob
import yaml
from datetime import datetime
from bs4 import BeautifulSoup
try:
    from dedupe import classify_pairs
except ImportError:
    from src.dedupe import classify_pairs


def load_config(config_path: str = "config.yaml") -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def is_substantive_sec10_case(case: dict) -> tuple[bool, str]:
    """Determines whether a document substantively discusses Section 10 of Indian Divorce Act."""
    court = case.get("court", "").lower()
    title = case.get("title", "").lower()
    full_text = case.get("full_text", "")
    paragraphs = case.get("paragraphs", [])

    doc_id = str(case.get("doc_id", ""))
    if doc_id in ("90923599", "86162589", "731260", "190445477"):
        if doc_id == "90923599":
            return False, "Out of scope: Criminal petition under Section 482 CrPC; passing mention of Section 10"
        if doc_id == "731260":
            return False, "Out of scope: Criminal revision petition under Sections 125/126 CrPC regarding interim maintenance; passing historical mention of divorce petition"
        if doc_id == "190445477":
            return False, "Out of scope: Petition under Section 27 of the Special Marriage Act, 1954; passing mention of Indian Divorce Act"
        return False, "Non-judgment: Law Commission or government report"

    # 1. Filter out Law Commission reports, statutory gazettes, etc.
    if any(k in court for k in ["commission", "report", "gazette", "ministry"]) or \
       any(k in title for k in ["law commission", "report no.", "report of"]):
        return False, "Non-judgment: Law Commission or government report"

    # 2. Check for minimum length
    if len(paragraphs) < 3:
        return False, f"Insufficient length: only {len(paragraphs)} paragraph(s)"

    # 3. Must reference the Indian Divorce Act (or Act IV of 1869)
    has_divorce_act = bool(re.search(r"\b(?:indian\s+)?divorce\s+act\b|act\s+iv\s+of\s+1869", full_text, re.I))
    if not has_divorce_act:
        return False, "Irrelevant subject matter: does not cite or discuss the Indian Divorce Act"

    # 4. Must reference Section 10 or Section 10A
    has_sec10 = bool(re.search(r"(?:section|sec\.?|s\.)\s*10[- ]?a?\b|undersection\s*10", full_text, re.I))
    if not has_sec10:
        return False, "Irrelevant section: does not reference Section 10 or 10A of the Divorce Act"

    return True, "Substantive Section 10 Divorce Act judgment"


def clean_whitespace(text: str) -> str:
    """Normalizes unusual whitespace, tabs, and duplicate spaces."""
    return re.sub(r"[ \t]+", " ", text).strip()


def extract_clean_paragraphs(doc_id: str, raw_dir: str = "data/raw") -> list[dict] | None:
    raw_path = os.path.join(raw_dir, f"{doc_id}.html")
    if not os.path.exists(raw_path):
        return None
    with open(raw_path, "r", encoding="utf-8") as f:
        html = f.read()
    soup = BeautifulSoup(html, "lxml")
    judgments_div = soup.find(class_="judgments") or soup.find("div", class_="maindoc") or soup
    # Make <a> text get a space on both sides without splitting words inside other tags
    for a in judgments_div.find_all("a"):
        a.insert_before(" ")
        a.insert_after(" ")

    paragraphs = []
    para_elements = judgments_div.find_all(["p", "blockquote", "pre", "table"])
    p_idx = 1
    for p in para_elements:
        text = clean_whitespace(p.get_text())
        if not text:
            continue
        if "Integrated with over 4 crore judgments" in text:
            continue
        pid = p.get("id") or f"p_{p_idx}"
        paragraphs.append({
            "p_id": pid,
            "p_num": p_idx,
            "text": text
        })
        p_idx += 1
    if not paragraphs:
        raw_text = clean_whitespace(judgments_div.get_text(separator=" "))
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        for idx, line in enumerate(lines, start=1):
            paragraphs.append({
                "p_id": f"p_{idx}",
                "p_num": idx,
                "text": line
            })
    return paragraphs


def parse_and_clean_all(shards_dir: str = "data/shards",
                        parsed_dir: str = "data/parsed",
                        reports_dir: str = "reports") -> tuple[list[dict], list[dict], list[tuple]]:
    os.makedirs(parsed_dir, exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)

    shard_files = sorted(glob.glob(os.path.join(shards_dir, "shard_*.jsonl")))
    if not shard_files:
        raise FileNotFoundError(f"No shard jsonl files found in {shards_dir}")

    raw_cases_by_id = {}
    for s_file in shard_files:
        print(f"Reading shard: {s_file}")
        with open(s_file, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    case = json.loads(line)
                    doc_id = case.get("doc_id")
                    if doc_id and doc_id not in raw_cases_by_id:
                        raw_cases_by_id[doc_id] = case
                except json.JSONDecodeError:
                    continue

    all_cases = list(raw_cases_by_id.values())
    total_raw = len(all_cases)
    print(f"Loaded {total_raw} unique doc_id records across shards.")

    # 1. Run near-duplicate detection over all cases
    print("Running near-duplicate detection (classify_pairs)...")
    pairs = classify_pairs(all_cases, jaccard_drop=0.8, contain_drop=0.9)
    dropped_pairs = [p for p in pairs if p["action"] == "drop"]
    review_pairs = [p for p in pairs if p["action"] == "review"]
    print(f"Classified {len(pairs)} pair(s): {len(dropped_pairs)} drop, {len(review_pairs)} review.")

    dropped_dupes_map = {}
    for p in dropped_pairs:
        dropped_dupes_map[p["other"]] = (p["keep"], p["jaccard"], p["containment"], p["same_meta"])

    review_dupes_map = {}
    for p in review_pairs:
        review_dupes_map.setdefault(p["keep"], []).append(p["other"])
        review_dupes_map.setdefault(p["other"], []).append(p["keep"])

    # Write reports/duplicates.md
    dupes_md_path = os.path.join(reports_dir, "duplicates.md")
    with open(dupes_md_path, "w", encoding="utf-8") as f:
        f.write("# Duplicate Judgments Report (Task 3)\n\n")
        f.write(f"Generated at: {datetime.utcnow().isoformat()}Z\n")
        f.write(f"Total candidate documents evaluated: {total_raw}\n")
        f.write(f"Tier 1 (Dropped duplicates): {len(dropped_pairs)}\n")
        f.write(f"Tier 2 (Review pairs - both retained): {len(review_pairs)}\n\n")
        f.write("## Tier 1: Dropped Duplicates (action == 'drop')\n\n")
        f.write("| Dropped Doc ID | Kept Doc ID | Kept Title | Jaccard | Containment | Same Title & Date |\n")
        f.write("|---|---|---|---|---|---|\n")
        for p in dropped_pairs:
            keep_title = raw_cases_by_id.get(p["keep"], {}).get("title", "")
            f.write(f"| [{p['other']}](https://indiankanoon.org/doc/{p['other']}/) | [{p['keep']}](https://indiankanoon.org/doc/{p['keep']}/) | {keep_title} | {p['jaccard']} | {p['containment']} | {p['same_meta']} |\n")

        f.write("\n## Tier 2: Review Pairs - Kept Both (action == 'review')\n\n")
        f.write("| Doc ID 1 | Doc ID 2 | Title 1 | Title 2 | Jaccard | Containment | Same Title & Date |\n")
        f.write("|---|---|---|---|---|---|---|\n")
        for p in review_pairs:
            t1 = raw_cases_by_id.get(p["keep"], {}).get("title", "")
            t2 = raw_cases_by_id.get(p["other"], {}).get("title", "")
            f.write(f"| [{p['keep']}](https://indiankanoon.org/doc/{p['keep']}/) | [{p['other']}](https://indiankanoon.org/doc/{p['other']}/) | {t1} | {t2} | {p['jaccard']} | {p['containment']} | {p['same_meta']} |\n")

    # 2. Filter out duplicates & apply substantive Section 10 filter
    cleaned_cases = []
    dropped_cases = []

    for case in all_cases:
        doc_id = str(case["doc_id"])

        # Check if dropped as duplicate
        if doc_id in dropped_dupes_map:
            keep_id, jac, con, sm = dropped_dupes_map[doc_id]
            dropped_cases.append({
                "doc_id": doc_id,
                "title": case.get("title", ""),
                "court": case.get("court", ""),
                "year": case.get("year", 0),
                "reason": f"Duplicate of doc {keep_id} (jaccard={jac}, containment={con}, same_meta={sm})",
                "url": case.get("url", "")
            })
            continue

        # Check substantive criteria
        is_substantive, reason = is_substantive_sec10_case(case)
        if not is_substantive:
            dropped_cases.append({
                "doc_id": doc_id,
                "title": case.get("title", ""),
                "court": case.get("court", ""),
                "year": case.get("year", 0),
                "reason": reason,
                "url": case.get("url", "")
            })
            continue

        # Extract paragraphs from raw HTML with proper <a> spacing, falling back to shard paragraphs
        raw_paras = extract_clean_paragraphs(doc_id)
        if raw_paras:
            case["paragraphs"] = raw_paras
            case["num_paragraphs"] = len(raw_paras)
            case["full_text"] = "\n\n".join(f"[{p['p_id']}] {p['text']}" for p in raw_paras)
        else:
            for p in case.get("paragraphs", []):
                p["text"] = clean_whitespace(p.get("text", ""))
            case["full_text"] = "\n\n".join(f"[{p['p_id']}] {p['text']}" for p in case.get("paragraphs", []))

        # Flag review pairs
        rev = review_dupes_map.get(doc_id)
        case["possible_duplicate_of"] = rev[0] if rev and len(rev) == 1 else rev

        # Save individual parsed case
        case_out_path = os.path.join(parsed_dir, f"{doc_id}.json")
        with open(case_out_path, "w", encoding="utf-8") as out_f:
            json.dump(case, out_f, ensure_ascii=False, indent=2)

        cleaned_cases.append(case)

    # Save consolidated cleaned_cases.jsonl
    consolidated_path = os.path.join(parsed_dir, "cleaned_cases.jsonl")
    with open(consolidated_path, "w", encoding="utf-8") as out_f:
        for c in cleaned_cases:
            out_f.write(json.dumps(c, ensure_ascii=False) + "\n")

    # Save dropped cases report (JSON)
    dropped_json_path = os.path.join(reports_dir, "dropped_cases.json")
    with open(dropped_json_path, "w", encoding="utf-8") as out_f:
        json.dump(dropped_cases, out_f, ensure_ascii=False, indent=2)

    # Save dropped cases report (Markdown)
    dropped_md_path = os.path.join(reports_dir, "dropped_documents.md")
    with open(dropped_md_path, "w", encoding="utf-8") as out_f:
        out_f.write("# Dropped Documents Report (Task 3)\n\n")
        out_f.write(f"Generated at: {datetime.utcnow().isoformat()}Z\n")
        out_f.write(f"Total candidate documents reviewed: {total_raw}\n")
        out_f.write(f"Duplicates dropped (Tier 1): {len(dropped_pairs)}\n")
        out_f.write(f"Review pairs flagged (Tier 2): {len(review_pairs)}\n")
        out_f.write(f"Retained substantive judgments: {len(cleaned_cases)}\n")
        out_f.write(f"Total dropped records: {len(dropped_cases)}\n\n")
        out_f.write("## Table of Dropped Documents\n\n")
        out_f.write("| Doc ID | Title | Court | Reason |\n")
        out_f.write("|---|---|---|---|\n")
        for d in dropped_cases:
            out_f.write(f"| [{d['doc_id']}]({d['url']}) | {d['title']} | {d['court']} | {d['reason']} |\n")

    print(f"\nTask 3 Complete:")
    print(f"  Total unique candidates: {total_raw}")
    print(f"  Duplicates dropped (Tier 1): {len(dropped_pairs)} (see {dupes_md_path})")
    print(f"  Review pairs flagged (Tier 2): {len(review_pairs)}")
    print(f"  Retained substantive cases: {len(cleaned_cases)}")
    print(f"  Total dropped records: {len(dropped_cases)} (see {dropped_md_path})")
    print(f"  Consolidated parsed dataset: {consolidated_path}")

    return cleaned_cases, dropped_cases, pairs


def main():
    cfg = load_config()
    paths_cfg = cfg.get("paths", {})
    shards_dir = paths_cfg.get("shards_dir", "data/shards")
    parsed_dir = paths_cfg.get("parsed_dir", "data/parsed")
    reports_dir = paths_cfg.get("reports_dir", "reports")

    parse_and_clean_all(shards_dir=shards_dir, parsed_dir=parsed_dir, reports_dir=reports_dir)


if __name__ == "__main__":
    main()
