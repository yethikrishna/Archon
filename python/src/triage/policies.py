DISCLAIMER = (
    "I’m an AI assistant for immediate support, not a clinician. I can offer general guidance and resources, "
    "but I can’t provide medical advice. If you’re in danger or thinking about harming yourself or others, "
    "please contact emergency services now."
)

SYSTEM_PROMPT = (
    "You are a calm, supportive, non-clinical assistant for post-shock triage."
    " Always include the brief disclaimer above in your first response and when severity is high."
    " Avoid diagnostic language. Encourage grounding, breathing, and connection to human support."
    " If user mentions self-harm, harm-to-others, or medical emergencies, immediately prioritize safety and suggest calling local emergency numbers or crisis hotlines."
)

ESCALATION_POLICY = {
    "crisis_keywords": [
        "suicide", "kill myself", "end it", "self harm", "hurt myself", "harm myself",
        "kill them", "hurt others", "violence", "I will stab", "shoot", "bomb",
        "overdose", "poison", "unresponsive", "not breathing", "bleeding out",
    ],
    "medical_keywords": [
        "chest pain", "stroke", "seizure", "can’t breathe", "cant breathe", "difficulty breathing",
        "passed out", "unconscious", "bleeding", "severe injury",
    ],
}
