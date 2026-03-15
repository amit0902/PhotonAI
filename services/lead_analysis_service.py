def analyze_lead(lead):

    system_kw = lead["system_kw"]
    tilt = lead.get("tilt", 0)
    estimated_price = lead["estimated_price"]

    # -----------------------------------
    # Estimate margin
    # -----------------------------------

    installation_cost = system_kw * 42000
    margin = estimated_price - installation_cost
    margin_percent = round((margin / estimated_price) * 100, 1)

    # -----------------------------------
    # Priority logic
    # -----------------------------------

    if system_kw >= 4:
        priority = "HIGH"
    elif system_kw >= 2:
        priority = "MEDIUM"
    else:
        priority = "LOW"

    # -----------------------------------
    # Installation complexity
    # -----------------------------------

    notes = []

    if tilt == 0:
        notes.append("Flat roof – mounting structure required")

    if system_kw >= 3:
        notes.append("Good revenue opportunity")

    if margin_percent < 15:
        notes.append("Low margin project")

    return {
        "margin_percent": margin_percent,
        "priority": priority,
        "notes": notes
    }
