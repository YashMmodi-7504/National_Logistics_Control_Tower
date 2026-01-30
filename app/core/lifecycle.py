# app/core/lifecycle.py

class LifecycleError(Exception):
    """Raised when an invalid lifecycle transition is attempted."""
    pass


# Single source of truth for lifecycle transitions
LIFECYCLE_TRANSITIONS = {
    "NONE": {"CREATED"},  # virtual initial state

    "CREATED": {"MANAGER_APPROVED", "MANAGER_ON_HOLD", "HOLD_FOR_REVIEW", "CANCELLED"},
    "MANAGER_ON_HOLD": {"MANAGER_APPROVED", "CANCELLED", "CREATED"},
    "HOLD_FOR_REVIEW": {"MANAGER_APPROVED", "CANCELLED", "CREATED", "OVERRIDE_APPLIED"},  # Can release back to CREATED
    "MANAGER_APPROVED": {"SUPERVISOR_APPROVED", "HOLD_FOR_REVIEW", "CANCELLED"},
    "SUPERVISOR_APPROVED": {"IN_TRANSIT", "HOLD_FOR_REVIEW", "CANCELLED"},
    "IN_TRANSIT": {"RECEIVER_ACKNOWLEDGED", "HOLD_FOR_REVIEW", "CANCELLED"},
    "RECEIVER_ACKNOWLEDGED": {"WAREHOUSE_INTAKE", "HOLD_FOR_REVIEW"},
    "WAREHOUSE_INTAKE": {"OUT_FOR_DELIVERY", "HOLD_FOR_REVIEW"},
    "OUT_FOR_DELIVERY": {"DELIVERY_FAILED", "DELIVERED", "HOLD_FOR_REVIEW", "CANCELLED"},
    "DELIVERY_FAILED": {"OUT_FOR_DELIVERY", "CANCELLED"},
    "DELIVERED": {"LIFECYCLE_CLOSED"},
    "CANCELLED": set(),  # Terminal state
    "LIFECYCLE_CLOSED": set(),
}



def validate_transition(current_state: str, next_state: str) -> None:
    """
    Validate whether a lifecycle transition is allowed.

    Raises LifecycleError if invalid.
    """
    if current_state not in LIFECYCLE_TRANSITIONS:
        raise LifecycleError(f"Unknown current state: {current_state}")

    allowed_next_states = LIFECYCLE_TRANSITIONS[current_state]

    if next_state not in allowed_next_states:
        raise LifecycleError(
            f"Invalid transition: {current_state} → {next_state}"
        )
