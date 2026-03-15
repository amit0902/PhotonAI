from langchain_core.messages import HumanMessage
from services.pvlib_service import simulate_pv
from services.weather_service import load_nrel_weather
from services.carbon_service import calculate_carbon_offset
import pandas as pd


def pv_agent(state, llm):

    state["messages"].append({
        "role": "assistant",
        "content": "🔧 Running detailed PVlib simulation using historical irradiance data..."
    })

    # -----------------------------------------
    # 1️⃣ Load Weather
    # -----------------------------------------

    weather = load_nrel_weather(
        "bangalore_nsrdb_2016_2020.csv",
        tz="Asia/Kolkata"
    )

    # -----------------------------------------
    # 2️⃣ Run Annual Simulation
    # -----------------------------------------

    annual_energy = simulate_pv(
        city=state["city"],
        tilt=state["tilt"],
        azimuth=state["azimuth"],
        weather=weather,
        system_kw=state["system_kw"]
    )

    annual_energy = round(annual_energy)

    # -----------------------------------------
    # 3️⃣ Monthly Breakdown (Simple Aggregation)
    # -----------------------------------------

    # If simulate_pv returns hourly series, aggregate:
    if isinstance(annual_energy, pd.Series):
        monthly = annual_energy.resample("M").sum()
        monthly_dict = monthly.round().to_dict()
        annual_energy = round(monthly.sum())
    else:
        # fallback if simulate_pv returns scalar
        monthly_dict = "Monthly breakdown unavailable in current model."

    # -----------------------------------------
    # 4️⃣ Derived Metrics
    # -----------------------------------------

    specific_yield = round(annual_energy / state["system_kw"], 2)
    performance_ratio = 0.75  # placeholder engineering assumption
    carbon = calculate_carbon_offset(annual_energy)

    state["annual_kwh"] = annual_energy

    # -----------------------------------------
    # 5️⃣ Professional Advisory Output
    # -----------------------------------------

    prompt = f"""
You are a senior solar PV design engineer.

Provide a technical but clear simulation breakdown.

Include:

• Annual generation summary
• Seasonal/monthly generation behavior
• Specific yield (kWh per kWp)
• Performance ratio explanation
• Carbon impact insight

Tone: professional and engineering-focused.
Limit to 5 short sections.

City: {state['city']}
Tilt: {state['tilt']}°
Azimuth: {state['azimuth']}°
System Size: {state['system_kw']} kWp

Annual Generation: {annual_energy} kWh
Specific Yield: {specific_yield} kWh/kWp
Performance Ratio (assumed): {performance_ratio}
Monthly Generation: {monthly_dict}
Carbon Offset: {carbon}
"""

    response = llm.invoke([HumanMessage(content=prompt)])

    state["messages"].append({
        "role": "assistant",
        "content": response.content
    })

    state["current_stage"] = "post_recommendation"

    return state