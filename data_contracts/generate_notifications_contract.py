"""
NOTIFICATIONS CONTRACT GENERATOR

Purpose:
- UI notification stress testing
- Event-driven notification validation

Requirements:
• Based on events
• Realistic recipient mapping
• Read/unread distribution

Author: National Logistics Control Tower
Phase: Data Contracts
"""

import csv
import random
from datetime import datetime, timedelta

random.seed(42)

# Event → Notification mapping
NOTIFICATION_RULES = {
    "RECEIVER_ACKNOWLEDGED": {
        "recipients": ["SENDER_MANAGER", "SENDER_SUPERVISOR"],
        "template": "📦 Shipment {shipment_id} has successfully reached the Receiver Manager."
    },
    "DELIVERY_CONFIRMED": {
        "recipients": ["SENDER", "SENDER_MANAGER", "SENDER_SUPERVISOR", "RECEIVER_MANAGER", "WAREHOUSE_MANAGER"],
        "template": "✅ Shipment {shipment_id} has been delivered to the customer."
    },
    "MANAGER_APPROVED": {
        "recipients": ["SENDER_SUPERVISOR"],
        "template": "✓ Shipment {shipment_id} approved by Sender Manager."
    },
    "SUPERVISOR_APPROVED": {
        "recipients": ["SENDER_MANAGER"],
        "template": "✓ Shipment {shipment_id} approved by Supervisor."
    },
    "OUT_FOR_DELIVERY": {
        "recipients": ["RECEIVER_MANAGER", "CUSTOMER"],
        "template": "🚚 Shipment {shipment_id} is out for delivery."
    }
}

def generate_notification_id(index):
    """Generate deterministic notification ID."""
    return f"NOTIF-{str(index).zfill(8)}"

def should_be_read(days_ago):
    """Determine if notification should be read based on age."""
    if days_ago > 7:
        return True
    elif days_ago > 3:
        return random.choice([True, False])
    else:
        return random.choice([True, False, False])  # Favor unread for recent

def generate_notifications():
    """Generate notifications contract CSV."""
    
    # Load events
    events = []
    try:
        with open("data_contracts/events_contract.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            events = list(reader)
    except FileNotFoundError:
        print("❌ Error: events_contract.csv not found.")
        return 0
    
    filename = "data_contracts/notifications_contract.csv"
    
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow([
            "notification_id",
            "shipment_id",
            "recipient_role",
            "message",
            "triggered_event",
            "created_at",
            "read"
        ])
        
        notification_count = 0
        
        for event in events:
            event_type = event["event_type"]
            shipment_id = event["shipment_id"]
            timestamp = event["timestamp"]
            
            # Check if this event triggers notifications
            if event_type in NOTIFICATION_RULES:
                rule = NOTIFICATION_RULES[event_type]
                message = rule["template"].format(shipment_id=shipment_id)
                
                # Create notification for each recipient
                for recipient in rule["recipients"]:
                    notification_count += 1
                    notification_id = generate_notification_id(notification_count)
                    
                    # Determine read status
                    event_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                    days_ago = (datetime.now() - event_time).days
                    read_status = should_be_read(days_ago)
                    
                    writer.writerow([
                        notification_id,
                        shipment_id,
                        recipient,
                        message,
                        event_type,
                        timestamp,
                        read_status
                    ])
        
        print(f"✅ Generated {notification_count} rows → {filename}")
    
    return notification_count

if __name__ == "__main__":
    row_count = generate_notifications()
    print(f"📊 Total notifications: {row_count}")
