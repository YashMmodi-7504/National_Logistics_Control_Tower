import os
import requests

ORS_API_KEY = os.getenv("ORS_API_KEY")
ORS_REVERSE_URL = "https://api.openrouteservice.org/geocode/reverse"

def reverse_geocode_state(lat: float, lon: float) -> str | None:
    """
    Reverse geocode coordinates → Indian state using ORS
    """
    if not ORS_API_KEY:
        return None

    params = {
        "api_key": ORS_API_KEY,
        "point.lat": lat,
        "point.lon": lon,
        "size": 1,
    }

    try:
        response = requests.get(ORS_REVERSE_URL, params=params, timeout=5)
        response.raise_for_status()

        data = response.json()
        features = data.get("features", [])

        if not features:
            return None

        props = features[0]["properties"]

        # ORS usually returns state in "region" or "state"
        return (
            props.get("region")
            or props.get("state")
            or props.get("county")
        )

    except Exception:
        return None
