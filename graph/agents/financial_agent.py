from services.financial_graph_service import generate_breakeven_chart


def financial_agent(state):

    system_kw = state.get("system_kw", 0)
    annual_generation = state.get("annual_kwh", 0)
    monthly_units = state.get("monthly_units", 0)

    grid_mode = state.get("grid_mode", "net_metering")

    # -----------------------------------------
    # Assumptions
    # -----------------------------------------

    cost_per_kw = 50000
    tariff = 7
    system_lifetime = 25

    # -----------------------------------------
    # System Cost
    # -----------------------------------------

    system_cost = system_kw * cost_per_kw

    # -----------------------------------------
    # Government Subsidy Calculation
    # -----------------------------------------

    subsidy = 0

    if system_kw <= 2:
        subsidy = system_kw * 30000

    elif system_kw <= 3:
        subsidy = (2 * 30000) + ((system_kw - 2) * 18000)

    else:
        subsidy = 78000

    subsidy = min(subsidy, 78000)

    # -----------------------------------------
    # Net Cost
    # -----------------------------------------

    net_cost = system_cost - subsidy

    # -----------------------------------------
    # Energy Utilization by System Type
    # -----------------------------------------

    if grid_mode == "net_metering":

        usable_energy = annual_generation
        mode_description = "Grid-connected system with **net metering** (excess solar exported to grid)."

    elif grid_mode == "self_consumption":

        usable_energy = annual_generation * 0.85
        mode_description = "Grid-connected **self-consumption system** without exporting electricity."

    elif grid_mode == "backup_priority":

        usable_energy = annual_generation * 0.80
        mode_description = "Hybrid solar system with **battery backup priority**."

    else:

        usable_energy = annual_generation
        mode_description = "Grid-connected solar system."

    # -----------------------------------------
    # Savings Calculation
    # -----------------------------------------

    annual_savings = usable_energy * tariff

    payback = net_cost / annual_savings if annual_savings else 0

    lifetime_savings = (annual_savings * system_lifetime) - net_cost

    # -----------------------------------------
    # Comparison with Net Metering
    # -----------------------------------------

    comparison_text = ""

    if grid_mode != "net_metering":

        net_metering_savings = annual_generation * tariff
        savings_difference = net_metering_savings - annual_savings

        comparison_text = f"""

### 🔎 Comparison with Net Metering

If this system were configured with **net metering**, your estimated annual savings could be approximately:

**₹{net_metering_savings:,.0f} per year**

Under the selected configuration, the usable solar energy is slightly lower, resulting in:

**₹{annual_savings:,.0f} per year**

Difference in annual savings: **₹{savings_difference:,.0f}**

"""

    # -----------------------------------------
    # Electricity Bill without Solar
    # -----------------------------------------

    annual_bill_without_pv = monthly_units * 12 * tariff

    # -----------------------------------------
    # Store Results in State
    # -----------------------------------------

    state["system_cost"] = round(system_cost, 0)
    state["subsidy_amount"] = round(subsidy, 0)
    state["net_system_cost"] = round(net_cost, 0)
    state["annual_savings"] = round(annual_savings, 0)
    state["breakeven_years"] = round(payback, 1)
    state["lifetime_savings"] = round(lifetime_savings, 0)

    # -----------------------------------------
    # Generate Breakeven Chart
    # -----------------------------------------

    chart = generate_breakeven_chart(
        net_cost,
        annual_bill_without_pv
    )

    state["breakeven_chart"] = chart

    # -----------------------------------------
    # Financial Summary Table
    # -----------------------------------------

    summary_table = f"""
### 📊 System Design & Financial Overview

**System Configuration**

{mode_description}

---

| **System Design Summary** | **Financial Analysis** |
|--------------------------|------------------------|
| System Size: {system_kw} kWp | Installation Cost: ₹{system_cost:,.0f} |
| Annual Generation: {annual_generation:,.0f} kWh | Government Subsidy: ₹{subsidy:,.0f} |
| Panels Installed: {state.get("panel_count")} | Net System Cost: ₹{net_cost:,.0f} |
| Inverter: {state.get("inverter_name")} | Annual Savings: ₹{annual_savings:,.0f} |
| Battery: {state.get("battery_name")} | Payback Period: {payback:.1f} years |
| CO₂ Avoided: {state.get("annual_kwh") * 0.82 / 1000:.1f} tonnes | Lifetime Savings: ₹{lifetime_savings:,.0f} |

"""

    message = f"""
{summary_table}

{comparison_text}

Below is a break-even analysis showing how the cost of electricity without solar compares with installing a rooftop solar system.
"""

    state["messages"].append({
        "role": "assistant",
        "content": message.strip()
    })

    return state