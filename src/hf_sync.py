"""Hugging Face Dataset Sync & On-Demand Case Retrieval Module.

Connects the Section 10 Indian Divorce Act search engine to the Hugging Face Hub dataset:
https://huggingface.co/datasets/anabaena/section10-divorce-corpus
"""

from __future__ import annotations

import os
import json
import logging
import urllib.request
from pathlib import Path
from typing import Optional, Dict, Any, List

logger = logging.getLogger("hf_sync")

DEFAULT_HF_REPO = "anabaena/section10-divorce-corpus"
ROOT = Path(__file__).resolve().parent.parent
PARSED_DIR = ROOT / "data" / "parsed"
LABELED_FILE = ROOT / "data" / "labeled" / "cases.jsonl"


def get_hf_repo() -> str:
    return os.environ.get("HF_DATASET_REPO", DEFAULT_HF_REPO)


def fetch_case_from_hf(doc_id: str, cache_locally: bool = True) -> Optional[Dict[str, Any]]:
    """Fetches a parsed case JSON directly from Hugging Face Hub raw dataset."""
    if not doc_id or not str(doc_id).isdigit():
        return None

    repo_id = get_hf_repo()
    url = f"https://huggingface.co/datasets/{repo_id}/raw/main/parsed/{doc_id}.json"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Section10-App/2.0 (Legal-NLP)"}
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status == 200:
                raw_bytes = resp.read()
                data = json.loads(raw_bytes.decode("utf-8"))
                if cache_locally:
                    try:
                        PARSED_DIR.mkdir(parents=True, exist_ok=True)
                        target = PARSED_DIR / f"{doc_id}.json"
                        with open(target, "w", encoding="utf-8") as f:
                            f.write(raw_bytes.decode("utf-8"))
                        logger.info(f"Cached case {doc_id} from Hugging Face to {target}")
                    except Exception as e:
                        logger.warning(f"Failed to cache case {doc_id} locally: {e}")
                return data
    except Exception as e:
        logger.debug(f"Hugging Face fetch failed for {doc_id} ({url}): {e}")
        return None

    return None


def fetch_hf_dataset_metadata() -> Dict[str, Any]:
    """Retrieves dataset commit and metadata information from Hugging Face."""
    repo_id = get_hf_repo()
    api_url = f"https://huggingface.co/api/datasets/{repo_id}"
    req = urllib.request.Request(api_url, headers={"User-Agent": "Section10-App/2.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status == 200:
                return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        logger.warning(f"Could not fetch HF dataset metadata: {e}")
    return {"id": repo_id, "url": f"https://huggingface.co/datasets/{repo_id}"}


def get_case_hf_url(doc_id: str) -> str:
    """Returns the web URL to inspect the case on Hugging Face."""
    repo_id = get_hf_repo()
    return f"https://huggingface.co/datasets/{repo_id}/blob/main/parsed/{doc_id}.json"
