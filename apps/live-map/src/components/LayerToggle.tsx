import React from 'react'
import type { MapLayer } from '../lib/api'

export function LayerToggle({ layer, checked, onChange }: { layer: MapLayer; checked: boolean; onChange: (v: boolean) => void }) {
  return (
    <label style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 6 }}>
      <input type="checkbox" checked={checked} onChange={e => onChange(e.target.checked)} />
      <span style={{ width: 12, height: 12, background: layer.style.color, display: 'inline-block' }} />
      <span>{layer.name}</span>
    </label>
  )
}
