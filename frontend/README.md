# Section 10 Precedent Search: frontend v2

Bold, editorial redesign (serif display type, paper/ink palette with an oxblood accent, automatic dark mode).
React 18 + Vite, no UI libraries.

## Install over the existing frontend
```bash
# from the repo root
mv frontend frontend_old
unzip section10-frontend-v2.zip   # creates ./frontend
cd frontend && npm install && npm run build
cd .. && .venv/bin/python api.py   # serves the build at http://localhost:8000
```
Dev mode: `uvicorn api:app --reload --port 8000` and `cd frontend && npm run dev` (proxy to :8000 is preconfigured).

## What it expects from the API (unchanged endpoints)
- `POST /api/search` -> `{results[], stats{summary}, out_of_scope_notice, low_confidence, top_score}`
- `GET /api/config` -> optional `{grounds[], sample_queries[], case_count}`; the UI has fallbacks for all three.
- Each result: `doc_id, title, year, court, url, score, primary_ground, disposal, marriage_dissolved, relief, non_merits, possible_duplicate_of, best_chunk{text,segment_type}, petitioner_argument, respondent_argument, reasoning`.

All key mapping lives in `src/lib/api.js` (`normalizeCase`, `buildPayload`). If a field is renamed, fix it there only.
`buildPayload` sends aliases for the filter names (FastAPI ignores unknown fields); prune to the real ones once confirmed.

## Kept from v1 (do not remove)
Scope notice, "retrieved cases are not a success rate", low-confidence and adjacent-statute banners, "Not determined" instead of "unclear",
"Marriage ended" wording, neutral outcome colours, human-readable grounds, Indian Kanoon links, footer disclaimer.

## New
Query-term highlighting, relevance bars, copy-citation, shareable `?q=` links, skeleton loading, light/dark toggle, keyboard and screen-reader support, mobile layout.
