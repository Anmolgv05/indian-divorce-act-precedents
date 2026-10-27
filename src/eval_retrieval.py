"""
Task 6: Retrieval Evaluation Script.
Compares dense-only vs hybrid (dense + TF-IDF) retrieval across the 12 evaluation queries.
Calculates Precision@5 using keyword-in-best-chunk and expected primary grounds.
"""

import json
import re
import os
import sys
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.search import search


def evaluate(eval_file: str = "tests/retrieval_eval.json", top_k: int = 5):
    with open(eval_file, "r", encoding="utf-8") as f:
        queries = json.load(f)

    results_table = []
    dense_kw_scores = []
    hybrid_kw_scores = []
    dense_gr_scores = []
    hybrid_gr_scores = []

    for item in queries:
        topic = item["topic"]
        q = item["query"]
        kw_re = re.compile(item["keyword_regex"], re.I)
        expected_grounds = set(item.get("expected_primary_grounds", []))

        # 1. Dense retrieval
        dense_results = search(q, top_k=top_k, mode="dense", include_non_merits=True)
        dense_kw_hits = sum(1 for r in dense_results if kw_re.search(r["best_chunk"]["text"]))
        dense_gr_hits = sum(1 for r in dense_results if r["primary_ground"] in expected_grounds)
        dense_kw_p = dense_kw_hits / top_k
        dense_gr_p = dense_gr_hits / top_k
        dense_kw_scores.append(dense_kw_p)
        dense_gr_scores.append(dense_gr_p)

        # 2. Hybrid retrieval
        hybrid_results = search(q, top_k=top_k, mode="hybrid", include_non_merits=True)
        hybrid_kw_hits = sum(1 for r in hybrid_results if kw_re.search(r["best_chunk"]["text"]))
        hybrid_gr_hits = sum(1 for r in hybrid_results if r["primary_ground"] in expected_grounds)
        hybrid_kw_p = hybrid_kw_hits / top_k
        hybrid_gr_p = hybrid_gr_hits / top_k
        hybrid_kw_scores.append(hybrid_kw_p)
        hybrid_gr_scores.append(hybrid_gr_p)

        results_table.append({
            "topic": topic,
            "dense_kw_p": dense_kw_p,
            "hybrid_kw_p": hybrid_kw_p,
            "dense_gr_p": dense_gr_p,
            "hybrid_gr_p": hybrid_gr_p,
        })

    print("=" * 90)
    print(f"{'Topic':<25} | {'Dense P@5 (kw)':<15} | {'Hybrid P@5 (kw)':<15} | {'Dense P@5 (gr)':<15} | {'Hybrid P@5 (gr)':<15}")
    print("-" * 90)
    for r in results_table:
        print(f"{r['topic']:<25} | {r['dense_kw_p']:<15.2f} | {r['hybrid_kw_p']:<15.2f} | {r['dense_gr_p']:<15.2f} | {r['hybrid_gr_p']:<15.2f}")
    print("=" * 90)

    mean_dense_kw = sum(dense_kw_scores) / len(dense_kw_scores)
    mean_hybrid_kw = sum(hybrid_kw_scores) / len(hybrid_kw_scores)
    mean_dense_gr = sum(dense_gr_scores) / len(dense_gr_scores)
    mean_hybrid_gr = sum(hybrid_gr_scores) / len(hybrid_gr_scores)

    print(f"{'MEAN':<25} | {mean_dense_kw:<15.2f} | {mean_hybrid_kw:<15.2f} | {mean_dense_gr:<15.2f} | {mean_hybrid_gr:<15.2f}")
    print("=" * 90)

    print("\nSummary:")
    print(f"Keyword-in-chunk P@5: Dense = {mean_dense_kw:.1%}, Hybrid = {mean_hybrid_kw:.1%} (Delta: {mean_hybrid_kw - mean_dense_kw:+.1%})")
    print(f"Primary Ground   P@5: Dense = {mean_dense_gr:.1%}, Hybrid = {mean_hybrid_gr:.1%} (Delta: {mean_hybrid_gr - mean_dense_gr:+.1%})")

    if mean_hybrid_kw >= mean_dense_kw:
        print("Verdict: Hybrid retrieval matches or outperforms dense-only retrieval.")
    else:
        print("Verdict: Dense retrieval outperformed hybrid retrieval.")

    return {
        "dense_kw": mean_dense_kw,
        "hybrid_kw": mean_hybrid_kw,
        "dense_gr": mean_dense_gr,
        "hybrid_gr": mean_hybrid_gr
    }


def main():
    parser = argparse.ArgumentParser(description="Evaluate retrieval precision@5.")
    parser.add_argument("--eval-file", type=str, default="tests/retrieval_eval.json", help="Path to evaluation queries JSON")
    parser.add_argument("--top-k", type=int, default=5, help="Number of results to evaluate")
    args = parser.parse_args()

    evaluate(eval_file=args.eval_file, top_k=args.top_k)


if __name__ == "__main__":
    main()
