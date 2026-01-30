"""
Defines SLA baselines and risk curves.
"""

BASE_SLA_HOURS = {
    "CREATED": 72,
    "MANAGER_APPROVED": 72,
    "SUPERVISOR_APPROVED": 72,
    "IN_TRANSIT": 48,
    "WAREHOUSE_INTAKE": 24,
    "OUT_FOR_DELIVERY": 8,
}

RISK_INFLATION_CURVE = [
    (0, 1.0),
    (20, 1.1),
    (40, 1.25),
    (60, 1.45),
    (80, 1.7),
    (100, 2.0),
]
