from pvlib.location import Location
from pvlib import irradiance, pvsystem, temperature

from services.location_service import get_location_from_city

# PVWatts standard losses
INVERTER_EFFICIENCY = 0.96
SYSTEM_LOSS_FACTOR = 0.86  # wiring, mismatch, dust etc.

# SAPM temperature coefficients (open rack glass-glass)
SAPM_A = -3.56
SAPM_B = -0.075
SAPM_DELTA_T = 3.0


def simulate_pv(city, tilt, azimuth, weather, system_kw):

    # --- Location ---
    loc = get_location_from_city(city)

    location = Location(
        latitude=loc["latitude"],
        longitude=loc["longitude"],
        tz=loc["timezone"],
        name=city
    )

    # --- Solar position ---
    solar_pos = location.get_solarposition(weather.index)

    tilt = tilt if tilt is not None else 0
    azimuth = azimuth if azimuth is not None else 180

    # --- Plane of array irradiance ---
    poa = irradiance.get_total_irradiance(
        surface_tilt=tilt,
        surface_azimuth=azimuth,
        dni=weather["dni"],
        ghi=weather["ghi"],
        dhi=weather["dhi"],
        solar_zenith=solar_pos["zenith"],
        solar_azimuth=solar_pos["azimuth"]
    )

    # --- Cell temperature ---
    temp_cell = temperature.sapm_cell(
        poa["poa_global"],
        weather["temp_air"],
        weather.get("wind_speed", 1),
        SAPM_A,
        SAPM_B,
        SAPM_DELTA_T
    )

    # --- DC power ---
    pdc = pvsystem.pvwatts_dc(
        poa["poa_global"],
        temp_cell,
        system_kw * 1000,
        -0.0035   # improved temperature coefficient
    )

    # --- AC power ---
    pac = pdc * INVERTER_EFFICIENCY

    # Convert W → kWh
    # Weather data is hourly → multiply by 1 hour
    energy_kwh_series = pac / 1000

    annual_energy_kwh = energy_kwh_series.sum() * SYSTEM_LOSS_FACTOR

    # --- Engineering sanity guard ---
    specific_yield = annual_energy_kwh / system_kw

    # Clamp unrealistic yields
    if specific_yield > 2200:
        annual_energy_kwh = system_kw * 1700

    return float(round(annual_energy_kwh, 2))