"""
SHIPMENTS CONTRACT GENERATOR

Purpose:
- Generate synthetic shipment data for stress testing
- Train ML models on shipment lifecycle patterns
- Validate geo + corridor intelligence

Requirements:
• 10,000 rows minimum
• Deterministic (seeded)
• Realistic Indian geo data
• Reproducible

Author: National Logistics Control Tower
Phase: Data Contracts
"""

import csv
import random
from datetime import datetime, timedelta

# Deterministic seed for reproducibility
random.seed(42)

# Indian Cities and States
INDIAN_CITIES_STATES = [
    ("Mumbai", "Maharashtra"),
    ("Pune", "Maharashtra"),
    ("Nagpur", "Maharashtra"),
    ("Delhi", "Delhi"),
    ("Gurgaon", "Haryana"),
    ("Noida", "Uttar Pradesh"),
    ("Bangalore", "Karnataka"),
    ("Mysore", "Karnataka"),
    ("Chennai", "Tamil Nadu"),
    ("Coimbatore", "Tamil Nadu"),
    ("Kolkata", "West Bengal"),
    ("Hyderabad", "Telangana"),
    ("Ahmedabad", "Gujarat"),
    ("Surat", "Gujarat"),
    ("Jaipur", "Rajasthan"),
    ("Lucknow", "Uttar Pradesh"),
    ("Kanpur", "Uttar Pradesh"),
    ("Indore", "Madhya Pradesh"),
    ("Bhopal", "Madhya Pradesh"),
    ("Kochi", "Kerala"),
    ("Thiruvananthapuram", "Kerala"),
    ("Guwahati", "Assam"),
    ("Chandigarh", "Punjab"),
    ("Ludhiana", "Punjab"),
    ("Patna", "Bihar"),
    ("Bhubaneswar", "Odisha"),
    ("Visakhapatnam", "Andhra Pradesh"),
    ("Vijayawada", "Andhra Pradesh"),
    ("Raipur", "Chhattisgarh"),
    ("Ranchi", "Jharkhand"),
]

DELIVERY_TYPES = ["NORMAL", "EXPRESS"]
DELIVERY_CATEGORIES = ["RESIDENTIAL", "COMMERCIAL"]
STATES = ["CREATED", "MANAGER_APPROVED", "IN_TRANSIT", "RECEIVER_ACKNOWLEDGED", 
          "WAREHOUSE_INTAKE", "OUT_FOR_DELIVERY", "DELIVERED", "HOLD"]
PRIORITIES = ["LOW", "MEDIUM", "HIGH"]

def generate_shipment_id(index):
    """Generate deterministic shipment ID."""
    year = 2026
    seq = str(index).zfill(5)
    return f"SHIP-{year}-{seq}"

def generate_created_at():
    """Generate timestamp within last 60 days."""
    days_ago = random.randint(0, 60)
    hours_ago = random.randint(0, 23)
    minutes_ago = random.randint(0, 59)
    
    timestamp = datetime.now() - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")

def generate_weight():
    """Generate parcel weight (0.5 - 50 kg)."""
    return round(random.uniform(0.5, 50.0), 2)

def generate_priority(delivery_type, weight):
    """Generate priority based on delivery type and weight."""
    if delivery_type == "EXPRESS" or weight > 30:
        return random.choice(["MEDIUM", "HIGH"])
    return random.choice(["LOW", "MEDIUM"])

def generate_state(created_days_ago):
    """Generate current state based on age."""
    if created_days_ago < 1:
        return random.choice(["CREATED", "MANAGER_APPROVED", "IN_TRANSIT"])
    elif created_days_ago < 3:
        return random.choice(["IN_TRANSIT", "RECEIVER_ACKNOWLEDGED", "WAREHOUSE_INTAKE"])
    elif created_days_ago < 7:
        return random.choice(["WAREHOUSE_INTAKE", "OUT_FOR_DELIVERY", "DELIVERED"])
    else:
        return random.choice(["DELIVERED", "HOLD"])

def generate_shipments(num_rows=10000):
    """Generate shipments contract CSV."""
    
    filename = "data_contracts/shipments_contract.csv"
    
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow([
            "shipment_id",
            "created_at",
            "source_city",
            "source_state",
            "destination_city",
            "destination_state",
            "weight_kg",
            "delivery_type",
            "delivery_category",
            "current_state",
            "priority",
            "corridor"
        ])
        
        # Generate rows
        for i in range(1, num_rows + 1):
            shipment_id = generate_shipment_id(i)
            created_at = generate_created_at()
            
            # Ensure source != destination
            source_city, source_state = random.choice(INDIAN_CITIES_STATES)
            dest_options = [cs for cs in INDIAN_CITIES_STATES if cs[1] != source_state]
            destination_city, destination_state = random.choice(dest_options)
            
            weight_kg = generate_weight()
            delivery_type = random.choice(DELIVERY_TYPES)
            delivery_category = random.choice(DELIVERY_CATEGORIES)
            
            # Determine age for state progression
            created_dt = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
            days_ago = (datetime.now() - created_dt).days
            
            current_state = generate_state(days_ago)
            priority = generate_priority(delivery_type, weight_kg)
            corridor = f"{source_state} -> {destination_state}"
            
            writer.writerow([
                shipment_id,
                created_at,
                source_city,
                source_state,
                destination_city,
                destination_state,
                weight_kg,
                delivery_type,
                delivery_category,
                current_state,
                priority,
                corridor
            ])
            
            if i % 1000 == 0:
                print(f"Generated {i} shipments...")
    
    print(f"✅ Generated {num_rows} rows → {filename}")
    return num_rows

if __name__ == "__main__":
    row_count = generate_shipments(10000)
    print(f"📊 Total rows: {row_count}")
