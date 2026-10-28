import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { loadConfig, search, decomposeQuery, fallbackResearch } from './lib/api.js'
import { queryTerms } from './lib/format.js'
import Filters from './components/Filters.jsx'
import Stats from './components/Stats.jsx'
import CaseCard from './components/CaseCard.jsx'
import { Banner } from './components/Banners.jsx'
import SiteNav from './SiteNav.jsx'
import Summary from './Summary.jsx'
import PrintReport from './PrintReport.jsx'


const FALLBACK_SAMPLES = [
  'husband alleges wife deserted him for three years',
  'wife seeks divorce on ground of husband’s adultery',
  'marriage not consummated',
  'cruelty by husband, wife seeks dissolution',
  'confirmation of decree nisi by the High Court',
  'divorce under Hindu Marriage Act section 13',
]
const FALLBACK_GROUNDS = ['adultery', 'cruelty', 'desertion', 'non_consummation', 'nullity_sec19', 'mutual_consent_10A', 'procedural', 'constitutional_validity']
const DEFAULT_FILTERS = { ground: '', topK: 8, yearMin: '', yearMax: '', includeNonMerits: false, showDuplicates: false }

function useTheme() {
  const [theme, setTheme] = useState(() => document.documentElement.dataset.theme || '')
  const toggle = () => {
    const dark = theme ? theme === 'dark' : window.matchMedia('(prefers-color-scheme: dark)').matches
    const next = dark ? 'light' : 'dark'
    setTheme(next)
    document.documentElement.dataset.theme = next
    try { localStorage.setItem('s10-theme', next) } catch { /* private mode */ }
  }
  return toggle
}

