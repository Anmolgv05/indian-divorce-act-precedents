import os
import re
import pytest
import pandas as pd
from src.search import search, stats

INDEX_DIR = "data/index"


@pytest.fixture(scope="module")
def check_index_exists():
    emb_path = os.path.join(INDEX_DIR, "embeddings.npy")
    meta_path = os.path.join(INDEX_DIR, "meta.parquet")
    if not os.path.exists(emb_path) or not os.path.exists(meta_path):
        pytest.skip("Index files do not exist yet. Run src/embed_index.py first.")


def test_desertion_query_metrics(check_index_exists):
    # (a) desertion query: report real fraction of primary_ground matches and keyword-in-chunk
    query = "husband alleges wife deserted him for three years"
    results = search(query, top_k=5, index_dir=INDEX_DIR)
    assert len(results) == 5

    pg_matches = sum(1 for r in results if r["primary_ground"] == "desertion")
    pg_fraction = pg_matches / len(results)

    kw_re = re.compile(r"desert", re.I)
    kw_matches = sum(1 for r in results if kw_re.search(r["best_chunk"]["text"]))
    kw_fraction = kw_matches / len(results)

    print(f"\n[Desertion Query] primary_ground matches: {pg_matches}/5 ({pg_fraction:.0%}), keyword-in-chunk: {kw_matches}/5 ({kw_fraction:.0%})")
    assert kw_fraction >= 0.8, f"Expected keyword-in-chunk >= 80%, got {kw_fraction:.0%}"


def test_adultery_query_metrics(check_index_exists):
    # (b) adultery query: report real fraction of primary_ground matches and keyword-in-chunk
    query = "wife seeks divorce on ground of husband's adultery"
    results = search(query, top_k=5, index_dir=INDEX_DIR)
    assert len(results) == 5

    pg_matches = sum(1 for r in results if r["primary_ground"] == "adultery")
    pg_fraction = pg_matches / len(results)

    kw_re = re.compile(r"adulter", re.I)
    kw_matches = sum(1 for r in results if kw_re.search(r["best_chunk"]["text"]))
    kw_fraction = kw_matches / len(results)

    print(f"\n[Adultery Query] primary_ground matches: {pg_matches}/5 ({pg_fraction:.0%}), keyword-in-chunk: {kw_matches}/5 ({kw_fraction:.0%})")
    assert kw_fraction >= 0.8, f"Expected keyword-in-chunk >= 80%, got {kw_fraction:.0%}"


def test_non_consummation_query_metrics(check_index_exists):
    # (c) non-consummation query: report real fraction of primary_ground matches and keyword-in-chunk
    query = "marriage not consummated"
    results = search(query, top_k=5, index_dir=INDEX_DIR)
    assert len(results) == 5

    pg_matches = sum(1 for r in results if r["primary_ground"] in ["non_consummation", "nullity_sec19"])
    pg_fraction = pg_matches / len(results)

    kw_re = re.compile(r"consummat", re.I)
    kw_matches = sum(1 for r in results if kw_re.search(r["best_chunk"]["text"]))
    kw_fraction = kw_matches / len(results)

    print(f"\n[Non-consummation Query] primary_ground matches: {pg_matches}/5 ({pg_fraction:.0%}), keyword-in-chunk: {kw_matches}/5 ({kw_fraction:.0%})")
    assert kw_fraction >= 0.8, f"Expected keyword-in-chunk >= 80%, got {kw_fraction:.0%}"


