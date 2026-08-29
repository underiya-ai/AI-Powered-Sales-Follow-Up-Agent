from langgraph.types import interrupt

from backend.pipeline.state import SalesState


def human_approval(state: SalesState) -> SalesState:
    """
    Human-in-the-Loop approval node.

    Pauses the graph and waits for human decision.

    Actions:
    - approve → email can be sent
    - edit    → edited email can be sent
    - reject  → email will not be sent
    """

    email = state.get("email")

    if not email:
        raise ValueError(
            "Email is required for human approval"
        )

    # Pause the graph and wait for human decision
    approval = interrupt({
        "message": "Please review the generated email.",
        "email": email,
        "lead_score": state.get("lead_score"),
        "lead_priority": state.get("lead_priority"),
        "next_best_action": state.get("next_best_action"),
        "follow_up": state.get("follow_up")
    })

    if not isinstance(approval, dict):
        raise ValueError(
            "Invalid human approval response"
        )

    action = approval.get("action")

   
    # Approve

    if action == "approve":

        state["human_approval"] = "approved"

        state["approval_status"] = "approved"

        state["pipeline_status"] = "email_approved"

        return state

    
    # Edit

    elif action == "edit":

        edited_email = approval.get("email")

        if not edited_email:
            raise ValueError(
                "Edited email is required"
            )

        if not isinstance(edited_email, dict):
            raise ValueError(
                "Edited email must be an object"
            )

        if not edited_email.get("subject"):
            raise ValueError(
                "Edited email subject is required"
            )

        if not edited_email.get("body"):
            raise ValueError(
                "Edited email body is required"
            )

        # Replace generated email with edited email
        state["email"] = {
            "subject": edited_email["subject"],
            "body": edited_email["body"]
        }

        state["human_approval"] = "edited"

        state["approval_status"] = "edited"

        state["pipeline_status"] = "email_edited"

        return state

    
    # REJECT
    

    elif action == "reject":

        state["human_approval"] = "rejected"

        state["approval_status"] = "rejected"

        state["pipeline_status"] = "email_rejected"

        return state

    # INVALID ACTION
    

    else:

        raise ValueError(
            "Invalid action. Use approve, edit, or reject."
        )