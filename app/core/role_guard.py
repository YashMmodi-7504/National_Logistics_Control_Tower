# app/core/role_guard.py

class AuthorizationError(Exception):
    """Raised when a role attempts an unauthorized action."""
    pass


# ==================================================
# STATE → ROLES ALLOWED TO ACT IN THAT STATE
# ==================================================
STATE_ROLE_AUTHORITY = {
    # Virtual initial state
    "NONE": {"SENDER"},

    # Sender side
    "CREATED": {"SENDER", "SENDER_MANAGER"},
    "MANAGER_ON_HOLD": {"SENDER_MANAGER"},
    "MANAGER_APPROVED": {"SENDER_MANAGER", "SENDER_SUPERVISOR"},
    "SUPERVISOR_APPROVED": {"SENDER_MANAGER", "SENDER_SUPERVISOR", "SYSTEM"},
    "HOLD_FOR_REVIEW": {"SENDER_MANAGER", "SENDER_SUPERVISOR"},

    # Transit & receiver side
    "IN_TRANSIT": {"SENDER_MANAGER", "RECEIVER_MANAGER"},
    "RECEIVER_ACKNOWLEDGED": {"SENDER_MANAGER", "WAREHOUSE_MANAGER"},
    "WAREHOUSE_INTAKE": {"SENDER_MANAGER", "WAREHOUSE_MANAGER"},

    # Last mile
    "OUT_FOR_DELIVERY": {"SENDER_MANAGER", "CUSTOMER"},
    "DELIVERY_FAILED": {"SYSTEM"},
    "DELIVERED": {"SYSTEM"},
    
    # Cancelled
    "CANCELLED": {"SENDER_MANAGER", "SENDER_SUPERVISOR", "SYSTEM"},

    # Terminal
    "LIFECYCLE_CLOSED": set(),
}


# ==================================================
# EVENT → ROLES ALLOWED TO EMIT THAT EVENT
# ==================================================
EVENT_ROLE_AUTHORITY = {
    # Sender events
    "SHIPMENT_CREATED": {"SENDER"},
    "MANAGER_APPROVED": {"SENDER_MANAGER"},
    "MANAGER_ON_HOLD": {"SENDER_MANAGER"},
    "MANAGER_CANCELLED": {"SENDER_MANAGER", "SENDER_SUPERVISOR"},
    "SUPERVISOR_APPROVED": {"SENDER_SUPERVISOR"},

    # System dispatch
    "DISPATCHED": {"SYSTEM"},

    # Receiver & warehouse
    "RECEIVER_ACKNOWLEDGED": {"RECEIVER_MANAGER"},
    "WAREHOUSE_INTAKE_STARTED": {"WAREHOUSE_MANAGER"},
    "OUT_FOR_DELIVERY": {"WAREHOUSE_MANAGER"},

    # Last mile
    "DELIVERY_CONFIRMED": {"CUSTOMER"},
    "DELIVERY_FAILED": {"SYSTEM"},

    # ------------------------------
    # HUMAN OVERRIDE (NEW)
    # ------------------------------
    "HUMAN_OVERRIDE_RECORDED": {
        "SENDER_MANAGER",
        "SENDER_SUPERVISOR",
        "WAREHOUSE_MANAGER",
    },
    
    # ------------------------------
    # METADATA UPDATE
    # ------------------------------
    "METADATA_UPDATED": {
        "SENDER_MANAGER",
        "SENDER_SUPERVISOR",
    },

    # Closure
    "LIFECYCLE_CLOSED": {"SYSTEM"},
}


def validate_role_authority(
    role: str,
    current_state: str,
    event_type: str
) -> None:
    """
    Validate whether a role is authorized to emit an event
    given the current lifecycle state.
    """

    # --------------------------------------------------
    # 1. State-level authority
    # --------------------------------------------------
    allowed_roles_for_state = STATE_ROLE_AUTHORITY.get(current_state, set())

    if role not in allowed_roles_for_state:
        raise AuthorizationError(
            f"Role '{role}' is not allowed to act in state '{current_state}'"
        )

    # --------------------------------------------------
    # 2. Event-level authority
    # --------------------------------------------------
    allowed_roles_for_event = EVENT_ROLE_AUTHORITY.get(event_type, set())

    if role not in allowed_roles_for_event:
        raise AuthorizationError(
            f"Role '{role}' is not allowed to emit event '{event_type}'"
        )
