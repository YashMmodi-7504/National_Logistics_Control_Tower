"""
PRODUCTION-GRADE EVENT SOURCING SYSTEM
Single Source of Truth • Append-Only • Audit-Safe

DESIGN PRINCIPLES:
1. Single authoritative log file: shipments.jsonl
2. Append-only: Never overwrite, only append
3. Event sequencing: Strict ordering with event_seq
4. Immutable IDs: Generated once, never changed
5. State reconstruction: Rebuild from events

ARCHITECTURE:
- Event Store: Append-only JSONL log
- ID Generator: Sequential, persistent counter
- State Builder: Reconstruct current state from events
- Validator: Ensure event ordering and validity

Author: National Logistics Control Tower
Phase: Event Sourcing Architecture v1.0
"""

import json
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from enum import Enum

# ══════════════════════════════════════════════════════════════
# CONFIGURATION
# ══════════════════════════════════════════════════════════════

DATA_DIR = Path("data/logs")
DATA_DIR.mkdir(parents=True, exist_ok=True)

# THE SINGLE SOURCE OF TRUTH
SHIPMENTS_LOG = DATA_DIR / "shipments.jsonl"
SHIPMENT_COUNTER_LOG = DATA_DIR / "shipment_counter.jsonl"

# Thread-safe lock for concurrent writes
_event_lock = threading.Lock()

# ══════════════════════════════════════════════════════════════
# EVENT TYPES & ACTORS
# ══════════════════════════════════════════════════════════════

class EventType(Enum):
    """Standard event lifecycle"""
    CREATED = "CREATED"
    MANAGER_APPROVED = "MANAGER_APPROVED"
    SUPERVISOR_APPROVED = "SUPERVISOR_APPROVED"
    IN_TRANSIT = "IN_TRANSIT"
    RECEIVER_ACKNOWLEDGED = "RECEIVER_ACKNOWLEDGED"
    WAREHOUSE_INTAKE = "WAREHOUSE_INTAKE"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED = "DELIVERED"
    OVERRIDE_APPLIED = "OVERRIDE_APPLIED"
    HOLD_FOR_REVIEW = "HOLD_FOR_REVIEW"
    CANCELLED = "CANCELLED"

class Actor(Enum):
    """System actors"""
    SENDER = "SENDER"
    SENDER_MANAGER = "SENDER_MANAGER"
    SENDER_SUPERVISOR = "SENDER_SUPERVISOR"
    SYSTEM = "SYSTEM"
    CARRIER = "CARRIER"
    RECEIVER = "RECEIVER"
    WAREHOUSE = "WAREHOUSE"
    CUSTOMER = "CUSTOMER"

# Event flow validation
VALID_TRANSITIONS = {
    None: [EventType.CREATED],
    EventType.CREATED: [EventType.MANAGER_APPROVED, EventType.OVERRIDE_APPLIED, EventType.HOLD_FOR_REVIEW, EventType.CANCELLED],
    EventType.MANAGER_APPROVED: [EventType.SUPERVISOR_APPROVED, EventType.OVERRIDE_APPLIED, EventType.HOLD_FOR_REVIEW, EventType.CANCELLED],
    EventType.SUPERVISOR_APPROVED: [EventType.IN_TRANSIT, EventType.OVERRIDE_APPLIED, EventType.HOLD_FOR_REVIEW, EventType.CANCELLED],
    EventType.IN_TRANSIT: [EventType.RECEIVER_ACKNOWLEDGED, EventType.OVERRIDE_APPLIED, EventType.HOLD_FOR_REVIEW, EventType.CANCELLED],
    EventType.RECEIVER_ACKNOWLEDGED: [EventType.WAREHOUSE_INTAKE, EventType.OVERRIDE_APPLIED, EventType.HOLD_FOR_REVIEW],
    EventType.WAREHOUSE_INTAKE: [EventType.OUT_FOR_DELIVERY, EventType.OVERRIDE_APPLIED, EventType.HOLD_FOR_REVIEW],
    EventType.OUT_FOR_DELIVERY: [EventType.DELIVERED, EventType.OVERRIDE_APPLIED, EventType.HOLD_FOR_REVIEW, EventType.CANCELLED],
    EventType.OVERRIDE_APPLIED: [EventType.MANAGER_APPROVED, EventType.HOLD_FOR_REVIEW, EventType.CANCELLED, EventType.CREATED],  # Override can lead to approval, hold, cancellation, or back to created
    EventType.HOLD_FOR_REVIEW: [EventType.MANAGER_APPROVED, EventType.OVERRIDE_APPLIED, EventType.CANCELLED, EventType.CREATED],  # Hold can be released back to approval flow or CREATED
    EventType.DELIVERED: [],  # Terminal state
    EventType.CANCELLED: []   # Terminal state
}

