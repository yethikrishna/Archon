import React, { useEffect, useMemo, useState } from 'react'
import { MapContainer, TileLayer, Marker, Popup, GeoJSON, useMap, CircleMarker } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import supercluster from 'supercluster'
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

function ClusterLayer({ points, onClick }: { points: GeoJSONFeature[]; onClick: (f: any) => void }) {
  const map = useMap()
  const [clusters, setClusters] = useState<any[]>([])
  const index = useMemo(() => {
    const idx = new supercluster({ radius: 60, maxZoom: 18 })
    const features = points.map((p, i) => ({
      type: 'Feature',
      geometry: p.geometry,
      properties: { cluster: false, index: i, ...(p.properties || {}) }
    })) as any
    idx.load(features)
    return idx
  }, [points])
  useEffect(() => {
    const update = () => {
      const b = map.getBounds()
      const z = map.getZoom()
      const clusters = index.getClusters([b.getWest(), b.getSouth(), b.getEast(), b.getNorth()], Math.round(z))
      setClusters(clusters)
    }
    update()
    map.on('moveend zoomend', update)
    return () => { map.off('moveend zoomend', update) }
  }, [index])
  return (
    <>
      {clusters.map((c, i) => {
        const [lon, lat] = c.geometry.coordinates
        if (c.properties.cluster) {
          const count = c.properties.point_count as number
          const size = Math.min(40, 20 + Math.log(count + 1) * 8)
          return (
            <CircleMarker key={`c-${i}`} center={[lat, lon]} pathOptions={{ color: '#111827', fillColor: '#60a5fa', fillOpacity: 0.8 }} radius={size/4}>
              <Popup>{count} features</Popup>
            </CircleMarker>
          )
        } else {
          const idx = c.properties.index
          const f = points[idx]
          return (
            <Marker key={`m-${i}`} position={[lat, lon] as any} eventHandlers={{ click: () => onClick(f) }}>
              <Popup>{f.properties?.title || f.properties?.id || 'Feature'}</Popup>
            </Marker>
          )
        }
      })}
    </>
  )
}

export default function App() {
  const [layers, setLayers] = useState<MapLayer[]>([])
  const [visible, setVisible] = useState<Record<string, boolean>>({})
  const [data, setData] = useState<Record<string, GeoJSONFeature[]>>({})
  const [selected, setSelected] = useState<any | null>(null)
  const [alertSeverity, setAlertSeverity] = useState<'all'|'low'|'med'|'high'>('all')

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
        if (id === 'alerts' && alertSeverity !== 'all' && f.properties?.severity && f.properties.severity !== alertSeverity) return
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
        <div style={{ marginTop: 8 }}>
          <label>Alert severity:
            <select value={alertSeverity} onChange={e => setAlertSeverity(e.target.value as any)} style={{ marginLeft: 6 }}>
              <option value="all">All</option>
              <option value="low">Low</option>
              <option value="med">Medium</option>
              <option value="high">High</option>
            </select>
          </label>
        </div>
      </div>
      <MapContainer center={defaultCenter} zoom={6} style={{ height: '100%' }}>
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" attribution="&copy; OpenStreetMap" />
        {polygons.map((f, i) => (
          <GeoJSON key={`poly-${i}`} data={f as any} eventHandlers={{ click: () => setSelected(f) }} />
        ))}
        <ClusterLayer points={points} onClick={(f) => setSelected(f)} />
        <FitBounds features={[...points, ...polygons]} />
      </MapContainer>
      <DetailsPanel feature={selected} onClose={() => setSelected(null)} />
    </div>
  )
}
