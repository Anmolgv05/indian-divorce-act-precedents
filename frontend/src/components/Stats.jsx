import React, { useState } from 'react'
import { tally } from '../lib/api.js'

export default function Stats({ results, stats, topScore }) {
  const [activeTab, setActiveTab] = useState('roadmap')
  const t = tally(results)
  if (!t.total) return null
  const pct = (n) => `${(n / t.total) * 100}%`

  const guidance = stats.precedent_guidance || {}
  const roadmaps = guidance.evidentiary_roadmaps || []
  const traps = guidance.statutory_traps || []
  const checklist = guidance.litigation_checklist || []

  return (
    <section className="stats" aria-label="Outcome distribution and precedent intelligence">
      <div className="stats-header">
        <p className="stats-line">
          {stats.summary ||
            `Of the ${t.total} retrieved cases, ${t.ended} ended the marriage (dissolution/nullity), ${t.notEnded} did not, ${t.other} unclear or not applicable.`}
        </p>
        {guidance.operative_ratio && (
          <span className="stats-ratio-badge" title="Success rate among decided merits cases">
            {guidance.operative_ratio}
          </span>
        )}
      </div>

      <div className="bar" role="img"
        aria-label={`${t.ended} ended, ${t.notEnded} not ended, ${t.other} not determined`}>
        <i className="seg seg-ended" style={{ width: pct(t.ended) }} />
        <i className="seg seg-not" style={{ width: pct(t.notEnded) }} />
        <i className="seg seg-other" style={{ width: pct(t.other) }} />
      </div>
      <ul className="legend">
        <li><i className="dot seg-ended" />Marriage ended <b>{t.ended}</b></li>
        <li><i className="dot seg-not" />Not ended <b>{t.notEnded}</b></li>
        <li><i className="dot seg-other" />Not determined <b>{t.other}</b></li>
        {topScore > 0 && <li className="legend-score">Top match <b>{topScore.toFixed(2)}</b></li>}
      </ul>

      {stats.outcome_synthesis && (
        <div className="outcome-synthesis-box">
          <div className="outcome-synthesis-head">
            <span className="outcome-synthesis-kicker">ADVOCATE'S PRECEDENT INTELLIGENCE</span>
            <span className="outcome-synthesis-badge">SYNTHESIS</span>
          </div>
          <p className="outcome-synthesis-text">{stats.outcome_synthesis}</p>

          {(roadmaps.length > 0 || traps.length > 0 || checklist.length > 0) && (
            <div className="guidance-panel">
              <nav className="guidance-tabs" aria-label="Litigation guidance sections">
                <button
                  type="button"
                  className={`guidance-tab ${activeTab === 'roadmap' ? 'active' : ''}`}
                  onClick={() => setActiveTab('roadmap')}
                >
                  📋 Evidentiary Roadmaps ({roadmaps.length})
                </button>
                <button
                  type="button"
                  className={`guidance-tab ${activeTab === 'traps' ? 'active' : ''}`}
                  onClick={() => setActiveTab('traps')}
                >
                  ⚠️ Statutory Traps & Defenses ({traps.length})
                </button>
                <button
                  type="button"
                  className={`guidance-tab ${activeTab === 'checklist' ? 'active' : ''}`}
                  onClick={() => setActiveTab('checklist')}
                >
                  ⚖️ Litigation Checklist ({checklist.length})
                </button>
              </nav>

              <div className="guidance-content">
                {activeTab === 'roadmap' && (
                  <div className="guidance-cards">
                    {roadmaps.map((item, idx) => (
                      <div key={idx} className="guidance-card">
                        <h4 className="guidance-card-title">{item.ground}</h4>
                        <p className="guidance-card-text">{item.requirement}</p>
                      </div>
                    ))}
                  </div>
                )}

                {activeTab === 'traps' && (
                  <div className="guidance-cards">
                    {traps.map((item, idx) => (
                      <div key={idx} className="guidance-card guidance-card-warning">
                        <h4 className="guidance-card-title">{item.title}</h4>
                        <p className="guidance-card-text">{item.detail}</p>
                      </div>
                    ))}
                  </div>
                )}

                {activeTab === 'checklist' && (
                  <ol className="guidance-checklist">
                    {checklist.map((step, idx) => (
                      <li key={idx} className="guidance-checklist-item">
                        {step}
                      </li>
                    ))}
                  </ol>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      <p className="stats-note">Retrieved cases illustrate judicial trends and evidentiary thresholds across reported rulings, not a statistical guarantee. Verify citations in primary law reports.</p>
    </section>
  )
}

