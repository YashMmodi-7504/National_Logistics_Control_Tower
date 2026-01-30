"""
Test script to verify event sourcing system works
"""

import sys
sys.path.insert(0, 'D:\\National-Logistics-Control-Tower\\National-Logistics-Control-Tower')

from app.storage.event_log import (
    create_shipment,
    get_all_shipments_by_state,
    reconstruct_shipment_state,
    get_audit_report
)

print("=" * 60)
print("EVENT SOURCING SYSTEM TEST")
print("=" * 60)

# Test 1: Create a shipment
print("\n1. Creating test shipment...")
try:
    shipment_id = create_shipment(
        source="Mumbai, Maharashtra",
        destination="Delhi, Delhi",
        weight_kg=10.5,
        delivery_type="EXPRESS"
    )
    print(f"✅ Created shipment: {shipment_id}")
except Exception as e:
    print(f"❌ Error creating shipment: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Read shipments in CREATED state
print("\n2. Reading CREATED shipments...")
try:
    created_shipments = get_all_shipments_by_state("CREATED")
    print(f"✅ Found {len(created_shipments)} shipments in CREATED state")
    for ship in created_shipments[:3]:  # Show first 3
        print(f"   - {ship['shipment_id']}: {ship['current_state']}")
except Exception as e:
    print(f"❌ Error reading shipments: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Reconstruct specific shipment
print(f"\n3. Reconstructing shipment {shipment_id}...")
try:
    state = reconstruct_shipment_state(shipment_id)
    if state:
        print(f"✅ Shipment found:")
        print(f"   - Current State: {state['current_state']}")
        print(f"   - Created At: {state['created_at']}")
        print(f"   - Event Count: {state['event_count']}")
        print(f"   - Payload: {state['current_payload']}")
    else:
        print(f"❌ Shipment not found")
except Exception as e:
    print(f"❌ Error reconstructing state: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Audit report
print("\n4. Generating audit report...")
try:
    report = get_audit_report()
    print(f"✅ Audit Report:")
    print(f"   - Total Events: {report['total_events']}")
    print(f"   - Total Shipments: {report['total_shipments']}")
    print(f"   - Log Integrity: {report['log_integrity']}")
    print(f"   - State Distribution: {report['current_state_distribution']}")
except Exception as e:
    print(f"❌ Error generating report: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
