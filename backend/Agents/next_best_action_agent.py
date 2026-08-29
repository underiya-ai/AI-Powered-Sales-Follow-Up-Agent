import json

from backend.pipeline.state import SalesState
from backend.utils.llm import groq_llm, gemini_llm


def next_best_action_agent(state: SalesState) -> SalesState:
    """
    Next Best Action Agent

    Determines the most appropriate action that should be
    taken after analyzing the customer conversation and lead score.
    """

    conversation_analysis = state.get("conversation_analysis")
    lead_score = state.get("lead_score")
    lead_priority = state.get("lead_priority")

    if not conversation_analysis:
        raise ValueError(
            "Conversation analysis is required for NextBestActionAgent"
        )

    if lead_score is None:
        raise ValueError(
            "Lead score is required for NextBestActionAgent"
        )

    if not lead_priority:
        raise ValueError(
            "Lead priority is required for NextBestActionAgent"
        )

    prompt = f"""
You are a Next Best Action Agent for an AI Sales Assistant.

Your job is to determine the SINGLE most useful next action
the sales team should take based ONLY on the available
conversation intelligence and lead scoring information.

Conversation Intelligence:
{json.dumps(conversation_analysis, indent=2)}

Lead Score:
{lead_score}

Lead Priority:
{lead_priority}

Determine what the salesperson should do next.

Possible actions may include:
- Send pricing information
- Send security documentation
- Schedule a product demo
- Contact the customer
- Answer a specific requirement
- Address an objection
- Schedule a follow-up
- Prepare additional product information

Choose the action that is most directly supported by the conversation.

Return ONLY valid JSON using exactly this structure:

{{
    "action": "Send pricing and security documentation",
    "reason": "The customer explicitly requested pricing and security documentation.",
    "urgency": "HIGH"
}}

Rules:

- action is REQUIRED.
- reason is REQUIRED.
- urgency is REQUIRED.
- NEVER return null.
- NEVER return an empty string.
- urgency must be exactly HIGH, MEDIUM, or LOW.
- Do not invent information.
- Use ONLY the provided conversation intelligence and lead score.
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

    # Remove markdown code fences
    if content.startswith("```"):
        content = content.replace("```json", "")
        content = content.replace("```", "")
        content = content.strip()

    try:
        action_data = json.loads(content)

    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Next Best Action Agent returned invalid JSON: {content}"
        ) from exc

    
    # Validate action
    

    action = action_data.get("action")

    if not isinstance(action, str) or not action.strip():
        raise ValueError(
            f"Next Best Action Agent returned invalid action: {action}"
        )

    
    # Validate reason


    reason = action_data.get("reason")

    if not isinstance(reason, str) or not reason.strip():
        raise ValueError(
            f"Next Best Action Agent returned invalid reason: {reason}"
        )

    
    # Validate urgency
    

    urgency = action_data.get("urgency")

    if urgency not in {"HIGH", "MEDIUM", "LOW"}:
        raise ValueError(
            f"Invalid urgency returned by NextBestActionAgent: {urgency}"
        )

    
    # Store in LangGraph state
    

    state["next_best_action"] = {
        "action": action.strip(),
        "reason": reason.strip(),
        "urgency": urgency
    }

    state["pipeline_status"] = "next_best_action_completed"

    return state