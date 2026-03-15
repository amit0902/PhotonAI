def goal_router_agent(state):

    goal = state.get("installation_goal")

    if not goal:
        state["current_stage"] = "ask_goal"
        return state

    if goal == "heavy_load":
        state["current_stage"] = "run_heavy_load"
        return state

    if goal == "bill_reduction":
        state["current_stage"] = "ask_bill_target"
        return state

    if goal in ["full_offset", "carbon_offset"]:
        state["current_stage"] = "run_full_analysis"
        return state

    state["current_stage"] = "ask_goal"
    return state