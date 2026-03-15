def init_node(state):

    # Initialize message history
    if "messages" not in state:
        state["messages"] = []

    # Initialize completion flag
    if "completed" not in state:
        state["completed"] = False

    # If this is a fresh session (no name yet), force ask_name
    if not state.get("name"):
        state["current_stage"] = "ask_name"

    return state