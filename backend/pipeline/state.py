from typing import TypedDict


class SalesState(TypedDict, total=False):

    conversation_id: int
    conversation_type: str
    filename: str
    transcript: str

    customer_email: str

    conversation_analysis: dict

    lead_score: int
    lead_priority: str
    lead_scoring_reason: str

    next_best_action: dict
    follow_up: dict

    email: dict

    approval_status: str
    human_approval: dict

    email_send_result: dict

    pipeline_status: str