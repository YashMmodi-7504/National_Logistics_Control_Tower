# Production-Grade Event Sourcing System
## National Logistics Control Tower

---

## 🎯 ARCHITECTURE OVERVIEW

This system implements a **production-grade event sourcing architecture** with:

- ✅ **Single Source of Truth**: One append-only log file
- ✅ **Immutable Shipment IDs**: Generated once, never changed
- ✅ **Event Sequencing**: Strict ordering with `event_seq`
- ✅ **Audit-Safe**: Complete history preserved
- ✅ **State Reconstruction**: Current state derived from events

---

## 📁 FOLDER STRUCTURE

```
d:\National-Logistics-Control-Tower\National-Logistics-Control-Tower\
│
├── app/
│   └── storage/
│       └── event_log.py          # Event sourcing engine
│
├── data/
│   └── logs/
│       ├── shipments.jsonl       # 🔥 THE SINGLE SOURCE OF TRUTH
│       └── shipment_counter.jsonl # Shipment ID counter (append-only)
│
└── app.py                         # Main application
```

---

## 🔄 EVENT SCHEMA

Every log entry follows this strict schema:

```json
{
  "shipment_id": "SHP-0000000001",
  "event_seq": 1,
  "event_type": "CREATED",
  "timestamp": "2026-01-21T12:00:00.000Z",
  "actor": "SENDER",
  "payload": {
    "source": "Mumbai, Maharashtra",
    "destination": "Delhi, Delhi",
    "weight_kg": 5.0,
    "delivery_type": "EXPRESS"
  }
}
```

### Field Descriptions:

- **shipment_id**: Immutable unique identifier (generated once)
- **event_seq**: Sequential number (1, 2, 3, ...) ensuring ordering
- **event_type**: Type of event (see Event Flow below)
- **timestamp**: ISO-8601 UTC timestamp
- **actor**: Who triggered the event
- **payload**: Event-specific data

---

## 🚦 STANDARD EVENT FLOW

```
CREATED
  ↓
MANAGER_APPROVED
  ↓
SUPERVISOR_APPROVED
  ↓
IN_TRANSIT
  ↓
RECEIVER_ACKNOWLEDGED
  ↓
WAREHOUSE_INTAKE
  ↓
OUT_FOR_DELIVERY
  ↓
DELIVERED
```

### Event Types:

| Event Type | Actor | Description |
|-----------|-------|-------------|
| `CREATED` | SENDER | Shipment created |
| `MANAGER_APPROVED` | SENDER_MANAGER | Manager approval |
| `OVERRIDE_APPLIED` | SENDER_MANAGER | Manager override applied |
| `SUPERVISOR_APPROVED` | SENDER_SUPERVISOR | Supervisor approval |
| `IN_TRANSIT` | SYSTEM | Dispatched by system |
| `RECEIVER_ACKNOWLEDGED` | RECEIVER | Receiver confirmed |
| `WAREHOUSE_INTAKE` | WAREHOUSE | Warehouse received |
| `OUT_FOR_DELIVERY` | WAREHOUSE | Out for delivery |
| `DELIVERED` | CUSTOMER | Customer confirmed |
| `CANCELLED` | * | Shipment cancelled |

---

## 🆔 SHIPMENT ID GENERATION

### Strategy: Sequential, Immutable

**Format**: `SHP-0000000001`, `SHP-0000000002`, ...

### Guarantees:

1. **Generated Once**: ID created during CREATED event only
2. **Never Regenerated**: Same shipment = same ID forever
3. **Thread-Safe**: Uses file locking for concurrent writes
4. **Persistent**: Counter stored in append-only log

### Implementation:

```python
from app.storage.event_log import generate_shipment_id

# Generate ID (happens automatically during create_shipment)
shipment_id = generate_shipment_id()
# Returns: "SHP-0000000001"
```

### Counter Log Example (`shipment_counter.jsonl`):

