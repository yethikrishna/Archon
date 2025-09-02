from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class SeverityLevel(str, Enum):
    minimal = "minimal"
    mild = "mild"
    moderate = "moderate"
    severe = "severe"
    crisis = "crisis"


class TriageMessage(BaseModel):
    role: str  # user | assistant | system
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    safety_flags: List[str] = Field(default_factory=list)


class SeverityScore(BaseModel):
    phq4_total: int
    gad2_total: int
    crisis_indicators: List[str] = Field(default_factory=list)
    level: SeverityLevel


class TriageOutcome(BaseModel):
    severity: SeverityScore
    call_to_action: str
    resources: List[Dict[str, Any]] = Field(default_factory=list)
    escalate: bool = False
    escalation_reasons: List[str] = Field(default_factory=list)
    disclaimer: str = ""


class TriageCase(BaseModel):
    id: str
    user_id: Optional[str] = None
    session_id: str
    started_at: datetime = Field(default_factory=datetime.utcnow)
    closed_at: Optional[datetime] = None
    transcript: List[TriageMessage] = Field(default_factory=list)
    outcome: Optional[TriageOutcome] = None
    audit_log: List[Dict[str, Any]] = Field(default_factory=list)
    pii_minimized: bool = True

    def add_event(self, event: str, meta: Optional[Dict[str, Any]] = None):
        self.audit_log.append({
            "timestamp": datetime.utcnow().isoformat(),
            "event": event,
            "meta": meta or {},
        })

    def close(self):
        self.closed_at = datetime.utcnow()
