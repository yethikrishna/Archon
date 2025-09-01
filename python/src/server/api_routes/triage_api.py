from __future__ import annotations
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

from ..services.prompt_service import prompt_service
from ..config.logfire_config import get_logger
from ...triage.state_machine import TriageSession
from ...triage.models import TriageMessage
from ...triage.queue import queue
from ...triage.llm_orchestrator import call_mastra_pipeline
from ...triage.safety import safety_check_output, safety_check_input
from ...triage.prompts import FOLLOWUP_GROUNDING

router = APIRouter(prefix="/api/triage", tags=["triage"])
logger = get_logger(__name__)

# In-memory session store
SESSIONS: Dict[str, TriageSession] = {}


class StartRequest(BaseModel):
    user_id: Optional[str] = None
    region: Optional[str] = None


class StartResponse(BaseModel):
    session_id: str
    message: str


class NextRequest(BaseModel):
    session_id: str
    answer_value: int
    user_text: Optional[str] = None


class NextResponse(BaseModel):
    next_question: Optional[str] = None
    done: bool = False
    outcome: Optional[Dict[str, Any]] = None
    assistant_message: Optional[str] = None


@router.post("/start", response_model=StartResponse)
async def start(req: StartRequest):
    s = TriageSession(user_id=req.user_id, region=req.region)
    SESSIONS[s.id] = s
    logger.info(f"Triage session started {s.id}")
    return StartResponse(session_id=s.id, message=s.start_message())


@router.post("/next", response_model=NextResponse)
async def next_step(req: NextRequest):
    s = SESSIONS.get(req.session_id)
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")

    # Record user message with safety flags
    if req.user_text:
        in_safety = safety_check_input(req.user_text)
        s.case.transcript.append(TriageMessage(role="user", content=req.user_text, safety_flags=in_safety.flags))

    nxt = s.apply_answer(req.answer_value, user_text=req.user_text)
    if nxt:
        # Provide optional supportive assistant message via Mastra
        ai = await call_mastra_pipeline([
            {"role": "system", "content": "Crisis-safe, brief, non-diagnostic encouragement only."},
            {"role": "user", "content": req.user_text or ""},
        ])
        assistant_text = ai.get("text") or FOLLOWUP_GROUNDING
        out_safety = safety_check_output(assistant_text)
        if out_safety.escalate:
            assistant_text = FOLLOWUP_GROUNDING
        s.case.transcript.append(TriageMessage(role="assistant", content=assistant_text, safety_flags=out_safety.flags))
        return NextResponse(next_question=nxt, done=False, assistant_message=assistant_text)

    # Finalize
    outcome = s.finalize_outcome()
    # Enqueue for counselor if escalate
    if outcome.escalate:
        queue.enqueue(s.case)
        s.case.add_event("enqueued_for_counselor")
    s.case.close()
    # Redact any potential PII in transcript (minimal store policy)
    # For demo, we simply mark as minimized
    s.case.pii_minimized = True
    return NextResponse(done=True, outcome=outcome.model_dump())


# Voice via Twilio-compatible webhook (TwiML)
class VoiceRequest(BaseModel):
    session_id: Optional[str] = None


@router.post("/voice/twilio")
async def voice_twilio(req: VoiceRequest):
    # Minimal TwiML instructing to gather speech and move through steps
    from fastapi.responses import Response
    s = None
    if req.session_id:
        s = SESSIONS.get(req.session_id)
    if not s:
        s = TriageSession()
        SESSIONS[s.id] = s
    # Return TwiML prompt for current question
    prompt = s.current_question() or "Thank you. A counselor will contact you shortly. If this is an emergency, hang up and dial your local emergency number."
    twiml = f"""
<Response>
  <Say>{prompt}</Say>
  <Pause length=\"1\"/>
  <Gather input=\"speech dtmf\" timeout=\"5\" speechTimeout=\"auto\"/>
</Response>
"""
    return Response(content=twiml.strip(), media_type="application/xml")


@router.get("/queue")
async def list_queue():
    return [c.model_dump() for c in queue.list()]
