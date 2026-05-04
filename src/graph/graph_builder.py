"""
LangGraph graph builder — wires all nodes into a compiled research graph.

Defines the node topology, conditional routing logic, and compiles the
StateGraph with a checkpointer for debugging and state inspection.

Graph topology:
    START → planner → researcher ──→ validator ──→ researcher (loop)
                                    │                  │
                                    └──→ synthesizer ←─┘
                                              │
                                              → END

Usage:
    from src.graph.graph_builder import build_research_graph
    graph = build_research_graph()
    result = graph.invoke({"original_query": "NVIDIA", ...})
"""

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from src.graph.state import ResearchState
from src.graph.nodes.planner import PlannerNode
from src.graph.nodes.researcher import ResearcherNode
from src.graph.nodes.validator import ValidatorNode
from src.graph.nodes.synthesizer import SynthesizerNode


def route_after_researcher(state: ResearchState) -> str:
    """Route to validator if subtasks remain, otherwise to synthesizer.

    Args:
        state: Current research state.

    Returns:
        "validator" if there are still subtasks to validate,
        "synthesizer" if all subtasks have been processed.
    """
    if state["current_subtask_idx"] < len(state["subtasks"]):
        return "validator"
    return "synthesizer"


def route_after_validator(state: ResearchState) -> str:
    """Route back to researcher if pending subtasks remain, otherwise to synthesizer.

    Scans all subtasks; if any are still "pending" (either a retry or the
    next one), route back to researcher. Otherwise route to synthesizer.

    Args:
        state: Current research state.

    Returns:
        "researcher" if any subtask is still pending,
        "synthesizer" if all are done or failed.
    """
    for st in state["subtasks"]:
        if st["status"] == "pending":
            return "researcher"
    return "synthesizer"


def build_research_graph() -> StateGraph:
    """Construct and compile the LangGraph research graph.

    Creates node instances, wires them with edges and conditional
    routing, and compiles with an in-memory checkpointer.

    Returns:
        A compiled StateGraph ready for invocation.
    """
    # Instantiate all nodes (each creates its own dependencies by default).
    planner = PlannerNode()
    researcher = ResearcherNode()
    validator = ValidatorNode()
    synthesizer = SynthesizerNode()

    # Define the graph with the ResearchState schema.
    workflow = StateGraph(ResearchState)

    # Register all nodes.
    workflow.add_node("planner", planner.call)
    workflow.add_node("researcher", researcher.call)
    workflow.add_node("validator", validator.call)
    workflow.add_node("synthesizer", synthesizer.call)

    # Define edges.
    workflow.add_edge("planner", "researcher")

    workflow.add_conditional_edges(
        "researcher",
        route_after_researcher,
        {"validator": "validator", "synthesizer": "synthesizer"},
    )

    workflow.add_conditional_edges(
        "validator",
        route_after_validator,
        {"researcher": "researcher", "synthesizer": "synthesizer"},
    )

    workflow.add_edge("synthesizer", END)

    # Set the entry point.
    workflow.set_entry_point("planner")

    # Compile with in-memory checkpointer for state inspection.
    checkpointer = MemorySaver()
    return workflow.compile(checkpointer=checkpointer)