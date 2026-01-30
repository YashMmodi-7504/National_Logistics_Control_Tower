"""
Synthetic Data Generator for National Logistics Control Tower

Creates 1000 realistic shipments across different states and stages
"""

import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.storage.event_log import create_shipment, transition_shipment, EventType, Actor
from app.core.india_states import INDIA_STATES

# Delivery types distribution
DELIVERY_TYPES = ["NORMAL"] * 7 + ["EXPRESS"] * 3  # 70% normal, 30% express

# State distribution for shipment stages
STATE_DISTRIBUTION = {
    "CREATED": 0.15,  # 15% waiting for manager approval
    "MANAGER_APPROVED": 0.10,  # 10% waiting for supervisor
    "SUPERVISOR_APPROVED": 0.05,  # 5% waiting for dispatch
    "IN_TRANSIT": 0.20,  # 20% in transit
    "RECEIVER_ACKNOWLEDGED": 0.15,  # 15% acknowledged by receiver
    "WAREHOUSE_INTAKE": 0.10,  # 10% in warehouse
    "OUT_FOR_DELIVERY": 0.15,  # 15% out for delivery
    "DELIVERED": 0.10,  # 10% delivered
}


def generate_realistic_weight():
    """Generate realistic parcel weight (1-50kg, most under 20kg)"""
    if random.random() < 0.7:
        return round(random.uniform(1.0, 20.0), 1)
    else:
        return round(random.uniform(20.0, 50.0), 1)


def get_random_city_state():
    """Get a random Indian state"""
    return random.choice(INDIA_STATES)


def create_synthetic_shipment(index, target_state):
    """Create a single synthetic shipment at the specified state"""
    
    # Generate shipment details
    source_state = get_random_city_state()
    dest_state = get_random_city_state()
    
    # Ensure different source and destination
    while dest_state == source_state:
        dest_state = get_random_city_state()
    
    source = f"Warehouse {random.randint(1, 5)}, {source_state}"
    destination = f"Hub {random.randint(1, 3)}, {dest_state}"
    weight_kg = generate_realistic_weight()
    delivery_type = random.choice(DELIVERY_TYPES).upper()
    
    # Create the shipment (will be in CREATED state initially)
    shipment_id = create_shipment(
        source=source,
        destination=destination,
        weight_kg=weight_kg,
        delivery_type=delivery_type,
        delivery_category=delivery_type
    )
    
    print(f"[{index+1}/1000] Created {shipment_id} - {source_state} → {dest_state} ({delivery_type})")
    
    # Advance to target state
    if target_state == "CREATED":
        return shipment_id
    
    # Manager approval
    if target_state in ["MANAGER_APPROVED", "SUPERVISOR_APPROVED", "IN_TRANSIT", "RECEIVER_ACKNOWLEDGED", "WAREHOUSE_INTAKE", "OUT_FOR_DELIVERY", "DELIVERED"]:
        transition_shipment(
            shipment_id=shipment_id,
            to_state=EventType.MANAGER_APPROVED,
            actor=Actor.SENDER_MANAGER,
            approval_notes="Auto-approved for synthetic data"
        )
    
    if target_state == "MANAGER_APPROVED":
        return shipment_id
    
    # Supervisor approval
    if target_state in ["SUPERVISOR_APPROVED", "IN_TRANSIT", "RECEIVER_ACKNOWLEDGED", "WAREHOUSE_INTAKE", "OUT_FOR_DELIVERY", "DELIVERED"]:
        transition_shipment(
            shipment_id=shipment_id,
            to_state=EventType.SUPERVISOR_APPROVED,
            actor=Actor.SENDER_SUPERVISOR,
            approval_notes="Auto-approved for synthetic data"
        )
    
    if target_state == "SUPERVISOR_APPROVED":
        return shipment_id
    
    # System dispatch
    if target_state in ["IN_TRANSIT", "RECEIVER_ACKNOWLEDGED", "WAREHOUSE_INTAKE", "OUT_FOR_DELIVERY", "DELIVERED"]:
        transition_shipment(
            shipment_id=shipment_id,
            to_state=EventType.IN_TRANSIT,
            actor=Actor.SYSTEM,
            dispatch_timestamp=datetime.now().isoformat()
        )
    
    if target_state == "IN_TRANSIT":
        return shipment_id
    
    # Receiver acknowledgment
    if target_state in ["RECEIVER_ACKNOWLEDGED", "WAREHOUSE_INTAKE", "OUT_FOR_DELIVERY", "DELIVERED"]:
        transition_shipment(
            shipment_id=shipment_id,
            to_state=EventType.RECEIVER_ACKNOWLEDGED,
            actor=Actor.RECEIVER,
            acknowledgment_timestamp=datetime.now().isoformat()
        )
    
    if target_state == "RECEIVER_ACKNOWLEDGED":
        return shipment_id
    
    # Warehouse intake
    if target_state in ["WAREHOUSE_INTAKE", "OUT_FOR_DELIVERY", "DELIVERED"]:
        transition_shipment(
            shipment_id=shipment_id,
            to_state=EventType.WAREHOUSE_INTAKE,
            actor=Actor.WAREHOUSE,
            intake_timestamp=datetime.now().isoformat()
        )
    
    if target_state == "WAREHOUSE_INTAKE":
        return shipment_id
    
    # Out for delivery
    if target_state in ["OUT_FOR_DELIVERY", "DELIVERED"]:
        transition_shipment(
            shipment_id=shipment_id,
            to_state=EventType.OUT_FOR_DELIVERY,
            actor=Actor.WAREHOUSE,
            dispatch_timestamp=datetime.now().isoformat()
        )
    
    if target_state == "OUT_FOR_DELIVERY":
        return shipment_id
    
    # Delivered
    if target_state == "DELIVERED":
        transition_shipment(
            shipment_id=shipment_id,
            to_state=EventType.DELIVERED,
            actor=Actor.CUSTOMER,
            delivery_confirmation_timestamp=datetime.now().isoformat()
        )
    
    return shipment_id


def main():
    """Generate 1000 synthetic shipments"""
    print("=" * 60)
    print("SYNTHETIC DATA GENERATOR")
    print("National Logistics Control Tower")
    print("=" * 60)
    print(f"\nGenerating 1000 shipments across {len(INDIA_STATES)} states...")
    print(f"Distribution: {STATE_DISTRIBUTION}\n")
    
    # Calculate how many shipments per state
    total_shipments = 1000
    shipments_per_state = {}
    
    for state, percentage in STATE_DISTRIBUTION.items():
        count = int(total_shipments * percentage)
        shipments_per_state[state] = count
    
    # Adjust to exactly 1000
    diff = total_shipments - sum(shipments_per_state.values())
    shipments_per_state["IN_TRANSIT"] += diff
    
    print("Shipments per state:")
    for state, count in shipments_per_state.items():
        print(f"  {state}: {count}")
    print()
    
    # Generate shipments
    created_count = 0
    for state, count in shipments_per_state.items():
        print(f"\nGenerating {count} shipments in state: {state}")
        for i in range(count):
            try:
                create_synthetic_shipment(created_count, state)
                created_count += 1
            except Exception as e:
                print(f"  ⚠️ Error creating shipment: {e}")
    
    print("\n" + "=" * 60)
    print(f"✅ COMPLETE: Generated {created_count}/1000 shipments")
    print("=" * 60)
    print("\nData saved to: data/logs/shipments.jsonl")
    print("\nRestart your Streamlit app to see the new data!")


if __name__ == "__main__":
    main()
