// ---------------------------------------------------------------------------
// API layer. normalizeCase() absorbs minor key differences between backend
// versions, so a renamed field degrades gracefully instead of crashing the UI.
// If the backend uses a key not listed here, add it in ONE place below.
// ---------------------------------------------------------------------------
const pick = (o, ...keys) => {
  for (const k of keys) if (o && o[k] !== undefined && o[k] !== null) return o[k]
  return undefined
}

const toText = (v) => {
  if (v == null) return ''
  if (typeof v === 'string') return v
  if (Array.isArray(v)) return v.map(toText).filter(Boolean).join('\n\n')
  if (typeof v === 'object') return toText(pick(v, 'text', 'chunk_text', 'content'))
  return String(v)
}

export function normalizeCase(r) {
  const docId = pick(r, 'doc_id', 'id')
  const best = pick(r, 'best_chunk') || {}
  const seg = pick(r, 'segments') || {}
  const yr = Number(pick(r, 'year'))
  return {
    docId,
    doc_id: docId,
    id: docId,
    title: pick(r, 'title') || `Judgment ${docId}`,
    year: Number.isFinite(yr) && yr > 0 ? yr : null,
    court: pick(r, 'court') || '',
    url: pick(r, 'url', 'link') || `https://indiankanoon.org/doc/${docId}/`,
    score: Number(pick(r, 'score', 'hybrid_score', 'relevance')) || 0,
    ground: pick(r, 'primary_ground', 'ground') || 'unclear',
    primary_ground: pick(r, 'primary_ground', 'ground') || 'unclear',
    grounds: pick(r, 'grounds') || [],
    disposal: pick(r, 'disposal') || 'unclear',
    dissolved: pick(r, 'marriage_dissolved', 'dissolved') || 'unclear',
    marriage_dissolved: pick(r, 'marriage_dissolved', 'dissolved') || 'unclear',
    relief: pick(r, 'relief') || 'unclear',
    outcomeSummary: pick(r, 'outcome_summary', 'holding') || '',
    nonMerits: !!pick(r, 'non_merits', 'nonMerits'),
    non_merits: !!pick(r, 'non_merits', 'nonMerits'),
    duplicateOf: pick(r, 'possible_duplicate_of', 'duplicate_of') || null,
    excerpt: toText(typeof best === 'string' ? best : best.text) || toText(pick(r, 'best_chunk_text', 'excerpt')),
    passage: toText(typeof best === 'string' ? best : best.text) || toText(pick(r, 'best_chunk_text', 'excerpt')),
    best_chunk: best,
    excerptType: (typeof best === 'object' && best.segment_type) || pick(r, 'best_segment_type') || '',

    roles: [
      { key: 'petitioner_argument', title: "Petitioner's argument",
        text: toText(pick(r, 'petitioner_argument', 'petitioner_arguments') ?? seg.petitioner_argument) },
      { key: 'respondent_argument', title: "Respondent's argument",
        text: toText(pick(r, 'respondent_argument', 'respondent_arguments') ?? seg.respondent_argument) },
      { key: 'reasoning', title: "Court's reasoning",
        text: toText(pick(r, 'reasoning') ?? seg.reasoning) },
    ].filter((x) => x.text),
  }
}

// The request carries a few aliases for each filter; FastAPI ignores unknown
// fields, so whichever name the backend models is the one that takes effect.
// Once confirmed, prune this to the real names.
export function buildPayload({ query, topK, ground, yearMin, yearMax, includeNonMerits, showDuplicates }) {
  const p = { query, top_k: topK, include_non_merits: includeNonMerits }
  if (ground) { p.ground = ground; p.primary_ground = ground }
  if (yearMin || yearMax) {
    p.year_min = yearMin || undefined; p.year_max = yearMax || undefined
    p.min_year = yearMin || undefined; p.max_year = yearMax || undefined
    p.year_range = [yearMin || 1800, yearMax || 2100]
  }
  p.show_duplicates = showDuplicates; p.include_duplicates = showDuplicates
  p.collapse_duplicates = !showDuplicates
  return p
}

export async function search(params, signal) {
  const res = await fetch('/api/search', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(buildPayload(params)), signal,
  })
  if (!res.ok) throw new Error(`The search service answered with ${res.status}.`)
  const d = await res.json()
  return {
    results: (d.results || []).map(normalizeCase),
    stats: d.stats || {},
    notice: d.out_of_scope_notice || null,
    lowConfidence: !!(d.low_confidence ?? d.stats?.low_confidence),
    topScore: Number(d.top_score ?? d.results?.[0]?.score) || 0,
    detectedLanguage: d.detected_language || null,
    effectiveQuery: d.effective_query || null,
    entitiesDetected: d.entities_detected || null,
    fallbackAvailable: !!d.fallback_available,
  }
}

export async function decomposeQuery(query) {
  const res = await fetch('/api/ai/decompose', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  })
  if (!res.ok) throw new Error('AI decomposition failed')
  return await res.json()
}

export async function fallbackResearch(query, topScore, cases = []) {
  const res = await fetch('/api/ai/fallback-research', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, top_score: topScore, cases }),
  })
  if (!res.ok) throw new Error('AI precedent research failed')
  return await res.json()
}

export async function loadConfig() {
  try {
    const res = await fetch('/api/config')
    if (!res.ok) return {}
    return await res.json()
  } catch { return {} }
}

// Outcome tally for the distribution bar. Same exclusion rule as the backend:
// non-merits, constitutional and procedural cases are never counted as outcomes.
export function tally(results) {
  let ended = 0, notEnded = 0, other = 0
  for (const c of results) {
    const excluded = c.nonMerits || c.ground === 'constitutional_validity' || c.ground === 'procedural'
    if (excluded || c.dissolved === 'unclear') other++
    else if (c.dissolved === 'yes') ended++
    else if (c.dissolved === 'no') notEnded++
    else other++
  }
  return { ended, notEnded, other, total: results.length }
}
