from typing import TypedDict, Optional





class SalesState(TypedDict, total=False):

    # Conversation
    conversation_id: int
    conversation_type: str
    filename: str
    transcript: str

    # Conversation Intelligence
    conversation_analysis: Optional[dict]

    # Lead Scoring
    lead_score: Optional[int]
    lead_priority: Optional[str]
    lead_scoring_reason: Optional[str]

    # Next Best Action
    next_best_action: Optional[dict]

    # Follow-Up
    follow_up: Optional[dict]

    # Email
    email: Optional[dict]
    customer_email: str

    # Human Approval
    human_approval: Optional[dict]
    approval_status: Optional[str]

    # Pipeline
    sales_goal: Optional[str]
    pipeline_status: Optional[str]