export default function App() {
  const toggleTheme = useTheme()
  const [config, setConfig] = useState({})
  const [query, setQuery] = useState('')
  const [filters, setFilters] = useState(DEFAULT_FILTERS)
  const [showFilters, setShowFilters] = useState(false)
  const [state, setState] = useState({ status: 'idle', data: null, error: '', asked: '' })
  const [decomp, setDecomp] = useState({ status: 'idle', data: null, error: '' })
  const [aiResearch, setAiResearch] = useState({ status: 'idle', data: null, error: '' })
  const abort = useRef(null)
  const inputRef = useRef(null)

  useEffect(() => { loadConfig().then(setConfig) }, [])

  const run = useCallback(async (q, f = filters) => {
    const text = q.trim()
    if (!text) return
    abort.current?.abort()
    const ctl = new AbortController()
    abort.current = ctl
    setState((s) => ({ ...s, status: 'loading', error: '', asked: text }))
    setAiResearch({ status: 'idle', data: null, error: '' })
    try {
      const data = await search({ query: text, ...f }, ctl.signal)
      setState({ status: 'done', data, error: '', asked: text })
    } catch (e) {
      if (e.name === 'AbortError') return
      setState({ status: 'error', data: null, asked: text,
        error: e.message === 'Failed to fetch' ? 'Cannot reach the search service. Is the API running on port 8000?' : e.message })
    }
    try { const u = new URL(window.location); u.searchParams.set('q', text); window.history.replaceState(null, '', u) } catch { /* ignore */ }
  }, [filters])

  const handleDecompose = async () => {
    if (!query.trim()) return
    setDecomp({ status: 'loading', data: null, error: '' })
    try {
      const res = await decomposeQuery(query)
      setDecomp({ status: 'done', data: res, error: '' })
    } catch (e) {
      setDecomp({ status: 'error', data: null, error: e.message })
    }
  }

  const handleFallbackResearch = async () => {
    if (!state.asked) return
    setAiResearch({ status: 'loading', data: null, error: '' })
    try {
      const res = await fallbackResearch(state.asked, state.data?.topScore || 0, state.data?.results || [])
      setAiResearch({ status: 'done', data: res, error: '' })
    } catch (e) {
      setAiResearch({ status: 'error', data: null, error: e.message })
    }
  }

  // Deep link: ?q=... runs on load.
  useEffect(() => {
    let q = new URLSearchParams(window.location.search).get('q')
    if (!q && window.location.hash.includes('?')) {
      const hashQuery = window.location.hash.slice(window.location.hash.indexOf('?'))
      q = new URLSearchParams(hashQuery).get('q')
    }
    if (q) { setQuery(q); run(q) }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const onSubmit = (e) => { e.preventDefault(); run(query) }
  const pickSample = (s) => { setQuery(s); run(s); inputRef.current?.focus() }
  const terms = useMemo(() => queryTerms(state.asked), [state.asked])
  const samples = config.sample_queries?.length ? config.sample_queries : FALLBACK_SAMPLES
  const grounds = config.grounds?.length ? config.grounds : FALLBACK_GROUNDS
  const data = state.data
  const scoreMax = data?.results?.[0]?.score || 1
  const caseCount = config.case_count ?? config.num_cases ?? config.cases

  return (
    <>
      <SiteNav />

      <main id="main">
        <section className="hero no-print">
          <p className="eyebrow">Precedent search · Indian Divorce Act, 1869</p>
          <h1>Find the judgments <em>that read like your facts.</em></h1>
          <p className="lede">
            Describe a situation in plain words. Get similar Section 10 judgments with the exact passages that matched
            {caseCount ? `, drawn from ${caseCount} reported cases` : ''}. Similar past cases, not predictions, not legal advice.
          </p>

          <form className="search no-print" onSubmit={onSubmit} role="search">
            <label htmlFor="q" className="sr">Describe the case</label>
            <div className="search-box">
              <input id="q" ref={inputRef} value={query} onChange={(e) => setQuery(e.target.value)}
                placeholder="e.g. wife left the matrimonial home and refused to return for five years" autoComplete="off" autoFocus />
              {query && <button type="button" className="clear" onClick={() => { setQuery(''); inputRef.current?.focus() }} aria-label="Clear query">×</button>}
              <button type="submit" className="go" disabled={state.status === 'loading' || !query.trim()}>
                {state.status === 'loading' ? <span className="spin" aria-label="Searching" /> : <>Search <span aria-hidden="true">→</span></>}
              </button>
            </div>
            <div className="search-sub">
              <button type="button" className="refine" aria-expanded={showFilters} aria-controls="filters" onClick={() => setShowFilters(!showFilters)}>
                Refine <i className={showFilters ? 'up' : ''} aria-hidden="true" />
              </button>
              <button
                type="button"
                className="ai-assist-btn"
                style={{
                  background: 'none', border: '1px dashed var(--accent, #2563eb)',
                  color: 'var(--accent, #2563eb)', borderRadius: '6px', padding: '0.2rem 0.6rem',
                  fontSize: '0.82rem', fontWeight: 600, cursor: 'pointer'
                }}
                onClick={handleDecompose}
                disabled={decomp.status === 'loading' || !query.trim()}
              >
                {decomp.status === 'loading' ? '⚡ Analyzing...' : '⚡ AI Scenario Breakdown'}
              </button>
              <div className="samples" aria-label="Example searches">
                <span>Try</span>
                {samples.slice(0, 6).map((s) => <button key={s} type="button" onClick={() => pickSample(s)}>{s}</button>)}
              </div>
            </div>
            {decomp.status === 'done' && decomp.data && (
              <div className="decomp-box" style={{
                background: 'var(--panel, #f8fafc)', border: '1px solid var(--border, #e2e8f0)',
                borderRadius: '8px', padding: '0.85rem 1rem', margin: '0.75rem 0', fontSize: '0.88rem'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                  <strong style={{ color: 'var(--accent)' }}>⚡ AI Query Breakdown for SLM:</strong>
                  <button type="button" onClick={() => setDecomp({ status: 'idle', data: null, error: '' })} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--muted)' }}>✕</button>
                </div>
                {decomp.data.grounds?.length > 0 && <div style={{ marginBottom: '0.25rem' }}><b>Identified Grounds:</b> {decomp.data.grounds.join(', ')}</div>}
                {decomp.data.statutory_sections?.length > 0 && <div style={{ marginBottom: '0.25rem' }}><b>Sections:</b> {decomp.data.statutory_sections.join(', ')}</div>}
                {decomp.data.slm_search_queries?.length > 0 && (
                  <div style={{ marginTop: '0.5rem' }}>
                    <b>Targeted SLM Queries (click to search):</b>
                    <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap', marginTop: '0.3rem' }}>
                      {decomp.data.slm_search_queries.map((q) => (
                        <button key={q} type="button" className="rd-btn sm" onClick={() => pickSample(q)} style={{ fontSize: '0.8rem', padding: '0.2rem 0.5rem' }}>
                          🔍 {q}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
            {showFilters && <div className="no-print"><Filters value={filters} onChange={setFilters} grounds={grounds} /></div>}
          </form>
        </section>

        <section id="results" className="results" aria-live="polite">
          {state.status === 'loading' && (
            <div className="skeletons" aria-hidden="true">{[0, 1, 2].map((i) => <div key={i} className="sk" style={{ '--i': i }} />)}</div>
          )}

          {state.status === 'error' && <Banner tone="warn" title="Search unavailable">{state.error}</Banner>}

          {state.status === 'done' && data && (
            <>
              <div className="results-head">
                <h2>{data.results.length} similar {data.results.length === 1 ? 'judgment' : 'judgments'}</h2>
                <p>for “{state.asked}”</p>
              </div>

              {/* Entity Resolution Pills */}
              {data.entitiesDetected && (
                (data.entitiesDetected.courts?.length > 0) ||
                (data.entitiesDetected.grounds?.length > 0) ||
                (data.entitiesDetected.sections?.length > 0) ||
                (data.entitiesDetected.statutory_bars?.length > 0)
              ) && (
                <div className="entity-pills-bar" style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap', margin: '0.5rem 0 1rem' }}>
                  {data.entitiesDetected.courts?.map((c) => <span key={c} className="kg-conn-pill" style={{ background: '#e0f2fe', color: '#0369a1' }}>🏛️ {c}</span>)}
                  {data.entitiesDetected.grounds?.map((g) => <span key={g} className="kg-conn-pill" style={{ background: '#fef3c7', color: '#b45309' }}>⚖️ Ground: {g}</span>)}
                  {data.entitiesDetected.sections?.map((s) => <span key={s} className="kg-conn-pill" style={{ background: '#dcfce7', color: '#15803d' }}>📜 {s}</span>)}
                  {data.entitiesDetected.statutory_bars?.map((b) => <span key={b} className="kg-conn-pill" style={{ background: '#fee2e2', color: '#b91c1c' }}>⚠️ Statutory Bar: {b}</span>)}
                </div>
              )}

              {data.detectedLanguage && (
                <div className="multilingual-badge-banner" role="status" style={{
                  background: 'var(--panel, #f8f9fa)',
                  border: '1px solid var(--border, #e2e8f0)',
                  borderRadius: '8px',
                  padding: '0.75rem 1rem',
                  margin: '0.5rem 0 1rem',
                  fontSize: '0.88rem',
                  color: 'var(--ink, #1a202c)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.6rem',
                  flexWrap: 'wrap'
                }}>
                  <span style={{ fontWeight: 600, color: 'var(--accent, #1d4ed8)' }}>🌐 {data.detectedLanguage} Query Detected</span>
                  <span>— Matched English precedents for statutory terms: <em>"{data.effectiveQuery}"</em></span>
                </div>
              )}

              {data.notice && <Banner tone="note" title="Different statute?">{data.notice}</Banner>}

              {/* Parallel AI Fallback Panel for Low Confidence or Weak Matches */}
              {(data.lowConfidence || data.fallbackAvailable || data.results.length === 0) && (
                <div className="ai-fallback-panel" style={{
                  background: 'var(--panel, #f8fafc)',
                  border: '1px solid var(--accent, #2563eb)',
                  borderRadius: '12px',
                  padding: '1.25rem 1.5rem',
                  margin: '1rem 0 1.5rem',
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.75rem' }}>
                    <div>
                      <h3 style={{ fontSize: '1.05rem', margin: 0, color: 'var(--ink)' }}>🤖 Research Precedents with Parallel AI</h3>
                      <p style={{ margin: '0.2rem 0 0', color: 'var(--muted)', fontSize: '0.88rem' }}>
                        Local database confidence is low. Trigger live web-grounded research across High Court &amp; Supreme Court decisions.
                      </p>
                    </div>
                    <button
                      type="button"
                      className="rd-btn strong"
                      disabled={aiResearch.status === 'loading'}
                      onClick={handleFallbackResearch}
                      style={{ background: 'var(--accent)', color: '#fff', padding: '0.5rem 1rem', borderRadius: '6px', cursor: 'pointer' }}
                    >
                      {aiResearch.status === 'loading' ? 'Researching precedents…' : 'Run Deep Precedent Research ↗'}
                    </button>
                  </div>
                  {aiResearch.status === 'done' && aiResearch.data && (
                    <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid var(--border)' }}>
                      <p style={{ whiteSpace: 'pre-wrap', lineHeight: 1.6, fontSize: '0.94rem' }}>{aiResearch.data.research_synthesis}</p>
                      {aiResearch.data.citations?.length > 0 && (
                        <div style={{ marginTop: '1rem' }}>
                          <h4 style={{ fontSize: '0.9rem', color: 'var(--muted)', marginBottom: '0.4rem' }}>Verified Sources &amp; Precedents:</h4>
                          <ul style={{ paddingLeft: '1.2rem', margin: 0, fontSize: '0.88rem' }}>
                            {aiResearch.data.citations.map((c, idx) => (
                              <li key={idx}><a href={c.url} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--accent)' }}>{c.title}</a></li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}
                  {aiResearch.status === 'error' && (
                    <p style={{ color: 'var(--danger, #dc2626)', marginTop: '0.75rem', fontSize: '0.88rem' }}>Failed to retrieve AI precedent research: {aiResearch.error}</p>
                  )}
                </div>
              )}

              {data.lowConfidence && (
                <Banner tone="warn" title="Weak matches">
                  Nothing in the collection is close to this query, so the cases below may be unrelated. Rephrase with facts and a ground, such as adultery, cruelty or desertion.
                </Banner>
              )}
              <Stats results={data.results} stats={data.stats} topScore={data.topScore} />
              {data.results.length === 0
                ? <p className="empty">No judgments matched these filters. Widen the year range or clear the ground filter. <a href="#/section-10">What is Section 10?</a></p>
                : (
                  <>
                    <div className="summary-report-wrap" style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '1rem', flexWrap: 'wrap' }}>
                      <Summary query={state.asked} results={data.results} />
                      <PrintReport query={state.asked} count={data.results.length} />
                    </div>
                    <div className="cases">
                      {data.results.map((c, i) => (
                        <CaseCard key={c.docId} c={c} rank={i + 1} terms={terms} scoreMax={scoreMax} />
                      ))}
                    </div>
                  </>
                )}
            </>
          )}


          {state.status === 'idle' && (
            <>
              <p className="idle-scope" style={{ textAlign: 'center', margin: '0 auto 1.5rem', color: 'var(--muted)', fontSize: '0.92rem' }}>
                Scope is Section 10 of the Indian Divorce Act (Christian matrimonial law).{' '}
                <a href="#/section-10" style={{ color: 'var(--accent)', textDecoration: 'underline' }}>What is Section 10?</a>
              </p>
              <div className="idle">
                <div><b>01</b><h3>Describe</h3><p>Write what happened in your own words. Facts work better than legal terms.</p></div>
                <div><b>02</b><h3>Compare</h3><p>Read the matching passage, the arguments of each side and the court’s reasoning.</p></div>
                <div><b>03</b><h3>Verify</h3><p>Every card links to the full judgment on Indian Kanoon. Always read the original.</p></div>
              </div>
            </>
          )}
        </section>
      </main>

      <footer className="foot no-print">
        <p>
          Grounds, disposal and outcome are assigned by automated rules reading each judgment’s operative part, and can be wrong.
          This is an educational research tool: it retrieves similar past cases. It does not predict outcomes or give legal advice.
        </p>
        <p style={{ marginTop: '0.8rem', display: 'flex', gap: '1.2rem', justifyContent: 'center' }}>
          <a href="#/cases" style={{ color: 'var(--ink)', textDecoration: 'underline' }}>Browse all cases</a>
          <a href="#/about" style={{ color: 'var(--ink)', textDecoration: 'underline' }}>About Section 10 Divorce Search</a>
        </p>
      </footer>
    </>
  )
}
