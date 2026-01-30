"""
Supervisor Tab - Minimal Implementation
"""
import streamlit as st

def render_supervisor(shipments):
    """Render supervisor interface - SIMPLE dispatch"""
    st.markdown("## 👔 Supervisor Operations")
    
    # Filter approved shipments (in-memory)
    manager_approved = [s for s in shipments if s.get('current_state') == 'MANAGER_APPROVED']
    
    st.metric("Ready for Dispatch", len(manager_approved))
    
    st.divider()
    st.markdown("### 🚀 Dispatch Shipments")
    
    if manager_approved:
        for ship in manager_approved[:15]:  # Limit to 15
            with st.expander(f"📦 {ship['shipment_id']}"):
                metadata = ship.get('current_payload', {})
                
                st.write(f"**Route:** {metadata.get('source')} → {metadata.get('destination')}")
                st.write(f"**Type:** {metadata.get('delivery_type', 'NORMAL')}")
                
                if st.button("Approve & Dispatch", key=f"dispatch_{ship['shipment_id']}"):
                    from app.storage.event_log import transition_shipment
                    
                    # Two transitions: Supervisor approval → In Transit
                    transition_shipment(
                        shipment_id=ship['shipment_id'],
                        event_type="SUPERVISOR_APPROVED",
                        role="SENDER_SUPERVISOR"
                    )
                    transition_shipment(
                        shipment_id=ship['shipment_id'],
                        event_type="IN_TRANSIT",
                        role="SYSTEM"
                    )
                    
                    st.success(f"✅ {ship['shipment_id']} dispatched!")
                    st.rerun()
    else:
        st.info("No shipments ready for dispatch")
