from app.core.event_emitter import emit_event

# STEP 1: Sender creates shipment
event0 = emit_event(
    shipment_id="SHIP_001",
    current_state="NONE",
    next_state="CREATED",
    event_type="SHIPMENT_CREATED",
    role="SENDER"
)
print("Shipment created:", event0)

# STEP 2: Manager approves
event1 = emit_event(
    shipment_id="SHIP_001",
    current_state="CREATED",
    next_state="MANAGER_APPROVED",
    event_type="MANAGER_APPROVED",
    role="SENDER_MANAGER"
)
print("Manager approved:", event1)

# STEP 3: Invalid attempt (should fail)
try:
    emit_event(
        shipment_id="SHIP_001",
        current_state="MANAGER_APPROVED",
        next_state="SUPERVISOR_APPROVED",
        event_type="SUPERVISOR_APPROVED",
        role="SENDER_MANAGER"
    )
except Exception as e:
    print("Blocked as expected:", e)
