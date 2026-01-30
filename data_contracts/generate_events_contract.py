"""
EVENTS CONTRACT GENERATOR

Purpose:
- Generate event replay data for testing
- SLA & corridor analytics validation
- Event-driven system stress testing

Requirements:
• 3-8 events per shipment
• Realistic event sequences
• Deterministic (seeded)

Author: National Logistics Control Tower
Phase: Data Contracts
"""

import csv
import random
from datetime import datetime, timedelta

random.seed(42)

# Event flow sequences
EVENT_SEQUENCES = [
    [
        ("SHIPMENT_CREATED", "NONE", "CREATED", "SENDER"),
        ("MANAGER_APPROVED", "CREATED", "MANAGER_APPROVED", "SENDER_MANAGER"),
        ("SUPERVISOR_APPROVED", "MANAGER_APPROVED", "SUPERVISOR_APPROVED", "SENDER_SUPERVISOR"),
        ("DISPATCHED", "SUPERVISOR_APPROVED", "IN_TRANSIT", "SYSTEM"),
        ("RECEIVER_ACKNOWLEDGED", "IN_TRANSIT", "RECEIVER_ACKNOWLEDGED", "RECEIVER_MANAGER"),
        ("OUT_FOR_DELIVERY", "WAREHOUSE_INTAKE", "OUT_FOR_DELIVERY", "WAREHOUSE_MANAGER"),
        ("DELIVERY_CONFIRMED", "OUT_FOR_DELIVERY", "DELIVERED", "CUSTOMER"),
    ],
    # Shortened sequences for variety
    [
        ("SHIPMENT_CREATED", "NONE", "CREATED", "SENDER"),
        ("MANAGER_APPROVED", "CREATED", "MANAGER_APPROVED", "SENDER_MANAGER"),
        ("DISPATCHED", "MANAGER_APPROVED", "IN_TRANSIT", "SYSTEM"),
    ],
    [
        ("SHIPMENT_CREATED", "NONE", "CREATED", "SENDER"),
        ("MANAGER_APPROVED", "CREATED", "MANAGER_APPROVED", "SENDER_MANAGER"),
        ("SUPERVISOR_APPROVED", "MANAGER_APPROVED", "SUPERVISOR_APPROVED", "SENDER_SUPERVISOR"),
        ("DISPATCHED", "SUPERVISOR_APPROVED", "IN_TRANSIT", "SYSTEM"),
        ("RECEIVER_ACKNOWLEDGED", "IN_TRANSIT", "RECEIVER_ACKNOWLEDGED", "RECEIVER_MANAGER"),
    ],
]

def generate_event_id(shipment_id, event_num):
    """Generate deterministic event ID."""
    return f"EVT-{shipment_id}-{str(event_num).zfill(2)}"

def generate_timestamp(base_time, event_num):
    """Generate progressive timestamps."""
    hours_delta = event_num * random.randint(2, 12)
    minutes_delta = random.randint(0, 59)
    
    timestamp = base_time + timedelta(hours=hours_delta, minutes=minutes_delta)
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")

def generate_events(num_shipments=10000):
    """Generate events contract CSV."""
    
    # First, load shipments to get IDs and timestamps
    shipments = []
    try:
        with open("data_contracts/shipments_contract.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            shipments = list(reader)
    except FileNotFoundError:
        print("❌ Error: shipments_contract.csv not found. Run generate_shipments_contract.py first.")
        return 0
    
    filename = "data_contracts/events_contract.csv"
    
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow([
            "event_id",
            "shipment_id",
            "event_type",
            "previous_state",
            "new_state",
            "role",
            "timestamp"
        ])
        
        total_events = 0
        
        for shipment in shipments:
            shipment_id = shipment["shipment_id"]
            created_at_str = shipment["created_at"]
            base_time = datetime.strptime(created_at_str, "%Y-%m-%d %H:%M:%S")
            
            # Choose event sequence based on current state
            current_state = shipment["current_state"]
            
            # Select appropriate sequence
            if current_state in ["CREATED", "MANAGER_APPROVED"]:
                sequence = EVENT_SEQUENCES[1][:2]
            elif current_state in ["IN_TRANSIT", "RECEIVER_ACKNOWLEDGED"]:
                sequence = EVENT_SEQUENCES[2]
            elif current_state == "DELIVERED":
                sequence = EVENT_SEQUENCES[0]
            else:
                sequence = random.choice(EVENT_SEQUENCES)[:random.randint(3, 6)]
            
            # Generate events
            for event_num, (event_type, prev_state, new_state, role) in enumerate(sequence, 1):
                event_id = generate_event_id(shipment_id, event_num)
                timestamp = generate_timestamp(base_time, event_num - 1)
                
                writer.writerow([
                    event_id,
                    shipment_id,
                    event_type,
                    prev_state,
                    new_state,
                    role,
                    timestamp
                ])
                
                total_events += 1
            
            if total_events % 10000 == 0:
                print(f"Generated {total_events} events...")
    
    print(f"✅ Generated {total_events} rows → {filename}")
    return total_events

if __name__ == "__main__":
    row_count = generate_events(10000)
    print(f"📊 Total events: {row_count}")
