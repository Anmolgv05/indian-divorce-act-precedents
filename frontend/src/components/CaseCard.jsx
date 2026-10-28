import React, { useEffect, useState } from 'react'
import Highlight from './Highlight.jsx'
import { citation, groundLabel, label, DISPOSAL_LABELS, DISSOLVED_LABELS, RELIEF_LABELS, segmentLabel, prettyTitle } from '../lib/format.js'

function Role({ role, terms }) {
  const [open, setOpen] = useState(false)
  return (
    <div className={`role ${open ? 'open' : ''}`}>
      <button type="button" className="role-head" aria-expanded={open} onClick={() => setOpen(!open)}>
        <span>{role.title}</span><i aria-hidden="true" />
      </button>
      {open && <p className="role-body"><Highlight text={role.text} terms={terms} /></p>}
    </div>
  )
}

let _readerEnabled = null;
let _readerPromise = null;
function checkReaderEnabled(callback) {
  if (_readerEnabled !== null) {
    callback(_readerEnabled);
    return;
  }
  if (!_readerPromise) {
    _readerPromise = fetch("/api/reader/status")
      .then((r) => (r.ok ? r.json() : { enabled: false }))
      .then((d) => {
        _readerEnabled = Boolean(d?.enabled);
        return _readerEnabled;
      })
      .catch(() => {
        _readerEnabled = false;
        return false;
      });
  }
  _readerPromise.then(callback);
}

export default function CaseCard({ c, rank, terms, scoreMax }) {
  const [copied, setCopied] = useState(false)
  const [canRead, setCanRead] = useState(_readerEnabled ?? false)

  useEffect(() => {
    checkReaderEnabled(setCanRead)
  }, [])

  const rank1 = typeof rank === 'number' && rank >= 1 ? rank : (Number(rank) || 0) + 1
  const copy = async () => {
    try { await navigator.clipboard.writeText(citation(c)); setCopied(true); setTimeout(() => setCopied(false), 1600) } catch { /* clipboard unavailable */ }
  }
  const width = `${Math.max(6, Math.min(100, (c.score / (scoreMax || 1)) * 100))}%`
  const docId = c.docId || c.doc_id
  return (
    <article id={`case-${rank1}`} className="case" style={{ '--i': rank1 - 1 }}>
      <div className="case-rank" aria-hidden="true">{String(rank1).padStart(2, '0')}</div>

      <div className="case-main">
        <header className="case-head">
          <h3><a href={c.url} target="_blank" rel="noopener noreferrer">{prettyTitle(c.title)}</a></h3>
          <p className="case-meta">
            <span>{c.year ?? 'n/a'}</span>
            {c.court && <><b>·</b><span>{c.court}</span></>}
            <b>·</b><span className="mono">IK {c.docId}</span>
          </p>
        </header>

        <ul className="chips">
          <li className="chip chip-ground">{groundLabel(c.ground)}</li>
          <li className="chip">{label(DISPOSAL_LABELS, c.disposal)}</li>
          <li className={`chip chip-${c.dissolved}`}>{label(DISSOLVED_LABELS, c.dissolved)}</li>
          {c.relief && c.relief !== 'unclear' && <li className="chip">{label(RELIEF_LABELS, c.relief)}</li>}
          {c.nonMerits && <li className="chip chip-flag">Non-merits</li>}
          {c.duplicateOf && <li className="chip chip-flag" title={`Near-duplicate of ${c.duplicateOf}`}>Possible duplicate</li>}
        </ul>

        {c.outcomeSummary && (
          <div className="case-outcome">
            <span className="case-outcome-badge">Outcome</span>
            <span className="case-outcome-text">{c.outcomeSummary}</span>
          </div>
        )}

        {c.excerpt && (
          <blockquote className="excerpt">
            {c.excerptType && <span className="excerpt-tag">{segmentLabel(c.excerptType)}</span>}
            <p><Highlight text={c.excerpt} terms={terms} /></p>
          </blockquote>
        )}

        {c.roles.length > 0 && <div className="roles">{c.roles.map((r) => <Role key={r.key} role={r} terms={terms} />)}</div>}

        <footer className="case-foot">
          <div className="score" title="Hybrid relevance (dense + TF-IDF). Not a probability.">
            <span>Relevance</span><i><b style={{ width }} /></i><em>{c.score.toFixed(2)}</em>
          </div>
          <div className="actions">
            <button type="button" className="link" onClick={copy}>{copied ? 'Copied' : 'Copy citation'}</button>
            {canRead && docId && (
              <a className="link" href={`#/read/${docId}`}>Read in site</a>
            )}
            <a className="link" href={`https://huggingface.co/datasets/AnmolGV/section10-divorce-corpus/blob/main/parsed/${docId}.json`} target="_blank" rel="noopener noreferrer">HF Data ↗</a>
            <a className="link strong" href={c.url} target="_blank" rel="noopener noreferrer">Indian Kanoon <span aria-hidden="true">↗</span></a>
          </div>
        </footer>
      </div>
    </article>
  )
}
