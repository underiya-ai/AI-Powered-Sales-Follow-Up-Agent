from typing import TypedDict, Optional


class SalesState(TypedDict, total=False):

    # Conversation
    conversation_id: int
    conversation_type: str
    filename: str
    transcript: str

    # Sales Orchestrator
    sales_goal: str
    pipeline_status: str
    orchestration_decision: Optional[dict]

    # Conversation Intelligence
    conversation_analysis: Optional[dict]

    # Lead Scoring
    lead_score: Optional[int]
    lead_priority: Optional[str]
    lead_score_reason: Optional[str]

    # Next Best Action
    next_best_action: Optional[dict]

    # Follow-Up
    follow_up: Optional[dict]

    # Email
    email: Optional[dict]