# ---------------------------------------------------
# PV MODULE DATABASE
# ---------------------------------------------------

PANELS = [

    # Global Tier-1 Panels
    {"name": "LONGi LR5-72HPH 550M", "watt": 550},
    {"name": "JA Solar JAM72S30 545W", "watt": 545},
    {"name": "Trina Vertex S 540W", "watt": 540},

    # Indian Manufacturers
    {"name": "Tata Power Solar MonoPERC 540W", "watt": 540},
    {"name": "Vikram Solar Somera 545W", "watt": 545},
    {"name": "Waaree Bi-55 535W", "watt": 535},
    {"name": "Mahindra Susten MonoPERC 540W", "watt": 540},
]


# ---------------------------------------------------
# INVERTER DATABASE
# ---------------------------------------------------

INVERTERS = [

    # Global Brands
    {"name": "Huawei SUN2000 6kW Hybrid", "kw": 6},
    {"name": "SMA Sunny Boy 5.0", "kw": 5},

    # Indian Brands
    {"name": "Microtek Solar Hybrid PCU 5kW", "kw": 5},
    {"name": "Microtek Solar PCU 3kW", "kw": 3},

    # Industrial
    {"name": "Siemens SINVERT PVM 5kW", "kw": 5},
]


# ---------------------------------------------------
# BATTERY DATABASE
# ---------------------------------------------------

BATTERIES = [

    {"name": "Tesla Powerwall", "kwh": 13.5},
    {"name": "LG Chem RESU", "kwh": 10},
    {"name": "BYD Battery Box", "kwh": 7},

    # Indian Batteries
    {"name": "Exide Solar Lithium Battery", "kwh": 5},
    {"name": "Amaron Solar Battery", "kwh": 7},
    {"name": "Microtek Solar Battery", "kwh": 5},
]


# ---------------------------------------------------
# PANEL SELECTION
# ---------------------------------------------------

def select_panel(system_kw, brand=None):

    # Filter by brand if provided
    if brand:
        filtered = [
            panel for panel in PANELS
            if brand.lower() in panel["name"].lower()
        ]

        if filtered:
            return max(filtered, key=lambda x: x["watt"])

    # fallback
    return max(PANELS, key=lambda x: x["watt"])


# ---------------------------------------------------
# INVERTER SELECTION
# ---------------------------------------------------

def select_inverter(required_kw, brand=None):

    candidates = INVERTERS

    if brand:
        filtered = [
            inv for inv in INVERTERS
            if brand.lower() in inv["name"].lower()
        ]

        if filtered:
            candidates = filtered

    for inverter in candidates:
        if inverter["kw"] >= required_kw:
            return inverter

    return candidates[-1]


# ---------------------------------------------------
# BATTERY SELECTION
# ---------------------------------------------------

def select_battery(required_kwh, brand=None):

    candidates = BATTERIES

    if brand:
        filtered = [
            bat for bat in BATTERIES
            if brand.lower() in bat["name"].lower()
        ]

        if filtered:
            candidates = filtered

    for battery in candidates:
        if battery["kwh"] >= required_kwh:
            return battery

    return candidates[-1]