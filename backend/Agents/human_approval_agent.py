from langgraph.types import interrupt

from backend.pipeline.state import SalesState


def human_approval(state: SalesState) -> SalesState:
    """
    Human-in-the-Loop approval node.

    Pauses the LangGraph pipeline after email generation
    and waits for human approval.
    """

    email = state.get("email")

    if not email:
        raise ValueError(
            "Email is required for human approval"
        )

    approval = interrupt({
        "message": "Please review the generated email.",
        "email": email,
        "lead_score": state.get("lead_score"),
        "lead_priority": state.get("lead_priority"),
        "next_best_action": state.get("next_best_action"),
        "follow_up": state.get("follow_up")
    })

    # Human's response will be supplied when the graph resumes
    state["human_approval"] = approval

    state["pipeline_status"] = "human_approval_completed"

    return state