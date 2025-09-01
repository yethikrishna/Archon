export type GeoJSONFeature = {
  type: 'Feature'
  geometry: any
  properties: Record<string, any>
}

export type MapLayer = {
  id: string
  name: string
  geometry_type: 'Point' | 'Polygon' | 'LineString' | 'Raster' | 'Mixed'
  visible: boolean
  cluster: boolean
  style: { color: string; fillColor?: string; weight: number; opacity: number; fillOpacity?: number }
  description?: string
}

const BASE = import.meta.env.VITE_ARCHON_BASE_URL || ''

export async function fetchLayers(): Promise<MapLayer[]> {
  const r = await fetch(`${BASE}/api/map/layers`)
  return r.json()
}

export async function fetchFeatures(layerId?: string): Promise<any> {
  const u = new URL(`${BASE}/api/map/features`, window.location.origin)
  if (layerId) u.searchParams.set('layerId', layerId)
  const r = await fetch(u.toString())
  return r.json()
}

export function connectStream(onMessage: (evt: any) => void) {
  const url = `${BASE}/ws/stream`
  const es = new EventSource(url)
  es.onmessage = (e) => {
    try { onMessage(JSON.parse(e.data)) } catch {}
  }
  return () => es.close()
}