```json
{"counter": 1, "timestamp": "2026-01-21T12:00:00.000Z", "action": "ID_GENERATED"}
{"counter": 2, "timestamp": "2026-01-21T12:05:00.000Z", "action": "ID_GENERATED"}
{"counter": 3, "timestamp": "2026-01-21T12:10:00.000Z", "action": "ID_GENERATED"}
```

---

## 📝 APPEND-ONLY LOGGING

### Core Principle: NEVER OVERWRITE

**Rule**: Every state change creates a new event. No updates, only appends.

### Central Log Writer:

```python
from app.storage.event_log import append_event, EventType, Actor

# Append event (thread-safe)
event = append_event(
    shipment_id="SHP-0000000001",
    event_type=EventType.MANAGER_APPROVED,
    actor=Actor.SENDER_MANAGER,
    payload={"approval_type": "manual"}
)
```

### Log File Example (`shipments.jsonl`):

```json
{"shipment_id": "SHP-0000000001", "event_seq": 1, "event_type": "CREATED", "timestamp": "2026-01-21T12:00:00.000Z", "actor": "SENDER", "payload": {"source": "Mumbai", "destination": "Delhi", "weight_kg": 5.0}}
{"shipment_id": "SHP-0000000001", "event_seq": 2, "event_type": "MANAGER_APPROVED", "timestamp": "2026-01-21T12:10:00.000Z", "actor": "SENDER_MANAGER", "payload": {"approval_type": "manual"}}
{"shipment_id": "SHP-0000000001", "event_seq": 3, "event_type": "SUPERVISOR_APPROVED", "timestamp": "2026-01-21T12:20:00.000Z", "actor": "SENDER_SUPERVISOR", "payload": {"approval_type": "supervisor"}}
```

---

## 🔍 STATE RECONSTRUCTION

### How It Works:

Current state is **derived from events**, not stored separately.

### Example:

```python
from app.storage.event_log import reconstruct_shipment_state

# Reconstruct current state from events
state = reconstruct_shipment_state("SHP-0000000001")

print(state)
# {
#   "shipment_id": "SHP-0000000001",
#   "current_state": "SUPERVISOR_APPROVED",
#   "created_at": "2026-01-21T12:00:00.000Z",
#   "last_updated": "2026-01-21T12:20:00.000Z",
#   "event_count": 3,
#   "event_sequence": ["CREATED", "MANAGER_APPROVED", "SUPERVISOR_APPROVED"],
#   "full_history": [...],  # All events
#   "current_payload": {...}  # Merged payload
# }
```

---

## 📋 USAGE EXAMPLES

### 1. Create Shipment

```python
from app.storage.event_log import create_shipment

# Create new shipment (ID generated automatically)
shipment_id = create_shipment(
    source="Mumbai, Maharashtra",
    destination="Delhi, Delhi",
    weight_kg=5.0,
    delivery_type="EXPRESS"
)

print(shipment_id)  # SHP-0000000001
```

**What happens:**
1. Sequential ID generated: `SHP-0000000001`
2. Counter incremented in `shipment_counter.jsonl`
3. CREATED event appended to `shipments.jsonl`

### 2. Update Shipment (State Transition)

```python
from app.storage.event_log import transition_shipment, EventType, Actor

# Transition to MANAGER_APPROVED
transition_shipment(
    shipment_id="SHP-0000000001",
    to_state=EventType.MANAGER_APPROVED,
    actor=Actor.SENDER_MANAGER,
    approval_type="manual"
)
```

**What happens:**
1. Validates transition is allowed
2. Calculates next `event_seq` automatically
3. Appends MANAGER_APPROVED event to log
4. State changes from CREATED → MANAGER_APPROVED

### 3. Search Shipment

```python
from app.storage.event_log import search_shipment

# Search by ID
shipment = search_shipment("SHP-0000000001")

if shipment:
    print(f"Current state: {shipment['current_state']}")
    print(f"Event count: {shipment['event_count']}")
    print(f"Full history: {shipment['full_history']}")
else:
    print("Shipment not found")
```

