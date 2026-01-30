"""
SLA CONTRACT GENERATOR

Purpose:
- SLA breach modeling and prediction
- Time-based risk curve training

Requirements:
• Based on shipments contract
• Realistic ETA calculations
• Deterministic breach probabilities

Author: National Logistics Control Tower
Phase: Data Contracts
"""

import csv
import random
from datetime import datetime

random.seed(42)

RISK_LEVELS = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

def calculate_expected_eta(corridor, delivery_type):
    """Calculate expected ETA based on corridor and type."""
    # Base ETA (hours) for different corridor distances
    base_eta = random.randint(24, 120)
    
    if delivery_type == "EXPRESS":
        base_eta = int(base_eta * 0.7)  # 30% faster
    
    return base_eta

def calculate_actual_hours(shipment):
    """Calculate actual hours elapsed."""
    created_at = datetime.strptime(shipment["created_at"], "%Y-%m-%d %H:%M:%S")
    elapsed = (datetime.now() - created_at).total_seconds() / 3600
    return round(elapsed, 2)

def calculate_sla_utilization(actual_hours, expected_eta):
    """Calculate SLA utilization percentage."""
    return round(actual_hours / expected_eta, 3)

def calculate_breach_probability(sla_utilization, priority):
    """Calculate breach probability based on utilization."""
    if sla_utilization < 0.6:
        base_prob = random.uniform(0.05, 0.15)
    elif sla_utilization < 0.85:
        base_prob = random.uniform(0.25, 0.45)
    elif sla_utilization < 1.0:
        base_prob = random.uniform(0.55, 0.75)
    else:
        base_prob = random.uniform(0.80, 0.95)
    
    # Priority adjustment
    if priority == "HIGH":
        base_prob *= 0.9
    elif priority == "LOW":
        base_prob *= 1.1
    
    return round(min(base_prob, 0.99), 3)

def determine_risk_level(breach_probability):
    """Determine risk level from breach probability."""
    if breach_probability >= 0.75:
        return "CRITICAL"
    elif breach_probability >= 0.50:
        return "HIGH"
    elif breach_probability >= 0.25:
        return "MEDIUM"
    else:
        return "LOW"

def generate_sla_contract():
    """Generate SLA contract CSV."""
    
    # Load shipments
    shipments = []
    try:
        with open("data_contracts/shipments_contract.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            shipments = list(reader)
    except FileNotFoundError:
        print("❌ Error: shipments_contract.csv not found.")
        return 0
    
    filename = "data_contracts/sla_contract.csv"
    
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow([
            "shipment_id",
            "expected_eta_hours",
            "actual_hours",
            "sla_utilization",
            "breach_probability",
            "risk_level"
        ])
        
        for shipment in shipments:
            shipment_id = shipment["shipment_id"]
            corridor = shipment["corridor"]
            delivery_type = shipment["delivery_type"]
            priority = shipment["priority"]
            
            expected_eta = calculate_expected_eta(corridor, delivery_type)
            actual_hours = calculate_actual_hours(shipment)
            sla_utilization = calculate_sla_utilization(actual_hours, expected_eta)
            breach_probability = calculate_breach_probability(sla_utilization, priority)
            risk_level = determine_risk_level(breach_probability)
            
            writer.writerow([
                shipment_id,
                expected_eta,
                actual_hours,
                sla_utilization,
                breach_probability,
                risk_level
            ])
    
    print(f"✅ Generated {len(shipments)} rows → {filename}")
    return len(shipments)

if __name__ == "__main__":
    row_count = generate_sla_contract()
    print(f"📊 Total SLA records: {row_count}")
