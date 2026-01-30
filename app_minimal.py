"""
National Logistics Control Tower - Performance-Optimized Architecture
Staff+ Level Design: Minimal main file with lazy-loaded modules
"""
import streamlit as st
from datetime import datetime

# ═══════════════════════════════════════════════════════════════
# PAGE CONFIG (MUST BE FIRST)
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="National Logistics Control Tower",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ═══════════════════════════════════════════════════════════════
# SESSION STATE (MINIMAL)
# ═══════════════════════════════════════════════════════════════
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.active_tab = None
    st.session_state.selected_state = None

# ═══════════════════════════════════════════════════════════════
# DATA LOADING (ONCE PER SESSION)
# ═══════════════════════════════════════════════════════════════
@st.cache_resource
def get_shipment_data():
    """Load ALL shipments ONCE per session. Filter in-memory."""
    from app.storage.event_log import get_all_shipments_by_state
    return get_all_shipments_by_state()

# ═══════════════════════════════════════════════════════════════
# HEADER (MINIMAL)
# ═══════════════════════════════════════════════════════════════
st.title("📦 National Logistics Control Tower")
st.caption("Event-driven • Real-time tracking")

# ═══════════════════════════════════════════════════════════════
# TAB NAVIGATION (LAZY LOADED)
# ═══════════════════════════════════════════════════════════════
tab_names = ["📤 Sender", "📊 Manager", "👔 Supervisor", "🔍 Viewer", "🏢 Receiver", "📈 COO"]
tabs = st.tabs(tab_names)

# ═══════════════════════════════════════════════════════════════
# TAB 1: SENDER (LAZY)
# ═══════════════════════════════════════════════════════════════
with tabs[0]:
    if st.session_state.active_tab != "SENDER":
        st.session_state.active_tab = "SENDER"
    
    from ui.sender import render_sender
    render_sender()

# ═══════════════════════════════════════════════════════════════
# TAB 2: MANAGER (LAZY)
# ═══════════════════════════════════════════════════════════════
with tabs[1]:
    if st.session_state.active_tab != "MANAGER":
        st.session_state.active_tab = "MANAGER"
        
    from ui.manager import render_manager
    shipments = get_shipment_data()
    render_manager(shipments)

# ═══════════════════════════════════════════════════════════════
# TAB 3: SUPERVISOR (LAZY)
# ═══════════════════════════════════════════════════════════════
with tabs[2]:
    if st.session_state.active_tab != "SUPERVISOR":
        st.session_state.active_tab = "SUPERVISOR"
        
    from ui.supervisor import render_supervisor
    shipments = get_shipment_data()
    render_supervisor(shipments)

# ═══════════════════════════════════════════════════════════════
# TAB 4: VIEWER (LAZY)
# ═══════════════════════════════════════════════════════════════
with tabs[3]:
    if st.session_state.active_tab != "VIEWER":
        st.session_state.active_tab = "VIEWER"
        
    from ui.viewer import render_viewer
    shipments = get_shipment_data()
    render_viewer(shipments)

# ═══════════════════════════════════════════════════════════════
# TAB 5: RECEIVER (LAZY)
# ═══════════════════════════════════════════════════════════════
with tabs[4]:
    if st.session_state.active_tab != "RECEIVER":
        st.session_state.active_tab = "RECEIVER"
        
    from ui.receiver import render_receiver
    shipments = get_shipment_data()
    render_receiver(shipments)

# ═══════════════════════════════════════════════════════════════
# TAB 6: COO (LAZY - NO AUTO-LOAD)
# ═══════════════════════════════════════════════════════════════
with tabs[5]:
    if st.session_state.active_tab != "COO":
        st.session_state.active_tab = "COO"
    
    st.markdown("## 📈 COO Dashboard")
    st.info("👆 Click 'Load Dashboard' to view analytics")
    
    if st.button("Load Dashboard", type="primary"):
        from ui.coo import render_coo
        shipments = get_shipment_data()
        render_coo(shipments)

# ═══════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════
st.divider()
st.caption(f"⚡ Optimized Architecture • Last updated: {datetime.now().strftime('%H:%M:%S')}")
