from typing import TypedDict, Optional


class SalesState(TypedDict, total=False):

    conversation_id: int

    conversation_type: str

    filename: str

    transcript: str

    conversation_analysis: dict

    lead_score: int

    lead_priority: str

    next_best_action: dict

    follow_up: dict

    email: dict