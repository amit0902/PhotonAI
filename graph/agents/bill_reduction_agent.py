def bill_reduction_agent(state, llm):

    monthly_units = state["monthly_units"]
    target_units = state["bill_target_units"]

    # Safety check
    if target_units >= monthly_units:

        state["messages"].append({
            "role": "assistant",
            "content": (
                "Your target consumption is already higher than or equal to "
                "your current usage, so a solar system is not required to "
                "achieve this reduction goal."
            )
        })

        state["current_stage"] = "choose_design_path"
        return state


    # Monthly energy to offset
    monthly_offset = monthly_units - target_units

    annual_target = monthly_offset * 12

    state["target_energy"] = annual_target
    state["installation_goal"] = "bill_reduction"

    state["messages"].append({
        "role": "assistant",
        "content": (
            f"Understood. Your current consumption is {monthly_units:.0f} units per month, "
            f"and you would like to reduce it to about {target_units:.0f} units.\n\n"
            f"This means the solar system should offset approximately "
            f"{monthly_offset:.0f} units per month "
            f"({annual_target:.0f} kWh annually).\n\n"
            "I will now design a solar PV system optimized to achieve this target."
        )
    })

    return state