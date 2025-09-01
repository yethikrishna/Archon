import React, { useEffect, useMemo, useState } from 'react'
import { MapContainer, TileLayer, Marker, Popup, GeoJSON, useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { connectStream, fetchFeatures, fetchLayers, GeoJSONFeature, MapLayer } from './lib/api'
import { LayerToggle } from './components/LayerToggle'
import { DetailsPanel } from './components/DetailsPanel'

const defaultCenter: [number, number] = [37.7749, -122.4194]

function FitBounds({ features }: { features: GeoJSONFeature[] }) {
  const map = useMap()
  useEffect(() => {
    if (!features.length) return
    const group = L.featureGroup(features.map(f => L.geoJSON(f as any)))
    map.fitBounds(group.getBounds().pad(0.2))
  }, [features])
  return null
}

export default function App() {
  const [layers, setLayers] = useState<MapLayer[]>([])
  const [visible, setVisible] = useState<Record<string, boolean>>({})
  const [data, setData] = useState<Record<string, GeoJSONFeature[]>>({})
  const [selected, setSelected] = useState<any | null>(null)

  useEffect(() => {
    fetchLayers().then(ls => {
      setLayers(ls)
      setVisible(Object.fromEntries(ls.map(l => [l.id, l.visible])))
    })
    fetchFeatures().then(res => {
      const all = res.features || {}
      setData(all)
    })
    const close = connectStream((evt) => {
      if (evt.type === 'snapshot') {
        setData(evt.payload || {})
      } else if (evt.type === 'layer_update' || evt.type === 'layer_append') {
        const id = evt.layerId
        const f = evt.payload?.features || []
        setData(prev => ({ ...prev, [id]: evt.type === 'layer_update' ? f : [...(prev[id] || []), ...f] }))
      }
    })
    return close
  }, [])

  const points = useMemo(() => {
    const out: GeoJSONFeature[] = []
    Object.entries(data).forEach(([id, feats]) => {
      const layer = layers.find(l => l.id === id)
      if (!layer || !visible[id]) return
      feats.forEach(f => {
        if (f.geometry?.type === 'Point' || layer.geometry_type === 'Point' || layer.geometry_type === 'Mixed') out.push(f)
      })
    })
    return out
  }, [data, layers, visible])

  const polygons = useMemo(() => {
    const out: GeoJSONFeature[] = []
    Object.entries(data).forEach(([id, feats]) => {
      const layer = layers.find(l => l.id === id)
      if (!layer || !visible[id]) return
      feats.forEach(f => {
        if (f.geometry?.type === 'Polygon' || f.geometry?.type === 'MultiPolygon' || layer.geometry_type === 'Polygon') out.push(f)
      })
    })
    return out
  }, [data, layers, visible])

  return (
    <div style={{ height: '100%', position: 'relative' }}>
      <div className="controls">
        <strong>Layers</strong>
        <div>
          {layers.map(l => (
            <LayerToggle key={l.id} layer={l} checked={!!visible[l.id]} onChange={(v) => setVisible(prev => ({ ...prev, [l.id]: v }))} />
          ))}
        </div>
      </div>
      <MapContainer center={defaultCenter} zoom={6} style={{ height: '100%' }}>
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" attribution="&copy; OpenStreetMap" />
        {polygons.map((f, i) => (
          <GeoJSON key={`poly-${i}`} data={f as any} eventHandlers={{ click: () => setSelected(f) }} />
        ))}
        {points.map((f, i) => (
          <Marker key={`pt-${i}`} position={[f.geometry.coordinates[1], f.geometry.coordinates[0]] as any} eventHandlers={{ click: () => setSelected(f) }}>
            <Popup>{f.properties?.title || f.properties?.id || 'Feature'}</Popup>
          </Marker>
        ))}
        <FitBounds features={[...points, ...polygons]} />
      </MapContainer>
      <DetailsPanel feature={selected} onClose={() => setSelected(null)} />
    </div>
  )
}
