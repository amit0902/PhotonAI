import re
from utils.appliance_parser import parse_appliances


# =====================================================
# NAME EXTRACTION
# =====================================================

def extract_name(text):

    text = text.strip()

    patterns = [
        r"my name is (.+)",
        r"i am (.+)",
        r"i'm (.+)",
        r"this is (.+)"
    ]

    text_lower = text.lower()

    for pattern in patterns:

        match = re.search(pattern, text_lower)

        if match:
            name = match.group(1)
            name = re.sub(r"[^a-zA-Z\s]", "", name)
            return name.title()

    # fallback
    return re.sub(r"[^a-zA-Z\s]", "", text).title()

# =====================================================
# GLOBAL PARAMETER EXTRACTION
# =====================================================
def extract_parameters(state, text):

    updated_fields = []
    text_lower = text.lower()

    # -------------------------
    # Monthly Energy
    # -------------------------
    energy_match = re.search(r"(\d+(\.\d+)?)\s*(kwh|units)", text_lower)
    if energy_match:
        state["monthly_units"] = float(energy_match.group(1))
        updated_fields.append("monthly_units")

    # -------------------------
    # Tilt
    # -------------------------
    tilt_match = re.search(r"tilt.*?(\d+(\.\d+)?)", text_lower)
    if tilt_match:
        state["tilt"] = float(tilt_match.group(1))
        updated_fields.append("tilt")

    # -------------------------
    # Azimuth
    # -------------------------
    az_match = re.search(r"(azimuth|direction).*?(\d+(\.\d+)?)", text_lower)
    if az_match:
        state["azimuth"] = float(az_match.group(2))
        updated_fields.append("azimuth")

    # -------------------------
    # City
    # -------------------------
    for city in ["bangalore", "mumbai", "pune"]:
        if city in text_lower:
            state["city"] = city.capitalize()
            updated_fields.append("city")

    return state, updated_fields


