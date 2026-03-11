CITY_LOCATIONS = {
    "Bangalore": {
        "latitude": 12.9716,
        "longitude": 77.5946,
        "timezone": "Asia/Kolkata"
    },
    "Pune": {
        "latitude": 18.5204,
        "longitude": 73.8567,
        "timezone": "Asia/Kolkata"
    },
    "Mumbai": {
        "latitude": 19.0760,
        "longitude": 72.8777,
        "timezone": "Asia/Kolkata"
    }
}


def get_location_from_city(city: str):

    city_clean = city.strip().lower()

    for known_city in CITY_LOCATIONS:
        if known_city.lower() == city_clean:
            return CITY_LOCATIONS[known_city]

    raise ValueError(
        f"City '{city}' not supported yet. "
        f"Supported cities: {', '.join(CITY_LOCATIONS.keys())}"
    )
