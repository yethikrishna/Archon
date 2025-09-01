from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from ..services.map_stream import MapLayer, store

router = APIRouter(prefix="/api/map", tags=["map"])
stream_router = APIRouter()


class IngestBody(BaseModel):
    layerId: str
    features: List[Dict[str, Any]] | Dict[str, Any]
    replace: Optional[bool] = False


@router.on_event("startup")
async def _startup():
    await store.start()


@router.get("/layers")
async def get_layers() -> List[MapLayer]:
    return store.get_layers()


@router.get("/features")
async def get_features(layerId: Optional[str] = Query(None)):
    if layerId:
        if layerId not in store.features:
            raise HTTPException(status_code=404, detail="Layer not found")
        return {"layerId": layerId, "features": store.features[layerId]}
    return {"features": store.features}


@router.post("/ingest")
async def ingest_features(body: IngestBody):
    feats: List[Dict[str, Any]]
    if isinstance(body.features, dict) and body.features.get("type") == "FeatureCollection":
        feats = body.features.get("features", [])
    elif isinstance(body.features, list):
        feats = body.features
    else:
        raise HTTPException(status_code=400, detail="Invalid features format")
    if body.layerId not in store.features:
        raise HTTPException(status_code=404, detail="Layer not found")
    if body.replace:
        await store.set_features(body.layerId, feats)
    else:
        await store.add_features(body.layerId, feats)
    return {"ok": True, "count": len(feats)}


@stream_router.get("/ws/stream")
async def sse_stream():
    gen = store.stream()
    return StreamingResponse(gen, media_type="text/event-stream")
