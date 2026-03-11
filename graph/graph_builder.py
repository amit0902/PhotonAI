from langgraph.graph import StateGraph, END
from graph.state import SolarState
from graph.nodes.init_node import init_node
from graph.nodes.input_node import input_node
from graph.nodes.controller_node import controller_node


def build_graph(llm):
    graph = StateGraph(SolarState)

    graph.add_node("init", init_node)
    graph.add_node("input", input_node)
    graph.add_node("controller", lambda s: controller_node(s, llm))

    graph.set_entry_point("init")

    graph.add_edge("init", "input")
    graph.add_edge("input", "controller")
    graph.add_edge("controller", END)

    return graph.compile()