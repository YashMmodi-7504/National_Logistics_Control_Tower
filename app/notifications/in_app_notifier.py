"""
IN-APP NOTIFICATION ENGINE

Purpose:
- Event-driven notification system
- Non-blocking toast + inbox style
- Timestamped and role-aware
- No email/SMS - in-app only

Requirements:
• Trigger on specific events (RECEIVER_ACKNOWLEDGED, DELIVERY_CONFIRMED)
• Store notifications in memory for session
• Display as toast + inbox panel
• Never block UI

Author: National Logistics Control Tower
Phase: Enhanced Notifications
"""

import time
from typing import Dict, List, Optional
from datetime import datetime


# In-memory notification store (session-level)
_notification_store: List[Dict] = []


def emit_notification(
    shipment_id: str,
    event_type: str,
    message: str,
    recipients: List[str],
    metadata: Optional[Dict] = None
) -> None:
    """
    Emit an in-app notification.
    
    Args:
        shipment_id: Shipment ID
        event_type: Event type that triggered notification
        message: Notification message
        recipients: List of roles to notify
        metadata: Additional metadata
    """
    notification = {
        "id": f"NOTIF-{int(time.time() * 1000)}",
        "shipment_id": shipment_id,
        "event_type": event_type,
        "message": message,
        "recipients": recipients,
        "timestamp": datetime.now().isoformat(),
        "read": False,
        "metadata": metadata or {}
    }
    
    _notification_store.append(notification)


def get_notifications_for_role(role: str, unread_only: bool = False) -> List[Dict]:
    """
    Get notifications for a specific role.
    
    Args:
        role: Role to filter by
        unread_only: Only return unread notifications
        
    Returns:
        List of notifications
    """
    notifications = [
        n for n in _notification_store
        if role in n["recipients"]
    ]
    
    if unread_only:
        notifications = [n for n in notifications if not n["read"]]
    
    # Sort by timestamp (newest first)
    notifications.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return notifications


def mark_as_read(notification_id: str, role: str = None) -> bool:
    """
    Mark a notification as read.
    
    Args:
        notification_id: ID of the notification to mark as read
        role: Role attempting to mark as read (for security validation)
        
    Returns:
        bool: True if notification was found and marked, False otherwise
    """
    for notification in _notification_store:
        if notification["id"] == notification_id:
            # If role is provided, validate that role is in recipients
            if role is not None and role not in notification.get("recipients", []):
                # Role not authorized to mark this notification
                continue
            notification["read"] = True
            return True
    return False


def clear_notifications() -> None:
    """Clear all notifications (admin only)."""
    global _notification_store
    _notification_store = []


def get_unread_count(role: str) -> int:
    """Get count of unread notifications for a role."""
    return len([
        n for n in _notification_store
        if role in n["recipients"] and not n["read"]
    ])


# Event-driven notification triggers
def handle_receiver_acknowledged(shipment_id: str, metadata: Dict) -> None:
    """
    Handle RECEIVER_ACKNOWLEDGED event.
    
    Notifies:
    - SENDER_MANAGER
    - SENDER_SUPERVISOR
    """
    message = f"📦 Shipment {shipment_id} has successfully reached the Receiver Manager."
    
    emit_notification(
        shipment_id=shipment_id,
        event_type="RECEIVER_ACKNOWLEDGED",
        message=message,
        recipients=["SENDER_MANAGER", "SENDER_SUPERVISOR"],
        metadata=metadata
    )


def handle_delivery_confirmed(shipment_id: str, metadata: Dict) -> None:
    """
    Handle DELIVERY_CONFIRMED event.
    
    Notifies:
    - SENDER
    - SENDER_MANAGER
    - SENDER_SUPERVISOR
    - RECEIVER_MANAGER
    - WAREHOUSE_MANAGER
    """
    message = f"✅ Shipment {shipment_id} has been delivered to the customer."
    
    emit_notification(
        shipment_id=shipment_id,
        event_type="DELIVERY_CONFIRMED",
        message=message,
        recipients=[
            "SENDER",
            "SENDER_MANAGER",
            "SENDER_SUPERVISOR",
            "RECEIVER_MANAGER",
            "WAREHOUSE_MANAGER"
        ],
        metadata=metadata
    )


def process_event_for_notifications(event: Dict) -> None:
    """
    Process an event and trigger appropriate notifications.
    
    Args:
        event: Event dictionary from event store
    """
    event_type = event.get("event_type")
    shipment_id = event.get("shipment_id")
    metadata = event.get("metadata", {})
    
    if event_type == "RECEIVER_ACKNOWLEDGED":
        handle_receiver_acknowledged(shipment_id, metadata)
    elif event_type == "DELIVERY_CONFIRMED":
        handle_delivery_confirmed(shipment_id, metadata)
