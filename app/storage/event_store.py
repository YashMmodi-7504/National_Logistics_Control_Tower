# app/storage/event_store.py

import json
import uuid
from datetime import datetime
from typing import Dict, List

EVENT_STORE_FILE = "event_store.jsonl"


def _current_utc_time() -> str:
    return datetime.utcnow().isoformat() + "Z"


def append_event(event: Dict) -> Dict:
    """
    Append an immutable event to the event store.
    """
    event_record = {
        "event_id": str(uuid.uuid4()),
        "timestamp": _current_utc_time(),
        **event
    }

    with open(EVENT_STORE_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(event_record) + "\n")

    return event_record


def load_all_events() -> List[Dict]:
    """
    Load all events from the event store.
    """
    events = []

    try:
        with open(EVENT_STORE_FILE, "r", encoding="utf-8") as f:
            for line in f:
                events.append(json.loads(line.strip()))
    except FileNotFoundError:
        pass  # No events yet

    return events
