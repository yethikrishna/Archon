# Psychological Post-Shock Kit (Psych Kit)

Purpose: Rapid, safe mental health triage that routes people to the right level of help after a shock or stressful event. This kit is non-clinical and designed to minimize harm, preserve privacy, and escalate when risk is detected.

Disclaimers
- I’m an AI assistant for immediate support, not a clinician. I can offer general guidance and resources, but I can’t provide medical advice. If you’re in danger or thinking about harming yourself or others, please contact emergency services now.
- The assistant does not diagnose or treat. It provides supportive language, grounding suggestions, and resource navigation.

Ethics & Safety
- Non-maleficence: Avoid diagnostic language and prescriptive medical advice.
- Respect for autonomy: Users can stop at any time and control what they share.
- Justice & inclusion: Language is neutral, trauma-informed, and culturally sensitive.
- Transparency: Disclaimers are repeated at first contact and for high severity outcomes.

Layered Safety Architecture
1) Static guardrails: keyword/regex detection for self-harm, harm-to-others, and medical emergencies.
2) Provider moderation: When available, model-level moderation is invoked and responses are blocked or rewritten.
3) Crisis heuristics: Session-wide crisis indicators trigger immediate escalation to a human and Dialect Alert Network.
4) Post-generation filter: All candidate messages pass through the safety filter; unsafe content is replaced with a safe fallback.
5) Auditability: Every flag and decision is logged to the case audit log.

Triage Method
- Conversational state machine using PHQ‑4/GAD‑2 style prompts adapted for crisis contexts.
- Scoring:
  - PHQ‑4 total: 0–2 minimal, 3–5 mild, 6–8 moderate, 9–12 severe
  - GAD‑2 total: 0–2 minimal, 3–4 mild, 5–6 moderate‑severe (flag)
  - Crisis indicators escalate to crisis level regardless of totals.
- Outcomes:
  - Minimal/Mild: Self-care tips and non-urgent resources.
  - Moderate/Severe/Crisis: Immediate escalation to a licensed counselor queue and presentation of hotlines; if danger is present, direct to local emergency services.

Channels
- Web: REST endpoints at /api/triage/start and /api/triage/next.
- Voice: Twilio-compatible /api/triage/voice/twilio returns TwiML prompts. Speech handling is delegated to provider infrastructure.

RAG Context
- Optional lookup of local coping resources and government helplines (region-aware). Defaults to a static, privacy-preserving list; can integrate with Archon/Airweave connectors when configured.
- Storage policy: Minimal PII, ephemeral session memory; audit logs avoid storing raw PII where possible.

Handoff & Audit
- TriageCase artifacts include transcript (with minimal PII), severity, resources, escalation reasons, and audit trail.
- Cases that meet escalation criteria are queued for licensed counselors. Queue endpoints allow downstream operators to claim cases.

Testing & Acceptance
- A dedicated test suite includes 20+ edge cases for safety detection and ensures 0 unsafe output escapes.
- Simulated conversations produce severity scores and an appropriate call‑to‑action (self‑care vs connect to counselor).

Configuration
- MASTRA_PSYCH_KIT_URL: Optional URL to a Mastra-based orchestrator that integrates multiple LLM providers with moderation.
- Region hints can be passed on session start to tailor resources (e.g., US, UK, IE).

Compliance & Privacy
- Data minimization: Only necessary metadata is stored; transcripts are marked as PII‑minimized.
- Security: No secrets are logged. External calls abide by provider terms and moderation policies.
- Escalation: Self-harm, harm-to-others, and medical emergencies trigger immediate escalation and display of emergency resources.
