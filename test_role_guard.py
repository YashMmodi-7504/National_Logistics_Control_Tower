from app.core.role_guard import validate_role_authority, AuthorizationError

# Valid action
validate_role_authority(
    role="SENDER_MANAGER",
    current_state="MANAGER_ON_HOLD",
    event_type="MANAGER_APPROVED"
)

# Invalid action
try:
    validate_role_authority(
        role="SENDER",
        current_state="MANAGER_ON_HOLD",
        event_type="MANAGER_APPROVED"
    )
except AuthorizationError as e:
    print("Blocked:", e)
