from .policies import DISCLAIMER, SYSTEM_PROMPT

INITIAL_MESSAGE = (
    f"{DISCLAIMER}\n\n"
    "I’m here with you. To understand how best to help right now, I’ll ask a few brief questions."
    " You can stop anytime. First: In the past two weeks, how often have you had little interest or pleasure in doing things?"
    " (0=Not at all, 1=Several days, 2=More than half the days, 3=Nearly every day)"
)

QUESTION_TEXT = {
    "anhedonia": "In the past two weeks, how often have you had little interest or pleasure in doing things? (0-3)",
    "depressed": "How often have you felt down, depressed, or hopeless? (0-3)",
    "nervous": "How often have you felt nervous, anxious, or on edge? (0-3)",
    "control_worry": "How often have you found it difficult to control your worrying? (0-3)",
}

FOLLOWUP_GROUNDING = (
    "Let’s try a quick grounding exercise: Name 5 things you can see, 4 things you can touch, 3 things you can hear,"
    " 2 things you can smell, and 1 thing you can taste. Breathing slowly can also help."
)