### 4. Get All Shipments by State

```python
from app.storage.event_log import get_all_shipments_by_state

# Get all shipments in CREATED state
created_shipments = get_all_shipments_by_state("CREATED")

for ship in created_shipments:
    print(f"{ship['shipment_id']}: {ship['current_state']}")
```

### 5. Audit Report

```python
from app.storage.event_log import get_audit_report, verify_log_integrity

# Generate audit report
report = get_audit_report()
print(f"Total events: {report['total_events']}")
print(f"Total shipments: {report['total_shipments']}")
print(f"Log integrity: {report['log_integrity']}")

# Verify integrity
is_valid, errors = verify_log_integrity()
if is_valid:
    print("✅ Log is valid")
else:
    print(f"❌ Log has errors: {errors}")
```

---

## 🛡️ GUARANTEES & SAFETY

### 1. ID Continuity

✅ **Guarantee**: Same shipment always has same ID

- ID generated once during creation
- Never regenerated or changed
- Persisted in append-only counter log

### 2. Event Ordering

✅ **Guarantee**: Events are strictly ordered

- Each event has sequential `event_seq`
- System validates transitions
- Prevents invalid state changes

### 3. No Log Mismatch

✅ **Guarantee**: Single source of truth

- All flows write to same log file
- No separate logs for sender/receiver/etc
- State reconstruction always consistent

### 4. Audit Safety

✅ **Guarantee**: Complete history preserved

- Never overwrite events
- Full audit trail available
- Can replay events to any point in time

### 5. Concurrency Safety

✅ **Guarantee**: Thread-safe writes

- File locking prevents race conditions
- Atomic writes ensure consistency
- Multiple processes can write safely

---

## 🚫 STRICT RULES (ENFORCED BY SYSTEM)

### ❌ DO NOT:

1. **Create multiple log files** → Use `shipments.jsonl` only
2. **Overwrite existing events** → Append only
3. **Regenerate shipment IDs** → ID generated once
4. **Skip event sequencing** → System auto-calculates
5. **Write unordered events** → Transitions validated

### ✅ DO:

1. **Always use event sourcing functions** → `create_shipment()`, `transition_shipment()`
2. **Reconstruct state from events** → Use `reconstruct_shipment_state()`
3. **Validate log integrity** → Use `verify_log_integrity()`
4. **Generate audit reports** → Use `get_audit_report()`

---

## 🔮 FUTURE EXTENSIBILITY

### Easy Migration Paths:

1. **Kafka Integration**:
   ```python
   # Replace file writes with Kafka producer
   producer.send('shipment-events', event)
   ```

2. **Database Integration**:
   ```python
   # Replace file reads with database queries
   events = db.query("SELECT * FROM shipment_events WHERE shipment_id = ?")
   ```

3. **AI Analytics**:
   ```python
   # Feed events to ML pipeline
   for event in read_all_events():
       analytics_engine.process(event)
   ```

---

## 📊 DEMO WORKFLOW

### Complete End-to-End Example:

