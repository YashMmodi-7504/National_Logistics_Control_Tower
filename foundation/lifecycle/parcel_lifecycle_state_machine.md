# Parcel Lifecycle State Machine

## Purpose
This document defines the single authoritative lifecycle state machine
for all parcels in the National Logistics Control Tower.

All system behavior, permissions, events, analytics, and audits
must conform to this lifecycle.

---

## Core Design Principles

- Lifecycle is linear with controlled loops
- No state can be skipped
- Every transition is event-driven
- Each state has a single owning role
- Closed states are immutable

---

## Lifecycle States (IN ORDER)

### 1. CREATED
Owner: Sender

Description:
- Shipment intent is created
- Only minimal inputs exist (shipment ID, source, destination)
- AI enrichment occurs here
- No approvals yet

Allowed Transitions:
- ? MANAGER_APPROVED
- ? MANAGER_ON_HOLD

---

### 2. MANAGER_ON_HOLD
Owner: Sender Manager

Description:
- Shipment is paused for review or clarification
- No execution allowed

Allowed Transitions:
- ? MANAGER_APPROVED
- ? CANCELLED (optional, future)

---

### 3. MANAGER_APPROVED
Owner: Sender Manager

Description:
- Manager has approved or overridden AI recommendation
- Shipment is cleared for supervisor intake

Allowed Transitions:
- ? SUPERVISOR_APPROVED

---

### 4. SUPERVISOR_APPROVED
Owner: Sender Supervisor

Description:
- Supervisor confirms execution readiness
- Load planning and batching permitted

Allowed Transitions:
- ? IN_TRANSIT

---

### 5. IN_TRANSIT
Owner: System (Handover State)

Description:
- Shipment has left Sender ecosystem
- Receiver-side responsibility begins
- No sender-side actions allowed

Allowed Transitions:
- ? RECEIVER_ACKNOWLEDGED

---

### 6. RECEIVER_ACKNOWLEDGED
Owner: Receiver Manager

Description:
- Receiver confirms physical receipt
- Receipt may be full, partial, or damaged

Allowed Transitions:
- ? WAREHOUSE_INTAKE

---

### 7. WAREHOUSE_INTAKE
Owner: Warehouse / Hub Manager

Description:
- Shipment enters warehouse execution queue
- SLA recalculated
- AI prioritization applies

Allowed Transitions:
- ? OUT_FOR_DELIVERY

---

### 8. OUT_FOR_DELIVERY
Owner: Warehouse / Delivery Execution

Description:
- Shipment released for last-mile delivery
- Customer expectation begins

Allowed Transitions:
- ? DELIVERY_FAILED
- ? DELIVERED

---

### 9. DELIVERY_FAILED
Owner: System (Execution)

Description:
- Delivery attempt failed
- Failure categorized
- Retry eligibility evaluated

Allowed Transitions:
- ? OUT_FOR_DELIVERY
- ? ESCALATED (optional, future)

---

### 10. DELIVERED
Owner: Customer

Description:
- Customer confirms successful delivery
- Execution completed

Allowed Transitions:
- ? LIFECYCLE_CLOSED

---

### 11. LIFECYCLE_CLOSED
Owner: System (Terminal State)

Description:
- Shipment lifecycle is complete
- All data is immutable
- Analytics and audit only

Allowed Transitions:
- NONE (terminal)

---

## Forbidden Transitions (EXAMPLES)

The following are explicitly forbidden:

- CREATED ? SUPERVISOR_APPROVED
- MANAGER_APPROVED ? OUT_FOR_DELIVERY
- IN_TRANSIT ? OUT_FOR_DELIVERY
- RECEIVER_ACKNOWLEDGED ? DELIVERED
- DELIVERED ? any previous state

Any attempt to violate transitions must be blocked.

---

## Immutability Rules

- States before LIFECYCLE_CLOSED allow controlled transitions only
- After LIFECYCLE_CLOSED:
  - No edits
  - No events
  - No overrides
  - No recalculations

---

## Why This Lifecycle Exists

This lifecycle ensures:
- Clear ownership at every step
- No ambiguity in responsibility
- Event-driven consistency
- Legal and audit defensibility
- Real-world logistics realism

This document is FINAL once Step 1.2 is locked.
