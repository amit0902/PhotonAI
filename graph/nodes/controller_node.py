from graph.agents.energy_assessment_agent import energy_assessment_agent
from graph.agents.full_analysis_agent import full_analysis_agent
from graph.agents.string_sizing_agent import run_string_sizing
from graph.agents.full_pvlib_agent import pv_agent
from graph.agents.heavy_load_agent import heavy_load_agent
from graph.agents.question_agent import question_agent
from graph.agents.bill_reduction_agent import bill_reduction_agent
from graph.agents.financial_agent import financial_agent


def controller_node(state, llm):

    while True:

        stage = state.get("current_stage")

        # ======================================================
        # QUESTION STAGES (Handled by LLM)
        # ======================================================
        if stage in [
            "ask_name",
            "ask_energy",
            "ask_city",
            "ask_tilt",
            "ask_azimuth",
            "ask_panel_brand",
            "ask_inverter_brand",
            "ask_battery_brand",
        ]:

            state = question_agent(state, llm)
            break


        # ======================================================
        # ENERGY ASSESSMENT
        # ======================================================
        elif stage == "energy_assessment":

            state = energy_assessment_agent(state, llm)

            state["current_stage"] = "post_assessment_review"
            continue


        # ======================================================
        # POST ENERGY REVIEW
        # ======================================================
        elif stage == "post_assessment_review":

            state["messages"].append({
                "role": "assistant",
                "content": (
                    "Would you like to adjust any inputs such as consumption, "
                    "tilt, or azimuth before we proceed with the solar system design?"
                )
            })

            break


        # ======================================================
        # USER MODIFYING PARAMETERS
        # ======================================================
        elif stage == "await_parameter_modification":

            state["messages"].append({
                "role": "assistant",
                "content": (
                    "Sure. Please tell me which parameter you'd like to update:\n\n"
                    "• Monthly consumption (kWh)\n"
                    "• City\n"
                    "• Tilt angle\n"
                    "• Azimuth angle\n\n"
                    "You can simply type the new value."
                )
            })

            break


        # ======================================================
        # DESIGN PATH SELECTION
        # ======================================================
        elif stage == "choose_design_path":

            state["messages"].append({
                "role": "assistant",
                "content": (
                    "Now that we've assessed your energy profile, "
                    "how would you like to proceed?\n\n"
                    "1️⃣ Design a system to fully offset your annual consumption\n"
                    "2️⃣ Design a system to strategically reduce your electricity bill\n"
                    "3️⃣ Design a system to power specific heavy appliances\n\n"
                    "Please select 1, 2, or 3."
                )
            })

            break


        # ======================================================
        # HEAVY APPLIANCE QUESTIONS
        # ======================================================
        elif stage == "ask_heavy_name":

            state["messages"].append({
                "role": "assistant",
                "content": (
                    "Which appliances would you like to power using solar?\n\n"
                    "You can enter them like this:\n\n"
                    "1 fridge 0.2kW 24h\n"
                    "2 AC 1.5kW 5h\n\n"
                    "Or we can enter them step-by-step."
                )
            })

            break


        elif stage == "ask_heavy_kw":

            state["messages"].append({
                "role": "assistant",
                "content": "What is the rated power of this appliance in kW? (example: 1.5)"
            })

            break


        elif stage == "ask_heavy_quantity":

            state["messages"].append({
                "role": "assistant",
                "content": "How many such appliances do you have?"
            })

            break


        elif stage == "ask_heavy_hours":

            state["messages"].append({
                "role": "assistant",
                "content": "On average, how many hours per day does it operate?"
            })

            break


        elif stage == "ask_add_more":

            state["messages"].append({
                "role": "assistant",
                "content": "Would you like to add another appliance? (yes/no)"
            })

            break


        # ======================================================
        # HEAVY LOAD PROCESSING
        # ======================================================
        elif stage == "run_heavy_load":

            state = heavy_load_agent(state)

            state["current_stage"] = "run_full_analysis"
            continue


        # ======================================================
        # GRID MODE SELECTION
        # ======================================================
        elif stage == "ask_grid_mode":

            state["messages"].append({
                "role": "assistant",
                "content": (
                    "To complete the system design, how would you like your solar system "
                    "to interact with the utility grid?\n\n"
                    "1️⃣ Grid-connected with net metering (export excess energy)\n"
                    "2️⃣ Grid-connected without exporting energy\n"
                    "3️⃣ Backup-focused system prioritizing battery storage\n\n"
                    "Please select 1, 2, or 3."
                )
            })

            break


        # ======================================================
        # BILL REDUCTION TARGET
        # ======================================================
        elif stage == "ask_bill_target":

            state["messages"].append({
                "role": "assistant",
                "content": (
                    "To design a solar system that reduces your electricity bill, "
                    "please tell me the maximum number of units per month you would "
                    "like your electricity consumption to stay below.\n\n"
                    "For example: 200 units."
                )
            })

            break


        elif stage == "run_bill_reduction":

            state = bill_reduction_agent(state, llm)

            state["current_stage"] = "run_full_analysis"
            continue


        # ======================================================
        # FULL SYSTEM DESIGN
        # ======================================================
        elif stage == "run_full_analysis":

            state = full_analysis_agent(state, llm)

            state["current_stage"] = "run_financial_analysis"
            continue


        elif stage == "run_financial_analysis":

            state = financial_agent(state)

            state["current_stage"] = "post_recommendation"
            break


        # ======================================================
        # POST DESIGN OPTIONS
        # ======================================================
        elif stage == "post_recommendation":

            state["messages"].append({
                "role": "assistant",
                "content": (
                    "Would you like to explore further technical depth?\n\n"
                    "1️⃣ Detailed PVlib simulation\n"
                    "2️⃣ String sizing (series × parallel)\n"
                    "3️⃣ Restart analysis with new parameters\n"
                    "4️⃣ Stop"
                )
            })

            break


        # ======================================================
        # ADVANCED OPTIONS
        # ======================================================
        elif stage == "run_full_pvlib":

            state = pv_agent(state, llm)

            state["current_stage"] = "post_recommendation"
            continue


        elif stage == "run_string_sizing":

            state = run_string_sizing(state)

            state["current_stage"] = "post_recommendation"
            continue


        # ======================================================
        # SAFETY EXIT
        # ======================================================
        else:
            break

    return state