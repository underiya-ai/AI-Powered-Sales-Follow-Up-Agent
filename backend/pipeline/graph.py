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

from backend.service.gmail_service import send_email as gmail_send_email


def wait_for_customer_email(state: SalesState) -> SalesState:

    state["pipeline_status"] = "waiting_for_customer_email"

    return state



def approval_router(state: SalesState):

    approval_status = state.get("approval_status")

    if approval_status == "approved":
        return "send_email"

    if approval_status == "rejected":
        return END

    # Edited email ko send nahi karna
    if approval_status == "edited":
        return END

    raise ValueError(
        f"Invalid approval status: {approval_status}"
    )


def send_email(state: SalesState) -> SalesState:

    email = state.get("email")
    customer_email = state.get("customer_email")

    if not email:
        raise ValueError(
            "Email is required before sending"
        )

    if not customer_email:
        raise ValueError(
            "Customer email is required before sending"
        )

    subject = email.get("subject")
    body = email.get("body")

    if not subject or not body:
        raise ValueError(
            "Email subject and body are required"
        )

    result = gmail_send_email(
        to_email=customer_email,
        subject=subject,
        body=body
    )

    print("\nEMAIL SENT SUCCESSFULLY")
    print("To:", customer_email)
    print("Subject:", subject)
    print("Message ID:", result.get("id"))

    state["email_send_result"] = result
    state["pipeline_status"] = "email_sent"

    return state




def create_sales_graph():

    graph = StateGraph(SalesState)



    graph.add_node(
        "sales_orchestrator",
        sales_orchestrator
    )
    graph.add_node(
    "wait_for_customer_email",
    wait_for_customer_email
)
    graph.add_node(
        "conversation_intelligence",
        conversation_intelligence
    )

    graph.add_node(
        "lead_scoring",
        lead_scoring_agent
    )

    graph.add_node(
        "next_action_agent",
        next_best_action_agent
    )

    graph.add_node(
        "follow_up_agent",
        follow_up_agent
    )

    graph.add_node(
        "email_agent",
        email_agent
    )

    graph.add_node(
        "human_approval",
        human_approval
    )

    graph.add_node(
        "send_email",
        send_email
    )

 

    graph.add_edge(
        START,
        "sales_orchestrator"
    )

    graph.add_edge(
        "sales_orchestrator",
        "conversation_intelligence"
    )

    graph.add_edge(
        "conversation_intelligence",
        "lead_scoring"
    )

    graph.add_edge(
        "lead_scoring",
        "next_action_agent"
    )

    graph.add_edge(
        "next_action_agent",
        "follow_up_agent"
    )


    graph.add_edge(
        "follow_up_agent",
        "wait_for_customer_email"
    )

    graph.add_edge(
        "wait_for_customer_email",
        END
    )

   

    checkpointer = MemorySaver()

    return graph.compile(
        checkpointer=checkpointer
    )


def create_email_graph():

    graph = StateGraph(SalesState)

    graph.add_node(
        "email_agent",
        email_agent
    )

    graph.add_node(
        "human_approval",
        human_approval
    )

    graph.add_node(
        "send_email",
        send_email
    )

    # START
    graph.add_edge(
        START,
        "email_agent"
    )

    # Email generation
    graph.add_edge(
        "email_agent",
        "human_approval"
    )

    # Approval routing
    graph.add_conditional_edges(
        "human_approval",
        approval_router,
        {
            "send_email": "send_email",
            END: END
        }
    )

    # Send email
    graph.add_edge(
        "send_email",
        END
    )

    checkpointer = MemorySaver()

    return graph.compile(
        checkpointer=checkpointer
    )



sales_graph = create_sales_graph()

email_graph = create_email_graph()