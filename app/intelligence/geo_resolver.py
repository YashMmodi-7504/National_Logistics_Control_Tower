# app/intelligence/geo_resolver.py

from typing import Dict, Optional

# ==================================================
# 🇮🇳 STATE CENTROIDS (AUTHORITATIVE)
# ==================================================
STATE_CENTROIDS: Dict[str, Dict[str, float]] = {
    "Andhra Pradesh": {"lat": 15.9129, "lon": 79.7400},
    "Arunachal Pradesh": {"lat": 28.2180, "lon": 94.7278},
    "Assam": {"lat": 26.2006, "lon": 92.9376},
    "Bihar": {"lat": 25.0961, "lon": 85.3131},
    "Chhattisgarh": {"lat": 21.2787, "lon": 81.8661},
    "Goa": {"lat": 15.2993, "lon": 74.1240},
    "Gujarat": {"lat": 22.2587, "lon": 71.1924},
    "Haryana": {"lat": 29.0588, "lon": 76.0856},
    "Himachal Pradesh": {"lat": 31.1048, "lon": 77.1734},
    "Jharkhand": {"lat": 23.6102, "lon": 85.2799},
    "Karnataka": {"lat": 15.3173, "lon": 75.7139},
    "Kerala": {"lat": 10.8505, "lon": 76.2711},
    "Madhya Pradesh": {"lat": 22.9734, "lon": 78.6569},
    "Maharashtra": {"lat": 19.7515, "lon": 75.7139},
    "Manipur": {"lat": 24.6637, "lon": 93.9063},
    "Meghalaya": {"lat": 25.4670, "lon": 91.3662},
    "Mizoram": {"lat": 23.1645, "lon": 92.9376},
    "Nagaland": {"lat": 26.1584, "lon": 94.5624},
    "Odisha": {"lat": 20.9517, "lon": 85.0985},
    "Punjab": {"lat": 31.1471, "lon": 75.3412},
    "Rajasthan": {"lat": 27.0238, "lon": 74.2179},
    "Sikkim": {"lat": 27.5330, "lon": 88.5122},
    "Tamil Nadu": {"lat": 11.1271, "lon": 78.6569},
    "Telangana": {"lat": 18.1124, "lon": 79.0193},
    "Tripura": {"lat": 23.9408, "lon": 91.9882},
    "Uttar Pradesh": {"lat": 26.8467, "lon": 80.9462},
    "Uttarakhand": {"lat": 30.0668, "lon": 79.0193},
    "West Bengal": {"lat": 22.9868, "lon": 87.8550},
}

# ==================================================
# BASIC STATE NORMALIZATION
# ==================================================
STATE_ALIASES = {
    "MH": "Maharashtra",
    "GJ": "Gujarat",
    "RJ": "Rajasthan",
    "UP": "Uttar Pradesh",
    "MP": "Madhya Pradesh",
    "TN": "Tamil Nadu",
    "KA": "Karnataka",
}

# ==================================================
# GEO RESOLVER
# ==================================================
def resolve_location(raw_location: Optional[str]) -> Dict:
    """
    Resolve a free-text location into structured geo metadata.
    """
    if not raw_location:
        return {"raw": None, "state": None, "confidence": 0.0}

    raw = raw_location.strip()

    for alias, state in STATE_ALIASES.items():
        if alias.lower() in raw.lower():
            return {
                "raw": raw,
                "state": state,
                "confidence": 0.9
            }

    for state in STATE_CENTROIDS.keys():
        if state.lower() in raw.lower():
            return {
                "raw": raw,
                "state": state,
                "confidence": 0.95
            }

    return {
        "raw": raw,
        "state": None,
        "confidence": 0.4
    }
