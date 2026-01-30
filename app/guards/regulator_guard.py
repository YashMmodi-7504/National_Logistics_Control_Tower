"""
REGULATOR GUARD

Purpose:
- Enforce regulator restrictions
- Fail closed on violations
- Court-defensible access control

Rules:
- Regulator CANNOT:
  - Call event emitter
  - Access live read models
  - Invoke intelligence engines
- Regulator CAN:
  - Read snapshots
  - Export compliance data
"""

from typing import Dict, Any
from app.policies.regulator_policy import (
    is_snapshot_allowed,
    is_operation_forbidden,
    ALLOWED_SNAPSHOTS,
    FORBIDDEN_OPERATIONS,
)


class RegulatorAccessViolation(PermissionError):
    """Raised when regulator attempts forbidden operation."""
    pass


# ==================================================
# GUARD FUNCTIONS
# ==================================================

def assert_regulator_access(context: Dict[str, Any]) -> None:
    """
    Enforce regulator access restrictions.
    
    Args:
        context: Dictionary with:
            - operation: str (required) - operation being attempted
            - snapshot_name: str (optional) - snapshot being accessed
            - resource: str (optional) - resource being accessed
    
    Raises:
        RegulatorAccessViolation: If access is denied
        
    Rules:
        - Fail closed: deny if context is invalid
        - Explicit checks only
        - No heuristics
    """
    # Validate context
    if not isinstance(context, dict):
        raise RegulatorAccessViolation(
            "Invalid access context: must be dictionary"
        )
    
    operation = context.get("operation")
    if not operation or not isinstance(operation, str):
        raise RegulatorAccessViolation(
            "Invalid access context: operation required"
        )
    
    # Check if operation is explicitly forbidden
    if is_operation_forbidden(operation):
        raise RegulatorAccessViolation(
            f"Regulator cannot perform operation: {operation}"
        )
    
    # If accessing a snapshot, verify it's allowed
    if operation == "read_snapshot":
        snapshot_name = context.get("snapshot_name")
        
        if not snapshot_name or not isinstance(snapshot_name, str):
            raise RegulatorAccessViolation(
                "Invalid access context: snapshot_name required for read_snapshot"
            )
        
        if not is_snapshot_allowed(snapshot_name):
            raise RegulatorAccessViolation(
                f"Regulator cannot access snapshot: {snapshot_name}"
            )
    
    # If accessing live read model, deny
    if operation == "read_live_model":
        raise RegulatorAccessViolation(
            "Regulator cannot access live read models"
        )
    
    # If invoking intelligence engine, deny
    if operation == "invoke_engine":
        raise RegulatorAccessViolation(
            "Regulator cannot invoke intelligence engines"
        )


def can_read_snapshot(snapshot_name: str) -> bool:
    """
    Check if regulator can read a specific snapshot.
    
    Args:
        snapshot_name: Name of the snapshot
    
    Returns:
        True if allowed, False otherwise
    """
    return is_snapshot_allowed(snapshot_name)


def can_export_compliance(export_type: str) -> bool:
    """
    Check if regulator can perform a compliance export.
    
    Args:
        export_type: Type of export
    
    Returns:
        True (regulators can always export compliance data)
    """
    # Regulators always have export access for compliance
    return True


def validate_regulator_operation(operation: str) -> None:
    """
    Validate if an operation is allowed for regulator.
    
    Args:
        operation: Operation name
    
    Raises:
        RegulatorAccessViolation: If operation is forbidden
    """
    if is_operation_forbidden(operation):
        raise RegulatorAccessViolation(
            f"Operation forbidden for regulator: {operation}"
        )


# ==================================================
# DECORATOR FOR REGULATOR-SAFE FUNCTIONS
# ==================================================

def regulator_safe(operation_name: str):
    """
    Decorator to mark functions as regulator-safe.
    
    Args:
        operation_name: Name of the operation for audit trail
    
    Returns:
        Decorator function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Validate operation is allowed
            context = {
                "operation": operation_name,
                "function": func.__name__,
            }
            assert_regulator_access(context)
            return func(*args, **kwargs)
        return wrapper
    return decorator
