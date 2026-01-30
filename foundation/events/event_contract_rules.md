# Event Contract Rules

## Purpose
This document defines mandatory rules that all domain events
must follow across the platform.

These rules protect truth, replayability, and audit integrity.

---

## Event Structure (Logical)

Every event MUST include:

- event_id (globally unique)
- event_type (from Event Catalog)
- shipment_id
- previous_state
- new_state
- emitting_role
- timestamp (UTC)
- version

Optional:
- metadata (read-only context)

---

## Immutability Rules

- Events cannot be edited
- Events cannot be deleted
- Events cannot be reordered
- Events cannot be reinterpreted

If an error occurs, a NEW event explains it.

---

## Idempotency Rules

- Replaying the same event_id must have no side effects
- Duplicate events must be ignored safely
- State transitions must be deterministic

---

## Validation Rules

Before accepting an event:

- Event type must exist in catalog
- Transition must be allowed by lifecycle
- Emitting role must own current state
- Event schema must match version

Invalid events are rejected.

---

## Ordering Rules

- Events are processed in timestamp order
- State must always move forward
- Time travel is prohibited

---

## Versioning Rules

- Event schemas are versioned
- Old versions remain valid
- Breaking changes are not allowed

---

## Why These Rules Exist

These rules ensure:
- Reliable recovery
- No hidden corruption
- Legal defensibility
- Predictable system behavior
- Enterprise-grade robustness

This document is FINAL once Step 1.3 is locked.
