"""
Receiver Tab - Minimal Implementation
"""
import streamlit as st

def render_receiver(shipments):
    """Render receiver interface - SIMPLE acknowledgment"""
    st.markdown("## 📥 Receiver Warehouse")
    
    # Filter in-transit shipments (in-memory)
    in_transit = [s for s in shipments if s.get('current_state') == 'IN_TRANSIT']
    arrived = [s for s in shipments if s.get('current_state') == 'ARRIVED']
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("In Transit", len(in_transit))
    with col2:
        st.metric("Arrived (Pending Ack)", len(arrived))
    
    st.divider()
    
    # Acknowledge arrivals
    st.markdown("### ✅ Acknowledge Arrivals")
    
    if arrived:
        for ship in arrived[:20]:  # Limit to 20
            with st.expander(f"📦 {ship['shipment_id']}"):
                metadata = ship.get('current_payload', {})
                
                st.write(f"**Route:** {metadata.get('source')} → {metadata.get('destination')}")
                st.write(f"**Weight:** {metadata.get('weight', 0)} kg")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Acknowledge", key=f"ack_{ship['shipment_id']}"):
                        from app.storage.event_log import transition_shipment
                        
                        transition_shipment(
                            shipment_id=ship['shipment_id'],
                            event_type="RECEIVER_ACKNOWLEDGED",
                            role="RECEIVER_WAREHOUSE"
                        )
                        st.success("Acknowledged!")
                        st.rerun()
                
                with col2:
                    if st.button("❌ Report Issue", key=f"issue_{ship['shipment_id']}"):
                        st.warning("Issue reporting - simplified (not implemented)")
    else:
        st.info("No shipments pending acknowledgment")
    
    # Optional: Show in-transit list
    if st.button("📋 View In-Transit Shipments"):
        st.divider()
        st.markdown("### 🚚 In Transit")
        for ship in in_transit[:30]:  # Limit to 30
            st.write(f"📦 **{ship['shipment_id']}** - {ship.get('current_payload', {}).get('source', 'N/A')} → {ship.get('current_payload', {}).get('destination', 'N/A')}")
