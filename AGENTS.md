# AGENTS.md — Section 10 Indian Divorce Act Case Search

Read this fully before doing any task. Then follow TASKS.md in order.

## Goal
A small, free, reproducible system for course submission:
1. **Database**: 100–200 Indian court judgments citing **Section 10, Indian Divorce Act, 1869**, each segmented and labeled (facts, arguments, law, reasoning, outcome).
2. **Search app**: user describes a situation in plain English, system returns similar cases, how courts ruled, and the arguments used. **No LLM required.**

## Hard constraints
- Everything free: no paid APIs, no GPU, must run on a normal laptop CPU.
- No fine-tuning. Pretrained small models only (sentence-transformers, small zero-shot classifier).
- Keep it basic and readable. Prefer plain Python over frameworks.
- Be polite when scraping: >=2s delay between requests, descriptive User-Agent, cache every response to disk, never re-fetch a cached page.
- Reproducible: pinned `requirements.txt`, every step is a script runnable from the CLI, fixed random seeds.
- Output of each stage is a file on disk so stages can be re-run independently.

## Architecture
```
Indian Kanoon (Sec 10 citing judgments)
  -> 01 collect_urls   -> data/urls.txt
  -> 02 scrape         -> data/raw/{doc_id}.html  (+ shard jsonl)
  -> 03 parse_clean    -> data/parsed/{doc_id}.json
  -> 04 segment_label  -> data/labeled/cases.jsonl
  -> 05 validate       -> reports/validation.md (+ manual review sample)
  -> 06 embed_index    -> data/index/embeddings.npy + meta.parquet
  -> 07 app (Gradio)   -> app/app.py
  -> 08 publish        -> HF dataset repo + HF Space
```

## Repo layout
```
.
├── AGENTS.md
├── TASKS.md
├── requirements.txt
├── config.yaml              # shard id, delay, paths, model names
├── src/
│   ├── collect_urls.py
│   ├── scrape.py
│   ├── parse_clean.py
│   ├── segment_label.py
│   ├── validate.py
│   ├── embed_index.py
│   ├── search.py            # retrieval + extractive answer (no UI code)
│   └── labels.py            # label taxonomy + keyword rules
├── app/app.py
├── data/ (gitignored except labeled/ and index/)
├── reports/
└── tests/
```

## Label schema (one record per judgment, in cases.jsonl)
```json
{
  "doc_id": "123456",
  "url": "https://indiankanoon.org/doc/123456/",
  "title": "", "court": "", "date": "YYYY-MM-DD", "year": 0,
  "grounds": ["adultery"],
  "primary_ground": "adultery",
  "disposal": "allowed | dismissed | partly_allowed | remanded | disposed_of | unclear",
  "marriage_dissolved": "yes | no | unclear",
  "petitioner_gender": "husband | wife | unclear",
  "statutes_cited": ["Section 10", "Section 10A", "..."],
  "precedents_cited": ["..."],
  "segments": [
    {"type": "facts | issue | petitioner_argument | respondent_argument | law | reasoning | conclusion",
     "text": "...", "p_ids": ["p_3", "p_4", "p_5"]}
  ],
  "label_source": {"grounds": "rule|zeroshot|manual", "disposal": "rule|manual", "marriage_dissolved": "rule|manual"}
}
```

### Ground taxonomy (aligned with Indian Divorce Act, 1869 as amended)
adultery, cruelty, desertion, conversion, unsound_mind, leprosy, venereal_disease, presumed_dead_7_years, non_consummation, restitution_noncompliance, wife_specific (rape/sodomy/bestiality), mutual_consent_10a, nullity_sec19, procedural (confirmation/jurisdiction/interim), other, unclear.

## Labeling strategy (in order of preference)
1. If the Indian Kanoon page exposes structured tags (facts, issues, arguments, reasoning, conclusion), harvest them directly.
2. Otherwise segment by paragraph numbers and rule-based cues (e.g. "contended", "learned counsel for the appellant/respondent", "we are of the view", "in the result", "appeal is allowed/dismissed").
3. Ground: keyword rules first, then zero-shot classifier (small NLI model, CPU) only for cases rules mark unclear.
4. Outcome: rules on the final 15% of the text. Anything ambiguous -> `unclear`, never guess.
5. Manually review 20 random cases and report accuracy in `reports/validation.md`.

## Retrieval and answer (no LLM)
- Embed **segments**, not whole judgments. Model: `BAAI/bge-small-en-v1.5` (fallback `all-MiniLM-L6-v2`).
- Cosine kNN with sklearn. Top-k segments -> group by case -> rank cases.
- Answer is **extractive and templated**: matching cases (with links), grounds, outcomes, petitioner vs respondent arguments, key reasoning passage, and simple stats ("N of M similar cases granted").
- Always show a disclaimer: educational project, not legal advice. Always cite the source URL.
- Optional later: a flag to add a tiny generator. Off by default.

## Working agreement for the agent
- Do one task from TASKS.md at a time. Run it, show output, then stop for review.
- Write small tests for parsing and labeling functions using 2–3 saved sample pages.
- Never invent case data. If a field cannot be extracted, set it to null/unclear.
- Do not commit raw HTML or secrets.
