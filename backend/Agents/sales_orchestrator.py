import json

from backend.pipeline.state import SalesState
from backend.utils.llm import gemini_llm, groq_llm


def sales_orchestrator(state: SalesState) -> SalesState:
    """
    SalesOrchestrator

    Uses Gemini/Groq to understand the sales conversation
    and decide which downstream sales agents are required.
    """

    transcript = state.get("transcript", "").strip()

    if not transcript:
        raise ValueError("Transcript is required")

    prompt = f"""
You are SalesOrchestrator, the supervisor of an AI sales assistant.

Your job is NOT to write an email or calculate the final lead score.

Your job is to examine the customer's conversation and decide
what the downstream sales pipeline needs to do.

Customer conversation:

{transcript}

Analyze the conversation and return ONLY valid JSON.

Use exactly this structure:

{{
    "sales_intent": "string",
    "urgency": "low | medium | high",
    "requires_follow_up": true,
    "required_agents": [
        "conversation_intelligence",
        "lead_scoring",
        "next_best_action",
        "follow_up",
        "email"
    ],
    "reason": "short explanation"
}}

Rules:

1. Always include conversation_intelligence.
2. Always include lead_scoring.
3. Include next_best_action when the customer has a clear sales-related request.
4. Include follow_up when the customer needs a response or future action.
5. Include email when a personalized customer response should be prepared.
6. Do not generate the email yourself.
7. Do not calculate a numerical lead score yourself.
8. Return JSON only.
"""

    try:
        response = gemini_llm.invoke(prompt)
    except Exception:
        response = groq_llm.invoke(prompt)

    content = response.content

    if isinstance(content, list):
        content = "".join(
            item.get("text", "")
            if isinstance(item, dict)
            else str(item)
            for item in content
        )

    content = content.strip()

    # Remove markdown JSON fences if the model returns them
    if content.startswith("```"):
        content = content.replace("```json", "")
        content = content.replace("```", "")
        content = content.strip()

    try:
        decision = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"SalesOrchestrator returned invalid JSON: {content}"
        ) from exc

    state["sales_goal"] = (
        "Analyze the customer conversation, "
        "score the lead, determine the next best action, "
        "schedule a follow-up, and generate a personalized email."
    )

    state["orchestration_decision"] = decision
    state["pipeline_status"] = "orchestration_completed"

    return state 