# =====================================================
# INPUT NODE
# =====================================================
def input_node(state):

    if not state.get("messages"):
        return state

    last_msg = state["messages"][-1]

    if last_msg["role"] != "user":
        return state

    user_text = last_msg["content"].strip()
    stage = state.get("current_stage")

    # =====================================================
    # GLOBAL PARAMETER OVERRIDE
    # =====================================================
    state, updated_fields = extract_parameters(state, user_text)

    required_fields = ["monthly_units", "city", "tilt", "azimuth"]

    if updated_fields and all(state.get(f) is not None for f in required_fields):

        state["messages"].append({
            "role": "assistant",
            "content": (
                f"I've updated {', '.join(updated_fields)} as requested. "
                "Re-running the solar performance assessment with the updated inputs."
            )
        })

        state["current_stage"] = "energy_assessment"
        return state


    # =====================================================
    # ASK NAME
    # =====================================================
    if stage == "ask_name":

        state["name"] = extract_name(user_text)
        state["current_stage"] = "ask_energy"
        return state


    # =====================================================
    # ASK ENERGY
    # =====================================================
    elif stage == "ask_energy":

        match = re.search(r"\d+(\.\d+)?", user_text)

        if match:
            state["monthly_units"] = float(match.group())
            state["current_stage"] = "ask_city"
        else:
            state["messages"].append({
                "role": "assistant",
                "content": "Please provide your average monthly electricity consumption in kWh."
            })

        return state


    # =====================================================
    # ASK CITY
    # =====================================================
    elif stage == "ask_city":

        text = user_text.lower()

        supported_cities = ["bangalore"]

        for city in supported_cities:
            if city in text:
                state["city"] = city.capitalize()
                state["current_stage"] = "ask_tilt"
                return state

        state["messages"].append({
            "role": "assistant",
            "content": (
                "Sorry, I couldn't recognize the city. "
                "Currently I support Bangalore only. "
            )
        })

        return state


    # =====================================================
    # ASK TILT
    # =====================================================
    elif stage == "ask_tilt":

        match = re.search(r"\d+(\.\d+)?", user_text)

        state["tilt"] = float(match.group()) if match else 0

        state["current_stage"] = "ask_azimuth"
        return state


    # =====================================================
    # ASK AZIMUTH
    # =====================================================
    elif stage == "ask_azimuth":

        match = re.search(r"\d+(\.\d+)?", user_text)

        state["azimuth"] = float(match.group()) if match else 180

        state["current_stage"] = "energy_assessment"
        return state


    # =====================================================
    # POST ENERGY ASSESSMENT REVIEW
    # =====================================================
    elif stage == "post_assessment_review":

        text = user_text.lower()

        if "change" in text or "modify" in text:
            state["current_stage"] = "await_parameter_modification"
            return state

        if any(word in text for word in ["proceed", "yes", "ok", "fine"]):
            state["current_stage"] = "choose_design_path"
            return state

        state["messages"].append({
            "role": "assistant",
            "content": (
                "Would you like to adjust any inputs such as consumption, tilt, "
                "or azimuth before we proceed with the system design?"
            )
        })

        return state


    # =====================================================
    # USER MODIFYING PARAMETERS
    # =====================================================
    elif stage == "await_parameter_modification":

        state["messages"].append({
            "role": "assistant",
            "content": (
                "Please tell me the updated value for consumption, tilt, azimuth, "
                "or city so I can recompute the system."
            )
        })

        return state


    # =====================================================
    # CHOOSE DESIGN PATH
    # =====================================================
    elif stage == "choose_design_path":

        text = user_text.lower().strip()

        if "1" in text:
            state["installation_goal"] = "full_offset"
            state["current_stage"] = "ask_grid_mode"
            return state

        elif "2" in text:
            state["installation_goal"] = "bill_reduction"
            state["current_stage"] = "ask_bill_target"
            return state

        elif "3" in text:
            state["installation_goal"] = "heavy_load"
            state["current_stage"] = "ask_heavy_name"
            return state

        else:
            state["messages"].append({
                "role": "assistant",
                "content": "Please choose 1, 2, or 3 so I can proceed correctly."
            })
            return state


    # =====================================================
    # BILL REDUCTION TARGET
    # =====================================================
    elif stage == "ask_bill_target":

        match = re.search(r"\d+(\.\d+)?", user_text)

        if match:
            state["bill_target_units"] = float(match.group())
            state["current_stage"] = "run_bill_reduction"
        else:
            state["messages"].append({
                "role": "assistant",
                "content": (
                    "Please specify the monthly unit threshold "
                    "you would like to stay below."
                )
            })

        return state


    # =====================================================
    # GRID INTERACTION MODE
    # =====================================================
    elif stage == "ask_grid_mode":

        text = user_text.lower()

        if "1" in text:
            state["grid_mode"] = "net_metering"

        elif "2" in text:
            state["grid_mode"] = "self_consumption"

        elif "3" in text:
            state["grid_mode"] = "backup_priority"

        else:
            state["messages"].append({
                "role": "assistant",
                "content": "Please choose 1, 2 or 3."
            })
            return state

        state["current_stage"] = "run_full_analysis"
        return state


    # =====================================================
    # POST RECOMMENDATION OPTIONS
    # =====================================================
    elif stage == "post_recommendation":

        text = user_text.lower().strip()

        if any(word in text for word in ["ok", "okay", "fine", "thanks", "thank you"]):
            state["messages"].append({
                "role": "assistant",
                "content": (
                    "You're welcome. If you'd like to explore deeper technical "
                    "analysis or refine the design further, just let me know."
                )
            })
            return state

        if "1" in text:
            state["current_stage"] = "run_full_pvlib"
            return state

        elif "2" in text:
            state["current_stage"] = "run_string_sizing"
            return state

        elif "3" in text or "restart" in text:
            state["current_stage"] = "ask_energy"
            return state

        elif "4" in text or "stop" in text:

            state["completed"] = True

            state["messages"].append({
                "role": "assistant",
                "content": "Thank you for using Solar Advisor ☀️"
            })

            return state

        else:
            state["messages"].append({
                "role": "assistant",
                "content": (
                    "If you'd like to proceed further, please select:\n"
                    "1 for detailed PV simulation\n"
                    "2 for string sizing\n"
                    "3 to restart\n"
                    "4 to stop"
                )
            })

            return state


    elif stage == "ask_panel_brand":

        text = user_text.lower()

        if "1" in text:
            state["panel_brand"] = "Tata"

        elif "2" in text:
            state["panel_brand"] = "Waaree"

        elif "3" in text:
            state["panel_brand"] = "Vikram"

        elif "4" in text:
            state["panel_brand"] = "LONGi"

        elif "5" in text:
            state["panel_brand"] = "JA Solar"

        else:
            state["messages"].append({
                "role": "assistant",
                "content": "Please select a valid option."
            })
            return state

        state["current_stage"] = "ask_inverter_brand"
        return state

    elif stage == "ask_inverter_brand":

        text = user_text.lower()

        if "1" in text:
            state["inverter_brand"] = "Microtek"

        elif "2" in text:
            state["inverter_brand"] = "Huawei"

        elif "3" in text:
            state["inverter_brand"] = "SMA"

        elif "4" in text:
            state["inverter_brand"] = "Siemens"

        else:
            state["messages"].append({
                "role": "assistant",
                "content": "Please choose a valid inverter brand."
            })
            return state

        state["current_stage"] = "ask_battery_brand"
        return state

    elif stage == "ask_battery_brand":

        text = user_text.lower()

        if "1" in text:
            state["battery_brand"] = "Tesla"

        elif "2" in text:
            state["battery_brand"] = "LG"

        elif "3" in text:
            state["battery_brand"] = "BYD"

        elif "4" in text:
            state["battery_brand"] = "Exide"

        elif "5" in text:
            state["battery_brand"] = "Amaron"

        else:
            state["messages"].append({
                "role": "assistant",
                "content": "Please choose a valid battery brand."
            })
            return state

        state["current_stage"] = "run_full_analysis"
        return state

    # =====================================================
    # HEAVY APPLIANCE FLOW
    # =====================================================

    elif stage == "ask_heavy_name":

        appliances = parse_appliances(user_text)

        if appliances:

            state.setdefault("heavy_loads", [])

            state["heavy_loads"].extend(appliances)

            state["current_stage"] = "run_heavy_load"

            return state

        # fallback to guided flow
        state.setdefault("heavy_loads", [])

        state["current_appliance"] = {
            "name": user_text.strip(),
            "kw": None,
            "quantity": None,
            "hours": None
        }

        state["current_stage"] = "ask_heavy_kw"

        return state


    elif stage == "ask_heavy_kw":

        match = re.search(r"\d+(\.\d+)?", user_text)

        if match:

            kw = float(match.group())

            state.setdefault("current_appliance", {})

            state["current_appliance"]["kw"] = kw

            state["current_stage"] = "ask_heavy_quantity"

        else:

            state["messages"].append({
                "role": "assistant",
                "content": "Please provide the appliance rated power in kW."
            })

        return state


    elif stage == "ask_heavy_quantity":

        match = re.search(r"\d+", user_text)

        if match:

            qty = int(match.group())

            state.setdefault("current_appliance", {})

            state["current_appliance"]["quantity"] = qty

            state["current_stage"] = "ask_heavy_hours"

        else:

            state["messages"].append({
                "role": "assistant",
                "content": "How many such appliances do you have?"
            })

        return state


    elif stage == "ask_heavy_hours":

        match = re.search(r"\d+(\.\d+)?", user_text)

        if match:

            hours = float(match.group())

            state.setdefault("heavy_loads", [])

            appliance = {
                "name": state.get("current_appliance", {}).get("name"),
                "kw": state.get("current_appliance", {}).get("kw"),
                "quantity": state.get("current_appliance", {}).get("quantity"),
                "hours": hours
            }

            state["heavy_loads"].append(appliance)

            # Reset appliance
            state["current_appliance"] = {}

            state["current_stage"] = "ask_add_more"

        else:

            state["messages"].append({
                "role": "assistant",
                "content": "Please provide the average hours of operation per day."
            })

        return state

    elif stage == "ask_add_more":

        text = user_text.lower().strip()

        if text in ["yes", "y"]:

            state["current_stage"] = "ask_heavy_name"

            return state

        if text in ["no", "n"]:

            state["current_stage"] = "run_heavy_load"

            return state

        state["messages"].append({
            "role": "assistant",
            "content": "Would you like to add another appliance? (yes / no)"
        })

        return state

    # =====================================================
    # SAFETY FALLBACK
    # =====================================================
    if state.get("current_stage") is None:
        state["current_stage"] = "ask_name"

    return state