```python
from app.storage.event_log import *

# 1. Create shipment
ship_id = create_shipment(
    source="Mumbai",
    destination="Delhi",
    weight_kg=10.0,
    delivery_type="EXPRESS"
)
print(f"✅ Created: {ship_id}")

# 2. Manager approves
transition_shipment(ship_id, EventType.MANAGER_APPROVED, Actor.SENDER_MANAGER)
print(f"✅ Manager approved: {ship_id}")

# 3. Supervisor approves
transition_shipment(ship_id, EventType.SUPERVISOR_APPROVED, Actor.SENDER_SUPERVISOR)
print(f"✅ Supervisor approved: {ship_id}")

# 4. System dispatches
transition_shipment(ship_id, EventType.IN_TRANSIT, Actor.SYSTEM)
print(f"✅ Dispatched: {ship_id}")

# 5. Receiver acknowledges
transition_shipment(ship_id, EventType.RECEIVER_ACKNOWLEDGED, Actor.RECEIVER)
print(f"✅ Receiver acknowledged: {ship_id}")

# 6. Warehouse receives
transition_shipment(ship_id, EventType.WAREHOUSE_INTAKE, Actor.WAREHOUSE)
print(f"✅ Warehouse received: {ship_id}")

# 7. Out for delivery
transition_shipment(ship_id, EventType.OUT_FOR_DELIVERY, Actor.WAREHOUSE)
print(f"✅ Out for delivery: {ship_id}")

# 8. Customer confirms
transition_shipment(ship_id, EventType.DELIVERED, Actor.CUSTOMER)
print(f"✅ Delivered: {ship_id}")

# 9. Check final state
final_state = search_shipment(ship_id)
print(f"Final state: {final_state['current_state']}")
print(f"Event sequence: {final_state['event_sequence']}")
```

**Output:**
```
✅ Created: SHP-0000000001
✅ Manager approved: SHP-0000000001
✅ Supervisor approved: SHP-0000000001
✅ Dispatched: SHP-0000000001
✅ Receiver acknowledged: SHP-0000000001
✅ Warehouse received: SHP-0000000001
✅ Out for delivery: SHP-0000000001
✅ Delivered: SHP-0000000001
Final state: DELIVERED
Event sequence: ['CREATED', 'MANAGER_APPROVED', 'SUPERVISOR_APPROVED', 'IN_TRANSIT', 'RECEIVER_ACKNOWLEDGED', 'WAREHOUSE_INTAKE', 'OUT_FOR_DELIVERY', 'DELIVERED']
```

---

## ✅ PRODUCTION QUALITY CHECKLIST

- [x] Single source of truth
- [x] Append-only logging
- [x] Event sequencing
- [x] Immutable shipment IDs
- [x] Thread-safe writes
- [x] State reconstruction
- [x] Transition validation
- [x] Audit trail
- [x] Integrity verification
- [x] Timestamp monotonicity
- [x] Actor tracking
- [x] Payload merging
- [x] Error handling
- [x] Deterministic behavior
- [x] Scalability ready

---

## 🎓 BEST PRACTICES

### 1. Always Use Convenience Functions

**❌ Bad:**
```python
# Don't write to log directly
with open('shipments.jsonl', 'a') as f:
    f.write(json.dumps(event) + '\n')
```

**✅ Good:**
```python
# Use event sourcing functions
transition_shipment(ship_id, EventType.MANAGER_APPROVED, Actor.SENDER_MANAGER)
```

### 2. Reconstruct State, Don't Store It

**❌ Bad:**
```python
# Don't maintain separate state variables
current_state = "CREATED"
current_state = "MANAGER_APPROVED"  # Loses history
```

**✅ Good:**
```python
# Reconstruct from events
state = reconstruct_shipment_state(ship_id)
print(state['current_state'])
print(state['event_sequence'])  # Full history preserved
```

### 3. Validate Integrity Regularly

```python
# Run integrity check in CI/CD
is_valid, errors = verify_log_integrity()
assert is_valid, f"Log integrity failed: {errors}"
```

### 4. Generate Audit Reports

```python
# Daily audit report
report = get_audit_report()
send_to_compliance_team(report)
```

---

## 🏆 CONCLUSION

This event sourcing system is:

- **Production-grade**: Thread-safe, atomic writes, validated transitions
- **Audit-safe**: Complete history, integrity verification, timestamps
- **Deterministic**: Same events = same state always
- **Scalable**: Easy migration to Kafka/DB
- **AI-ready**: Events feed directly to analytics

**No demo shortcuts. No log mismatches. No ID continuity issues.**

---

**Author**: National Logistics Control Tower Team  
**Version**: 1.0 - Event Sourcing Architecture  
**Date**: January 21, 2026
