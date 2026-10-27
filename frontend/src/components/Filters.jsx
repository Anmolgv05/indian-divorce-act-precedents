import React from 'react'
import { groundLabel } from '../lib/format.js'

export default function Filters({ value, onChange, grounds }) {
  const set = (k) => (e) => {
    const v = e.target.type === 'checkbox' ? e.target.checked : e.target.value
    onChange({ ...value, [k]: v })
  }
  return (
    <div className="filters" id="filters">
      <label className="field">
        <span>Primary ground</span>
        <select value={value.ground} onChange={set('ground')}>
          <option value="">Any ground</option>
          {grounds.map((g) => <option key={g} value={g}>{groundLabel(g)}</option>)}
        </select>
      </label>
      <label className="field">
        <span>Results <b>{value.topK}</b></span>
        <input type="range" min="3" max="20" value={value.topK} onChange={(e) => onChange({ ...value, topK: +e.target.value })} />
      </label>
      <div className="field">
        <span>Year range</span>
        <div className="years">
          <input type="number" inputMode="numeric" placeholder="1869" min="1869" max="2026" value={value.yearMin} onChange={set('yearMin')} aria-label="From year" />
          <em>to</em>
          <input type="number" inputMode="numeric" placeholder="2026" min="1869" max="2026" value={value.yearMax} onChange={set('yearMax')} aria-label="To year" />
        </div>
      </div>
      <label className="check">
        <input type="checkbox" checked={value.includeNonMerits} onChange={set('includeNonMerits')} />
        <span>Include non-merits matters <small>transfer petitions and similar</small></span>
      </label>
      <label className="check">
        <input type="checkbox" checked={value.showDuplicates} onChange={set('showDuplicates')} />
        <span>Show possible duplicate records</span>
      </label>
    </div>
  )
}
