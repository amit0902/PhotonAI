from langchain_core.messages import HumanMessage


def energy_assessment_agent(state, llm):

    annual = state["monthly_units"] * 12
    state["annual_consumption"] = annual

    prompt = f"""
You are a professional solar energy consultant.

Provide an Energy Demand Assessment only.
Do NOT size the solar system yet.

Use EXACTLY 3 bullet points.

Each bullet must be on a new line.

Format:

• Annual Energy Requirement: sentence one. sentence two.
• Solar Feasibility in the City: sentence one. sentence two.
• Roof Orientation Suitability: sentence one. sentence two.

Tone: professional and consultative.
Limit to 3 bullet points having 2 sentences each.
"""
    summary_table=f"""
### 📊 Energy Profile Summary

| Parameter | Value |
|----------|------|
| Customer | {state['name']} |
| City | {state['city']} |
| Monthly Consumption | {state['monthly_units']} kWh |
| Annual Consumption | {annual} kWh |
| Roof Tilt | {state['tilt']}° |
| Azimuth | {state['azimuth']}° |
"""

    response = llm.invoke([HumanMessage(content=prompt)])

    state["messages"].append({
        "role": "assistant",
        "content": response.content + summary_table
    })

    return state