import re
from utils.appliance_parser import parse_appliances

# =====================================================
# GLOBAL PARAMETER EXTRACTION
# =====================================================
def extract_parameters(state, text):

    updated_fields = []
    text_lower = text.lower()

    # -------------------------
    # Monthly Energy
    # -------------------------
    energy_match = re.search(r"(\d+(\.\d+)?)\s*(kwh|units)", text_lower)
    if energy_match:
        state["monthly_units"] = float(energy_match.group(1))
        updated_fields.append("monthly_units")

    # -------------------------
    # Tilt
    # -------------------------
    tilt_match = re.search(r"tilt.*?(\d+(\.\d+)?)", text_lower)
    if tilt_match:
        state["tilt"] = float(tilt_match.group(1))
        updated_fields.append("tilt")

    # -------------------------
    # Azimuth
    # -------------------------
    az_match = re.search(r"(azimuth|direction).*?(\d+(\.\d+)?)", text_lower)
    if az_match:
        state["azimuth"] = float(az_match.group(2))
        updated_fields.append("azimuth")

    # -------------------------
    # City
    # -------------------------
    for city in ["bangalore", "mumbai", "pune"]:
        if city in text_lower:
            state["city"] = city.capitalize()
            updated_fields.append("city")

    return state, updated_fields


