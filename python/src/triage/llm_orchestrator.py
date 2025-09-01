from __future__ import annotations
import os
from typing import List, Dict, Any
import httpx
from .policies import DISCLAIMER, SYSTEM_PROMPT


async def call_mastra_pipeline(messages: List[Dict[str, str]]) -> Dict[str, Any]:
    base = os.getenv("MASTRA_PSYCH_KIT_URL")
    if not base:
        return {
            "text": (
                f"{DISCLAIMER}\n\nI hear how hard this is. Let’s take this one step at a time. "
                "If you’re in immediate danger, please contact local emergency services now."
            ),
            "provider": "fallback",
            "moderation": {"flagged": False, "reasons": []},
            "triggers": [],
        }
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.post(f"{base.rstrip('/')}/psych-kit/chat", json={"messages": messages})
        r.raise_for_status()
        return r.json()