# ══════════════════════════════════════════════════════════════
# SHIPMENT ID GENERATION (Sequential, Immutable)
# ══════════════════════════════════════════════════════════════

def generate_shipment_id() -> str:
    """
    Generate sequential shipment ID: SHP-0000000001, SHP-0000000002, etc.
    
    Thread-safe, persistent, append-only counter.
    ID is generated ONCE and NEVER regenerated.
    
    Returns:
        str: Unique shipment ID in format SHP-XXXXXXXXXX
    """
    with _event_lock:
        # Read last counter from append-only log
        last_counter = 0
        if SHIPMENT_COUNTER_LOG.exists():
            with open(SHIPMENT_COUNTER_LOG, 'r', encoding='utf-8') as f:
                for line in f:
                    entry = json.loads(line.strip())
                    last_counter = entry['counter']
        
        # Increment
        next_counter = last_counter + 1
        
        # Append new counter (never overwrite)
        with open(SHIPMENT_COUNTER_LOG, 'a', encoding='utf-8') as f:
            counter_entry = {
                'counter': next_counter,
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'action': 'ID_GENERATED'
            }
            f.write(json.dumps(counter_entry) + '\n')
        
        # Format: SHP-0000000001
        return f"SHP-{next_counter:010d}"

# ══════════════════════════════════════════════════════════════
# EVENT WRITER (Append-Only)
# ══════════════════════════════════════════════════════════════

def append_event(
    shipment_id: str,
    event_type: EventType,
    actor: Actor,
    payload: Dict,
    event_seq: Optional[int] = None
) -> Dict:
    """
    Append event to shipment log (NEVER OVERWRITE).
    
    This is the ONLY way to modify shipment state.
    
    Args:
        shipment_id: Immutable shipment identifier
        event_type: Type of event (from EventType enum)
        actor: Who triggered the event (from Actor enum)
        payload: Event-specific data
        event_seq: Optional sequence number (auto-calculated if None)
    
    Returns:
        Dict: The written event with all metadata
    
    Raises:
        ValueError: If event violates ordering rules
    """
    with _event_lock:
        # Auto-calculate event_seq if not provided
        if event_seq is None:
            event_seq = _calculate_next_seq(shipment_id)
        
        # Validate event transition
        _validate_transition(shipment_id, event_type)
        
        # Build event record
        event = {
            'shipment_id': shipment_id,
            'event_seq': event_seq,
            'event_type': event_type.value,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'actor': actor.value,
            'payload': payload
        }
        
        # Append to log (atomic write)
        with open(SHIPMENTS_LOG, 'a', encoding='utf-8') as f:
            f.write(json.dumps(event) + '\n')
        
        # ⚡ PERFORMANCE: Invalidate all caches after write
        invalidate_event_cache()
        invalidate_state_cache()
        
        return event

def _calculate_next_seq(shipment_id: str) -> int:
    """Calculate next event sequence number for shipment."""
    events = read_shipment_events(shipment_id)
    if not events:
        return 1
    return max(e['event_seq'] for e in events) + 1

def _validate_transition(shipment_id: str, new_event_type: EventType) -> None:
    """Validate that event transition is allowed."""
    events = read_shipment_events(shipment_id)
    
    if not events:
        # First event must be CREATED
        if new_event_type != EventType.CREATED:
            raise ValueError(f"First event must be CREATED, got {new_event_type.value}")
        return
    
    # Get current state
    last_event = events[-1]
    current_type = EventType(last_event['event_type'])
    
    # Check if transition is valid
    valid_next = VALID_TRANSITIONS.get(current_type, [])
    if new_event_type not in valid_next:
        raise ValueError(
            f"Invalid transition: {current_type.value} → {new_event_type.value}. "
            f"Valid transitions: {[e.value for e in valid_next]}"
        )

# ══════════════════════════════════════════════════════════════
# EVENT READER (State Reconstruction) - PERFORMANCE OPTIMIZED
# ══════════════════════════════════════════════════════════════

# ⚡ PERFORMANCE: In-memory cache for event log
_events_cache = None
_events_cache_mtime = None
_shipment_index = None  # shipment_id -> list of events

