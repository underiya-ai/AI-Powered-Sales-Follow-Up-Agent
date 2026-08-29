import json

from backend.pipeline.state import SalesState
from backend.utils.llm import groq_llm, gemini_llm


def lead_scoring_agent(state: SalesState) -> SalesState:
    """
    Lead Scoring Agent

    Uses Conversation Intelligence output
    to score the sales lead.
    """

    conversation_analysis = state.get("conversation_analysis")

    if not conversation_analysis:
        raise ValueError(
            "Conversation analysis is required for LeadScoringAgent"
        )

    prompt = f"""
You are a Lead Scoring Agent for an AI Sales Assistant.

Evaluate the sales lead using ONLY the information provided below.

Conversation Intelligence:
{json.dumps(conversation_analysis, indent=2)}

Calculate a lead score from 0 to 100.

Consider:

- Customer intent
- Customer needs
- Pain points
- Requirements
- Buying signals
- Decision timeline

Scoring:

80-100 = HOT
50-79 = WARM
0-49 = COLD

Return ONLY valid JSON.

The JSON MUST contain all three fields.
NEVER return null.
NEVER leave any field empty.

Required format:

{{
    "lead_score": 92,
    "lead_priority": "HOT",
    "reason": "Explain clearly why this lead received this score and priority."
}}

Rules:

- lead_score must be an integer between 0 and 100.
- lead_priority must be exactly HOT, WARM, or COLD.
- reason is REQUIRED.
- reason must be a non-empty string.
- Do not invent information.
- Use ONLY the provided conversation intelligence.
- Return JSON only.
"""

    
    try:
        response = groq_llm.invoke(prompt)

    
    except Exception:
        response = gemini_llm.invoke(prompt)

    content = response.content

    if isinstance(content, list):
        content = "".join(
            item.get("text", "")
            if isinstance(item, dict)
            else str(item)
            for item in content
        )

    content = content.strip()

    if content.startswith("```"):
        content = content.replace("```json", "")
        content = content.replace("```", "")
        content = content.strip()

    try:
        scoring = json.loads(content)

    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Lead Scoring Agent returned invalid JSON: {content}"
        ) from exc

    
    # Validate lead score
    

    score = scoring.get("lead_score")

    if not isinstance(score, int) or not 0 <= score <= 100:
        raise ValueError(
            f"Invalid lead_score returned by LLM: {score}"
        )

    
    # Validate priority
    

    priority = scoring.get("lead_priority")

    if priority not in {"HOT", "WARM", "COLD"}:
        raise ValueError(
            f"Invalid lead_priority returned by LLM: {priority}"
        )

    
    # Validate reason
    

    reason = scoring.get("reason")

    if not isinstance(reason, str) or not reason.strip():
        raise ValueError(
            f"Lead Scoring Agent returned empty/null reason: {reason}"
        )

    
    # Store in LangGraph state
    

    state["lead_score"] = score
    state["lead_priority"] = priority
    state["lead_scoring_reason"] = reason.strip()

    state["pipeline_status"] = "lead_scoring_completed"

    return state