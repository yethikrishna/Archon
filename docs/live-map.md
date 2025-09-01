# Live Map Module

Overview
- Frontend app at apps/live-map renders base map, 5 layers (Alerts, Incidents, Sensors, Forecast Surfaces, Debris Tickets), clustering-ready, filter toggles, and click-to-details.
- Backend FastAPI endpoints:
  - GET /api/map/layers: static metadata for layers and style hints
  - GET /api/map/features[?layerId=id]: current features
  - POST /api/map/ingest: { layerId, features, replace? } to push features
  - GET /ws/stream: Server-Sent Events broadcasting snapshot and updates
- Airweave integration: optional polling of Airweave /api/v1/map/features to populate layers. Configure ARCHON_AIRWEAVE_BASE_URL and ARCHON_MAP_POLL_SECS.

Registering a new layer
1. Backend: Update python/src/server/services/map_stream.py MapStore.layers list with a new MapLayer. Restart server.
2. Frontend: No code changes required; the app reads /api/map/layers and auto-renders toggles.
3. Ingest features: POST /api/map/ingest with FeatureCollection or array of Features. Example:

```
POST /api/map/ingest
{
  "layerId": "alerts",
  "features": {
    "type": "FeatureCollection",
    "features": [ { "type": "Feature", "geometry": {"type":"Point","coordinates":[-122.4,37.78]}, "properties": {"id":"a1","severity":"high"} } ]
  },
  "replace": true
}
```

Streaming updates
- Clients connect to /ws/stream (text/event-stream). Events:
  - { type: "snapshot", payload: { [layerId]: Feature[] } }
  - { type: "layer_update", layerId, payload: { features: Feature[] } }
  - { type: "layer_append", layerId, payload: { features: Feature[] } }

AWS Location integration
- The design is provider-pluggable for geocoding and tiles. Default uses open OSM tiles. To use AWS:
  - Use awslabs/mcp aws-location-mcp-server as a provider or wire boto3 geo-places directly.
  - Provide AWS credentials and set ARCHON_GEO_PROVIDER=aws to switch.

E2E demo
- Run Archon backend, Airweave backend.
- Execute python/python3 scripts/seed_live_map.py to seed >20 records across layers and stream updates.
- Open apps/live-map and watch updates within ~2-3s.
