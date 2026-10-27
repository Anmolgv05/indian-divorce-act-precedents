"""
Task 5: Validation module for Section 10 Indian Divorce Act judgments.
1. Samples 20 stratified cases with seed 42 (excluding non-merits and review duplicates).
2. Generates reports/review_sheet.csv for reviewers B & C.
3. Generates reports/review_cases.md with text excerpts and segment previews.
4. Provides --score CLI to compute accuracy from completed review_sheet.csv.
"""

import os
import re
import csv
import json
import random
import argparse
try:
    from src.labels import clean_tail
except ImportError:
    from labels import clean_tail


def select_stratified_sample(cases: list[dict], target_size: int = 20, seed: int = 42) -> list[dict]:
    """Selects target_size cases stratified by disposal and grounds."""
    cand = [c for c in cases if not c.get("non_merits") and not c.get("possible_duplicate_of")]
    sorted_cand = sorted(cand, key=lambda c: str(c["doc_id"]))
    rng = random.Random(seed)

    selected_ids = set()
    selected = []

    # Stratum 1: at least 2 each of confirmed, not_confirmed, remanded
    for disp in ["confirmed", "not_confirmed", "remanded"]:
        pool = [c for c in sorted_cand if c["disposal"] == disp and c["doc_id"] not in selected_ids]
        for c in rng.sample(pool, min(2, len(pool))):
            selected.append(c)
            selected_ids.add(c["doc_id"])

    # Stratum 2: at least 3 non-adultery/cruelty grounds
    non_ac_pool = [c for c in sorted_cand if c["primary_ground"] not in ("adultery", "cruelty", "unclear") and c["doc_id"] not in selected_ids]
    for c in rng.sample(non_ac_pool, min(3, len(non_ac_pool))):
        selected.append(c)
        selected_ids.add(c["doc_id"])

    # Remaining slots filled randomly from rest of candidates
    remaining_pool = [c for c in sorted_cand if c["doc_id"] not in selected_ids]
    needed = target_size - len(selected)
    if needed > 0:
        for c in rng.sample(remaining_pool, needed):
            selected.append(c)
            selected_ids.add(c["doc_id"])

    return selected


def generate_review_artifacts(selected_cases: list[dict], parsed_dir: str = "data/parsed", reports_dir: str = "reports"):
    os.makedirs(reports_dir, exist_ok=True)

    csv_path = os.path.join(reports_dir, "review_sheet.csv")
    md_path = os.path.join(reports_dir, "review_cases.md")

    # 1. Write review_sheet.csv
    headers = [
        "doc_id", "url", "title",
        "primary_ground", "disposal", "marriage_dissolved", "relief", "petitioner_gender",
        "ground_ok", "disposal_ok", "dissolved_relief_ok", "petitioner_ok", "segments_ok",
        "correct_value_if_wrong", "notes"
    ]
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for c in selected_cases:
            writer.writerow([
                c["doc_id"],
                c.get("url", f"https://indiankanoon.org/doc/{c['doc_id']}/"),
                c.get("title", ""),
                c.get("primary_ground", ""),
                c.get("disposal", ""),
                c.get("marriage_dissolved", ""),
                c.get("relief", ""),
                c.get("petitioner_gender", ""),
                "", "", "", "", "", "", ""
            ])

    # 2. Write review_cases.md
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# Task 5: 20-Case Manual Validation Dossier\n\n")
        f.write("Review instructions for reviewers B and C:\n")
        f.write("- For each case, read the excerpt and verify the model's extracted labels.\n")
        f.write("- Mark `1` (or `yes`) in `reports/review_sheet.csv` if the label is accurate, or `0` (or `no`) if incorrect.\n")
        f.write("- If incorrect, record the true legal outcome in `correct_value_if_wrong`.\n")
        f.write("- Run `python src/validate.py --score reports/review_sheet.csv` to compute validation metrics.\n\n")
        f.write("---\n\n")

        for idx, c in enumerate(selected_cases, 1):
            doc_id = c["doc_id"]
            title = c.get("title", "")
            url = c.get("url", f"https://indiankanoon.org/doc/{doc_id}/")

            # Load original paragraphs for clean text and accurate tail
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

            full_text = " ".join(p["text"] for p in paras)
            head_600 = full_text[:600].strip()

            tail_text = clean_tail(paras, min_chars=1200)
            tail_800 = tail_text[-800:].strip() if len(tail_text) >= 800 else tail_text.strip()

            f.write(f"## [{idx}] Case {doc_id}: {title}\n\n")
            f.write(f"- **URL:** [{url}]({url})\n")
            f.write(f"- **Court & Date:** {c.get('court', 'Unknown')} ({c.get('date', 'Unknown')})\n")
            f.write(f"- **Model Ground:** `{c.get('primary_ground')}` (All detected: {c.get('grounds')})\n")
            f.write(f"- **Model Disposal:** `{c.get('disposal')}`\n")
            f.write(f"- **Model Dissolution:** `{c.get('marriage_dissolved')}` (Relief: `{c.get('relief')}`)\n")
            f.write(f"- **Model Petitioner:** `{c.get('petitioner_gender')}`\n\n")

            f.write("### Head Excerpt (First 600 chars):\n")
            f.write(f"> {head_600}\n\n")

            f.write("### Cleaned Tail (Last 800 chars):\n")
            f.write(f"> {tail_800}\n\n")

            f.write("### Segments Preview:\n")
            for s_idx, seg in enumerate(c.get("segments", []), 1):
                stype = seg.get("type", "unknown")
                pids = ", ".join(seg.get("p_ids", []))
                stext = seg.get("text", "").replace("\n", " ").strip()[:150]
                f.write(f"- **[{stype}]** (`{pids}`): {stext}...\n")

            f.write("\n---\n\n")

    print(f"Generated review sheet: {csv_path}")
    print(f"Generated review dossier: {md_path}")


