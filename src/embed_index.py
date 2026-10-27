"""
Task 6: Embedding and indexing module for Section 10 Indian Divorce Act judgments.
1. Chunks all judgment segments longer than ~200 words into overlapping windows (200 words, 40 words overlap).
2. Embeds all chunks using BAAI/bge-small-en-v1.5 with SentenceTransformers on CPU (normalized, batch size 32).
3. Fits TfidfVectorizer(sublinear_tf=True, ngram_range=(1,2), stop_words='english') on chunk text.
4. Saves data/index/embeddings.npy, data/index/meta.parquet, and data/index/tfidf_*.joblib.
5. Supports --meta-only to rebuild labels safely with chunk_hash validation without re-embedding.
"""

import os
import json
import hashlib
import argparse
import numpy as np
import pandas as pd
import joblib
import torch
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer


def chunk_text(text: str, max_words: int = 200, overlap: int = 40) -> list[str]:
    """Splits text into overlapping word chunks so nothing is truncated at 512 tokens."""
    words = text.split()
    if len(words) <= max_words:
        return [text]
    chunks = []
    step = max(1, max_words - overlap)
    for i in range(0, len(words), step):
        chunk_words = words[i:i + max_words]
        if not chunk_words:
            break
        chunks.append(" ".join(chunk_words))
        if i + max_words >= len(words):
            break
    return chunks


def build_chunks(cases: list[dict], max_words: int = 200, overlap: int = 40) -> list[dict]:
    """Flattens all cases and their segments into chunks with metadata and chunk_hash."""
    records = []
    for c in cases:
        doc_id = c["doc_id"]
        title = c.get("title", "")
        raw_year = c.get("year")
        year = int(raw_year) if (raw_year and int(raw_year) > 0) else None
        court = c.get("court", "")
        url = c.get("url", f"https://indiankanoon.org/doc/{doc_id}/")
        primary_ground = c.get("primary_ground", "unclear")
        disposal = c.get("disposal", "unclear")
        marriage_dissolved = c.get("marriage_dissolved", "unclear")
        relief = c.get("relief", "unclear")
        non_merits = c.get("non_merits", False)
        dup_of = c.get("possible_duplicate_of")
        if isinstance(dup_of, list):
            dup_of = ", ".join(str(x) for x in dup_of)

        grounds_list = c.get("grounds", [])
        grounds_str = ", ".join(grounds_list) if isinstance(grounds_list, list) else str(grounds_list)

        for seg in c.get("segments", []):
            stype = seg.get("type", "unknown")
            stext = seg.get("text", "").strip()
            p_ids = seg.get("p_ids", [])
            p_ids_str = ", ".join(p_ids)

            if not stext:
                continue

            sub_chunks = chunk_text(stext, max_words=max_words, overlap=overlap)
            for c_idx, chunk in enumerate(sub_chunks):
                ch_hash = hashlib.sha256(chunk.strip().encode("utf-8")).hexdigest()
                records.append({
                    "doc_id": str(doc_id),
                    "title": title,
                    "year": year,
                    "court": court,
                    "url": url,
                    "segment_type": stype,
                    "chunk_idx": c_idx,
                    "chunk_hash": ch_hash,
                    "p_ids": p_ids_str,
                    "text": chunk,
                    "grounds": grounds_str,
                    "primary_ground": primary_ground,
                    "disposal": disposal,
                    "marriage_dissolved": marriage_dissolved,
                    "relief": relief,
                    "non_merits": bool(non_merits),
                    "possible_duplicate_of": str(dup_of) if dup_of else None
                })
    return records


def fit_and_save_tfidf(texts: list[str], output_dir: str):
    """Fits and saves TfidfVectorizer and transformed chunk matrix."""
    print("Fitting TfidfVectorizer (sublinear_tf=True, ngram_range=(1,2), stop_words='english')...")
    vec = TfidfVectorizer(sublinear_tf=True, ngram_range=(1, 2), stop_words="english")
    tfidf_matrix = vec.fit_transform(texts)

    vec_path = os.path.join(output_dir, "tfidf_vectorizer.joblib")
    mat_path = os.path.join(output_dir, "tfidf_matrix.joblib")
    joblib.dump(vec, vec_path)
    joblib.dump(tfidf_matrix, mat_path)
    print(f"Saved TF-IDF vectorizer to {vec_path} and matrix (shape: {tfidf_matrix.shape}) to {mat_path}")
    return vec, tfidf_matrix


