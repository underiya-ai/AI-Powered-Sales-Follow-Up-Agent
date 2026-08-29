from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from backend.pipeline.state import SalesState
from backend.Agents.sales_orchestrator import sales_orchestrator
from backend.Agents.conversation_intelligence import conversation_intelligence
from backend.Agents.lead_scoring_agent import lead_scoring_agent
from backend.Agents.next_best_action_agent import next_best_action_agent
from backend.Agents.followup_agent import follow_up_agent
from backend.Agents.email_agent import email_agent
from backend.Agents.human_approval_agent import human_approval


def approval_router(state: SalesState):

    approval_status = state.get("approval_status")

    if approval_status in {"approved", "edited"}:
        return "send_email"

    if approval_status == "rejected":
        return END

    raise ValueError(
        f"Invalid approval status: {approval_status}"
    )

def send_email(state: SalesState) -> SalesState:
    """
    Temporary Email Sender.

    Gmail SMTP will be connected here next.
    """

    email = state.get("email")

    if not email:
        raise ValueError("Email is required")

    print("\n EMAIL READY TO SEND ")
    print("Subject:", email.get("subject"))
    print("Body:")
    print(email.get("body"))
  

    state["pipeline_status"] = "email_ready_to_send"

    return state



def create_sales_graph():

    graph = StateGraph(SalesState)

    graph.add_node("sales_orchestrator",sales_orchestrator)
    graph.add_node("conversation_intelligence",conversation_intelligence)
    graph.add_node("lead_scoring",lead_scoring_agent)
    graph.add_node("next_action_agent",next_best_action_agent)
    graph.add_node("follow_up_agent",follow_up_agent)
    graph.add_node("email_agent",email_agent)
    graph.add_node("human_approval",human_approval)
    graph.add_node("send_email",send_email)

    # Agents will be added here
    # graph.add_node("conversation_intelligence", ...)
    # graph.add_node("lead_scoring", ...)
    # graph.add_node("next_best_action", ...)
    # graph.add_node("follow_up", ...)
    # graph.add_node("email", ...)

    
    graph.add_edge(START, "sales_orchestrator")
    graph.add_edge("sales_orchestrator", "conversation_intelligence")  
    graph.add_edge("conversation_intelligence","lead_scoring")
    graph.add_edge("lead_scoring","next_action_agent")
    graph.add_edge("next_action_agent","follow_up_agent")
    graph.add_edge("follow_up_agent","email_agent")
    graph.add_edge("email_agent","human_approval")
    graph.add_conditional_edges(
        "human_approval",
        approval_router,{"send_email": "send_email",
            END: END}
    )
    graph.add_edge("send_email",END)


    checkpointer = MemorySaver()

    return graph.compile(checkpointer=checkpointer)


sales_graph = create_sales_graph()