import os
import csv
import pytest
from src.validate import select_stratified_sample, score_review_sheet


def make_dummy_case(doc_id, disposal="allowed", ground="adultery", non_merits=False, dup=None):
    return {
        "doc_id": str(doc_id),
        "url": f"https://indiankanoon.org/doc/{doc_id}/",
        "title": f"Case {doc_id} vs Other",
        "primary_ground": ground,
        "disposal": disposal,
        "marriage_dissolved": "yes" if disposal == "allowed" else "no",
        "relief": "dissolution" if disposal == "allowed" else "none",
        "petitioner_gender": "wife",
        "non_merits": non_merits,
        "possible_duplicate_of": dup,
        "segments": [{"type": "facts", "p_ids": ["p_1"], "text": "Sample facts."}]
    }


def test_select_stratified_sample():
    cases = []
    # confirmed (5)
    for i in range(1, 6): cases.append(make_dummy_case(f"conf_{i}", disposal="confirmed", ground="adultery"))
    # not_confirmed (5)
    for i in range(1, 6): cases.append(make_dummy_case(f"notconf_{i}", disposal="not_confirmed", ground="cruelty"))
    # remanded (5)
    for i in range(1, 6): cases.append(make_dummy_case(f"rem_{i}", disposal="remanded", ground="adultery"))
    # non-adultery/cruelty grounds (6)
    for i in range(1, 7): cases.append(make_dummy_case(f"other_{i}", disposal="allowed", ground="desertion"))
    # other cases (20)
    for i in range(1, 21): cases.append(make_dummy_case(f"norm_{i}", disposal="allowed", ground="adultery"))
    # excluded cases: non-merits and dup
    cases.append(make_dummy_case("ex_1", non_merits=True))
    cases.append(make_dummy_case("ex_2", dup="other_id"))

    sample = select_stratified_sample(cases, target_size=20, seed=42)
    assert len(sample) == 20
    doc_ids = {c["doc_id"] for c in sample}
    assert "ex_1" not in doc_ids
    assert "ex_2" not in doc_ids

    disposals = [c["disposal"] for c in sample]
    assert disposals.count("confirmed") >= 2
    assert disposals.count("not_confirmed") >= 2
    assert disposals.count("remanded") >= 2

    grounds = [c["primary_ground"] for c in sample]
    non_ac = [g for g in grounds if g not in ("adultery", "cruelty", "unclear")]
    assert len(non_ac) >= 3


def test_score_review_sheet(tmp_path, capsys):
    csv_file = tmp_path / "test_sheet.csv"
    with open(csv_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "doc_id", "url", "title", "primary_ground", "disposal", "marriage_dissolved", "relief", "petitioner_gender",
            "ground_ok", "disposal_ok", "dissolved_relief_ok", "petitioner_ok", "segments_ok", "correct_value_if_wrong", "notes"
        ])
        writer.writerow(["1", "url1", "T1", "adultery", "allowed", "yes", "dissolution", "wife", "1", "1", "1", "1", "1", "", ""])
        writer.writerow(["2", "url2", "T2", "cruelty", "dismissed", "no", "none", "husband", "0", "1", "1", "0", "1", "ground=desertion", ""])

    score_review_sheet(str(csv_file))
    captured = capsys.readouterr()
    assert "ground_ok" in captured.out
    assert "50.0%" in captured.out
    assert "100.0%" in captured.out
