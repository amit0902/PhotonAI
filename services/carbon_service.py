def calculate_carbon_offset(annual_kwh):

    # India grid emission factor (approx)
    emission_factor = 0.82  # kg CO2 per kWh

    avoided_kg = annual_kwh * emission_factor
    avoided_tonnes = avoided_kg / 1000

    # Optional relatable metrics
    trees_equivalent = avoided_kg / 21  # avg 21kg CO2 per tree/year

    return {
        "kg": round(avoided_kg, 0),
        "tonnes": round(avoided_tonnes, 2),
        "trees": round(trees_equivalent, 0)
    }