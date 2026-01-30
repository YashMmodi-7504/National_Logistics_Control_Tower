"""
MANAGER OVERRIDE WITH AUDIT TRAIL

Purpose:
- Allow managers to override AI decisions
- Require explicit reason for override
- Create immutable audit trail
- Link override to AI decision

Requirements:
• Override requires reason
• Stored as event (HUMAN_OVERRIDE_RECORDED)
• Linked to original AI prediction
• Immutable audit trail
• Cannot be deleted or modified

Author: National Logistics Control Tower
Phase: 9.9 - Manager Override
"""

import time
from typing import Dict, Any, Optional, List
from datetime import datetime


class OverrideReason:
    """Pre-defined override reasons."""
    
    BUSINESS_PRIORITY = "BUSINESS_PRIORITY"
    CUSTOMER_REQUEST = "CUSTOMER_REQUEST"
    MANAGEMENT_DIRECTIVE = "MANAGEMENT_DIRECTIVE"
    AI_ERROR = "AI_ERROR"
    OPERATIONAL_NEED = "OPERATIONAL_NEED"
    RISK_ACCEPTABLE = "RISK_ACCEPTABLE"
    CUSTOM = "CUSTOM"


def create_override_event(
    shipment_id: str,
    original_decision: str,
    override_decision: str,
    reason_code: str,
    reason_text: str,
    manager_role: str,
    ai_predictions: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create manager override event.
    
    Args:
        shipment_id: Shipment ID
        original_decision: Original AI/system decision
        override_decision: Manager's override decision
        reason_code: Pre-defined reason code
        reason_text: Human-readable explanation
        manager_role: Role of manager (SENDER_MANAGER, etc.)
        ai_predictions: Original AI predictions being overridden
        
    Returns:
        dict: Override event payload
        
    Examples:
        >>> create_override_event(
        ...     shipment_id="SHIP-20260119-120000-1234",
        ...     original_decision="REJECT",
        ...     override_decision="APPROVE",
        ...     reason_code=OverrideReason.BUSINESS_PRIORITY,
        ...     reason_text="VIP customer requires expedited delivery",
        ...     manager_role="SENDER_MANAGER",
        ...     ai_predictions={...}
        ... )
    """
    event = {
        "event_type": "HUMAN_OVERRIDE_RECORDED",
        "timestamp": time.time(),
        "shipment_id": shipment_id,
        "override_data": {
            "original_decision": original_decision,
            "override_decision": override_decision,
            "reason_code": reason_code,
            "reason_text": reason_text,
            "manager_role": manager_role,
            "ai_predictions": ai_predictions or {},
        },
        "metadata": {
            "override_timestamp": datetime.now().isoformat(),
            "immutable": True,
            "audit_required": True,
        }
    }
    
    return event


def validate_override_request(
    shipment_id: str,
    reason_code: str,
    reason_text: str,
    manager_role: str
) -> tuple[bool, Optional[str]]:
    """
    Validate override request.
    
    Args:
        shipment_id: Shipment ID
        reason_code: Reason code
        reason_text: Reason text
        manager_role: Manager role
        
    Returns:
        tuple: (is_valid, error_message)
        
    Examples:
        >>> validate_override_request(
        ...     "SHIP-123", "BUSINESS_PRIORITY", "VIP customer", "SENDER_MANAGER"
        ... )
        (True, None)
    """
    # Validate shipment ID
    if not shipment_id or not isinstance(shipment_id, str):
        return False, "Invalid shipment ID"
    
    # Validate reason code
    valid_codes = [
        OverrideReason.BUSINESS_PRIORITY,
        OverrideReason.CUSTOMER_REQUEST,
        OverrideReason.MANAGEMENT_DIRECTIVE,
        OverrideReason.AI_ERROR,
        OverrideReason.OPERATIONAL_NEED,
        OverrideReason.RISK_ACCEPTABLE,
        OverrideReason.CUSTOM,
    ]
    
    if reason_code not in valid_codes:
        return False, f"Invalid reason code. Must be one of: {', '.join(valid_codes)}"
    
    # Validate reason text
    if not reason_text or not isinstance(reason_text, str):
        return False, "Reason text is required"
    
    if len(reason_text.strip()) < 10:
        return False, "Reason text must be at least 10 characters"
    
    # Validate manager role
    valid_roles = ["SENDER_MANAGER", "RECEIVER_MANAGER", "COO"]
    if manager_role not in valid_roles:
        return False, f"Invalid manager role. Must be one of: {', '.join(valid_roles)}"
    
    return True, None


def record_override(
    shipment_id: str,
    original_decision: str,
    override_decision: str,
    reason_code: str,
    reason_text: str,
    manager_role: str,
    ai_predictions: Optional[Dict[str, Any]] = None
) -> tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
    """
    Record manager override with validation.
    
    Args:
        shipment_id: Shipment ID
        original_decision: Original decision
        override_decision: Override decision
        reason_code: Reason code
        reason_text: Reason explanation
        manager_role: Manager role
        ai_predictions: Original AI predictions
        
    Returns:
        tuple: (success, error_message, event)
        
    Notes:
        - Validates all inputs
        - Creates override event
        - Emits event to event store
        - Triggers notification
    """
    # Validate request
    is_valid, error = validate_override_request(
        shipment_id, reason_code, reason_text, manager_role
    )
    
    if not is_valid:
        return False, error, None
    
    # Create override event
    event = create_override_event(
        shipment_id=shipment_id,
        original_decision=original_decision,
        override_decision=override_decision,
        reason_code=reason_code,
        reason_text=reason_text,
        manager_role=manager_role,
        ai_predictions=ai_predictions,
    )
    
    # Emit event to event store
    try:
        from foundation.event_emitter import emit_event
        emit_event(event)
    except Exception as e:
        return False, f"Failed to record override: {str(e)}", None
    
    # Trigger notification
    try:
        from app.notifications.notifier import notify_manager_override
        notify_manager_override(event)
    except Exception:
        # Non-critical failure, override still recorded
        pass
    
    return True, None, event


def get_override_history_for_shipment(shipment_id: str) -> List[Dict[str, Any]]:
    """
    Get all overrides for a shipment.
    
    Args:
        shipment_id: Shipment ID
        
    Returns:
        List[dict]: All override events for this shipment, chronological
        
    Notes:
        - Reads from event store
        - Returns empty list if no overrides
    """
    try:
        from foundation.event_store import read_events
        
        events = read_events()
        
        # Filter override events for this shipment
        overrides = [
            e for e in events
            if e.get("event_type") == "HUMAN_OVERRIDE_RECORDED"
            and e.get("shipment_id") == shipment_id
        ]
        
        # Sort by timestamp
        overrides.sort(key=lambda e: e.get("timestamp", 0))
        
        return overrides
    
    except Exception:
        return []


def get_override_count_by_manager(manager_role: str, hours: int = 24) -> int:
    """
    Get count of overrides by manager in last N hours.
    
    Args:
        manager_role: Manager role
        hours: Time window in hours
        
    Returns:
        int: Override count
        
    Notes:
        - Used for audit alerts
        - High override count triggers notification
    """
    try:
        from foundation.event_store import read_events
        
        events = read_events()
        
        # Calculate time threshold
        threshold = time.time() - (hours * 3600)
        
        # Filter override events by manager and time
        overrides = [
            e for e in events
            if e.get("event_type") == "HUMAN_OVERRIDE_RECORDED"
            and e.get("override_data", {}).get("manager_role") == manager_role
            and e.get("timestamp", 0) > threshold
        ]
        
        return len(overrides)
    
    except Exception:
        return 0


def get_override_statistics() -> Dict[str, Any]:
    """
    Get system-wide override statistics.
    
    Returns:
        dict: Override statistics
            - total_overrides: All-time count
            - by_reason: Count by reason code
            - by_manager: Count by manager role
            - last_24h: Count in last 24 hours
            - override_rate: Percentage of decisions overridden
    """
    try:
        from foundation.event_store import read_events
        
        events = read_events()
        
        # Filter override events
        overrides = [
            e for e in events
            if e.get("event_type") == "HUMAN_OVERRIDE_RECORDED"
        ]
        
        # Total count
        total_overrides = len(overrides)
        
        # Count by reason
        by_reason = {}
        for override in overrides:
            reason = override.get("override_data", {}).get("reason_code", "UNKNOWN")
            by_reason[reason] = by_reason.get(reason, 0) + 1
        
        # Count by manager
        by_manager = {}
        for override in overrides:
            manager = override.get("override_data", {}).get("manager_role", "UNKNOWN")
            by_manager[manager] = by_manager.get(manager, 0) + 1
        
        # Last 24h
        threshold = time.time() - 86400
        last_24h = len([
            e for e in overrides
            if e.get("timestamp", 0) > threshold
        ])
        
        # Override rate (approximate)
        # Total decisions = total shipments created
        total_decisions = len([
            e for e in events
            if e.get("event_type") == "SHIPMENT_CREATED"
        ])
        
        override_rate = (total_overrides / total_decisions * 100) if total_decisions > 0 else 0
        
        return {
            "total_overrides": total_overrides,
            "by_reason": by_reason,
            "by_manager": by_manager,
            "last_24h": last_24h,
            "override_rate": round(override_rate, 2),
        }
    
    except Exception:
        return {
            "total_overrides": 0,
            "by_reason": {},
            "by_manager": {},
            "last_24h": 0,
            "override_rate": 0.0,
        }


def check_override_threshold(manager_role: str, threshold: int = 10) -> tuple[bool, int]:
    """
    Check if manager has exceeded override threshold.
    
    Args:
        manager_role: Manager role
        threshold: Maximum allowed overrides in 24h
        
    Returns:
        tuple: (exceeded, current_count)
        
    Notes:
        - Used to trigger audit alerts
        - COO receives notification if threshold exceeded
    """
    count = get_override_count_by_manager(manager_role, hours=24)
    exceeded = count >= threshold
    
    return exceeded, count
