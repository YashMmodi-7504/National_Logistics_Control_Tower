# app/ui/alerts_banner.py

import streamlit as st
from app.core.snapshot_store import read_alerts_snapshot


def render_alerts_banner():
    snapshot = read_alerts_snapshot()
    alerts = snapshot.get("alerts", [])

    if not alerts:
        return

    st.error("🚨 ACTIVE LOGISTICS ALERTS", icon="⚠️")

    for alert in alerts:
        corridor = alert.get("corridor")
        severity = alert.get("severity")
        reason = alert.get("reason")

        st.markdown(
            f"""
            **Corridor:** {corridor}  
            **Severity:** `{severity}`  
            **Reason:** {reason}
            ---
            """
        )
