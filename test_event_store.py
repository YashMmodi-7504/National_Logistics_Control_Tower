from app.storage.event_store import append_event, load_all_events

append_event({
    "event_type": "TEST_EVENT",
    "shipment_id": "SHIP_001",
    "role": "SYSTEM"
})

print(load_all_events())
