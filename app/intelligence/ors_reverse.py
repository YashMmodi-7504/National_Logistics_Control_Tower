import os
import requests

ORS_API_KEY = os.getenv("ORS_API_KEY")


def reverse_geocode_state(lat: float, lon: float) -> str | None:
    """
    Convert latitude & longitude to Indian state using OpenRouteService
    """
    if not ORS_API_KEY:
        return None

    url = "https://api.openrouteservice.org/geocode/reverse"
    params = {
        "api_key": ORS_API_KEY,
        "point.lat": lat,
        "point.lon": lon,
        "size": 1
    }

    try:
        r = requests.get(url, params=params, timeout=4)
        data = r.json()

        features = data.get("features", [])
        if not features:
            return None

        props = features[0]["properties"]
        return props.get("region")  # State name

    except Exception:
        return None
