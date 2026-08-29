from langgraph.graph import StateGraph, START, END

from backend.pipeline.state import SalesState


def create_sales_graph():

    graph = StateGraph(SalesState)

    # Agents will be added here
    # graph.add_node("conversation_intelligence", ...)
    # graph.add_node("lead_scoring", ...)
    # graph.add_node("next_best_action", ...)
    # graph.add_node("follow_up", ...)
    # graph.add_node("email", ...)

    graph.add_edge(START, END)

    return graph.compile()


sales_graph = create_sales_graph()