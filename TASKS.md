# TASKS.md — run in order, one at a time

Deadline target: ~2 weeks. Three people: **A** (pipeline owner), **B**, **C**.

## Team split
| Phase | Who | Output |
|---|---|---|
| 0 Setup | A | repo, requirements, config |
| 1 Collect URLs | A | `data/urls.txt`, split into 3 shards |
| 2 Scrape | A, B, C in parallel (one shard each) | `data/shards/shard_{0,1,2}.jsonl` |
| 3 Merge + parse | A | `data/parsed/` |
| 4 Segment + label | A (B, C review) | `data/labeled/cases.jsonl` |
| 5 Validate | B + C manually review 20 cases | `reports/validation.md` |
| 6 Embed + index | A | `data/index/` |
| 7 App | A | `app/app.py` |
| 8 Publish + screenshots | A, B, C | HF dataset, Space, screenshots, report |

---

## Task 0 — Setup
Create the repo layout from AGENTS.md. Add `requirements.txt` with pinned versions: requests, beautifulsoup4, lxml, pandas, pyarrow, pyyaml, tqdm, sentence-transformers, scikit-learn, numpy, gradio, transformers, torch (CPU), pytest, huggingface_hub. Add `config.yaml` (shard_id, shard_count, delay_seconds=2, user_agent, paths, embedding model). Add `.gitignore` (data/raw, data/parsed, .env).
**Done when:** `pip install -r requirements.txt` works on a clean venv.

## Task 1 — Collect URLs
Inspect how Indian Kanoon lists judgments citing a section (the "cited by" / search results for Section 10 of the Indian Divorce Act). Write `src/collect_urls.py` to collect document URLs/IDs, paginating politely, deduplicate, keep 150–250 candidates, save to `data/urls.txt`. Then write a small function that splits `urls.txt` into `shard_count` files by index modulo so shards never overlap.
First check robots.txt and report what is allowed before writing code.
**Done when:** `data/urls.txt` exists, no duplicates, shards created.

## Task 2 — Scrape (each person runs their own shard)
Write `src/scrape.py --shard N`. For each URL in its shard: fetch with delay and User-Agent, cache raw HTML in `data/raw/`, skip if cached, retry with backoff on errors, log failures to `reports/scrape_failures.txt`. Extract raw fields into `data/shards/shard_N.jsonl`: doc_id, url, title, court, date, full text with paragraph numbers preserved, and any structured tags the page exposes.
**Done when:** all three shards run and the merged count is >= 100 judgments.

## Task 3 — Parse and clean
`src/parse_clean.py`: merge shards, drop duplicates, drop documents that do not substantively discuss Section 10 (keep a list of dropped IDs and reasons), normalize whitespace, keep paragraph numbering. Write unit tests using 2–3 saved pages.

## Task 4 — Segment and label
Implement `src/labels.py` (taxonomy + keyword rules) and `src/segment_label.py` following the labeling strategy in AGENTS.md. Produce `data/labeled/cases.jsonl` matching the schema exactly. Print a summary table: counts per ground, per outcome, % unclear.
**Done when:** schema validates for every record and unclear rate is reported.

## Task 5 — Validate
`src/validate.py`: sample 20 random cases with a fixed seed and write a markdown checklist where reviewers (B and C) mark ground / outcome / segmentation as correct or wrong. After review, compute accuracy and write it into `reports/validation.md`. Fix rules for the most common errors and re-run Task 4.

## Task 6 — Embed and index
`src/embed_index.py`: embed every segment, save `embeddings.npy` and `meta.parquet` (doc_id, segment type, text, ground, outcome, year, url). Add a test that a query like "husband alleges wife deserted him for three years" returns desertion cases near the top.

## Task 7 — Search + app
`src/search.py`: `search(query, top_k, filters)` returns ranked cases with their best segments, plus stats on outcomes. Build the extractive answer template described in AGENTS.md. `app/app.py`: Gradio UI with a text box, optional filters (ground, outcome, year range), results as case cards with links, the argument/reasoning snippets, and the disclaimer.
**Done when:** `python app/app.py` runs locally and 5 test queries give sensible results.

## Task 8 — Publish
Push `data/labeled/` and `data/index/` to a Hugging Face dataset repo with a dataset card (source, method, label schema, limitations, how to reproduce). Deploy `app/` as a free HF Space. Take screenshots of 5 example queries for submission. Write a 1-page README covering approach, limitations (small dataset, rule-based labels, not legal advice), and future work.

---

## Handy prompts to paste into Antigravity
- "Read AGENTS.md and TASKS.md. Do only Task N. Show me the plan first, then implement, then run it and show output."
- "Before writing the scraper, fetch robots.txt and one sample document page, and tell me the HTML structure you found."
- "Add tests for what you just wrote using the saved sample pages, then run them."