# =====================================================
# INPUT NODE
# =====================================================
def input_node(state):

    if not state.get("messages"):
        return state

    last_msg = state["messages"][-1]

    if last_msg["role"] != "user":
        return state

    user_text = last_msg["content"].strip()
    stage = state.get("current_stage")

    # =====================================================
    # GLOBAL PARAMETER OVERRIDE
    # =====================================================
    state, updated_fields = extract_parameters(state, user_text)

    required_fields = ["monthly_units", "city", "tilt", "azimuth"]

    if updated_fields and all(state.get(f) is not None for f in required_fields):

        state["messages"].append({
            "role": "assistant",
            "content": (
                f"I’ve updated {', '.join(updated_fields)} as requested. "
                "Re-running the solar performance assessment with the updated inputs."
            )
        })

        state["current_stage"] = "energy_assessment"
        return state


    # =====================================================
    # ASK NAME
    # =====================================================
    if stage == "ask_name":

        state["name"] = user_text
        state["current_stage"] = "ask_energy"
        return state


    # =====================================================
    # ASK ENERGY
    # =====================================================
    elif stage == "ask_energy":

        match = re.search(r"\d+(\.\d+)?", user_text)

        if match:
            state["monthly_units"] = float(match.group())
            state["current_stage"] = "ask_city"
        else:
            state["messages"].append({
                "role": "assistant",
                "content": "Please provide your average monthly electricity consumption in kWh."
            })

        return state


    # =====================================================
    # ASK CITY
    # =====================================================
    elif stage == "ask_city":

        text = user_text.lower()

        supported_cities = ["bangalore"]

        for city in supported_cities:
            if city in text:
                state["city"] = city.capitalize()
                state["current_stage"] = "ask_tilt"
                return state

        state["messages"].append({
            "role": "assistant",
            "content": (
                "Sorry, I couldn't recognize the city. "
                "Currently I support Bangalore only. "
            )
        })

        return state


    # =====================================================
    # ASK TILT
    # =====================================================
    elif stage == "ask_tilt":

        match = re.search(r"\d+(\.\d+)?", user_text)

        state["tilt"] = float(match.group()) if match else 0

        state["current_stage"] = "ask_azimuth"
        return state


    # =====================================================
    # ASK AZIMUTH
    # =====================================================
    elif stage == "ask_azimuth":

        match = re.search(r"\d+(\.\d+)?", user_text)

        state["azimuth"] = float(match.group()) if match else 180

        state["current_stage"] = "energy_assessment"
        return state


    # =====================================================
    # POST ENERGY ASSESSMENT REVIEW
    # =====================================================
    elif stage == "post_assessment_review":

        text = user_text.lower()

        if "change" in text or "modify" in text:
            state["current_stage"] = "await_parameter_modification"
            return state

        if any(word in text for word in ["proceed", "yes", "ok", "fine"]):
            state["current_stage"] = "choose_design_path"
            return state

        state["messages"].append({
            "role": "assistant",
            "content": (
                "Would you like to adjust any inputs such as consumption, tilt, "
                "or azimuth before we proceed with the system design?"
            )
        })

        return state


    # =====================================================
    # USER MODIFYING PARAMETERS
    # =====================================================
    elif stage == "await_parameter_modification":

        state["messages"].append({
            "role": "assistant",
            "content": (
                "Please tell me the updated value for consumption, tilt, azimuth, "
                "or city so I can recompute the system."
            )
        })

        return state


    # =====================================================
    # CHOOSE DESIGN PATH
    # =====================================================
    elif stage == "choose_design_path":

        text = user_text.lower().strip()

        if "1" in text:
            state["installation_goal"] = "full_offset"
            state["current_stage"] = "ask_grid_mode"
            return state

        elif "2" in text:
            state["installation_goal"] = "bill_reduction"
            state["current_stage"] = "ask_bill_target"
            return state

        elif "3" in text:
            state["installation_goal"] = "heavy_load"
            state["current_stage"] = "ask_heavy_name"
            return state

        else:
            state["messages"].append({
                "role": "assistant",
                "content": "Please choose 1, 2, or 3 so I can proceed correctly."
            })
            return state


    # =====================================================
    # BILL REDUCTION TARGET
    # =====================================================
    elif stage == "ask_bill_target":

        match = re.search(r"\d+(\.\d+)?", user_text)

        if match:
            state["bill_target_units"] = float(match.group())
            state["current_stage"] = "run_bill_reduction"
        else:
            state["messages"].append({
                "role": "assistant",
                "content": (
                    "Please specify the monthly unit threshold "
                    "you would like to stay below."
                )
            })

        return state


    # =====================================================
    # GRID INTERACTION MODE
    # =====================================================
    elif stage == "ask_grid_mode":

        text = user_text.lower()

        if "1" in text:
            state["grid_mode"] = "net_metering"

        elif "2" in text:
            state["grid_mode"] = "self_consumption"

        elif "3" in text:
            state["grid_mode"] = "backup_priority"

        else:
            state["messages"].append({
                "role": "assistant",
                "content": "Please choose 1, 2 or 3."
            })
            return state

        state["current_stage"] = "run_full_analysis"
        return state


    # =====================================================
    # POST RECOMMENDATION OPTIONS
    # =====================================================
    elif stage == "post_recommendation":

        text = user_text.lower().strip()

        if any(word in text for word in ["ok", "okay", "fine", "thanks", "thank you"]):
            state["messages"].append({
                "role": "assistant",
                "content": (
                    "You're welcome. If you'd like to explore deeper technical "
                    "analysis or refine the design further, just let me know."
                )
            })
            return state

        if "1" in text:
            state["current_stage"] = "run_full_pvlib"
            return state

        elif "2" in text:
            state["current_stage"] = "run_string_sizing"
            return state

        elif "3" in text or "restart" in text:
            state["current_stage"] = "ask_energy"
            return state

        elif "4" in text or "stop" in text:

            state["completed"] = True

            state["messages"].append({
                "role": "assistant",
                "content": "Thank you for using Solar Advisor ☀️"
            })

            return state

        else:
            state["messages"].append({
                "role": "assistant",
                "content": (
                    "If you'd like to proceed further, please select:\n"
                    "1 for detailed PV simulation\n"
                    "2 for string sizing\n"
                    "3 to restart\n"
                    "4 to stop"
                )
            })

            return state


    elif stage == "ask_panel_brand":

        text = user_text.lower()

        if "1" in text:
            state["panel_brand"] = "Tata"

        elif "2" in text:
            state["panel_brand"] = "Waaree"

        elif "3" in text:
            state["panel_brand"] = "Vikram"

        elif "4" in text:
            state["panel_brand"] = "LONGi"

        elif "5" in text:
            state["panel_brand"] = "JA Solar"

        else:
            state["messages"].append({
                "role": "assistant",
                "content": "Please select a valid option."
            })
            return state

        state["current_stage"] = "ask_inverter_brand"
        return state

    elif stage == "ask_inverter_brand":

        text = user_text.lower()

        if "1" in text:
            state["inverter_brand"] = "Microtek"

        elif "2" in text:
            state["inverter_brand"] = "Huawei"

        elif "3" in text:
            state["inverter_brand"] = "SMA"

        elif "4" in text:
            state["inverter_brand"] = "Siemens"

        else:
            state["messages"].append({
                "role": "assistant",
                "content": "Please choose a valid inverter brand."
            })
            return state

        state["current_stage"] = "ask_battery_brand"
        return state

    elif stage == "ask_battery_brand":

        text = user_text.lower()

        if "1" in text:
            state["battery_brand"] = "Tesla"

        elif "2" in text:
            state["battery_brand"] = "LG"

        elif "3" in text:
            state["battery_brand"] = "BYD"

        elif "4" in text:
            state["battery_brand"] = "Exide"

        elif "5" in text:
            state["battery_brand"] = "Amaron"

        else:
            state["messages"].append({
                "role": "assistant",
                "content": "Please choose a valid battery brand."
            })
            return state

        state["current_stage"] = "run_full_analysis"
        return state

    # =====================================================
    # HEAVY APPLIANCE FLOW
    # =====================================================

    elif stage == "ask_heavy_name":

        appliances = parse_appliances(user_text)

        if appliances:

            state.setdefault("heavy_loads", [])

            state["heavy_loads"].extend(appliances)

            state["current_stage"] = "run_heavy_load"

            return state

        # fallback to guided flow
        state.setdefault("heavy_loads", [])

        state["current_appliance"] = {
            "name": user_text.strip(),
            "kw": None,
            "quantity": None,
            "hours": None
        }

        state["current_stage"] = "ask_heavy_kw"

        return state


    elif stage == "ask_heavy_kw":

        match = re.search(r"\d+(\.\d+)?", user_text)

        if match:

            kw = float(match.group())

            state.setdefault("current_appliance", {})

            state["current_appliance"]["kw"] = kw

            state["current_stage"] = "ask_heavy_quantity"

        else:

            state["messages"].append({
                "role": "assistant",
                "content": "Please provide the appliance rated power in kW."
            })

        return state


    elif stage == "ask_heavy_quantity":

        match = re.search(r"\d+", user_text)

        if match:

            qty = int(match.group())

            state.setdefault("current_appliance", {})

            state["current_appliance"]["quantity"] = qty

            state["current_stage"] = "ask_heavy_hours"

        else:

            state["messages"].append({
                "role": "assistant",
                "content": "How many such appliances do you have?"
            })

        return state


    elif stage == "ask_heavy_hours":

        match = re.search(r"\d+(\.\d+)?", user_text)

        if match:

            hours = float(match.group())

            state.setdefault("heavy_loads", [])

            appliance = {
                "name": state.get("current_appliance", {}).get("name"),
                "kw": state.get("current_appliance", {}).get("kw"),
                "quantity": state.get("current_appliance", {}).get("quantity"),
                "hours": hours
            }

            state["heavy_loads"].append(appliance)

            # Reset appliance
            state["current_appliance"] = {}

            state["current_stage"] = "ask_add_more"

        else:

            state["messages"].append({
                "role": "assistant",
                "content": "Please provide the average hours of operation per day."
            })

        return state

    elif stage == "ask_add_more":

        text = user_text.lower().strip()

        if text in ["yes", "y"]:

            state["current_stage"] = "ask_heavy_name"

            return state

        if text in ["no", "n"]:

            state["current_stage"] = "run_heavy_load"

            return state

        state["messages"].append({
            "role": "assistant",
            "content": "Would you like to add another appliance? (yes / no)"
        })

        return state

    # =====================================================
    # SAFETY FALLBACK
    # =====================================================
    if state.get("current_stage") is None:
        state["current_stage"] = "ask_name"

    return state