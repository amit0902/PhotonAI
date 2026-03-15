from services.carbon_service import calculate_carbon_offset


def heavy_load_agent(state):

    if not state.get("heavy_loads"):

        state["messages"].append({
            "role": "assistant",
            "content": (
                "I don't see any appliance information yet.\n"
                "Let's start by adding your first appliance."
            )
        })

        state["current_stage"] = "ask_heavy_name"
        return state


    total_daily_kwh = 0
    table_rows = []

    for load in state["heavy_loads"]:

        name = load.get("name", "Appliance")
        kw = float(load.get("kw", 0))
        qty = int(load.get("quantity", 1))
        hours = float(load.get("hours", 0))

        appliance_daily = kw * qty * hours

        total_daily_kwh += appliance_daily

        table_rows.append(
            f"| {name} | {kw:.2f} | {qty} | {hours:.1f} | {appliance_daily:.2f} |"
        )


    annual_kwh = total_daily_kwh * 365
    monthly_kwh = total_daily_kwh * 30


    monthly_total = state.get("monthly_units", 0)

    if monthly_total:
        percentage = (monthly_kwh / monthly_total) * 100
    else:
        percentage = 0


    carbon_preview = calculate_carbon_offset(annual_kwh)


    appliance_table = (
        "| Appliance | Power (kW) | Qty | Hours/day | Daily Energy (kWh) |\n"
        "|-----------|-----------|-----|-----------|--------------------|\n"
        + "\n".join(table_rows)
    )


    summary = f"""
### ⚡ Appliance Energy Analysis

Based on the appliances you've listed, here is the estimated energy demand.

{appliance_table}

### Energy Summary

• **Daily Consumption from Selected Appliances:** {total_daily_kwh:.2f} kWh/day  
• **Monthly Energy from These Appliances:** {monthly_kwh:.0f} kWh  
• **Annual Energy Requirement:** {annual_kwh:.0f} kWh/year  

These appliances represent approximately **{percentage:.1f}% of your total electricity consumption**.

The solar system below will therefore be designed **only to power these appliances**, rather than your entire household demand.

### Environmental Impact

If powered by solar energy, these appliances could avoid approximately:

• **{carbon_preview['tonnes']} tonnes of CO₂ emissions annually**  
• Equivalent to planting **{carbon_preview['trees']} trees**

I will now design a solar PV system sized specifically for these appliances.
"""

    state["heavy_daily_kwh"] = round(total_daily_kwh, 2)
    state["heavy_annual_kwh"] = round(annual_kwh, 2)

    state["target_energy"] = annual_kwh
    state["installation_goal"] = "heavy_load"

    state["messages"].append({
        "role": "assistant",
        "content": summary.strip()
    })

    state["current_stage"] = "run_full_analysis"

    return state