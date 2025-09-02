from __future__ import annotations
from typing import Dict, Optional, List
import uuid
from datetime import datetime
from .models import TriageCase, TriageMessage, TriageOutcome
from .scoring import compute_score
from .prompts import QUESTION_TEXT, INITIAL_MESSAGE, FOLLOWUP_GROUNDING
from .safety import safety_check_input
from .rag import get_resources
from .policies import DISCLAIMER

TRIAGE_STEPS = [
    "anhedonia",
    "depressed",
    "nervous",
    "control_worry",
]


class TriageSession:
    def __init__(self, user_id: Optional[str] = None, region: Optional[str] = None):
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.region = region
        self.answers: Dict[str, int] = {}
        self.step_index = 0
        self.case = TriageCase(id=str(uuid.uuid4()), user_id=user_id, session_id=self.id)
        self.case.add_event("session_started", {"region": region})

    def current_question(self) -> str:
        if self.step_index >= len(TRIAGE_STEPS):
            return ""
        key = TRIAGE_STEPS[self.step_index]
        return QUESTION_TEXT[key]

    def start_message(self) -> str:
        return INITIAL_MESSAGE

    def apply_answer(self, value: int, user_text: Optional[str] = None) -> Optional[str]:
        if self.step_index >= len(TRIAGE_STEPS):
            return None
        key = TRIAGE_STEPS[self.step_index]
        self.answers[key] = max(0, min(3, int(value)))
        # Safety check input for crisis indicators
        if user_text:
            safety = safety_check_input(user_text)
            if safety.escalate:
                self.case.add_event("safety_flag_input", {"flags": safety.flags})
        self.step_index += 1
        if self.step_index < len(TRIAGE_STEPS):
            return self.current_question()
        return None

    def finalize_outcome(self) -> TriageOutcome:
        crisis_flags: List[str] = []
        for m in self.case.transcript:
            crisis_flags.extend(m.safety_flags)
        uniq_flags = sorted(set(crisis_flags))
        severity = compute_score(self.answers, uniq_flags)
        escalate = severity.level in (severity.level.moderate, severity.level.severe, severity.level.crisis)
        cta = ""
        if severity.level in (severity.level.minimal, severity.level.mild):
            cta = (
                "Based on your answers, self-care strategies may help today. "
                "Would you like some grounding tips and local non-urgent support resources?"
            )
        else:
            cta = (
                "It sounds like more support would help. I can connect you to a counselor now, "
                "or share crisis hotlines based on your location. If you’re in immediate danger, call local emergency services."
            )
        resources = get_resources(self.region)
        outcome = TriageOutcome(
            severity=severity,
            call_to_action=cta,
            resources=resources,
            escalate=escalate,
            escalation_reasons=uniq_flags,
            disclaimer=DISCLAIMER,
        )
        self.case.outcome = outcome
        self.case.add_event("outcome_finalized", {"severity": severity.level})
        if escalate:
            # Placeholder for Dialect Alert Network notification
            self.case.add_event("alert_network_notified", {"network": "Dialect"})
        return outcome
