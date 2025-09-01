import asyncio
import contextlib
import json
import os
from typing import Any, AsyncGenerator, Dict, List, Optional

import httpx
from pydantic import BaseModel, Field


class MapStyle(BaseModel):
    color: str = "#3388ff"
    fillColor: Optional[str] = None
    weight: int = 2
    opacity: float = 0.8
    fillOpacity: Optional[float] = None


class MapLayer(BaseModel):
    id: str
    name: str
    geometry_type: str = Field(description="Point | Polygon | LineString | Raster | Mixed")
    visible: bool = True
    cluster: bool = False
    style: MapStyle = Field(default_factory=MapStyle)
    description: Optional[str] = None


class MapEvent(BaseModel):
    type: str
    layerId: Optional[str] = None
    payload: Dict[str, Any] | List[Dict[str, Any]] | None = None


class MapStore:
    def __init__(self):
        self.layers: List[MapLayer] = [
            MapLayer(
                id="alerts",
                name="Alerts",
                geometry_type="Mixed",
                visible=True,
                cluster=True,
                style=MapStyle(color="#e11d48", fillColor="#fecaca", weight=2, opacity=0.9, fillOpacity=0.4),
                description="Point/polygon alerts with severity",
            ),
            MapLayer(
                id="incidents",
                name="Incidents",
                geometry_type="Polygon",
                visible=True,
                cluster=False,
                style=MapStyle(color="#f59e0b", fillColor="#fde68a", weight=2, opacity=0.9, fillOpacity=0.3),
                description="Incident footprints",
            ),
            MapLayer(
                id="sensors",
                name="Sensors",
                geometry_type="Point",
                visible=True,
                cluster=True,
                style=MapStyle(color="#2563eb", weight=2, opacity=0.9),
                description="Sensor locations",
            ),
            MapLayer(
                id="forecast",
                name="Forecast Surfaces",
                geometry_type="Polygon",
                visible=False,
                cluster=False,
                style=MapStyle(color="#10b981", fillColor="#a7f3d0", weight=1, opacity=0.6, fillOpacity=0.25),
                description="Forecast polygons or tiles",
            ),
            MapLayer(
                id="debris",
                name="Debris Tickets",
                geometry_type="Point",
                visible=False,
                cluster=True,
                style=MapStyle(color="#9333ea", weight=2, opacity=0.9),
                description="Reported debris cleanup tickets",
            ),
        ]
        self.features: Dict[str, List[Dict[str, Any]]] = {l.id: [] for l in self.layers}
        self._subscribers: List[asyncio.Queue[str]] = []
        self._lock = asyncio.Lock()
        self._airweave_base = os.getenv("ARCHON_AIRWEAVE_BASE_URL")
        self._poll_interval = int(os.getenv("ARCHON_MAP_POLL_SECS", "2"))
        self._poll_task: Optional[asyncio.Task] = None
        self._last_snapshot_hash: Dict[str, str] = {}

    async def start(self):
        if self._airweave_base and self._poll_task is None:
            self._poll_task = asyncio.create_task(self._poll_airweave())

    async def stop(self):
        if self._poll_task:
            self._poll_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._poll_task
            self._poll_task = None

    def get_layers(self) -> List[MapLayer]:
        return self.layers

    async def set_features(self, layer_id: str, features: List[Dict[str, Any]]):
        async with self._lock:
            self.features[layer_id] = features
        await self._broadcast(
            {
                "type": "layer_update",
                "layerId": layer_id,
                "payload": {"features": features},
            }
        )

    async def add_features(self, layer_id: str, features: List[Dict[str, Any]]):
        async with self._lock:
            self.features[layer_id].extend(features)
        await self._broadcast(
            {
                "type": "layer_append",
                "layerId": layer_id,
                "payload": {"features": features},
            }
        )

    async def clear(self):
        async with self._lock:
            for k in self.features:
                self.features[k] = []
        await self._broadcast({"type": "clear"})

    async def stream(self) -> AsyncGenerator[bytes, None]:
        q: asyncio.Queue[str] = asyncio.Queue()
        self._subscribers.append(q)
        try:
            snapshot = {
                "type": "snapshot",
                "payload": {k: v for k, v in self.features.items()},
            }
            yield self._encode(snapshot)
            while True:
                msg = await q.get()
                yield msg.encode("utf-8")
        finally:
            self._subscribers.remove(q)

    async def _broadcast(self, event: Dict[str, Any]):
        data = self._encode(event)
        for q in list(self._subscribers):
            try:
                q.put_nowait(data.decode("utf-8"))
            except Exception:
                pass

    def _encode(self, event: Dict[str, Any]) -> bytes:
        return f"event: message\ndata: {json.dumps(event)}\n\n".encode("utf-8")

    async def _poll_airweave(self):
        async with httpx.AsyncClient(timeout=10) as client:
            while True:
                try:
                    for layer in self.layers:
                        url = f"{self._airweave_base}/api/v1/map/features?layerId={layer.id}"
                        r = await client.get(url)
                        if r.status_code == 200:
                            body = r.json()
                            feats = body.get("features", [])
                            key = f"{layer.id}:{len(feats)}"
                            if self._last_snapshot_hash.get(layer.id) != key:
                                await self.set_features(layer.id, feats)
                                self._last_snapshot_hash[layer.id] = key
                except Exception:
                    pass
                await asyncio.sleep(self._poll_interval)


store = MapStore()
