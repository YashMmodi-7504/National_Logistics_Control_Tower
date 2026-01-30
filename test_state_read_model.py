from app.core.state_read_model import get_state_wise_sender_summary

summary = get_state_wise_sender_summary()

for state, metrics in summary.items():
    print(state)
    for k, v in metrics.items():
        print(f"  {k}: {v}")
