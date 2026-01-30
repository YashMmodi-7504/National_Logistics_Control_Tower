"""
CORRIDOR CONTRACT GENERATOR

Purpose:
- Corridor-level intelligence and risk analysis
- Lane performance metrics

Requirements:
• Aggregate from shipments
• Corridor-level statistics
• Risk band classification

Author: National Logistics Control Tower
Phase: Data Contracts
"""

import csv
import random
from collections import defaultdict

random.seed(42)

RISK_BANDS = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

def calculate_corridor_metrics(corridor_shipments):
    """Calculate aggregate metrics for a corridor."""
    total_shipments = len(corridor_shipments)
    
    # Average ETA (hours)
    avg_eta = random.randint(48, 96) + random.random()
    
    # Average delay (hours)
    delay_factor = random.uniform(0.05, 0.35)
    avg_delay = avg_eta * delay_factor
    
    # Breach probability
    if delay_factor < 0.15:
        breach_prob = random.uniform(0.10, 0.25)
    elif delay_factor < 0.25:
        breach_prob = random.uniform(0.30, 0.50)
    else:
        breach_prob = random.uniform(0.55, 0.80)
    
    # Risk band
    if breach_prob >= 0.60:
        risk_band = "HIGH"
    elif breach_prob >= 0.35:
        risk_band = "MEDIUM"
    else:
        risk_band = "LOW"
    
    return {
        "avg_eta": round(avg_eta, 2),
        "avg_delay": round(avg_delay, 2),
        "avg_breach_probability": round(breach_prob, 3),
        "shipment_count": total_shipments,
        "risk_band": risk_band
    }

def generate_corridor_contract():
    """Generate corridor contract CSV."""
    
    # Load shipments
    shipments = []
    try:
        with open("data_contracts/shipments_contract.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            shipments = list(reader)
    except FileNotFoundError:
        print("❌ Error: shipments_contract.csv not found.")
        return 0
    
    # Group by corridor
    corridors = defaultdict(list)
    for shipment in shipments:
        corridor = shipment["corridor"]
        corridors[corridor].append(shipment)
    
    filename = "data_contracts/corridor_contract.csv"
    
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow([
            "corridor",
            "avg_eta",
            "avg_delay",
            "avg_breach_probability",
            "shipment_count",
            "risk_band"
        ])
        
        for corridor, corridor_shipments in sorted(corridors.items()):
            metrics = calculate_corridor_metrics(corridor_shipments)
            
            writer.writerow([
                corridor,
                metrics["avg_eta"],
                metrics["avg_delay"],
                metrics["avg_breach_probability"],
                metrics["shipment_count"],
                metrics["risk_band"]
            ])
    
    print(f"✅ Generated {len(corridors)} rows → {filename}")
    return len(corridors)

if __name__ == "__main__":
    row_count = generate_corridor_contract()
    print(f"📊 Total corridors: {row_count}")
