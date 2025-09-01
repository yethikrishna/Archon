from __future__ import annotations
from typing import List, Dict, Any, Optional
import os

STATIC_RESOURCES: List[Dict[str, Any]] = [
    {
        "name": "988 Suicide & Crisis Lifeline (US)",
        "phone": "988",
        "url": "https://988lifeline.org/",
        "regions": ["US"],
    },
    {
        "name": "Emergency Services",
        "phone": "911",
        "regions": ["US"],
    },
    {
        "name": "Samaritans (UK & ROI)",
        "phone": "+44 116 123",
        "url": "https://www.samaritans.org/",
        "regions": ["UK", "IE"],
    },
]


def get_resources(region: Optional[str] = None) -> List[Dict[str, Any]]:
    region = (region or "").upper()
    items = []
    if region:
        for r in STATIC_RESOURCES:
            if region in r.get("regions", []):
                items.append(r)
    # Always include non-regional
    for r in STATIC_RESOURCES:
        if not r.get("regions"):
            items.append(r)
    return items
