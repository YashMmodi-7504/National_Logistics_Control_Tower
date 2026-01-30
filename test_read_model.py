from app.core.read_model import get_all_shipments_state, get_shipment_current_state

print("All shipments:")
print(get_all_shipments_state())

print("\nSingle shipment:")
print(get_shipment_current_state("SHIP_001"))
