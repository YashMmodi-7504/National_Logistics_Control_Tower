from app.core.lifecycle import validate_transition, LifecycleError

# Valid transition
validate_transition("CREATED", "MANAGER_APPROVED")

# Invalid transition (should raise error)
try:
    validate_transition("CREATED", "OUT_FOR_DELIVERY")
except LifecycleError as e:
    print("Blocked:", e)
