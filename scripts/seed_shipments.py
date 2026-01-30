import random
import time
from datetime import datetime, timedelta

from app.core.event_emitter import emit_event
from app.core.id_generator import generate_shipment_id

STATES = [
    "Gujarat", "Maharashtra", "Rajasthan", "Delhi", "Karnataka",
    "Tamil Nadu", "Kerala", "West Bengal", "Assam", "Uttar Pradesh",
    "Madhya Pradesh", "Punjab", "Haryana", "Bihar", "Odisha",
    "Telangana", "Andhra Pradesh", "Chhattisgarh", "Jharkhand",
]

TOTAL_SHIPMENTS = 50_000

print("🚀 Seeding shipments...")

for i in range(TOTAL_SHIPMENTS):
    shipment_id = generate_shipment_id()

    src = random.choice(STATES)
    dst = random.choice([s for s in STATES if s != src])

    emit_event(
        shipment_id=shipment_id,
        current_state="NONE",
        next_state="CREATED",
        event_type="SHIPMENT_CREATED",
        role="SENDER",
        metadata={
            "source": f"City, {src}",
            "destination": f"City, {dst}",
            "created_at": (
                datetime.utcnow()
                - timedelta(hours=random.randint(0, 72))
            ).isoformat()
        }
    )

    if i % 1000 == 0:
        print(f"Seeded {i} shipments")

print("✅ Seeding complete")
