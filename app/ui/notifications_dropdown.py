"""
Notifications Dropdown UI Component
Displays in-app notifications with unread count badge
"""

import streamlit as st
from typing import List, Dict
from datetime import datetime
from app.notifications.in_app_notifier import get_notifications_for_role


def render_notifications_dropdown(role: str = "SENDER_MANAGER") -> None:
    """
    Render a notifications dropdown in the top-right corner.
    
    Args:
        role: Current user role for filtering notifications
    """
    # Get notifications for role
    notifications = get_notifications_for_role(role)
    unread_count = len([n for n in notifications if not n.get("read", False)])
    
    # Create notification badge
    badge_html = f"""
    <style>
        .notif-badge {{
            position: relative;
            display: inline-block;
            cursor: pointer;
        }}
        .notif-badge .badge {{
            position: absolute;
            top: -5px;
            right: -5px;
            background: #dc3545;
            color: white;
            border-radius: 50%;
            padding: 2px 6px;
            font-size: 11px;
            font-weight: bold;
        }}
        .notif-item {{
            border-bottom: 1px solid #eee;
            padding: 8px;
            margin: 4px 0;
            border-radius: 4px;
            transition: background 0.2s;
        }}
        .notif-item:hover {{
            background: #f8f9fa;
        }}
        .notif-item.unread {{
            background: #e7f3ff;
            border-left: 3px solid #0066cc;
        }}
        .notif-header {{
            font-weight: bold;
            font-size: 13px;
            margin-bottom: 4px;
        }}
        .notif-time {{
            color: #666;
            font-size: 11px;
        }}
        .notif-message {{
            font-size: 12px;
            color: #333;
        }}
    </style>
    """
    
    st.markdown(badge_html, unsafe_allow_html=True)
    
    # Render notifications in expander
    with st.expander(f"🔔 Notifications ({unread_count})", expanded=False):
        if not notifications:
            st.info("No notifications yet")
        else:
            # Group by today/yesterday/older
            today = datetime.now().date()
            today_notifs = []
            older_notifs = []
            
            for notif in notifications:
                timestamp_str = notif.get("timestamp", "")
                try:
                    notif_time = datetime.fromisoformat(timestamp_str.replace("Z", "").replace("+00:00", ""))
                    if notif_time.date() == today:
                        today_notifs.append(notif)
                    else:
                        older_notifs.append(notif)
                except:
                    older_notifs.append(notif)
            
            # Render today's notifications
            if today_notifs:
                st.markdown("**📅 Today**")
                for notif in today_notifs[:10]:  # Limit to 10 most recent
                    _render_notification_item(notif)
            
            # Render older notifications
            if older_notifs:
                st.markdown("**📂 Earlier**")
                for notif in older_notifs[:10]:  # Limit to 10 most recent
                    _render_notification_item(notif)
            
            # Mark all as read button
            if unread_count > 0:
                if st.button("✅ Mark All as Read", key="mark_all_read"):
                    _mark_all_as_read(role)
                    st.rerun()


def _render_notification_item(notif: Dict) -> None:
    """Render a single notification item"""
    is_unread = not notif.get("read", False)
    unread_class = "unread" if is_unread else ""
    
    event_type = notif.get("event_type", "")
    message = notif.get("message", "")
    shipment_id = notif.get("shipment_id", "")
    timestamp = notif.get("timestamp", "")
    
    # Event icons
    icon_map = {
        "RECEIVER_ACKNOWLEDGED": "📦",
        "DELIVERY_CONFIRMED": "✅",
        "MANAGER_APPROVED": "👍",
        "SUPERVISOR_APPROVED": "✔️",
        "OVERRIDE_APPLIED": "⚠️",
        "SLA_BREACH": "🔴"
    }
    icon = icon_map.get(event_type, "🔔")
    
    # Time ago
    try:
        notif_time = datetime.fromisoformat(timestamp.replace("Z", "").replace("+00:00", ""))
        time_diff = datetime.now() - notif_time
        if time_diff.seconds < 60:
            time_ago = "Just now"
        elif time_diff.seconds < 3600:
            time_ago = f"{time_diff.seconds // 60}m ago"
        elif time_diff.seconds < 86400:
            time_ago = f"{time_diff.seconds // 3600}h ago"
        else:
            time_ago = f"{time_diff.days}d ago"
    except:
        time_ago = "Unknown"
    
    # Render notification
    with st.container():
        st.markdown(
            f'<div class="notif-item {unread_class}">'
            f'<div class="notif-header">{icon} {event_type.replace("_", " ").title()}</div>'
            f'<div class="notif-message">{message}</div>'
            f'<div class="notif-time">Shipment: {shipment_id} • {time_ago}</div>'
            f'</div>',
            unsafe_allow_html=True
        )


def _mark_all_as_read(role: str) -> None:
    """Mark all notifications as read for this role"""
    from app.notifications.in_app_notifier import _notification_store
    
    for notif in _notification_store:
        if role in notif.get("recipients", []):
            notif["read"] = True
