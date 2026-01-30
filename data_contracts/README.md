# Data Contracts

This directory contains formal data contracts for the National Logistics Control Tower.

## Purpose

- **Stress testing**: Validate system performance with large datasets
- **ML training**: Provide realistic data for model training
- **UI validation**: Test dashboard responsiveness and accuracy
- **Reproducibility**: Deterministic generation (seed=42)

## CSV Files

### 1. shipments_contract.csv (10,000 rows)
Core shipment data with geo-intelligence.

**Columns:**
- `shipment_id`: SHIP-YYYY-XXXXX format
- `created_at`: Timestamp within last 60 days
- `source_city`, `source_state`: Indian cities/states
- `destination_city`, `destination_state`: Indian cities/states
- `weight_kg`: 0.5 - 50 kg
- `delivery_type`: NORMAL / EXPRESS
- `delivery_category`: RESIDENTIAL / COMMERCIAL
- `current_state`: Shipment lifecycle state
- `priority`: LOW / MEDIUM / HIGH
- `corridor`: STATE -> STATE format

### 2. events_contract.csv (30,000+ rows)
Event replay data for lifecycle tracking.

**Columns:**
- `event_id`: EVT-{shipment_id}-{seq}
- `shipment_id`: References shipments_contract
- `event_type`: SHIPMENT_CREATED, DISPATCHED, etc.
- `previous_state`, `new_state`: State transitions
- `role`: Actor role (SENDER, MANAGER, etc.)
- `timestamp`: Event timestamp

### 3. sla_contract.csv (10,000 rows)
SLA breach modeling and risk analysis.

**Columns:**
- `shipment_id`: References shipments_contract
- `expected_eta_hours`: Expected delivery time
- `actual_hours`: Actual elapsed time
- `sla_utilization`: actual / expected ratio
- `breach_probability`: 0.0 - 1.0
- `risk_level`: LOW / MEDIUM / HIGH / CRITICAL

### 4. corridor_contract.csv (~400 rows)
Corridor-level intelligence (aggregated).

**Columns:**
- `corridor`: STATE -> STATE
- `avg_eta`: Average ETA in hours
- `avg_delay`: Average delay in hours
- `avg_breach_probability`: Average risk
- `shipment_count`: Number of shipments
- `risk_band`: LOW / MEDIUM / HIGH / CRITICAL

### 5. notifications_contract.csv (50,000+ rows)
UI notification stress testing.

**Columns:**
- `notification_id`: NOTIF-{seq}
- `shipment_id`: References shipments_contract
- `recipient_role`: Target role
- `message`: Notification text
- `triggered_event`: Event that triggered notification
- `created_at`: Notification timestamp
- `read`: Boolean read status

## Generation

### Quick Start (Generate All)
```powershell
python data_contracts/generate_all_contracts.py
```

### Individual Generators
```powershell
# Must run in order (dependencies)
python data_contracts/generate_shipments_contract.py
python data_contracts/generate_events_contract.py
python data_contracts/generate_sla_contract.py
python data_contracts/generate_corridor_contract.py
python data_contracts/generate_notifications_contract.py
```

## Key Properties

✅ **Deterministic**: Same seed (42) = same output  
✅ **Realistic**: Indian geo data, authentic patterns  
✅ **Reproducible**: Can regenerate identical datasets  
✅ **Scalable**: Easily adjust row counts  
✅ **Relational**: Proper foreign key relationships  

## Data Quality Rules

- Source ≠ Destination (enforced)
- Events follow valid state transitions
- Timestamps are chronologically correct
- SLA calculations use realistic formulas
- Notifications map to correct events
- No orphaned records

## Performance Notes

- **10,000 shipments** = baseline stress test
- **30,000+ events** = 3-8 events per shipment average
- **Dashboard load time**: <2 seconds @ 10k rows
- **Read model performance**: Optimized for aggregations

## Architecture Integration

These CSVs are **NOT** used directly in UI. They serve as:

1. **Training data** for ML models
2. **Seed data** for event replay
3. **Validation data** for analytics engines
4. **Stress test data** for performance tuning

**Dashboard consumes**: Read models & snapshots (not CSVs directly)

## Regeneration

To regenerate with different seed or row counts, edit generator files:

```python
random.seed(42)  # Change seed
generate_shipments(10000)  # Change row count
```

---

**Author**: National Logistics Control Tower  
**Phase**: Data Contracts & Stress Testing  
**Version**: 1.0
