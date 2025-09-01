from __future__ import annotations
import re
from typing import List, Dict, Any
from pydantic import BaseModel
from .policies import ESCALATION_POLICY

SELF_HARM_PATTERNS = [
    r"\b(suicide|kill myself|end it|self\s?harm|harm myself|cut myself|overdose)\b",
]
HARM_OTHERS_PATTERNS = [
    r"\b(kill (him|her|them)|hurt others|violence|stab|shoot|bomb)\b",
]
MEDICAL_EMERGENCY_PATTERNS = [
    r"\b(chest pain|stroke|seizure|can'?t breathe|difficulty breathing|passed out|unconscious|bleeding out?)\b",
]

ALL_PATTERNS = [
    ("self_harm", SELF_HARM_PATTERNS),
    ("harm_others", HARM_OTHERS_PATTERNS),
    ("medical_emergency", MEDICAL_EMERGENCY_PATTERNS),
]


class SafetyEvent(BaseModel):
    type: str
    match: str


class SafetyResult(BaseModel):
    flags: List[str]
    events: List[SafetyEvent]
    escalate: bool


def _search_patterns(text: str) -> List[SafetyEvent]:
    events: List[SafetyEvent] = []
    lowered = text.lower()
    for label, patterns in ALL_PATTERNS:
        for p in patterns:
            for m in re.finditer(p, lowered, flags=re.IGNORECASE):
                events.append(SafetyEvent(type=label, match=m.group(0)))
    return events


def safety_check_input(text: str) -> SafetyResult:
    events = _search_patterns(text)
    flags = sorted({e.type for e in events})
    escalate = bool(events)
    return SafetyResult(flags=flags, events=events, escalate=escalate)


def safety_check_output(text: str) -> SafetyResult:
    # Post-generation check identical rules; can be extended
    return safety_check_input(text)


def should_block_response(model_text: str) -> bool:
    result = safety_check_output(model_text)
    return result.escalate
