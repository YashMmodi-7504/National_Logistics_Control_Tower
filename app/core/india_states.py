"""
India States Data - Complete coverage of all states & UTs
Provides state centroids, metadata, and GeoJSON references
Includes: 28 States + 8 Union Territories = 36 regions
"""

# All Indian States + Union Territories (Complete as of 2026)
INDIA_STATES = [
    # Major States
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand",
    "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur",
    "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab",
    "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura",
    "Uttar Pradesh", "Uttarakhand", "West Bengal",
    # Union Territories
    "Delhi", "Jammu and Kashmir", "Ladakh", "Chandigarh", 
    "Dadra and Nagar Haveli and Daman and Diu", "Puducherry",
    "Andaman and Nicobar Islands", "Lakshadweep"
]

# State centroids for mapping (lat, lon)
STATE_CENTROIDS = {
    # Major States
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
    # Union Territories
    "Delhi": {"lat": 28.7041, "lon": 77.1025},
    "Jammu and Kashmir": {"lat": 33.7782, "lon": 76.5762},
    "Ladakh": {"lat": 34.1526, "lon": 77.5771},
    "Chandigarh": {"lat": 30.7333, "lon": 76.7794},
    "Dadra and Nagar Haveli and Daman and Diu": {"lat": 20.1809, "lon": 73.0169},
    "Puducherry": {"lat": 11.9416, "lon": 79.8083},
    "Andaman and Nicobar Islands": {"lat": 11.7401, "lon": 92.6586},
    "Lakshadweep": {"lat": 10.5667, "lon": 72.6417}
}

# State characteristics for realistic data generation
STATE_CHARACTERISTICS = {
    "Maharashtra": {"metro": True, "volume_multiplier": 1.5, "risk_base": 35},
    "Karnataka": {"metro": True, "volume_multiplier": 1.4, "risk_base": 32},
    "Tamil Nadu": {"metro": True, "volume_multiplier": 1.3, "risk_base": 30},
    "Delhi": {"metro": True, "volume_multiplier": 1.6, "risk_base": 38},
    "Uttar Pradesh": {"metro": False, "volume_multiplier": 1.2, "risk_base": 42},
    "Gujarat": {"metro": True, "volume_multiplier": 1.3, "risk_base": 33},
    "West Bengal": {"metro": True, "volume_multiplier": 1.2, "risk_base": 36},
    "Rajasthan": {"metro": False, "volume_multiplier": 0.9, "risk_base": 40},
    "Madhya Pradesh": {"metro": False, "volume_multiplier": 0.8, "risk_base": 38},
    "Telangana": {"metro": True, "volume_multiplier": 1.3, "risk_base": 31},
    "Haryana": {"metro": False, "volume_multiplier": 1.1, "risk_base": 34},
    "Punjab": {"metro": False, "volume_multiplier": 1.0, "risk_base": 35},
    "Kerala": {"metro": False, "volume_multiplier": 0.9, "risk_base": 28},
    "Andhra Pradesh": {"metro": False, "volume_multiplier": 1.0, "risk_base": 33},
    "Bihar": {"metro": False, "volume_multiplier": 0.7, "risk_base": 45},
    "Odisha": {"metro": False, "volume_multiplier": 0.7, "risk_base": 41},
    "Jharkhand": {"metro": False, "volume_multiplier": 0.6, "risk_base": 43},
    "Chhattisgarh": {"metro": False, "volume_multiplier": 0.6, "risk_base": 39},
    "Assam": {"metro": False, "volume_multiplier": 0.5, "risk_base": 46},
    "Uttarakhand": {"metro": False, "volume_multiplier": 0.5, "risk_base": 44},
    "Himachal Pradesh": {"metro": False, "volume_multiplier": 0.4, "risk_base": 42},
    "Goa": {"metro": False, "volume_multiplier": 0.4, "risk_base": 25},
    "Tripura": {"metro": False, "volume_multiplier": 0.3, "risk_base": 48},
    "Meghalaya": {"metro": False, "volume_multiplier": 0.3, "risk_base": 47},
    "Manipur": {"metro": False, "volume_multiplier": 0.3, "risk_base": 49},
    "Nagaland": {"metro": False, "volume_multiplier": 0.2, "risk_base": 50},
    "Mizoram": {"metro": False, "volume_multiplier": 0.2, "risk_base": 51},
    "Arunachal Pradesh": {"metro": False, "volume_multiplier": 0.2, "risk_base": 52},
    "Sikkim": {"metro": False, "volume_multiplier": 0.2, "risk_base": 45},
    # Union Territories
    "Jammu and Kashmir": {"metro": False, "volume_multiplier": 0.7, "risk_base": 48},
    "Ladakh": {"metro": False, "volume_multiplier": 0.2, "risk_base": 55},
    "Chandigarh": {"metro": True, "volume_multiplier": 0.8, "risk_base": 30},
    "Dadra and Nagar Haveli and Daman and Diu": {"metro": False, "volume_multiplier": 0.3, "risk_base": 35},
    "Puducherry": {"metro": False, "volume_multiplier": 0.4, "risk_base": 32},
    "Andaman and Nicobar Islands": {"metro": False, "volume_multiplier": 0.1, "risk_base": 60},
    "Lakshadweep": {"metro": False, "volume_multiplier": 0.1, "risk_base": 58}
}

# GeoJSON simplified state boundaries (ISO codes for Plotly)
STATE_ISO_CODES = {
    # Major States
    "Andhra Pradesh": "IN-AP",
    "Arunachal Pradesh": "IN-AR",
    "Assam": "IN-AS",
    "Bihar": "IN-BR",
    "Chhattisgarh": "IN-CT",
    "Goa": "IN-GA",
    "Gujarat": "IN-GJ",
    "Haryana": "IN-HR",
    "Himachal Pradesh": "IN-HP",
    "Jharkhand": "IN-JH",
    "Karnataka": "IN-KA",
    "Kerala": "IN-KL",
    "Madhya Pradesh": "IN-MP",
    "Maharashtra": "IN-MH",
    "Manipur": "IN-MN",
    "Meghalaya": "IN-ML",
    "Mizoram": "IN-MZ",
    "Nagaland": "IN-NL",
    "Odisha": "IN-OR",
    "Punjab": "IN-PB",
    "Rajasthan": "IN-RJ",
    "Sikkim": "IN-SK",
    "Tamil Nadu": "IN-TN",
    "Telangana": "IN-TG",
    "Tripura": "IN-TR",
    "Uttar Pradesh": "IN-UP",
    "Uttarakhand": "IN-UT",
    "West Bengal": "IN-WB",
    # Union Territories
    "Delhi": "IN-DL",
    "Jammu and Kashmir": "IN-JK",
    "Ladakh": "IN-LA",
    "Chandigarh": "IN-CH",
    "Dadra and Nagar Haveli and Daman and Diu": "IN-DN",
    "Puducherry": "IN-PY",
    "Andaman and Nicobar Islands": "IN-AN",
    "Lakshadweep": "IN-LD"
}
