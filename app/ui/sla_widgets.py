# app/ui/sla_widgets.py

import streamlit as st
from app.core.snapshot_store import read_sla_snapshot


def render_sla_overview():
    snapshot = read_sla_snapshot()
    data = snapshot.get("data", {})

    if not data:
        st.info("No SLA data available.")
        return

    high = sum(1 for v in data.values() if v["risk_level"] == "HIGH")
    med = sum(1 for v in data.values() if v["risk_level"] == "MEDIUM")
    low = sum(1 for v in data.values() if v["risk_level"] == "LOW")

    c1, c2, c3 = st.columns(3)
    c1.metric("🔴 High Risk", high)
    c2.metric("🟠 Medium Risk", med)
    c3.metric("🟢 Low Risk", low)
