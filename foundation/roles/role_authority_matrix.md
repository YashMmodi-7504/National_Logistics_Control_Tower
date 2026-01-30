# Role Authority Enforcement Model

## Purpose
This document defines the authority boundaries for every role
across every parcel lifecycle state.

This matrix is enforced at:
- Event emission layer
- API layer
- UI layer
- Audit layer

No code may bypass this model.

---

## Core Authority Principles

- Authority is role-based, not user-based
- A role owns specific lifecycle states
- A role may emit only allowed events
- Authority is revoked permanently after handover
- No emergency or admin bypass exists

---

## Roles Defined

Sender Roles:
- SENDER
- SENDER_MANAGER
- SENDER_SUPERVISOR

Receiver Roles:
- RECEIVER_MANAGER
- WAREHOUSE_MANAGER
- CUSTOMER

System Roles:
- SYSTEM (automated, no human login)

---

## Authority Matrix (State × Role × Allowed Events)

### STATE: CREATED
Owner: SENDER

Allowed:
- SENDER ? SHIPMENT_CREATED

Denied:
- All other roles

---

### STATE: MANAGER_ON_HOLD
Owner: SENDER_MANAGER

Allowed:
- SENDER_MANAGER ? MANAGER_APPROVED
- SENDER_MANAGER ? MANAGER_ON_HOLD

Denied:
- SENDER
- SENDER_SUPERVISOR
- Receiver roles

---

### STATE: MANAGER_APPROVED
Owner: SENDER_MANAGER

Allowed:
- SENDER_SUPERVISOR ? SUPERVISOR_APPROVED

Denied:
- SENDER
- SENDER_MANAGER
- Receiver roles

---

### STATE: SUPERVISOR_APPROVED
Owner: SENDER_SUPERVISOR

Allowed:
- SYSTEM ? DISPATCHED

Denied:
- All human roles

---

### STATE: IN_TRANSIT
Owner: SYSTEM

Allowed:
- RECEIVER_MANAGER ? RECEIVER_ACKNOWLEDGED

Denied:
- Sender roles
- Warehouse roles
- Customer

---

### STATE: RECEIVER_ACKNOWLEDGED
Owner: RECEIVER_MANAGER

Allowed:
- SYSTEM ? WAREHOUSE_INTAKE_STARTED

Denied:
- Sender roles
- Customer

---

### STATE: WAREHOUSE_INTAKE
Owner: WAREHOUSE_MANAGER

Allowed:
- WAREHOUSE_MANAGER ? OUT_FOR_DELIVERY

Denied:
- Receiver Manager
- Sender roles
- Customer

---

### STATE: OUT_FOR_DELIVERY
Owner: WAREHOUSE_MANAGER

Allowed:
- SYSTEM ? DELIVERY_FAILED
- CUSTOMER ? DELIVERY_CONFIRMED

Denied:
- Sender roles
- Receiver Manager

---

### STATE: DELIVERY_FAILED
Owner: SYSTEM

Allowed:
- SYSTEM ? OUT_FOR_DELIVERY

Denied:
- All human roles

---

### STATE: DELIVERED
Owner: CUSTOMER

Allowed:
- SYSTEM ? LIFECYCLE_CLOSED

Denied:
- All human roles

---

### STATE: LIFECYCLE_CLOSED
Owner: SYSTEM

Allowed:
- NONE

Denied:
- ALL ROLES

---

## Permanent Authority Revocation Rules

- Sender roles lose all authority after DISPATCHED
- Receiver Manager loses authority after WAREHOUSE_INTAKE_STARTED
- Warehouse Manager loses authority after OUT_FOR_DELIVERY
- Customer loses authority after DELIVERY_CONFIRMED

Authority is never restored.

---

## Enforcement Guarantees

- Any unauthorized event emission is rejected
- Violations are logged
- State is not mutated on failure
- No override path exists

---

## Why This Model Exists

This model ensures:
- Zero privilege escalation
- Clear legal accountability
- Secure-by-design implementation
- Predictable system behavior
- Enterprise-grade governance

This document is FINAL once Step 1.4 is locked.
