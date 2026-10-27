"""
Task 4: Segment and label parsed judgments (v3).
Applies rules from src/labels.py (v3) to all substantive cases in data/parsed/cleaned_cases.jsonl.
Outputs data/labeled/cases.jsonl matching the updated AGENTS.md schema.
Prints summary statistics, non-merits count, new disposal values, next 15 unclear tails,
and 10 cases where marriage_dissolved is unclear but disposal is allowed/confirmed.
"""

import os
import re
import json
import random
import yaml
from collections import Counter
try:
    from labels import (
        label_grounds,
        label_disposal,
        label_dissolved,
        label_petitioner,
        segment_paragraphs,
        is_non_merits,
        clean_tail
    )
except ImportError:
    from src.labels import (
        label_grounds,
        label_disposal,
        label_dissolved,
        label_petitioner,
        segment_paragraphs,
        is_non_merits,
        clean_tail
    )


def load_config(config_path: str = "config.yaml") -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def extract_statutes_cited(text: str) -> list[str]:
    statutes = set()
    matches = re.findall(r"\b(?:section|sec\.?|s\.)\s*(\d+[A-Za-z]?)\b", text, re.I)
    for m in matches:
        statutes.add(f"Section {m.upper()}")
    return sorted(list(statutes))


def label_dataset(
    input_jsonl: str = "data/parsed/cleaned_cases.jsonl",
    output_jsonl: str = "data/labeled/cases.jsonl"
) -> list[dict]:
    os.makedirs(os.path.dirname(output_jsonl), exist_ok=True)

    cases = []
    with open(input_jsonl, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                cases.append(json.loads(line))

    labeled_cases = []
    for c in cases:
        paragraphs = c.get("paragraphs", [])
        title = c.get("title", "")
        year = c.get("year", 0)

        grounds, primary_ground, scores = label_grounds(paragraphs, year=year, title=title)
        disposal = label_disposal(paragraphs)
        marriage_dissolved, relief = label_dissolved(paragraphs, ground=primary_ground)
        petitioner_gender = label_petitioner(paragraphs, title=title)
        non_merits = is_non_merits(title, paragraphs)
        segments = segment_paragraphs(paragraphs)
        statutes = extract_statutes_cited(c.get("full_text", ""))

        record = {
            "doc_id": c["doc_id"],
            "url": c.get("url", f"https://indiankanoon.org/doc/{c['doc_id']}/"),
            "title": title,
            "court": c.get("court", ""),
            "date": c.get("date", ""),
            "year": year,
            "citations": c.get("citations", ""),
            "grounds": grounds,
            "primary_ground": primary_ground,
            "disposal": disposal,
            "marriage_dissolved": marriage_dissolved,
            "relief": relief,
            "non_merits": non_merits,
            "possible_duplicate_of": c.get("possible_duplicate_of", None),
            "petitioner_gender": petitioner_gender,
            "statutes_cited": statutes,
            "precedents_cited": [],
            "segments": segments,
            "label_source": {
                "grounds": "rule",
                "disposal": "rule",
                "marriage_dissolved": "rule",
                "relief": "rule",
                "petitioner": "rule"
            }
        }
        labeled_cases.append(record)

    with open(output_jsonl, "w", encoding="utf-8") as f:
        for rec in labeled_cases:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    return labeled_cases


def print_full_report(labeled_file: str = "data/labeled/cases.jsonl", duplicates_file: str = "reports/duplicates.md", parsed_dir: str = "data/parsed"):
    if not os.path.exists(labeled_file):
        print(f"Labeled file not found: {labeled_file}")
        return

    labeled_cases = []
    with open(labeled_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                labeled_cases.append(json.loads(line))

    total = len(labeled_cases)
    if total == 0:
        print("No cases to summarize.")
        return

    # 1. Dedupe Report Counts
    print("\n" + "=" * 75)
    print("PART 1: DEDUPLICATION REPORT COUNTS")
    print("=" * 75)
    tier1_dropped = 0
    tier2_review = 0
    if os.path.exists(duplicates_file):
        with open(duplicates_file, "r", encoding="utf-8") as f:
            content = f.read()
        tier1_matches = re.findall(r"Tier 1.*?(\d+)", content)
        tier2_matches = re.findall(r"Tier 2.*?(\d+)", content)
        if tier1_matches:
            tier1_dropped = int(tier1_matches[0])
        if tier2_matches:
            tier2_review = int(tier2_matches[0])
        print(f"Tier 1 (Duplicates Dropped)       : {tier1_dropped}")
        print(f"Tier 2 (Review Pairs - Kept Both) : {tier2_review}")
        print(f"Full details written to: {duplicates_file}")
    else:
        print("No duplicates.md report found.")

    # 2. Counts and Summary Table
    ground_counts = Counter(c["primary_ground"] for c in labeled_cases)
    disposal_counts = Counter(c["disposal"] for c in labeled_cases)
    dissolved_counts = Counter(c["marriage_dissolved"] for c in labeled_cases)
    relief_counts = Counter(c["relief"] for c in labeled_cases)
    gender_counts = Counter(c["petitioner_gender"] for c in labeled_cases)
    non_merits_count = sum(1 for c in labeled_cases if c.get("non_merits"))

    unclear_grounds = ground_counts.get("unclear", 0)
    unclear_disposal = disposal_counts.get("unclear", 0)
    unclear_dissolved = dissolved_counts.get("unclear", 0)
    unclear_relief = relief_counts.get("unclear", 0)
    unclear_gender = gender_counts.get("unclear", 0)

    print("\n" + "=" * 75)
    print(f"PART 2: TASK 4 SUMMARY TABLE — {total} RETAINED CASES (v4 Rules)")
    print("=" * 75)

    print(f"\nNon-Merits Cases (Transfer petitions/Section 24 CPC): {non_merits_count}/{total} ({(non_merits_count/total)*100:.1f}%)")

    print("\n--- Primary Ground Counts ---")
    for g, count in ground_counts.most_common():
        pct = (count / total) * 100
        print(f"  {g:<28} : {count:>4} ({pct:>5.1f}%)")

    print("\n--- Disposal Counts (including confirmed, not_confirmed, modified, interim) ---")
    for d, count in disposal_counts.most_common():
        pct = (count / total) * 100
        print(f"  {d:<28} : {count:>4} ({pct:>5.1f}%)")

    print("\n--- Marriage Dissolved Counts ---")
    for m, count in dissolved_counts.most_common():
        pct = (count / total) * 100
        print(f"  {m:<28} : {count:>4} ({pct:>5.1f}%)")

    print("\n--- Relief Granted Counts (nullity, restitution, dissolution, judicial_separation, none, unclear) ---")
    for r, count in relief_counts.most_common():
        pct = (count / total) * 100
        print(f"  {r:<28} : {count:>4} ({pct:>5.1f}%)")

    print("\n--- Petitioner Gender Counts ---")
    for pg, count in gender_counts.most_common():
        pct = (count / total) * 100
        print(f"  {pg:<28} : {count:>4} ({pct:>5.1f}%)")

    print("\n--- Unclear Percentages ---")
    print(f"  Primary Ground Unclear   : {unclear_grounds}/{total} ({(unclear_grounds/total)*100:.1f}%)")
    print(f"  Disposal Unclear         : {unclear_disposal}/{total} ({(unclear_disposal/total)*100:.1f}%)")
    print(f"  Dissolved Unclear        : {unclear_dissolved}/{total} ({(unclear_dissolved/total)*100:.1f}%)")
    print(f"  Relief Unclear           : {unclear_relief}/{total} ({(unclear_relief/total)*100:.1f}%)")
    print(f"  Petitioner Gender Unclear: {unclear_gender}/{total} ({(unclear_gender/total)*100:.1f}%)")

    # 3. ALL remaining disposal=unclear cases printed directly from cases.jsonl
    unclear_disposal_cases = [c for c in labeled_cases if c.get("disposal") == "unclear"]
    print("\n" + "=" * 75)
    print(f"PART 3: ALL REMAINING DISPOSAL=UNCLEAR CASES DIRECTLY FROM cases.jsonl (Total: {len(unclear_disposal_cases)})")
    print("=" * 75)

    for idx, c in enumerate(unclear_disposal_cases, start=1):
        doc_id = c["doc_id"]
        title = c.get("title", "")
        primary = c.get("primary_ground", "")
        disposal = c.get("disposal", "")
        dissolved = c.get("marriage_dissolved", "")
        relief = c.get("relief", "")
        non_merits = c.get("non_merits", False)
        dup_of = c.get("possible_duplicate_of")

        # Load original paragraphs from parsed file to get accurate tail
        paras = []
        parsed_path = os.path.join(parsed_dir, f"{doc_id}.json")
        if os.path.exists(parsed_path):
            try:
                with open(parsed_path, "r", encoding="utf-8") as pf:
                    pdata = json.load(pf)
                    paras = pdata.get("paragraphs", [])
            except Exception:
                pass
        if not paras:
            for seg in c.get("segments", []):
                paras.append({"p_id": seg["p_ids"][0] if seg["p_ids"] else "p_0", "text": seg["text"]})

        tail_text = clean_tail(paras)
        last_300 = tail_text[-300:].strip() if len(tail_text) >= 300 else tail_text.strip()

        print(f"\n[{idx}] Doc ID: {doc_id} | {title}")
        print(f"    Disposal: {disposal} | Dissolved: {dissolved} | Relief: {relief} | Ground: {primary} | Non-Merits: {non_merits}" + (f" | DupOf: {dup_of}" if dup_of else ""))
        print(f"    Cleaned Tail (last 300 chars):")
        print(f"    \"{last_300}\"")

    # 4. List of non_merits=true cases
    non_merits_cases = [c for c in labeled_cases if c.get("non_merits") is True]
    print("\n" + "=" * 75)
    print(f"PART 4: LIST OF NON-MERITS CASES (Total: {len(non_merits_cases)})")
    print("=" * 75)

    for idx, c in enumerate(non_merits_cases, start=1):
        doc_id = c["doc_id"]
        title = c.get("title", "")
        court = c.get("court", "")
        year = c.get("year", 0)
        disposal = c.get("disposal", "")
        dissolved = c.get("marriage_dissolved", "")
        relief = c.get("relief", "")
        ground = c.get("primary_ground", "")
        url = c.get("url", "")
        print(f"  [{idx}] Doc ID: {doc_id} ({year}) - {court}")
        print(f"      Title: {title}")
        print(f"      Disposal: {disposal} | Dissolved: {dissolved} | Relief: {relief} | Ground: {ground}")
        print(f"      URL: {url}")

    print("\n" + "=" * 75)


def main():
    cfg = load_config()
    paths_cfg = cfg.get("paths", {})
    parsed_dir = paths_cfg.get("parsed_dir", "data/parsed")
    labeled_file = paths_cfg.get("labeled_file", "data/labeled/cases.jsonl")
    input_file = os.path.join(parsed_dir, "cleaned_cases.jsonl")
    dupes_file = os.path.join(paths_cfg.get("reports_dir", "reports"), "duplicates.md")

    label_dataset(input_jsonl=input_file, output_jsonl=labeled_file)
    print_full_report(labeled_file=labeled_file, duplicates_file=dupes_file, parsed_dir=parsed_dir)


if __name__ == "__main__":
    main()

