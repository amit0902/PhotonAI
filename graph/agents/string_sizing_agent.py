from services.equipment_database import select_panel
from services.equipment_database import select_battery


def run_string_sizing(state):

    system_kw = state.get("system_kw", 0)

    # ---------------------------------------------------
    # Select Panel From Equipment Database
    # ---------------------------------------------------

    panel = select_panel(system_kw)

    panel_name = panel["name"]
    panel_power = panel["watt"]

    # ---------------------------------------------------
    # Calculate Number of Panels
    # ---------------------------------------------------

    total_watts = system_kw * 1000

    panel_count = round(total_watts / panel_power)

    # ---------------------------------------------------
    # Basic String Design Logic
    # ---------------------------------------------------

    modules_per_string = min(10, panel_count)   # safe default
    parallel_strings = max(1, round(panel_count / modules_per_string))

    # ---------------------------------------------------
    # Save Results To State
    # ---------------------------------------------------

    state["panel_name"] = panel_name
    state["panel_power"] = panel_power
    state["panel_count"] = panel_count

    state["series"] = modules_per_string
    state["parallel"] = parallel_strings

    state["messages"].append({
        "role": "assistant",
        "content": (
            "🔧 Agent Activated: String Sizing Calculator\n\n"
            f"Panel Selected: {panel_name} ({panel_power} W)\n\n"
            f"Recommended Configuration:\n"
            f"{modules_per_string} modules in series x {parallel_strings} parallel strings\n"
            f"Total Modules: {panel_count}"
        )
    })

    return state