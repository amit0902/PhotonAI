from langchain_core.messages import HumanMessage


def question_agent(state, llm):

    stage = state["current_stage"]

    stage_instructions = {
        "ask_name": "Introduce yourself briefly and ask the user for their name.",
        "ask_energy": "Ask the user for their average monthly electricity consumption in kWh.",
        "ask_city": "Ask which city the rooftop is located in.",
        "ask_tilt": "Ask for roof tilt angle. Mention 0 if flat.",
        "ask_azimuth": "Ask for roof azimuth angle. Mention 180° is south-facing.",
        "ask_goal": "Ask the user's primary objective for installing solar. Offer the four options naturally.",
        "ask_bill_target": (
            "Ask the user what monthly electricity consumption target they would "
            "like to reach after installing solar. Mention their current monthly "
            "consumption and ask for the desired units per month."
        ),
        "ask_heavy_name": "Ask the appliance name.",
        "ask_heavy_kw": "Ask the appliance rated power in kW.",
        "ask_heavy_quantity": "Ask how many such appliances.",
        "ask_heavy_hours": "Ask average daily operating hours.",
        "ask_add_more": "Ask if the user wants to add another appliance."
    }

    instruction = stage_instructions.get(stage)

    # Safety guard (prevents LLM improvising wrong stage)
    if not instruction:
        return state

    prompt = f"""
You are a senior solar energy consultant having a natural, human conversation.

Guidelines:
- Sound warm, professional and intelligent.
- Do NOT repeat known information unnecessarily.
- Ask only ONE clear question.
- Avoid robotic structured phrasing.
- Keep it concise.

Context:
Name: {state.get("name")}
City: {state.get("city")}
Monthly Consumption: {state.get("monthly_units")}

Your task:
{instruction}
"""

    response = llm.invoke([HumanMessage(content=prompt)])

    state["messages"].append({
        "role": "assistant",
        "content": response.content.strip()
    })

    return state