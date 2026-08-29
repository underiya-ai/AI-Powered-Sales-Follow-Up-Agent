import json

from backend.pipeline.state import SalesState
from backend.utils.llm import groq_llm, gemini_llm


def email_agent(state: SalesState) -> SalesState:
    """
    Email Agent

    Generates a personalized sales follow-up email
    using the outputs of previous agents.

    Groq = Primary
    Gemini = Fallback
    """

    conversation_analysis = state.get("conversation_analysis")
    lead_score = state.get("lead_score")
    lead_priority = state.get("lead_priority")
    next_best_action = state.get("next_best_action")
    follow_up = state.get("follow_up")

    if not conversation_analysis:
        raise ValueError(
            "Conversation analysis is required for EmailAgent"
        )

    if lead_score is None:
        raise ValueError(
            "Lead score is required for EmailAgent"
        )

    if not next_best_action:
        raise ValueError(
            "Next best action is required for EmailAgent"
        )

    if not follow_up:
        raise ValueError(
            "Follow-up information is required for EmailAgent"
        )

    prompt = f"""
You are an Email Agent for an AI Sales Follow-Up Assistant.

Generate a professional and personalized sales follow-up email.

Use ONLY the information provided below.

Conversation Intelligence:
{json.dumps(conversation_analysis, indent=2)}

Lead Score:
{lead_score}

Lead Priority:
{lead_priority}

Next Best Action:
{json.dumps(next_best_action, indent=2)}

Follow-Up:
{json.dumps(follow_up, indent=2)}

Return ONLY valid JSON using exactly this structure:

{{
    "subject": "...",
    "body": "..."
}}

Rules:
- Make the email personalized to the customer.
- Clearly address the customer's needs.
- Mention the requested information when appropriate.
- Keep the email concise and professional.
- Do not invent pricing, product features, dates, or other information.
- Do not mention the lead score or internal AI analysis.
- Do not use markdown.
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

    # Remove markdown code fences if returned by LLM
    if content.startswith("```"):
        content = content.replace("```json", "")
        content = content.replace("```", "")
        content = content.strip()

    try:
        email = json.loads(content)

    except json.JSONDecodeError as exc:
        raise ValueError(
            f"EmailAgent returned invalid JSON: {content}"
        ) from exc

    # Validate required fields
    subject = email.get("subject")
    body = email.get("body")

    if not subject:
        raise ValueError(
            "Email subject is missing"
        )

    if not body:
        raise ValueError(
            "Email body is missing"
        )

    # Store email in shared LangGraph state
    state["email"] = {
        "subject": subject,
        "body": body
    }

    state["pipeline_status"] = "email_generation_completed"

    return state