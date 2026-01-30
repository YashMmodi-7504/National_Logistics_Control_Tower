"""
NOTIFICATION STORE

Purpose:
- Persistent storage for notifications
- Immutable append-only log
- Role-based filtering
- Read/unread status tracking

Storage:
- File: data/notifications.jsonl
- Format: JSON Lines (one notification per line)

Requirements:
• Immutable after creation
• Fast role-based queries
• Read status tracking
• No event store dependency

Author: National Logistics Control Tower
Phase: 9.2 - Notification Engine
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path


# Storage path
NOTIFICATION_STORE_PATH = "data/notifications.jsonl"


class Notification:
    """Immutable notification record."""
    
    def __init__(
        self,
        notification_id: str,
        timestamp: float,
        shipment_id: str,
        template_name: str,
        message: str,
        severity: str,
        recipients: List[str],
        metadata: Optional[Dict[str, Any]] = None,
        read_by: Optional[List[str]] = None
    ):
        """
        Initialize notification.
        
        Args:
            notification_id: Unique notification ID
            timestamp: Unix timestamp
            shipment_id: Associated shipment ID
            template_name: Template used to generate message
            message: Formatted notification message
            severity: Severity level (INFO, WARNING, URGENT, CRITICAL)
            recipients: List of role constants
            metadata: Additional context data
            read_by: List of roles who have read this
        """
        self.notification_id = notification_id
        self.timestamp = timestamp
        self.shipment_id = shipment_id
        self.template_name = template_name
        self.message = message
        self.severity = severity
        self.recipients = recipients
        self.metadata = metadata or {}
        self.read_by = read_by or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "notification_id": self.notification_id,
            "timestamp": self.timestamp,
            "shipment_id": self.shipment_id,
            "template_name": self.template_name,
            "message": self.message,
            "severity": self.severity,
            "recipients": self.recipients,
            "metadata": self.metadata,
            "read_by": self.read_by,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Notification":
        """Create notification from dictionary."""
        return cls(
            notification_id=data["notification_id"],
            timestamp=data["timestamp"],
            shipment_id=data["shipment_id"],
            template_name=data["template_name"],
            message=data["message"],
            severity=data["severity"],
            recipients=data["recipients"],
            metadata=data.get("metadata", {}),
            read_by=data.get("read_by", []),
        )
    
    def is_unread_for(self, role: str) -> bool:
        """Check if notification is unread for given role."""
        return role in self.recipients and role not in self.read_by


def _ensure_store_exists():
    """Ensure notification store file exists."""
    path = Path(NOTIFICATION_STORE_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    if not path.exists():
        path.touch()


def append_notification(notification: Notification) -> None:
    """
    Append notification to store.
    
    Args:
        notification: Notification to store
        
    Notes:
        - Append-only operation
        - Creates file if not exists
        - Thread-safe via file system append
    """
    _ensure_store_exists()
    
    with open(NOTIFICATION_STORE_PATH, "a", encoding="utf-8") as f:
        json.dump(notification.to_dict(), f)
        f.write("\n")


def read_all_notifications() -> List[Notification]:
    """
    Read all notifications from store.
    
    Returns:
        List[Notification]: All notifications, oldest first
        
    Notes:
        - Loads entire store into memory
        - For large stores, use read_notifications_for_role
    """
    _ensure_store_exists()
    
    notifications = []
    
    with open(NOTIFICATION_STORE_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    data = json.loads(line)
                    notifications.append(Notification.from_dict(data))
                except json.JSONDecodeError:
                    # Skip malformed lines
                    continue
    
    return notifications


def read_notifications_for_role(role: str, limit: Optional[int] = None) -> List[Notification]:
    """
    Read notifications for specific role.
    
    Args:
        role: Role constant (e.g., "SENDER_MANAGER")
        limit: Maximum notifications to return (most recent first)
        
    Returns:
        List[Notification]: Notifications for this role, newest first
    """
    all_notifications = read_all_notifications()
    
    # Filter by role
    role_notifications = [
        n for n in all_notifications
        if role in n.recipients
    ]
    
    # Sort by timestamp descending (newest first)
    role_notifications.sort(key=lambda n: n.timestamp, reverse=True)
    
    # Apply limit
    if limit is not None:
        role_notifications = role_notifications[:limit]
    
    return role_notifications


def read_unread_notifications_for_role(role: str) -> List[Notification]:
    """
    Read unread notifications for specific role.
    
    Args:
        role: Role constant
        
    Returns:
        List[Notification]: Unread notifications, newest first
    """
    role_notifications = read_notifications_for_role(role)
    
    return [
        n for n in role_notifications
        if n.is_unread_for(role)
    ]


def mark_notification_read(notification_id: str, role: str) -> bool:
    """
    Mark notification as read for specific role.
    
    Args:
        notification_id: Notification ID
        role: Role marking as read
        
    Returns:
        bool: True if marked, False if not found
        
    Notes:
        - Rewrites entire store (inefficient for large stores)
        - Consider implementing index for production use
    """
    _ensure_store_exists()
    
    notifications = read_all_notifications()
    found = False
    
    for notification in notifications:
        if notification.notification_id == notification_id:
            if role not in notification.read_by:
                notification.read_by.append(role)
                found = True
    
    if found:
        # Rewrite store
        with open(NOTIFICATION_STORE_PATH, "w", encoding="utf-8") as f:
            for notification in notifications:
                json.dump(notification.to_dict(), f)
                f.write("\n")
    
    return found


def get_notification_count_by_role(role: str) -> Dict[str, int]:
    """
    Get notification counts for role.
    
    Args:
        role: Role constant
        
    Returns:
        dict: Counts by category (total, unread, by_severity)
    """
    role_notifications = read_notifications_for_role(role)
    unread = [n for n in role_notifications if n.is_unread_for(role)]
    
    severity_counts = {}
    for notification in role_notifications:
        severity = notification.severity
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    return {
        "total": len(role_notifications),
        "unread": len(unread),
        "by_severity": severity_counts,
    }


def get_notifications_for_shipment(shipment_id: str) -> List[Notification]:
    """
    Get all notifications related to shipment.
    
    Args:
        shipment_id: Shipment ID
        
    Returns:
        List[Notification]: Notifications for this shipment, chronological
    """
    all_notifications = read_all_notifications()
    
    shipment_notifications = [
        n for n in all_notifications
        if n.shipment_id == shipment_id
    ]
    
    # Sort by timestamp ascending (chronological)
    shipment_notifications.sort(key=lambda n: n.timestamp)
    
    return shipment_notifications


def clear_notification_store():
    """
    Clear all notifications.
    
    WARNING: This is destructive and should only be used in testing.
    """
    if os.path.exists(NOTIFICATION_STORE_PATH):
        os.remove(NOTIFICATION_STORE_PATH)
