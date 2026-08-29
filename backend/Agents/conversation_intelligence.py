import json

from backend.pipeline.state import SalesState
from backend.utils.llm import gemini_llm,groq_llm


def conversation_intelligence(state: SalesState) -> SalesState:

    transcript = state.get("transcript", "").strip()

    if not transcript:
        raise ValueError("Transcript is required")

    prompt = f"""
You are a Conversation Intelligence Agent for an AI Sales Assistant.

Analyze the following sales conversation.

Conversation:
{transcript}

Extract useful sales intelligence.

Return ONLY valid JSON using this exact structure:

{{
  "customer_intent": "...",
  "customer_needs": ["..."],
  "pain_points": ["..."],
  "requirements": ["..."],
  "buying_signals": ["..."],
  "decision_timeline": "...",
  "summary": "..."
}}

Rules:
- Do not invent information.
- If something is not mentioned, use an empty list or "not mentioned".
- Focus only on information present in the conversation.
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
        analysis = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Conversation Intelligence returned invalid JSON: {content}"
        ) from exc

    state["conversation_analysis"] = analysis
    state["pipeline_status"] = "conversation_analysis_completed"

    return state