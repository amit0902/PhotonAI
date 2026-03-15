from langchain_core.messages import HumanMessage


def question_agent(state, llm):

    stage = state["current_stage"]
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
    })

    return state