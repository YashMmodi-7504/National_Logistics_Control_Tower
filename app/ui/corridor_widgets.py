# app/ui/corridor_widgets.py

import pandas as pd
import plotly.express as px
import streamlit as st
from app.core.snapshot_store import read_corridor_snapshot


def render_corridor_heatmap():
    snapshot = read_corridor_snapshot()
    data = snapshot.get("data", [])

    if not data:
        st.info("No corridor SLA data available.")
        return

    df = pd.DataFrame(data)

    fig = px.density_heatmap(
        df,
        x="source_state",
        y="destination_state",
        z="sla_risk_score",
        color_continuous_scale="RdYlGn_r",
        title="🚦 Corridor SLA Risk Heatmap"
    )

    st.plotly_chart(fig, use_container_width=True)