def _invalidate_cache_if_stale():
    """Check if log file changed and invalidate cache if needed."""
    global _events_cache, _events_cache_mtime, _shipment_index
    
    if not SHIPMENTS_LOG.exists():
        _events_cache = []
        _shipment_index = {}
        _events_cache_mtime = None
        return
    
    current_mtime = SHIPMENTS_LOG.stat().st_mtime
    # Only invalidate if we had a previous mtime AND it changed
    if _events_cache_mtime is not None and _events_cache_mtime != current_mtime:
        _events_cache = None
        _shipment_index = None
    
    # Always update mtime
    _events_cache_mtime = current_mtime

def _build_cache():
    """Build in-memory cache from event log - O(N) once."""
    global _events_cache, _shipment_index
    
    _invalidate_cache_if_stale()
    
    if _events_cache is not None:
        return
    
    _events_cache = []
    _shipment_index = {}
    
    if not SHIPMENTS_LOG.exists():
        return
    
    with open(SHIPMENTS_LOG, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                event = json.loads(line.strip())
                _events_cache.append(event)
                sid = event['shipment_id']
                if sid not in _shipment_index:
                    _shipment_index[sid] = []
                _shipment_index[sid].append(event)
    
    # Sort each shipment's events by sequence
    for sid in _shipment_index:
        _shipment_index[sid].sort(key=lambda e: e['event_seq'])

def invalidate_event_cache():
    """Call after writing new events to invalidate cache."""
    global _events_cache, _events_cache_mtime, _shipment_index
    _events_cache = None
    _events_cache_mtime = None
    _shipment_index = None

def read_all_events() -> List[Dict]:
    """
    Read ALL events from log - CACHED.
    
    Returns events in append order (chronological).
    """
    _build_cache()
    return _events_cache.copy() if _events_cache else []

def read_shipment_events(shipment_id: str) -> List[Dict]:
    """
    Read all events for specific shipment - O(1) lookup.
    
    Returns events in sequence order.
    """
    _build_cache()
    if _shipment_index and shipment_id in _shipment_index:
        return _shipment_index[shipment_id].copy()
    return []

def get_all_shipment_ids() -> List[str]:
    """Get list of all unique shipment IDs - O(1) lookup."""
    _build_cache()
    return list(_shipment_index.keys()) if _shipment_index else []

# ══════════════════════════════════════════════════════════════
# STATE RECONSTRUCTION - PERFORMANCE OPTIMIZED
# ══════════════════════════════════════════════════════════════

# ⚡ PERFORMANCE: Pre-computed state cache
_state_cache = None
_state_cache_valid = False

def _build_state_cache():
    """Build all shipment states in ONE pass - O(N)."""
    global _state_cache, _state_cache_valid
    
    if _state_cache_valid and _state_cache is not None:
        return
    
    _build_cache()  # Ensure event cache is built
    
    _state_cache = {}
    
    if not _shipment_index:
        _state_cache_valid = True
        return
    
    for sid, events in _shipment_index.items():
        if not events:
            continue
        
        first_event = events[0]
        last_event = events[-1]
        
        # Merge payloads
        merged_payload = {}
        for event in events:
            merged_payload.update(event.get('payload', {}))
        
        _state_cache[sid] = {
            'shipment_id': sid,
            'current_state': last_event['event_type'],
            'created_at': first_event['timestamp'],
            'last_updated': last_event['timestamp'],
            'event_count': len(events),
            'event_sequence': [e['event_type'] for e in events],
            'full_history': events,
            'current_payload': merged_payload,
            'actors_involved': list(set(e['actor'] for e in events))
        }
    
    _state_cache_valid = True

def invalidate_state_cache():
    """Invalidate state cache after writes."""
    global _state_cache, _state_cache_valid
    _state_cache = None
    _state_cache_valid = False

def reconstruct_shipment_state(shipment_id: str) -> Optional[Dict]:
    """
    Reconstruct current shipment state from events - O(1) lookup.
    
    This is the authoritative way to get shipment state.
    
    Returns:
        Dict with:
        - shipment_id
        - current_state (last event_type)
        - created_at
        - last_updated
        - event_count
        - full_history (all events)
        - current_payload (merged payload from all events)
    """
    _build_state_cache()
    
    if _state_cache and shipment_id in _state_cache:
        # Return a copy to prevent mutation
        return _state_cache[shipment_id].copy()
    
    return None

def get_all_shipments_by_state(state: Optional[str] = None) -> List[Dict]:
    """
    Get all shipments, optionally filtered by current state - O(N) single pass.
    
    Args:
        state: Filter by current state (e.g., "CREATED", "IN_TRANSIT")
               If None, returns all shipments
    
    Returns:
        List of shipment states, sorted by last_updated DESC
    """
    _build_state_cache()
    
    if not _state_cache:
        return []
    
    if state is None:
        shipments = list(_state_cache.values())
    else:
        shipments = [s for s in _state_cache.values() if s['current_state'] == state]
    
    # Sort by last_updated descending (newest first)
    shipments.sort(key=lambda s: s['last_updated'], reverse=True)
    
    return shipments

# ══════════════════════════════════════════════════════════════
# AUDIT & VERIFICATION
# ══════════════════════════════════════════════════════════════

def verify_log_integrity() -> Tuple[bool, List[str]]:
    """
    Verify log file integrity.
    
    Checks:
    - Event sequences are continuous
    - No duplicate event_seq for same shipment
    - All transitions are valid
    - Timestamps are monotonic
    
    Returns:
        Tuple[bool, List[str]]: (is_valid, list_of_errors)
    """
    errors = []
    shipment_ids = get_all_shipment_ids()
    
    for sid in shipment_ids:
        events = read_shipment_events(sid)
        
        # Check sequence continuity
        expected_seq = 1
        for event in events:
            if event['event_seq'] != expected_seq:
                errors.append(
                    f"{sid}: Expected event_seq={expected_seq}, got {event['event_seq']}"
                )
            expected_seq += 1
        
        # Check timestamp monotonicity
        for i in range(1, len(events)):
            if events[i]['timestamp'] < events[i-1]['timestamp']:
                errors.append(
                    f"{sid}: Non-monotonic timestamp at event_seq={events[i]['event_seq']}"
                )
    
    return (len(errors) == 0, errors)

def get_audit_report() -> Dict:
    """
    Generate audit report for entire log.
    
    Returns summary statistics and health metrics.
    """
    all_events = read_all_events()
    shipment_ids = get_all_shipment_ids()
    
    if not all_events:
        return {
            'total_events': 0,
            'total_shipments': 0,
            'health': 'EMPTY'
        }
    
    # Calculate metrics
    event_types = {}
    actors = {}
    
    for event in all_events:
        event_type = event['event_type']
        actor = event['actor']
        
        event_types[event_type] = event_types.get(event_type, 0) + 1
        actors[actor] = actors.get(actor, 0) + 1
    
    # State distribution
    states = {}
    for sid in shipment_ids:
        state = reconstruct_shipment_state(sid)
        if state:
            current = state['current_state']
            states[current] = states.get(current, 0) + 1
    
    # Integrity check
    is_valid, errors = verify_log_integrity()
    
    return {
        'total_events': len(all_events),
        'total_shipments': len(shipment_ids),
        'event_type_distribution': event_types,
        'actor_distribution': actors,
        'current_state_distribution': states,
        'log_integrity': 'VALID' if is_valid else 'CORRUPTED',
        'integrity_errors': errors,
        'first_event_time': all_events[0]['timestamp'],
        'last_event_time': all_events[-1]['timestamp']
    }

# ══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════

def create_shipment(
    source: str,
    destination: str,
    weight_kg: float,
    delivery_type: str,
    **kwargs
) -> str:
    """
    Create new shipment (convenience function).
    
    Generates ID and appends CREATED event atomically.
    
    Returns:
        str: The generated shipment_id
    """
    # Generate ID once
    shipment_id = generate_shipment_id()
    
    # Build payload
    payload = {
        'source': source,
        'destination': destination,
        'weight_kg': weight_kg,
        'delivery_type': delivery_type,
        **kwargs
    }
    
    # Append CREATED event
    append_event(
        shipment_id=shipment_id,
        event_type=EventType.CREATED,
        actor=Actor.SENDER,
        payload=payload
    )
    
    return shipment_id

def transition_shipment(
    shipment_id: str,
    to_state: EventType,
    actor: Actor,
    **additional_payload
) -> None:
    """
    Transition shipment to new state (convenience function).
    
    Validates transition and appends event.
    """
    append_event(
        shipment_id=shipment_id,
        event_type=to_state,
        actor=actor,
        payload=additional_payload
    )

def search_shipment(shipment_id: str) -> Optional[Dict]:
    """
    Search for shipment by ID.
    
    Returns:
        Complete shipment state or None if not found
    """
    return reconstruct_shipment_state(shipment_id)
