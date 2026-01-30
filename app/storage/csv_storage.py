"""
CSV-BASED SINGLE SOURCE OF TRUTH STORAGE LAYER

This module enforces ONE shipment → ONE lifecycle → ONE source of truth.

CSV Files:
- shipments_master.csv: Immutable creation records
- shipment_state_index.csv: CURRENT STATE (THE KEY FILE - all UI reads from here)
- shipment_events.csv: Append-only event log
- shipment_overrides.csv: Override history

All UI lists MUST read from shipment_state_index.csv
"""

import csv
import os
import threading
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

# CSV file paths
DATA_DIR = Path("data/logs")
DATA_DIR.mkdir(parents=True, exist_ok=True)

SHIPMENTS_MASTER_CSV = DATA_DIR / "shipments_master.csv"
SHIPMENT_STATE_INDEX_CSV = DATA_DIR / "shipment_state_index.csv"
SHIPMENT_EVENTS_CSV = DATA_DIR / "shipment_events.csv"
SHIPMENT_OVERRIDES_CSV = DATA_DIR / "shipment_overrides.csv"
SHIPMENT_COUNTER_CSV = DATA_DIR / "shipment_counter.csv"

# Thread-safe file lock
_csv_lock = threading.Lock()

# ══════════════════════════════════════════════════════════════
# SHIPMENT ID GENERATION (Sequential: SHIP_10001, SHIP_10002, ...)
# ══════════════════════════════════════════════════════════════

