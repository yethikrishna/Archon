import asyncio
import os
import random
import time
from typing import Any, Dict, List

import httpx

AIRWEAVE_BASE = os.getenv("AIRWEAVE_BASE_URL", "http://localhost:8000")


def point(lon: float, lat: float, props: Dict[str, Any]):
    return {"type": "Feature", "geometry": {"type": "Point", "coordinates": [lon, lat]}, "properties": props}


def polygon_rect(lon: float, lat: float, d: float, props: Dict[str, Any]):
    coords = [
        [lon - d, lat - d],
        [lon + d, lat - d],
        [lon + d, lat + d],
        [lon - d, lat + d],
        [lon - d, lat - d],
    ]
    return {"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [coords]}, "properties": props}


async def post(client: httpx.AsyncClient, layer: str, features: List[Dict[str, Any]], replace=False):
    url = f"{AIRWEAVE_BASE}/api/v1/map/ingest"
    body = {"layerId": layer, "features": {"type": "FeatureCollection", "features": features}, "replace": replace}
    r = await client.post(url, json=body)
    r.raise_for_status()


async def main():
    random.seed(42)
    base_lon, base_lat = -122.4194, 37.7749
    async with httpx.AsyncClient(timeout=10) as client:
        alerts = [
            point(base_lon + random.uniform(-0.3, 0.3), base_lat + random.uniform(-0.3, 0.3), {"id": f"alert-{i}", "severity": random.choice(["low","med","high"])})
            for i in range(10)
        ]
        incidents = [
            polygon_rect(base_lon + random.uniform(-0.5, 0.5), base_lat + random.uniform(-0.5, 0.5), random.uniform(0.01, 0.05), {"id": f"incident-{i}", "status": random.choice(["open","contained"])})
            for i in range(5)
        ]
        sensors = [
            point(base_lon + random.uniform(-1.0, 1.0), base_lat + random.uniform(-1.0, 1.0), {"id": f"sensor-{i}", "type": random.choice(["temp","aqi","wind"])})
            for i in range(5)
        ]
        debris = [
            point(base_lon + random.uniform(-0.6, 0.6), base_lat + random.uniform(-0.6, 0.6), {"id": f"debris-{i}", "priority": random.choice(["p1","p2","p3"])})
            for i in range(5)
        ]
        forecast = [
            polygon_rect(base_lon, base_lat, 0.6, {"id": "forecast-1", "model": "demo"})
        ]
        await post(client, "alerts", alerts, replace=True)
        await post(client, "incidents", incidents, replace=True)
        await post(client, "sensors", sensors, replace=True)
        await post(client, "debris", debris, replace=True)
        await post(client, "forecast", forecast, replace=True)
        for i in range(5):
            await asyncio.sleep(1.5)
            upd = [point(base_lon + random.uniform(-0.3, 0.3), base_lat + random.uniform(-0.3, 0.3), {"id": f"alert-new-{i}", "severity": random.choice(["low","med","high"])})]
            await post(client, "alerts", upd, replace=False)


if __name__ == "__main__":
    asyncio.run(main())
