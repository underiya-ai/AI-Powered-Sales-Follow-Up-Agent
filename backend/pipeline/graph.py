from langgraph.graph import StateGraph, START, END

from backend.pipeline.state import SalesState
from backend.Agents.sales_orchestrator import sales_orchestrator
from backend.Agents.conversation_intelligence import conversation_intelligence
from backend.Agents.lead_scoring_agent import lead_scoring_agent
from backend.Agents.next_best_action_agent import next_best_action_agent


def create_sales_graph():

    graph = StateGraph(SalesState)

    graph.add_node("sales_orchestrator",sales_orchestrator)
    graph.add_node("conversation_intelligence",conversation_intelligence)
    graph.add_node("lead_scoring",lead_scoring_agent)
    graph.add_node("next_action_agent",next_best_action_agent)

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
    graph.add_edge("next_action_agent",END)

    return graph.compile()


sales_graph = create_sales_graph()