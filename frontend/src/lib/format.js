// Human-readable labels. Raw labels never reach the screen.
export const GROUND_LABELS = {
  adultery: 'Adultery',
  cruelty: 'Cruelty',
  desertion: 'Desertion',
  non_consummation: 'Non-consummation',
  nullity_sec19: 'Nullity (s.19)',
  mutual_consent_10A: 'Mutual consent (s.10A)',
  constitutional_validity: 'Constitutional validity',
  procedural: 'Procedural / confirmation',
  wife_specific: 'Wife-specific grounds',
  unsound_mind: 'Unsound mind',
  leprosy: 'Leprosy',
  restitution_noncompliance: 'Non-compliance with restitution',
  unclear: 'Not determined',
}
export const DISPOSAL_LABELS = {
  allowed: 'Allowed', dismissed: 'Dismissed', partly_allowed: 'Partly allowed',
  remanded: 'Remanded', confirmed: 'Confirmed', not_confirmed: 'Not confirmed',
  modified: 'Modified', interim: 'Interim order', disposed_of: 'Disposed of',
  unclear: 'Not determined',
}
export const DISSOLVED_LABELS = { yes: 'Marriage ended', no: 'Marriage not ended', unclear: 'Not determined' }
export const RELIEF_LABELS = {
  dissolution: 'Dissolution', nullity: 'Nullity', judicial_separation: 'Judicial separation',
  restitution: 'Restitution of conjugal rights', none: 'No relief', unclear: 'Not determined',
}
export const SEGMENT_LABELS = {
  facts: 'Facts', issue: 'Issue', law: 'Law', reasoning: 'Reasoning', conclusion: 'Conclusion',
  petitioner_argument: "Petitioner's argument", respondent_argument: "Respondent's argument",
}

const titleCase = (s) => String(s).replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
export const label = (map, v) => (v == null || v === '' ? 'Not determined' : map[v] || titleCase(v))
export const groundLabel = (v) => label(GROUND_LABELS, v)
export const segmentLabel = (v) => label(SEGMENT_LABELS, v)

export const prettyTitle = (t = '') => t.replace(/\s+on\s+\d{1,2}\s+\w+,?\s+\d{4}\s*$/i, '').trim()

const STOP = new Set('the and for that with from have has had was were are not but his her she him they them this which who whom been being will would shall should could into upon over under than then there their also such any all can may out our its'.split(' '))
export function queryTerms(q = '') {
  return [...new Set(q.toLowerCase().match(/[a-z]{4,}/g) || [])].filter((w) => !STOP.has(w)).slice(0, 8)
}

export function citation(c) {
  const y = c.year ? ` (${c.year})` : ''
  return `${prettyTitle(c.title)}${y}${c.court ? `, ${c.court}` : ''}. ${c.url}`
}
