from typing import TypedDict, List, Optional, Dict


class Message(TypedDict):
    role: str
    content: str


class SolarState(TypedDict, total=False):

    # --------------------------------
    # Conversation
    # --------------------------------
    messages: List[Message]
    current_stage: str
    completed: bool

    # --------------------------------
    # User Inputs
    # --------------------------------
    name: Optional[str]
    monthly_units: Optional[float]
    city: Optional[str]
    tilt: Optional[float]
    azimuth: Optional[float]
    
    # Equipment Preferences
    panel_brand: Optional[str]
    inverter_brand: Optional[str]
    battery_brand: Optional[str]

    # --------------------------------
    # Energy Assessment
    # --------------------------------
    annual_consumption: Optional[float]
    target_energy: Optional[float]
    installation_goal: Optional[str]

    # --------------------------------
    # Heavy Load Inputs
    # --------------------------------
    heavy_loads: Optional[List[Dict]]
    heavy_total_kw: Optional[float]

    # --------------------------------
    # Bill Reduction Mode
    # --------------------------------
    bill_target_units: Optional[float]

    # --------------------------------
    # System Design Results
    # --------------------------------
    system_kw: Optional[float]
    annual_kwh: Optional[float]
    daily_load: Optional[float]

    # --------------------------------
    # Grid Interaction
    # --------------------------------
    grid_mode: Optional[str]

    # --------------------------------
    # PV Equipment
    # --------------------------------
    panel_name: Optional[str]
    panel_power: Optional[float]
    panel_count: Optional[int]

    # --------------------------------
    # PV Array Layout
    # --------------------------------
    series_strings: Optional[int]
    parallel_strings: Optional[int]

    # --------------------------------
    # Inverter
    # --------------------------------
    inverter_name: Optional[str]
    inverter_kw: Optional[float]

    # --------------------------------
    # Battery
    # --------------------------------
    battery_name: Optional[str]
    battery_kwh: Optional[float]
    battery_backup_hours: Optional[float]

    system_cost: Optional[float]
    annual_savings: Optional[float]
    payback_years: Optional[float]
    lifetime_savings: Optional[float]

    subsidy_amount: Optional[float]
    net_system_cost: Optional[float]
    breakeven_years: Optional[float]

    breakeven_chart: Optional[object]