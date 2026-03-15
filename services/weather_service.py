import pandas as pd

def load_nrel_weather(csv_path: str, tz: str):
    """
    Load NSRDB / NREL CSV (2016–2020)
    Expected:
    - timestamp as index
    - ghi, dni, dhi
    - temperature
    """

    df = pd.read_csv(
        csv_path,
        index_col=0,           # timestamp is index
        parse_dates=True
    )

    # Ensure timezone
    if df.index.tz is None:
        df.index = df.index.tz_localize(tz)

    # Rename to pvlib standard names
    df = df.rename(columns={
        "temperature": "temp_air"
    })

    # pvlib REQUIRES pressure (Pa)
    if "pressure" not in df.columns:
        df["pressure"] = 101325  # standard sea-level pressure

    # Validate required irradiance columns
    required = {"ghi", "dni", "dhi"}
    missing = required - set(df.columns)

    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    return df
