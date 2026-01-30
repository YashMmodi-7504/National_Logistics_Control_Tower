"""
Sender Tab - Minimal Implementation
Only loads when tab is active
"""
import streamlit as st

def render_sender():
    """Render sender interface - NO heavy imports until needed"""
    st.markdown("## 📦 Create New Shipment")
    
    with st.form("create_shipment_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            source = st.text_input("Source Location", placeholder="Mumbai, Maharashtra")
        with col2:
            destination = st.text_input("Destination Location", placeholder="Delhi, Delhi")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            weight = st.number_input("Weight (kg)", min_value=0.1, value=5.0, step=0.5)
        with col2:
            delivery_type = st.selectbox("Type", ["Normal", "Express"])
        with col3:
            category = st.selectbox("Category", ["Residential", "Commercial"])
        
        submitted = st.form_submit_button("Create Shipment", type="primary")
        
        if submitted and source and destination:
            # Lazy import ONLY when submitting
            from app.storage.event_log import generate_shipment_id, create_shipment
            
            shipment_id = generate_shipment_id()
            create_shipment(
                shipment_id=shipment_id,
                source=source,
                destination=destination,
                delivery_type=delivery_type.upper(),
                weight_kg=weight,
                sender_id="SENDER_001"
            )
            
            st.success(f"✅ Shipment {shipment_id} created successfully!")
            st.balloons()
    
    # Show recent shipments - SIMPLE list, no computations
    st.divider()
    st.markdown("### 📋 Recent Shipments")
    
    if st.button("Load My Shipments"):
        from app.storage.event_log import get_all_shipments_by_state
        created = get_all_shipments_by_state("CREATED")
        
        if created:
            for ship in created[:10]:  # Only show 10
                with st.expander(f"📦 {ship['shipment_id']}"):
                    metadata = ship['current_payload']
                    st.write(f"**From:** {metadata.get('source', 'N/A')}")
                    st.write(f"**To:** {metadata.get('destination', 'N/A')}")
                    st.write(f"**Type:** {metadata.get('delivery_type', 'NORMAL')}")
        else:
            st.info("No shipments created yet")
