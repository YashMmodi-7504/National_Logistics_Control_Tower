import json
import plotly.express as px


def render_india_heatmap(state_summary: dict):
    """
    Renders a Plotly choropleth map of India based on state-wise shipment data.
    """

    with open("app/data/india_states.geojson", "r", encoding="utf-8") as f:
        india_geojson = json.load(f)

    # Prepare dataframe-like lists
    states = []
    values = []

    for state, metrics in state_summary.items():
        states.append(state)
        values.append(metrics.get("total", 0))

    fig = px.choropleth(
        geojson=india_geojson,
        locations=states,
        featureidkey="properties.ST_NM",
        color=values,
        color_continuous_scale="Reds",
        range_color=(0, max(values) if values else 1),
        labels={"color": "Shipments"},
    )

    fig.update_geos(
        fitbounds="locations",
        visible=False
    )

    fig.update_layout(
        title="📍 India — State-wise Shipment Density",
        margin={"r":0,"t":50,"l":0,"b":0},
        height=600
    )

    return fig
