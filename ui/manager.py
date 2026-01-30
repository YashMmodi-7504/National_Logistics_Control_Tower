"""
Manager Tab - Minimal Implementation
Shows overview ONLY - no maps/charts until requested
"""
import streamlit as st

def render_manager(shipments):
    """Render manager dashboard - MINIMAL by default"""
    st.markdown("## 📊 Manager Dashboard")
    
    # Simple metrics - NO heavy computation
    if not shipments:
        st.info("No shipments to display")
        return
    
    # Filter by state (in-memory, fast)
    created = [s for s in shipments if s.get('current_state') == 'CREATED']
    approved = [s for s in shipments if s.get('current_state') == 'MANAGER_APPROVED']
    
    # Simple KPIs
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Shipments", len(shipments))
    col2.metric("Pending Approval", len(created))
    col3.metric("Approved", len(approved))
    col4.metric("Today", len([s for s in created if 'today' in str(s.get('created_at', ''))]))
    
    st.divider()
    
    # Approval Interface - SIMPLE list
    st.markdown("### ✅ Approve Shipments")
    
    if created:
        for ship in created[:20]:  # Limit to 20
            with st.expander(f"📦 {ship['shipment_id']}"):
                metadata = ship.get('current_payload', {})
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**Route:** {metadata.get('source', 'N/A')} → {metadata.get('destination', 'N/A')}")
                    st.write(f"**Type:** {metadata.get('delivery_type', 'NORMAL')}")
                    st.write(f"**Weight:** {metadata.get('weight_kg', 0)} kg")
                
                with col2:
                    if st.button("Approve", key=f"approve_{ship['shipment_id']}"):
                        from app.storage.event_log import transition_shipment
                        transition_shipment(
                            shipment_id=ship['shipment_id'],
                            event_type="MANAGER_APPROVED",
                            role="SENDER_MANAGER"
                        )
                        st.success("Approved!")
                        st.rerun()
    else:
        st.info("No shipments pending approval")
    
    # Analytics - OPTIONAL (behind button)
    st.divider()
    if st.button("📊 Load Analytics Dashboard"):
        render_analytics(shipments)

def render_analytics(shipments):
    """Heavy analytics - ONLY when explicitly requested"""
    import pandas as pd
    import plotly.express as px
    
    st.markdown("### 📈 Analytics")
    
    # Simple DataFrame
    df = pd.DataFrame([
        {
            'id': s['shipment_id'],
            'state': s.get('current_state', 'UNKNOWN'),
            'type': s.get('current_payload', {}).get('delivery_type', 'NORMAL')
        }
        for s in shipments[:100]  # Limit
    ])
    
    # Simple chart
    state_counts = df['state'].value_counts()
    fig = px.bar(state_counts, title="Shipments by State")
    st.plotly_chart(fig, use_container_width=True)
    
    st.dataframe(df, use_container_width=True)
