from langchain_core.messages import HumanMessage

from services.pvlib_service import simulate_pv
from services.weather_service import load_nrel_weather
from services.location_service import get_location_from_city
from services.carbon_service import calculate_carbon_offset

from services.equipment_database import (
    select_panel,
    select_inverter,
    select_battery
)


def full_analysis_agent(state, llm):

    # -----------------------------------------
    # 1️⃣ Load Location + Weather
    # -----------------------------------------

    location = get_location_from_city(state["city"])

    weather = load_nrel_weather(
        "bangalore_nsrdb_2016_2020.csv",
        tz=location["timezone"]
    )

    # -----------------------------------------
    # 2️⃣ Determine Target Energy
    # -----------------------------------------

    if state.get("target_energy"):
        annual_target = state["target_energy"]
    else:
        annual_target = state["monthly_units"] * 12
        state["target_energy"] = annual_target

    tilt = state.get("tilt", 0)
    azimuth = state.get("azimuth", 180)

    grid_mode = state.get("grid_mode", "net_metering")

    # -----------------------------------------
    # 3️⃣ PVlib Yield Simulation
    # -----------------------------------------

    generation_per_kw = simulate_pv(
        city=state["city"],
        tilt=tilt,
        azimuth=azimuth,
        weather=weather,
        system_kw=1
    )

    system_kw = round(annual_target / generation_per_kw, 1)

    # Adjust sizing based on grid mode
    if grid_mode == "self_consumption":
        # Avoid oversizing since export is not allowed
        system_kw = round(system_kw * 0.9, 1)

    estimated_generation = simulate_pv(
        city=state["city"],
        tilt=tilt,
        azimuth=azimuth,
        weather=weather,
        system_kw=system_kw
    )

    estimated_generation = round(estimated_generation)

    state["system_kw"] = system_kw
    state["annual_kwh"] = estimated_generation

    # -----------------------------------------
    # 4️⃣ Panel Selection
    # -----------------------------------------

    panel = select_panel(system_kw, state.get("panel_brand"))

    panel_watt = panel["watt"]
    panel_kw = panel_watt / 1000

    panel_count = max(1, int(round(system_kw / panel_kw)))

    state["panel_name"] = panel["name"]
    state["panel_count"] = panel_count

    # -----------------------------------------
    # 5️⃣ String Configuration
    # -----------------------------------------

    series = 12
    parallel = max(1, round(panel_count / series))

    state["series"] = series
    state["parallel"] = parallel

    # -----------------------------------------
    # 6️⃣ Inverter Sizing
    # -----------------------------------------

    inverter_kw = round(system_kw * 0.8, 1)

    inverter = select_inverter(inverter_kw, state.get("inverter_brand"))

    state["inverter_name"] = inverter["name"]
    state["inverter_kw"] = inverter["kw"]

    # -----------------------------------------
    # 7️⃣ Daily Load
    # -----------------------------------------

    daily_load = annual_target / 365
    state["daily_load"] = round(daily_load, 2)

    # -----------------------------------------
    # 8️⃣ Battery Sizing (ONLY for backup systems)
    # -----------------------------------------

    battery_name = "Not included"
    battery_kwh = 0

    if grid_mode == "backup_priority":

        backup_hours = 6

        battery_kwh = (
            daily_load * (backup_hours / 24)
        ) / (0.8 * 0.9)

        battery = select_battery(battery_kwh, state.get("battery_brand"))

        battery_name = battery["name"]
        battery_kwh = battery["kwh"]

    state["battery_name"] = battery_name
    state["battery_kwh"] = battery_kwh

    # -----------------------------------------
    # 9️⃣ Carbon Offset
    # -----------------------------------------

    carbon = calculate_carbon_offset(state["annual_kwh"])

    # -----------------------------------------
    # 🔟 Explain Grid Mode
    # -----------------------------------------

    grid_mode_description = {
        "net_metering": "Grid-connected solar system with **net metering**, where excess solar energy is exported to the grid for credits.",
        "self_consumption": "Grid-connected solar system configured for **self-consumption**, where solar power is primarily used by the home without exporting excess energy.",
        "backup_priority": "Hybrid solar system designed for **battery-backed power**, prioritizing energy availability during grid outages."
    }

    system_mode_text = grid_mode_description.get(grid_mode)

    # -----------------------------------------
    # 1️⃣1️⃣ LLM Engineering Report
    # -----------------------------------------

    prompt = f"""
You are a senior solar PV engineer preparing a solar feasibility report.

IMPORTANT RULES:
- Do NOT invent new engineering metrics.
- Only explain the values provided.
- Do NOT assume roof area or system efficiency.
- Keep explanations clear and professional.

System Configuration Mode
{system_mode_text}

Provide 5 short sections:

1. Energy Demand Assessment
2. Solar Resource Context
3. System Sizing Logic
4. Expected Annual Performance
5. Environmental Impact

Customer Profile
Name: {state['name']}
City: {state['city']}
Monthly Consumption: {state['monthly_units']} kWh
Annual Consumption: {state['annual_consumption']} kWh

Solar Inputs
Tilt: {tilt}°
Azimuth: {azimuth}°
Modeled Yield per kWp: {round(generation_per_kw,2)} kWh/year

System Design
Recommended Capacity: {system_kw} kWp
Estimated Generation: {estimated_generation} kWh/year

Environmental Impact
Annual CO2 avoided: {carbon['tonnes']} tonnes
Equivalent trees planted: {carbon['trees']}
"""

    response = llm.invoke([HumanMessage(content=prompt)])

    state["messages"].append({
        "role": "assistant",
        "content": response.content
    })

    return state