def test_self_retrieval_sanity(check_index_exists):
    # (d) self-retrieval sanity check using facts chunk returning rank 1
    meta_path = os.path.join(INDEX_DIR, "meta.parquet")
    df = pd.read_parquet(meta_path)
    facts_chunks = df[(df["segment_type"] == "facts") & (~df["non_merits"])]
    facts_chunks = facts_chunks[facts_chunks["text"].apply(lambda t: len(t.split()) >= 30)]

    sample_cases = facts_chunks.drop_duplicates(subset=["doc_id"]).head(5)
    assert len(sample_cases) >= 3

    rank_1_hits = 0
    top_3_hits = 0
    total = len(sample_cases)
    for _, row in sample_cases.iterrows():
        query_snippet = row["text"][:200]
        results = search(query_snippet, top_k=5, index_dir=INDEX_DIR)
        doc_id = str(row["doc_id"])
        if results and results[0]["doc_id"] == doc_id:
            rank_1_hits += 1
        if any(r["doc_id"] == doc_id for r in results[:3]):
            top_3_hits += 1

    hit_rate = rank_1_hits / total
    top_3_rate = top_3_hits / total
    assert top_3_rate >= 0.8, f"Expected at least 80% top-3 hits, got {top_3_hits}/{total} ({top_3_rate:.0%})"
    assert hit_rate >= 0.6, f"Expected at least 60% rank-1 hits, got {rank_1_hits}/{total} ({hit_rate:.0%})"


def test_stats_computation():
    mock_results = [
        {"marriage_dissolved": "yes", "primary_ground": "desertion", "non_merits": False},
        {"marriage_dissolved": "yes", "primary_ground": "adultery", "non_merits": False},
        {"marriage_dissolved": "no", "primary_ground": "cruelty", "non_merits": False},
        {"marriage_dissolved": "unclear", "primary_ground": "desertion", "non_merits": False},
        {"marriage_dissolved": "yes", "primary_ground": "constitutional_validity", "non_merits": False},  # excluded from X/Y
        {"marriage_dissolved": "yes", "primary_ground": "procedural", "non_merits": False},  # excluded from X/Y
        {"marriage_dissolved": "yes", "primary_ground": "adultery", "non_merits": True},  # excluded
    ]
    st = stats(mock_results)
    assert st["n_retrieved"] == 7
    assert st["ended"] == 2
    assert st["did_not_end"] == 1
    assert st["unclear_or_na"] == 4
    assert "Of the 7 retrieved cases, 2 ended the marriage (dissolution/nullity), 1 did not, 4 unclear or not applicable." in st["summary"]
    assert "(Note: retrieved cases are not a success rate)" in st["summary"]


def test_out_of_corpus_low_confidence(check_index_exists):
    # Off-topic query should trigger low_confidence
    off_topic = "how to bake a chocolate cake"
    results_off = search(off_topic, top_k=5, index_dir=INDEX_DIR, confidence_threshold=0.50)
    assert len(results_off) > 0
    assert results_off[0]["low_confidence"] is True
    assert getattr(results_off, "low_confidence", False) is True
    st_off = stats(results_off)
    assert st_off["low_confidence"] is True
    assert "Low confidence" in st_off["summary"]

    # In-corpus query should have high confidence
    in_corpus = "husband alleges wife deserted him for three years without reasonable cause"
    results_in = search(in_corpus, top_k=5, index_dir=INDEX_DIR, confidence_threshold=0.50)
    assert len(results_in) > 0
    assert results_in[0]["low_confidence"] is False
    st_in = stats(results_in)
    assert st_in["low_confidence"] is False
    assert "Low confidence" not in st_in["summary"]


def test_out_of_scope_notice_adjacent_law():
    from src.search import out_of_scope_notice

    adjacent_queries = [
        "divorce under Hindu Marriage Act section 13 cruelty and desertion",
        "mutual consent divorce under section 13B Hindu Marriage Act",
        "restitution of conjugal rights under section 9 Hindu Marriage Act",
        "divorce under Special Marriage Act section 27 on grounds of adultery",
        "mutual consent divorce under section 28 Special Marriage Act",
        "talaq and dissolution of Muslim Marriages Act 1939",
        "maintenance under Muslim Women Protection of Rights on Divorce Act",
        "divorce under Parsi Marriage and Divorce Act 1936",
        "maintenance of wife and children under section 125 CrPC",
        "protection order and residence order under Domestic Violence Act 2005",
    ]

    for q in adjacent_queries:
        notice = out_of_scope_notice(q)
        assert notice is not None, f"Expected out-of-scope notice for: {q}"
        assert "Indian Divorce Act" in notice

    # Clean in-corpus query should have NO notice
    in_corpus = "husband alleges wife deserted him for three years without reasonable cause"
    assert out_of_scope_notice(in_corpus) is None
