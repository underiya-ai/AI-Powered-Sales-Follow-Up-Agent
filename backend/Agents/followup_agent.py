import json
from datetime import datetime

from backend.pipeline.state import SalesState
from backend.utils.llm import groq_llm, gemini_llm


def follow_up_agent(state: SalesState) -> SalesState:
    """
    Follow-Up Agent

    Determines when and why the sales team should
    follow up with the customer.
    """

    conversation_analysis = state.get("conversation_analysis")
    lead_score = state.get("lead_score")
    lead_priority = state.get("lead_priority")
    next_best_action = state.get("next_best_action")

    if not conversation_analysis:
        raise ValueError(
            "Conversation analysis is required for FollowUpAgent"
        )

    if lead_score is None:
        raise ValueError(
            "Lead score is required for FollowUpAgent"
        )

    if not lead_priority:
        raise ValueError(
            "Lead priority is required for FollowUpAgent"
        )

    if not next_best_action:
        raise ValueError(
            "Next best action is required for FollowUpAgent"
        )

    current_date = datetime.now().strftime("%Y-%m-%d")

    prompt = f"""
You are a Follow-Up Agent for an AI Sales Assistant.

Your job is to determine the most appropriate follow-up
plan for the sales lead.

Use ONLY the information provided below.

Current date:
{current_date}

Conversation Intelligence:
{json.dumps(conversation_analysis, indent=2)}

Lead Score:
{lead_score}

Lead Priority:
{lead_priority}

Next Best Action:
{json.dumps(next_best_action, indent=2)}

Determine:

1. When the sales team should follow up.
2. The purpose of the follow-up.
3. The urgency of the follow-up.

The customer's decision timeline should be considered
when deciding the follow-up timing.

Return ONLY valid JSON using exactly this structure:

{{
    "follow_up_timing": "...",
    "purpose": "...",
    "urgency": "HIGH"
}}

Rules:

- follow_up_timing is REQUIRED.
- purpose is REQUIRED.
- urgency is REQUIRED.
- NEVER return null.
- NEVER return an empty string.
- urgency must be exactly HIGH, MEDIUM, or LOW.
- Do not invent a specific date unless it is supported
  by the conversation.
- If the conversation only provides a relative timeline
  such as "next week", use that relative timeline.
- The purpose must be directly connected to the
  customer's needs and the next best action.
- Use ONLY the provided information.
- Return JSON only.
"""

    # Groq = Primary
    try:
        response = groq_llm.invoke(prompt)

    # Gemini = Fallback
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

    # Remove markdown code fences
    if content.startswith("```"):
        content = content.replace("```json", "")
        content = content.replace("```", "")
        content = content.strip()

    try:
        follow_up_data = json.loads(content)

    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Follow-Up Agent returned invalid JSON: {content}"
        ) from exc

    
    # Validate follow-up timing
    

    follow_up_timing = follow_up_data.get(
        "follow_up_timing"
    )

    if (
        not isinstance(follow_up_timing, str)
        or not follow_up_timing.strip()
    ):
        raise ValueError(
            "Follow-Up Agent returned invalid follow_up_timing"
        )

    
    # Validate purpose


    purpose = follow_up_data.get("purpose")

    if not isinstance(purpose, str) or not purpose.strip():
        raise ValueError(
            "Follow-Up Agent returned invalid purpose"
        )


    # Validate urgency
    

    urgency = follow_up_data.get("urgency")

    if urgency not in {"HIGH", "MEDIUM", "LOW"}:
        raise ValueError(
            f"Invalid urgency returned by FollowUpAgent: {urgency}"
        )

    
    # Store in LangGraph state
    

    state["follow_up"] = {
        "follow_up_timing": follow_up_timing.strip(),
        "purpose": purpose.strip(),
        "urgency": urgency
    }

    state["pipeline_status"] = "follow_up_completed"

    return state