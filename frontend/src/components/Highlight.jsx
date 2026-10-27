import React from 'react'

export default function Highlight({ text, terms }) {
  if (!text) return null
  if (!terms.length) return <>{text}</>
  const rx = new RegExp(`(${terms.map((t) => t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|')})`, 'gi')
  return (
    <>
      {text.split(rx).map((part, i) =>
        i % 2 ? <mark key={i}>{part}</mark> : <React.Fragment key={i}>{part}</React.Fragment>
      )}
    </>
  )
}
