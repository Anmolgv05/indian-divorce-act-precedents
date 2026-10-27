import React from 'react'

export function Banner({ tone = 'note', title, children }) {
  return (
    <div className={`banner banner-${tone}`} role={tone === 'warn' ? 'alert' : 'status'}>
      <span className="banner-mark" aria-hidden="true"><b>{tone === 'warn' ? '!' : '§'}</b></span>
      <div>
        {title && <strong>{title}</strong>}
        <p>{children}</p>
      </div>
    </div>
  )
}