def generate_shipment_id() -> str:
    """
    Generate sequential shipment ID: SHIP_10001, SHIP_10002, etc.
    Thread-safe with persistent counter.
    """
    with _csv_lock:
        # Initialize counter file if not exists
        if not SHIPMENT_COUNTER_CSV.exists():
            with open(SHIPMENT_COUNTER_CSV, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['last_shipment_number'])
                writer.writerow([10000])
            current_number = 10000
        else:
            # Read current counter
            with open(SHIPMENT_COUNTER_CSV, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                row = next(reader)
                current_number = int(row['last_shipment_number'])
        
        # Increment
        next_number = current_number + 1
        
        # Write back
        with open(SHIPMENT_COUNTER_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['last_shipment_number'])
            writer.writerow([next_number])
        
        return f"SHIP_{next_number}"

# ══════════════════════════════════════════════════════════════
# MASTER SHIPMENTS (Immutable Creation Records)
# ══════════════════════════════════════════════════════════════

def append_shipment_master(shipment_data: Dict) -> None:
    """Append immutable shipment creation record."""
    with _csv_lock:
        file_exists = SHIPMENTS_MASTER_CSV.exists()
        
        with open(SHIPMENTS_MASTER_CSV, 'a', newline='', encoding='utf-8') as f:
            fieldnames = ['shipment_id', 'created_at', 'source', 'destination', 
                         'weight_kg', 'delivery_type', 'delivery_category']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(shipment_data)

# ══════════════════════════════════════════════════════════════
# STATE INDEX (CURRENT STATE - THE KEY FILE)
# ══════════════════════════════════════════════════════════════

def update_state_index(shipment_id: str, state_data: Dict) -> None:
    """
    Update or insert shipment in state index.
    This is THE KEY FILE - all UI reads from here.
    """
    with _csv_lock:
        # Read existing rows
        rows = []
        if SHIPMENT_STATE_INDEX_CSV.exists():
            with open(SHIPMENT_STATE_INDEX_CSV, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
        
        # Update or append
        found = False
        for row in rows:
            if row['shipment_id'] == shipment_id:
                row.update(state_data)
                found = True
                break
        
        if not found:
            rows.append({
                'shipment_id': shipment_id,
                **state_data
            })
        
        # Write back (sorted by last_event_time DESC)
        rows.sort(key=lambda x: x.get('last_event_time', ''), reverse=True)
        
        fieldnames = ['shipment_id', 'current_state', 'last_event_time', 
                     'source', 'destination', 'weight_kg', 'delivery_type', 
                     'override_status', 'override_reason']
        
        with open(SHIPMENT_STATE_INDEX_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

def get_shipments_by_state(state: str) -> List[Dict]:
    """
    Read shipments from state index filtered by current_state.
    Returns sorted by last_event_time DESC (newest first).
    """
    if not SHIPMENT_STATE_INDEX_CSV.exists():
        return []
    
    with _csv_lock:
        with open(SHIPMENT_STATE_INDEX_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            shipments = [row for row in reader if row['current_state'] == state]
    
    return shipments

def get_all_shipments_from_index() -> List[Dict]:
    """Read ALL shipments from state index."""
    if not SHIPMENT_STATE_INDEX_CSV.exists():
        return []
    
    with _csv_lock:
        with open(SHIPMENT_STATE_INDEX_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            shipments = list(reader)
    
    return shipments

def search_shipment_by_id(shipment_id: str) -> Optional[Dict]:
    """Search for shipment by ID in state index."""
    shipments = get_all_shipments_from_index()
    for shipment in shipments:
        if shipment['shipment_id'] == shipment_id:
            return shipment
    return None

# ══════════════════════════════════════════════════════════════
# EVENTS (Append-Only Log)
# ══════════════════════════════════════════════════════════════

def append_shipment_event(event_data: Dict) -> None:
    """Append event to audit log."""
    with _csv_lock:
        file_exists = SHIPMENT_EVENTS_CSV.exists()
        
        with open(SHIPMENT_EVENTS_CSV, 'a', newline='', encoding='utf-8') as f:
            fieldnames = ['timestamp', 'shipment_id', 'event_type', 'previous_state', 
                         'new_state', 'role', 'metadata']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(event_data)

# ══════════════════════════════════════════════════════════════
# OVERRIDES
# ══════════════════════════════════════════════════════════════

def append_override(override_data: Dict) -> None:
    """Append override to history."""
    with _csv_lock:
        file_exists = SHIPMENT_OVERRIDES_CSV.exists()
        
        with open(SHIPMENT_OVERRIDES_CSV, 'a', newline='', encoding='utf-8') as f:
            fieldnames = ['timestamp', 'shipment_id', 'override_type', 
                         'reason', 'manager_name']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(override_data)

def get_override_status(shipment_id: str) -> Dict:
    """Get latest override status for shipment."""
    if not SHIPMENT_OVERRIDES_CSV.exists():
        return {'has_override': False, 'display': '—', 'type': None}
    
    with _csv_lock:
        with open(SHIPMENT_OVERRIDES_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            overrides = [row for row in reader if row['shipment_id'] == shipment_id]
    
    if not overrides:
        return {'has_override': False, 'display': '—', 'type': None}
    
    latest = overrides[-1]
    override_type = latest['override_type']
    
    display_map = {
        'APPROVED': '🟢 Approved',
        'HOLD': '🟡 Hold',
        'REJECTED': '🔴 Rejected',
        'MODIFIED': '🟡 Modified'
    }
    
    return {
        'has_override': True,
        'display': display_map.get(override_type, '🟡 Modified'),
        'type': override_type,
        'reason': latest.get('reason', '')
    }

# ══════════════════════════════════════════════════════════════
# STATE TRANSITIONS (Lifecycle Management)
# ══════════════════════════════════════════════════════════════

def transition_shipment_state(shipment_id: str, from_state: str, to_state: str, 
                              role: str, event_type: str, metadata: str = "") -> bool:
    """
    Transition shipment from one state to another.
    Updates state index and appends event.
    """
    # Append event
    append_shipment_event({
        'timestamp': datetime.now().isoformat(),
        'shipment_id': shipment_id,
        'event_type': event_type,
        'previous_state': from_state,
        'new_state': to_state,
        'role': role,
        'metadata': metadata
    })
    
    # Update state index
    update_state_index(shipment_id, {
        'current_state': to_state,
        'last_event_time': datetime.now().isoformat()
    })
    
    return True
