"""
COO Dashboard - Minimal Implementation
ALL analytics behind explicit load button
"""
import streamlit as st

def render_coo(shipments):
    """Render COO dashboard - LAZY LOAD EVERYTHING"""
    st.markdown("## 📊 COO Analytics Dashboard")
    
    # Basic metrics only (no heavy computation)
    st.markdown("### Quick Metrics")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Shipments", len(shipments))
    with col2:
        delivered = len([s for s in shipments if s.get('current_state') == 'DELIVERED'])
        st.metric("Delivered", delivered)
    with col3:
        in_transit = len([s for s in shipments if s.get('current_state') == 'IN_TRANSIT'])
        st.metric("In Transit", in_transit)
    with col4:
        pending = len([s for s in shipments if s.get('current_state') == 'CREATED'])
        st.metric("Pending", pending)
    
    st.divider()
    
    # Everything else behind buttons
    st.markdown("### 📈 Detailed Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Load State Distribution Chart"):
            render_state_chart(shipments)
    
    with col2:
        if st.button("🗺️ Load Geographic Map"):
            render_geo_map(shipments)
    
    st.divider()
    
    if st.button("📋 Load Detailed Shipment Table"):
        render_shipment_table(shipments)


def render_state_chart(shipments):
    """Render state distribution - LAZY imports"""
    try:
        import pandas as pd
        import plotly.express as px
        
        st.markdown("#### State Distribution")
        
        # Count by state
        state_counts = {}
        for ship in shipments:
            state = ship.get('current_state', 'UNKNOWN')
            state_counts[state] = state_counts.get(state, 0) + 1
        
        df = pd.DataFrame(list(state_counts.items()), columns=['State', 'Count'])
        
        fig = px.bar(df, x='State', y='Count', title='Shipments by State')
        st.plotly_chart(fig, use_container_width=True)
        
    except ImportError:
        st.error("Install plotly: pip install plotly pandas")


def render_geo_map(shipments):
    """Render geographic map - LAZY imports"""
    try:
        import pandas as pd
        import pydeck as pdk
        
        st.markdown("#### Geographic Distribution")
        
        # Sample coordinates for demo (in production, use real geo data)
        locations = {
            'Mumbai': [19.0760, 72.8777],
            'Delhi': [28.6139, 77.2090],
            'Bangalore': [12.9716, 77.5946],
            'Kolkata': [22.5726, 88.3639],
            'Chennai': [13.0827, 80.2707]
        }
        
        # Count shipments by location
        location_data = []
        for ship in shipments[:100]:  # Limit to 100 for performance
            source = ship.get('current_payload', {}).get('source', '')
            if source in locations:
                location_data.append({
                    'lat': locations[source][0],
                    'lon': locations[source][1],
                    'count': 1
                })
        
        if location_data:
            df = pd.DataFrame(location_data)
            
            # Simple scatter map
            st.pydeck_chart(pdk.Deck(
                initial_view_state=pdk.ViewState(
                    latitude=20.5937,
                    longitude=78.9629,
                    zoom=4,
                    pitch=0,
                ),
                layers=[
                    pdk.Layer(
                        'ScatterplotLayer',
                        data=df,
                        get_position='[lon, lat]',
                        get_radius=50000,
                        get_color='[200, 30, 0, 160]',
                        pickable=True
                    ),
                ],
            ))
        else:
            st.info("No location data available")
            
    except ImportError:
        st.error("Install pydeck: pip install pydeck pandas")


def render_shipment_table(shipments):
    """Render shipment table - LAZY imports"""
    try:
        import pandas as pd
        
        st.markdown("#### Recent Shipments")
        
        # Convert to dataframe (limit to 100 for performance)
        data = []
        for ship in shipments[:100]:
            metadata = ship.get('current_payload', {})
            data.append({
                'ID': ship['shipment_id'],
                'State': ship['current_state'],
                'Source': metadata.get('source', 'N/A'),
                'Destination': metadata.get('destination', 'N/A'),
                'Type': metadata.get('delivery_type', 'NORMAL'),
                'Weight (kg)': metadata.get('weight', 0)
            })
        
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)
        
    except ImportError:
        st.error("Install pandas: pip install pandas")
