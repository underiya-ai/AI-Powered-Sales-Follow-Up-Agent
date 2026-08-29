from typing import TypedDict, Optional


class SalesState(TypedDict, total=False):
    # Conversation information
    conversation_id: int
    conversation_type: str
    filename: str
    transcript: str

    # Conversation Intelligence Agent
    conversation_analysis: Optional[dict]

    # Lead Scoring Agent
    lead_score: Optional[int]
    lead_priority: Optional[str]

    # Next Best Action Agent
    next_best_action: Optional[dict]

    # Follow-Up Agent
    follow_up: Optional[dict]

    # Email Agent
    email: Optional[dict]