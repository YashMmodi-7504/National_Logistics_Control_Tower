"""
Viewer Tab - Minimal Implementation
"""
import streamlit as st
from datetime import datetime

def render_viewer(shipments):
    """Render viewer interface - SIMPLE timeline view"""
    st.markdown("## 👀 Parcel Lifecycle Viewer")
    
    # Search by shipment ID
    search_id = st.text_input("🔍 Search Shipment ID", placeholder="SHP-...")
    
    if search_id:
        matching = [s for s in shipments if search_id.upper() in s['shipment_id'].upper()]
        
        if matching:
            for ship in matching[:5]:  # Max 5 results
                with st.expander(f"📦 {ship['shipment_id']} - {ship['current_state']}", expanded=True):
                    metadata = ship.get('current_payload', {})
                    
                    # Basic info
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**From:** {metadata.get('source', 'N/A')}")
                        st.write(f"**Type:** {metadata.get('delivery_type', 'NORMAL')}")
                    with col2:
                        st.write(f"**To:** {metadata.get('destination', 'N/A')}")
                        st.write(f"**State:** {ship['current_state']}")
                    
                    # Timeline button (lazy load)
                    if st.button("📅 Load Full Timeline", key=f"timeline_{ship['shipment_id']}"):
                        render_timeline(ship)
        else:
            st.warning("No matching shipments found")
    else:
        st.info("Enter a shipment ID to search")
        
        # Show recent shipments (limited)
        if st.button("Load Recent Shipments (Last 50)"):
            st.divider()
            for ship in shipments[:50]:
                st.write(f"**{ship['shipment_id']}** - {ship['current_state']} - {ship.get('current_payload', {}).get('source', 'N/A')} → {ship.get('current_payload', {}).get('destination', 'N/A')}")


def render_timeline(shipment):
    """Render full timeline for a shipment"""
    # Lazy import
    from app.storage.event_log import get_shipment_history
    
    st.markdown("### 📜 Event Timeline")
    
    events = get_shipment_history(shipment['shipment_id'])
    
    for i, event in enumerate(events):
        timestamp = event.get('timestamp', 'N/A')
        event_type = event.get('event_type', 'UNKNOWN')
        role = event.get('role', 'SYSTEM')
        
        # Simple timeline display
        if i == 0:
            icon = "🟢"
        elif i == len(events) - 1:
            icon = "🔴"
        else:
            icon = "🔵"
        
        st.write(f"{icon} **{event_type}** by {role} at {timestamp}")
