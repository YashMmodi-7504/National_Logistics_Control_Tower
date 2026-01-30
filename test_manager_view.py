"""
Test script to verify Manager can see shipments created by Sender
"""
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.storage.event_log import create_shipment, get_all_shipments_by_state

def test_sender_to_manager_flow():
    """Test that shipments created by Sender appear in Manager Priority Queue"""
    
    print("\n" + "="*80)
    print("TEST: Sender → Manager Flow (Event Sourcing)")
    print("="*80)
    
    # STEP 1: Sender creates a shipment
    print("\n1️⃣ SENDER: Creating new shipment...")
    shipment_id = create_shipment(
        source="Test City, Maharashtra",
        destination="Target City, Delhi",
        weight_kg=15.5,
        delivery_type="EXPRESS"
    )
    print(f"   ✅ Created shipment: {shipment_id}")
    
    # STEP 2: Manager queries for CREATED shipments
    print("\n2️⃣ MANAGER: Querying for CREATED shipments...")
    created_shipments = get_all_shipments_by_state("CREATED")
    print(f"   📊 Found {len(created_shipments)} shipments in CREATED state")
    
    # STEP 3: Verify our shipment appears
    print(f"\n3️⃣ VERIFICATION: Looking for {shipment_id}...")
    found = False
    for ship_state in created_shipments:
        if ship_state['shipment_id'] == shipment_id:
            found = True
            print(f"   ✅ FOUND! Shipment appears in Manager Priority Queue")
            print(f"   📦 Shipment ID: {ship_state['shipment_id']}")
            print(f"   📍 Route: {ship_state['current_payload'].get('source')} → {ship_state['current_payload'].get('destination')}")
            print(f"   ⚖️ Weight: {ship_state['current_payload'].get('weight_kg')} kg")
            print(f"   🚚 Type: {ship_state['current_payload'].get('delivery_type')}")
            print(f"   📅 Created: {ship_state['created_at']}")
            print(f"   📊 Event Count: {ship_state['event_count']}")
            break
    
    if not found:
        print(f"   ❌ ERROR: Shipment {shipment_id} NOT found in Manager view!")
        print(f"   📋 Available shipments:")
        for ship_state in created_shipments[:5]:
            print(f"      - {ship_state['shipment_id']}")
        return False
    
    # STEP 4: Show all CREATED shipments
    print(f"\n4️⃣ ALL CREATED SHIPMENTS (last 10):")
    for idx, ship_state in enumerate(created_shipments[-10:], 1):
        payload = ship_state['current_payload']
        print(f"   {idx}. {ship_state['shipment_id']}")
        print(f"      Route: {payload.get('source')} → {payload.get('destination')}")
        print(f"      Type: {payload.get('delivery_type')} | Weight: {payload.get('weight_kg')} kg")
        print(f"      Created: {ship_state['created_at']}")
        print()
    
    print("="*80)
    print("✅ TEST PASSED: Sender → Manager flow working correctly!")
    print("="*80)
    return True

if __name__ == "__main__":
    try:
        success = test_sender_to_manager_flow()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