def score_review_sheet(csv_path: str):
    """Computes accuracy metrics from a filled review_sheet.csv."""
    if not os.path.exists(csv_path):
        print(f"Error: Review sheet not found at {csv_path}")
        return

    fields = ["ground_ok", "disposal_ok", "dissolved_relief_ok", "petitioner_ok", "segments_ok"]
    counts = {f: {"correct": 0, "total": 0} for f in fields}

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            for fld in fields:
                val = row.get(fld, "").strip().lower()
                if val in ("1", "y", "yes", "true", "ok", "correct"):
                    counts[fld]["correct"] += 1
                    counts[fld]["total"] += 1
                elif val in ("0", "n", "no", "false", "wrong", "incorrect"):
                    counts[fld]["total"] += 1

    print("\n" + "=" * 65)
    print("TASK 5: MANUAL REVIEW ACCURACY REPORT")
    print("=" * 65)
    print(f"{'Field':<25} | {'Evaluated':<10} | {'Correct':<8} | {'Accuracy':<10}")
    print("-" * 65)

    total_eval = 0
    total_corr = 0
    for fld in fields:
        tot = counts[fld]["total"]
        cor = counts[fld]["correct"]
        total_eval += tot
        total_corr += cor
        if tot > 0:
            acc = (cor / tot) * 100
            print(f"{fld:<25} | {tot:>10} | {cor:>8} | {acc:>9.1f}%")
        else:
            print(f"{fld:<25} | {tot:>10} | {cor:>8} | {'Pending':>10}")

    print("-" * 65)
    if total_eval > 0:
        overall_acc = (total_corr / total_eval) * 100
        print(f"{'OVERALL AVERAGE':<25} | {total_eval:>10} | {total_corr:>8} | {overall_acc:>9.1f}%")
    else:
        print("Review sheet is blank or pending review from B and C.")
    print("=" * 65 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Task 5: Sample cases for manual validation and score review sheets.")
    parser.add_argument("--score", type=str, default=None, help="Path to filled review_sheet.csv to score")
    parser.add_argument("--labeled-file", type=str, default="data/labeled/cases.jsonl", help="Path to labeled cases.jsonl")
    parser.add_argument("--parsed-dir", type=str, default="data/parsed", help="Path to parsed cases directory")
    parser.add_argument("--reports-dir", type=str, default="reports", help="Path to reports directory")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for sampling (default: 42)")
    parser.add_argument("--count", type=int, default=20, help="Number of cases to sample (default: 20)")
    args = parser.parse_args()

    if args.score:
        score_review_sheet(args.score)
        return

    if not os.path.exists(args.labeled_file):
        print(f"Error: {args.labeled_file} does not exist.")
        return

    cases = []
    with open(args.labeled_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                cases.append(json.loads(line))

    selected = select_stratified_sample(cases, target_size=args.count, seed=args.seed)
    print(f"Selected {len(selected)} cases for manual review (seed={args.seed}).")
    generate_review_artifacts(selected, parsed_dir=args.parsed_dir, reports_dir=args.reports_dir)


if __name__ == "__main__":
    main()
