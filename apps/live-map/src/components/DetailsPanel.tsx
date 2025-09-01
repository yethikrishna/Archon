import React from 'react'

export function DetailsPanel({ feature, onClose }: { feature: any | null; onClose: () => void }) {
  if (!feature) return null
  const props = feature.properties || {}
  return (
    <div className="details">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h3>Details</h3>
        <button onClick={onClose}>Close</button>
      </div>
      <div style={{ marginBottom: 8 }}>
        <span className="badge" style={{ background: '#1f2937', color: '#e5e7eb' }}>{props.type || 'Feature'}</span>
      </div>
      <pre style={{ whiteSpace: 'pre-wrap' }}>{JSON.stringify(props, null, 2)}</pre>
    </div>
  )
}
