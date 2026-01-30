"""
PHASE 7.1 — ROLE DEFINITIONS

Define system roles and their access scopes.

Rules:
- No imports outside typing
- No logic, only declarations
- Roles must be explicit strings
- Scopes must be human-readable
- Used by access_guard.py
"""

from typing import Literal

# Role definitions
SENDER_MANAGER: Literal["SENDER_MANAGER"] = "SENDER_MANAGER"
SENDER_SUPERVISOR: Literal["SENDER_SUPERVISOR"] = "SENDER_SUPERVISOR"
RECEIVER_MANAGER: Literal["RECEIVER_MANAGER"] = "RECEIVER_MANAGER"
COO: Literal["COO"] = "COO"
SYSTEM: Literal["SYSTEM"] = "SYSTEM"
VIEWER: Literal["VIEWER"] = "VIEWER"

# Access scope definitions
SOURCE_STATE: Literal["SOURCE_STATE"] = "SOURCE_STATE"
DESTINATION_STATE: Literal["DESTINATION_STATE"] = "DESTINATION_STATE"
CORRIDOR: Literal["CORRIDOR"] = "CORRIDOR"
GLOBAL: Literal["GLOBAL"] = "GLOBAL"

# Role to scope mapping
ROLE_SCOPE_MAP: dict[str, str] = {
    SENDER_MANAGER: SOURCE_STATE,
    SENDER_SUPERVISOR: SOURCE_STATE,
    RECEIVER_MANAGER: DESTINATION_STATE,
    COO: GLOBAL,
    SYSTEM: GLOBAL,
    VIEWER: CORRIDOR,
}

# All roles
ALL_ROLES: list[str] = [
    SENDER_MANAGER,
    SENDER_SUPERVISOR,
    RECEIVER_MANAGER,
    COO,
    SYSTEM,
    VIEWER,
]

# All scopes
ALL_SCOPES: list[str] = [
    SOURCE_STATE,
    DESTINATION_STATE,
    CORRIDOR,
    GLOBAL,
]
