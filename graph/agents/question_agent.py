from langchain_core.messages import HumanMessage


def question_agent(state, llm):

    stage = state["current_stage"]
<<<<<<< HEAD

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
=======
    name = state.get("name")

    stage_questions = {
        "ask_energy": "What is your average monthly electricity consumption in kWh?",
        "ask_city": "Which city is your rooftop located in?",
        "ask_tilt": "What is the tilt angle of your roof? (Enter 0 if the roof is flat)",
        "ask_azimuth": "What is the azimuth angle of your roof? (180° means south-facing)",
        "ask_goal": "What is your primary goal for installing solar?",
        "ask_bill_target": "What monthly electricity consumption would you like to reach after installing solar?",
        "ask_heavy_name": "Which appliance would you like to power using solar?",
        "ask_heavy_kw": "What is the rated power of this appliance in kW?",
        "ask_heavy_quantity": "How many such appliances do you have?",
        "ask_heavy_hours": "On average, how many hours per day does it operate?",
        "ask_add_more": "Would you like to add another appliance?"
    }

    # ------------------------------
    # FIRST QUESTION (NO LLM)
    # ------------------------------

    if stage == "ask_name":

        message = """
Hello! I'm **PhotonAI**, your intelligent rooftop solar advisor.

To begin the assessment, may I know your name?
"""

        state["messages"].append({
            "role": "assistant",
            "content": message.strip()
        })

        return state

    # ------------------------------
    # OTHER QUESTIONS
    # ------------------------------

    question = stage_questions.get(stage)

    if not question:
        return state

    # Personalize conversation
    if name:
        message = f"{name}, {question}"
    else:
        message = question

    state["messages"].append({
        "role": "assistant",
        "content": message
>>>>>>> 36c2420 (Modified version of PhotonAI)
    })

    return state