# Event Catalog

## Purpose
This document lists all canonical domain events
used in the National Logistics Control Tower.

Events are the ONLY mechanism by which
the parcel lifecycle progresses.

---

## Core Principles

- Events are immutable
- Events are append-only
- Events represent facts, not intentions
- Events are idempotent
- Events are replayable

---

## Canonical Lifecycle Events

### EVENT: SHIPMENT_CREATED
Triggered When:
- Sender submits shipment intent

Lifecycle Impact:
- Initializes lifecycle at CREATED

Emitted By:
- Sender system

---

### EVENT: MANAGER_APPROVED
Triggered When:
- Sender Manager approves shipment

Lifecycle Impact:
- CREATED ? MANAGER_APPROVED

Emitted By:
- Sender Manager

---

### EVENT: MANAGER_ON_HOLD
Triggered When:
- Sender Manager places shipment on hold

Lifecycle Impact:
- CREATED ? MANAGER_ON_HOLD

Emitted By:
- Sender Manager

---

### EVENT: SUPERVISOR_APPROVED
Triggered When:
- Sender Supervisor confirms dispatch readiness

Lifecycle Impact:
- MANAGER_APPROVED ? SUPERVISOR_APPROVED

Emitted By:
- Sender Supervisor

---

### EVENT: DISPATCHED
Triggered When:
- Shipment leaves Sender ecosystem

Lifecycle Impact:
- SUPERVISOR_APPROVED ? IN_TRANSIT

Emitted By:
- System (on Supervisor confirmation)

---

### EVENT: RECEIVER_ACKNOWLEDGED
Triggered When:
- Receiver Manager confirms receipt

Lifecycle Impact:
- IN_TRANSIT ? RECEIVER_ACKNOWLEDGED

Emitted By:
- Receiver Manager

---

### EVENT: WAREHOUSE_INTAKE_STARTED
Triggered When:
- Shipment enters warehouse queue

Lifecycle Impact:
- RECEIVER_ACKNOWLEDGED ? WAREHOUSE_INTAKE

Emitted By:
- System

---

### EVENT: OUT_FOR_DELIVERY
Triggered When:
- Shipment released for last-mile delivery

Lifecycle Impact:
- WAREHOUSE_INTAKE ? OUT_FOR_DELIVERY

Emitted By:
- Warehouse Manager

---

### EVENT: DELIVERY_FAILED
Triggered When:
- Delivery attempt fails

Lifecycle Impact:
- OUT_FOR_DELIVERY ? DELIVERY_FAILED

Emitted By:
- System / Delivery execution

---

### EVENT: DELIVERY_CONFIRMED
Triggered When:
- Customer confirms delivery

Lifecycle Impact:
- OUT_FOR_DELIVERY ? DELIVERED

Emitted By:
- Customer

---

### EVENT: LIFECYCLE_CLOSED
Triggered When:
- Shipment lifecycle is finalized

Lifecycle Impact:
- DELIVERED ? LIFECYCLE_CLOSED

Emitted By:
- System

---

## Forbidden Events

The following events must NEVER exist:

- FORCE_STATE_CHANGE
- MANUAL_OVERRIDE_STATE
- ADMIN_EDIT_EVENT
- DELETE_EVENT

These violate audit integrity.

---

## Why This Catalog Exists

This catalog ensures:
- Predictable lifecycle progression
- Event-driven truth
- Safe replay and recovery
- Audit and compliance readiness

This document is FINAL once Step 1.3 is locked.
