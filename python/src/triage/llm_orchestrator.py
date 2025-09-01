from __future__ import annotations
import os
from typing import List, Dict, Any
import httpx
from .policies import DISCLAIMER, SYSTEM_PROMPT


async def call_mastra_pipeline(messages: List[Dict[str, str]]) -> Dict[str, Any]:
    base = os.getenv("MASTRA_PSYCH_KIT_URL")
    if not base:
        # Optional: lightweight provider moderation via OpenAI if key is present
        flagged = False
        try:
            from openai import OpenAI  # type: ignore
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                client = OpenAI(api_key=api_key)
                content = "\n".join([m.get("content", "") for m in messages if m.get("content")])
                mod = client.moderations.create(model="omni-moderation-latest", input=content)
                flagged = bool(getattr(mod, "results", [{}])[0].get("flagged", False))
        except Exception:
            flagged = False
        return {
            "text": (
                f"{DISCLAIMER}\n\nI hear how hard this is. Let’s take this one step at a time. "
                "If you’re in immediate danger, please contact local emergency services now."
            ),
            "provider": "fallback",
            "moderation": {"flagged": flagged, "reasons": ["provider"] if flagged else []},
            "triggers": ["crisis"] if flagged else [],
        }
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.post(f"{base.rstrip('/')}/psych-kit/chat", json={"messages": messages})
        r.raise_for_status()
        return r.json()
