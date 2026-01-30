"""
DATA CONTRACTS - BATCH GENERATOR

Purpose:
- Generate all data contract CSVs in order
- Single command execution
- Validation and reporting

Usage:
    python data_contracts/generate_all_contracts.py

Author: National Logistics Control Tower
Phase: Data Contracts
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from generate_shipments_contract import generate_shipments
from generate_events_contract import generate_events
from generate_sla_contract import generate_sla_contract
from generate_corridor_contract import generate_corridor_contract
from generate_notifications_contract import generate_notifications

def main():
    """Generate all data contracts."""
    
    print("=" * 60)
    print("DATA CONTRACTS GENERATOR")
    print("=" * 60)
    print()
    
    # 1. Shipments (foundational)
    print("1️⃣ Generating shipments_contract.csv...")
    shipments_count = generate_shipments(10000)
    print()
    
    # 2. Events (depends on shipments)
    print("2️⃣ Generating events_contract.csv...")
    events_count = generate_events()
    print()
    
    # 3. SLA (depends on shipments)
    print("3️⃣ Generating sla_contract.csv...")
    sla_count = generate_sla_contract()
    print()
    
    # 4. Corridors (aggregates shipments)
    print("4️⃣ Generating corridor_contract.csv...")
    corridor_count = generate_corridor_contract()
    print()
    
    # 5. Notifications (depends on events)
    print("5️⃣ Generating notifications_contract.csv...")
    notifications_count = generate_notifications()
    print()
    
    # Summary
    print("=" * 60)
    print("✅ DATA CONTRACTS GENERATION COMPLETE")
    print("=" * 60)
    print(f"📊 Shipments:      {shipments_count:,} rows")
    print(f"📊 Events:         {events_count:,} rows")
    print(f"📊 SLA Records:    {sla_count:,} rows")
    print(f"📊 Corridors:      {corridor_count:,} rows")
    print(f"📊 Notifications:  {notifications_count:,} rows")
    print("=" * 60)
    print()
    print("📁 Files created in: data_contracts/")
    print("   • shipments_contract.csv")
    print("   • events_contract.csv")
    print("   • sla_contract.csv")
    print("   • corridor_contract.csv")
    print("   • notifications_contract.csv")
    print()
    print("✅ All contracts are deterministic and reproducible (seed=42)")

if __name__ == "__main__":
    main()
