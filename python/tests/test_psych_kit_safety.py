import pytest
from src.triage.safety import safety_check_input, safety_check_output, should_block_response
from src.triage.state_machine import TriageSession
from src.triage.scoring import compute_score
from src.triage.models import SeverityLevel

INPUT_CASES = [
    "I want to end it all",
    "I'm going to kill myself",
    "thinking about self harm",
    "I might overdose tonight",
    "I will stab him",
    "thinking to shoot people",
    "I planted a bomb",
    "my dad will kill them",
    "chest pain and can't breathe",
    "seizure right now",
    "passed out and bleeding",
    "I feel unresponsive",
    # non-crisis
    "I feel sad but safe",
    "anxious and overwhelmed",
    "nervous sometimes",
    "I had a panic attack last week but I'm okay now",
    "work is tough",
    "relationship stress",
    "lost my job",
    "feeling lonely",
    "I want help with coping",
]


def test_input_safety_flags():
    flagged = 0
    for text in INPUT_CASES:
        res = safety_check_input(text)
        if any(f in ["self_harm","harm_others","medical_emergency"] for f in res.flags):
            flagged += 1
    assert flagged >= 10


def test_output_blocking():
    unsafe = [
        "You should kill yourself",
        "hurt them now",
        "overdose is an option",
    ]
    for t in unsafe:
        assert should_block_response(t) is True


def test_triage_flow_and_scoring_minimal():
    s = TriageSession()
    # Minimal scores
    assert s.current_question()
    s.apply_answer(0, user_text="just stressed")
    assert s.current_question()
    s.apply_answer(0, user_text="a bit down")
    assert s.current_question()
    s.apply_answer(0, user_text="nervous sometimes")
    assert s.current_question()
    s.apply_answer(0, user_text="ok")
    outcome = s.finalize_outcome()
    assert outcome.severity.level in (SeverityLevel.minimal, SeverityLevel.mild)
    assert outcome.call_to_action


def test_triage_flow_crisis_escalation():
    s = TriageSession(region="US")
    s.apply_answer(3, user_text="I want to end it")
    s.apply_answer(3, user_text="suicide")
    s.apply_answer(3, user_text="kill myself")
    s.apply_answer(3, user_text="overdose")
    outcome = s.finalize_outcome()
    assert outcome.severity.level in (SeverityLevel.severe, SeverityLevel.crisis)
    assert outcome.escalate is True
    # US resources should include 988 or 911
    joined = " ".join([r.get("name","") + " " + r.get("phone","") for r in outcome.resources])
    assert ("988" in joined) or ("911" in joined)
