def run_string_sizing(state):

    module_power = 420  # W typical panel
    total_kw = state["system_kw"]

    total_watts = total_kw * 1000
    total_modules = round(total_watts / module_power)

    modules_per_string = 5  # assumption
    strings = max(1, round(total_modules / modules_per_string))

    state["messages"].append({
        "role": "assistant",
        "content": (
            "🔧 Agent Activated: String Sizing Calculator\n\n"
            f"Recommended Configuration:\n"
            f"{modules_per_string} modules in series × {strings} parallel strings\n"
            f"Total Modules: {total_modules}"
        )
    })

    return state