def update_meta_only(
    labeled_file: str = "data/labeled/cases.jsonl",
    output_dir: str = "data/index"
):
    """Rebuilds metadata from cases.jsonl, asserting every chunk hash matches stored embeddings."""
    emb_path = os.path.join(output_dir, "embeddings.npy")
    meta_path = os.path.join(output_dir, "meta.parquet")
    if not os.path.exists(emb_path):
        raise FileNotFoundError(f"Embeddings file {emb_path} not found. Run full indexing first.")

    print(f"Loading labeled cases from {labeled_file}...")
    cases = []
    with open(labeled_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                cases.append(json.loads(line))

    chunk_records = build_chunks(cases, max_words=200, overlap=40)
    embeddings = np.load(emb_path)
    assert len(chunk_records) == embeddings.shape[0], (
        f"Chunk count mismatch: new {len(chunk_records)} vs embeddings {embeddings.shape[0]}"
    )

    if os.path.exists(meta_path):
        old_df = pd.read_parquet(meta_path)
        if "chunk_hash" in old_df.columns:
            for i, r in enumerate(chunk_records):
                old_hash = old_df.iloc[i]["chunk_hash"]
                assert r["chunk_hash"] == old_hash, (
                    f"Chunk hash mismatch at index {i}: {r['chunk_hash']} vs {old_hash}"
                )
            print(f"Verified {len(chunk_records)} chunk hashes against existing meta.parquet!")
        else:
            print("Existing meta.parquet did not have chunk_hash; verified chunk count.")

    new_df = pd.DataFrame(chunk_records)
    new_df.to_parquet(meta_path, index=False)
    print(f"Successfully refreshed metadata in {meta_path} (shape: {new_df.shape}) without re-embedding.")

    texts = [r["text"] for r in chunk_records]
    fit_and_save_tfidf(texts, output_dir)
    return new_df


def embed_and_index(
    labeled_file: str = "data/labeled/cases.jsonl",
    output_dir: str = "data/index",
    model_name: str = "BAAI/bge-small-en-v1.5",
    batch_size: int = 32
):
    os.makedirs(output_dir, exist_ok=True)

    print(f"Loading labeled cases from {labeled_file}...")
    cases = []
    with open(labeled_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                cases.append(json.loads(line))

    print(f"Loaded {len(cases)} cases. Splitting segments into chunks (200 words, 40 overlap)...")
    chunk_records = build_chunks(cases, max_words=200, overlap=40)
    print(f"Total chunks created: {len(chunk_records)}")

    texts = [r["text"] for r in chunk_records]

    # Check for existing cached embeddings by chunk_hash
    emb_path = os.path.join(output_dir, "embeddings.npy")
    meta_path = os.path.join(output_dir, "meta.parquet")
    cache = {}
    if os.path.exists(emb_path) and os.path.exists(meta_path):
        try:
            old_meta = pd.read_parquet(meta_path)
            old_emb = np.load(emb_path)
            if len(old_meta) == len(old_emb) and "chunk_hash" in old_meta.columns:
                for idx, h in enumerate(old_meta["chunk_hash"]):
                    cache[h] = old_emb[idx]
                print(f"Loaded {len(cache)} existing cached chunk embeddings from {emb_path}")
        except Exception as e:
            print(f"Warning: could not load existing cache: {e}")

    missing_indices = [i for i, r in enumerate(chunk_records) if r["chunk_hash"] not in cache]
    print(f"Chunks to embed: {len(missing_indices)} new (reusing {len(chunk_records) - len(missing_indices)} from cache)")

    if missing_indices:
        print(f"Loading embedding model: {model_name} on CPU...")
        model = SentenceTransformer(model_name, device="cpu")

        texts_to_embed = [chunk_records[i]["text"] for i in missing_indices]
        print(f"Encoding {len(texts_to_embed)} new chunks (batch_size={batch_size}, normalized, CPU)...")
        new_embeddings = model.encode(
            texts_to_embed,
            batch_size=batch_size,
            show_progress_bar=True,
            normalize_embeddings=True,
            convert_to_numpy=True
        )
        for idx, orig_idx in enumerate(missing_indices):
            cache[chunk_records[orig_idx]["chunk_hash"]] = new_embeddings[idx]

    embeddings = np.array([cache[r["chunk_hash"]] for r in chunk_records], dtype=np.float32)

    print(f"Saving embeddings to {emb_path} (shape: {embeddings.shape})...")
    np.save(emb_path, embeddings)

    print(f"Saving metadata to {meta_path}...")
    df = pd.DataFrame(chunk_records)
    df.to_parquet(meta_path, index=False)

    fit_and_save_tfidf(texts, output_dir)

    print("Indexing complete!")
    return embeddings, df


def main():
    parser = argparse.ArgumentParser(description="Task 6: Embed and index judgment chunks.")
    parser.add_argument("--labeled-file", type=str, default="data/labeled/cases.jsonl", help="Path to labeled cases.jsonl")
    parser.add_argument("--output-dir", type=str, default="data/index", help="Output directory for index artifacts")
    parser.add_argument("--model", type=str, default="BAAI/bge-small-en-v1.5", help="Embedding model name")
    parser.add_argument("--batch-size", type=int, default=32, help="Encoding batch size")
    parser.add_argument("--meta-only", action="store_true", help="Rebuild metadata and TF-IDF only (requires matching embeddings)")
    args = parser.parse_args()

    if args.meta_only:
        update_meta_only(labeled_file=args.labeled_file, output_dir=args.output_dir)
    else:
        embed_and_index(
            labeled_file=args.labeled_file,
            output_dir=args.output_dir,
            model_name=args.model,
            batch_size=args.batch_size
        )


if __name__ == "__main__":
    main()
