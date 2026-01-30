"""
REGULATOR DASHBOARD

Purpose:
- Render regulator UI in Streamlit
- Read-only, snapshot-driven interface
- Court-defensible and explainable

UI Rules:
- Read-only (no action buttons)
- Snapshot-driven (no live data)
- No filters that mutate scope
- No buttons that trigger actions
- No refresh controls
"""

import streamlit as st
from datetime import datetime
from app.audit.regulator_views import (
    get_sla_health_summary,
    get_corridor_health_summary,
    get_alerts_timeline,
    get_snapshot_metadata,
    get_heatmap_summary,
    get_compliance_status,
)
from app.compliance.compliance_export_engine import (
    export_audit_denials,
    export_role_activity,
    export_geo_violations,
)
from app.compliance.export_read_model import serialize_export
from app.compliance.export_types import (
    EXPORT_FORMAT_JSON,
    EXPORT_FORMAT_CSV,
)


def render_regulator_dashboard():
    """
    Render the complete regulator dashboard.
    
    This is the main entry point for the regulator UI.
    All data is read-only and snapshot-based.
    """
    st.header("🏛️ Regulator Dashboard")
    st.caption("Read-only • Snapshot-based • Court-defensible")
    
    # Access warning
    st.info(
        "ℹ️ **Regulator Mode Active**\n\n"
        "• All data is snapshot-based\n"
        "• No real-time operations available\n"
        "• All actions are audit-logged\n"
        "• Exports are compliance-ready"
    )
    
    st.divider()
    
    # Section 1: Compliance Status Overview
    _render_compliance_status_section()
    
    st.divider()
    
    # Section 2: SLA Breach Summary
    _render_sla_breach_section()
    
    st.divider()
    
    # Section 3: Corridor Risk Summary
    _render_corridor_risk_section()
    
    st.divider()
    
    # Section 4: Alerts Timeline
    _render_alerts_timeline_section()
    
    st.divider()
    
    # Section 5: Compliance Export Section
    _render_compliance_export_section()


# ==================================================
# SECTION 1: COMPLIANCE STATUS OVERVIEW
# ==================================================

def _render_compliance_status_section():
    """Render compliance status overview section."""
    st.subheader("📊 Compliance Status Overview")
    
    try:
        status = get_compliance_status()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Snapshots",
                status.get("total_snapshots", 0)
            )
        
        with col2:
            st.metric(
                "Available",
                status.get("available_snapshots", 0)
            )
        
        with col3:
            all_available = status.get("all_snapshots_available", False)
            st.metric(
                "Status",
                "✅ Complete" if all_available else "⚠️ Partial"
            )
        
        with col4:
            last_update = status.get("last_update")
            if last_update:
                update_str = datetime.fromtimestamp(last_update).strftime("%H:%M:%S")
            else:
                update_str = "N/A"
            st.metric("Last Update", update_str)
        
        # Show missing snapshots if any
        missing = status.get("missing_snapshots", [])
        if missing:
            st.warning(f"⚠️ Missing snapshots: {', '.join(missing)}")
        
        # Snapshot metadata table
        metadata = get_snapshot_metadata()
        if metadata:
            st.markdown("#### Snapshot Inventory")
            st.table({
                "Snapshot": [m["snapshot_name"] for m in metadata],
                "Status": ["✅ Available" if m["exists"] else "❌ Missing" for m in metadata],
                "Description": [m["description"] for m in metadata],
            })
    
    except Exception as e:
        st.error(f"❌ Error loading compliance status: {str(e)}")


# ==================================================
# SECTION 2: SLA BREACH SUMMARY
# ==================================================

def _render_sla_breach_section():
    """Render SLA breach summary section."""
    st.subheader("⏱️ SLA Breach Summary (Historical)")
    
    try:
        sla_data = get_sla_health_summary()
        
        if not sla_data.get("snapshot_exists"):
            st.warning("⚠️ SLA snapshot not available")
            return
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Shipments",
                sla_data.get("total_shipments", 0)
            )
        
        with col2:
            st.metric(
                "High Risk",
                sla_data.get("high_risk_count", 0),
                delta=None,
                delta_color="inverse"
            )
        
        with col3:
            st.metric(
                "Medium Risk",
                sla_data.get("medium_risk_count", 0)
            )
        
        with col4:
            avg_prob = sla_data.get("avg_breach_probability")
            if avg_prob is not None:
                st.metric(
                    "Avg Breach Risk",
                    f"{int(avg_prob * 100)}%"
                )
            else:
                st.metric("Avg Breach Risk", "N/A")
        
        # Risk distribution
        st.markdown("#### Risk Distribution")
        risk_data = {
            "Risk Level": ["High (>70%)", "Medium (40-70%)", "Low (<40%)"],
            "Count": [
                sla_data.get("high_risk_count", 0),
                sla_data.get("medium_risk_count", 0),
                sla_data.get("low_risk_count", 0),
            ],
        }
        st.table(risk_data)
    
    except Exception as e:
        st.error(f"❌ Error loading SLA data: {str(e)}")


# ==================================================
# SECTION 3: CORRIDOR RISK SUMMARY
# ==================================================

def _render_corridor_risk_section():
    """Render corridor risk summary section."""
    st.subheader("🛣️ Corridor Risk Summary")
    
    try:
        corridor_data = get_corridor_health_summary()
        
        if not corridor_data.get("snapshot_exists"):
            st.warning("⚠️ Corridor snapshot not available")
            return
        
        st.metric("Total Corridors", corridor_data.get("total_corridors", 0))
        
        corridors = corridor_data.get("corridors", [])
        if corridors:
            st.markdown("#### Corridor Health Table")
            
            # Create table data
            table_data = {
                "Corridor": [c["corridor"] for c in corridors],
                "Source": [c["source_state"] for c in corridors],
                "Destination": [c["destination_state"] for c in corridors],
                "Avg Breach Risk": [f"{int(c['avg_breach_probability'] * 100)}%" for c in corridors],
                "Shipments": [c["shipment_count"] for c in corridors],
            }
            
            st.dataframe(table_data, use_container_width=True)
        else:
            st.info("No corridor data available")
    
    except Exception as e:
        st.error(f"❌ Error loading corridor data: {str(e)}")


# ==================================================
# SECTION 4: ALERTS TIMELINE
# ==================================================

def _render_alerts_timeline_section():
    """Render alerts timeline section."""
    st.subheader("🚨 Alerts Timeline")
    
    try:
        alerts_data = get_alerts_timeline()
        
        if not alerts_data.get("snapshot_exists"):
            st.warning("⚠️ Alerts snapshot not available")
            return
        
        total_alerts = alerts_data.get("total_alerts", 0)
        
        if total_alerts == 0:
            st.success("✅ No active alerts")
            return
        
        st.warning(f"⚠️ {total_alerts} active corridor alerts")
        
        alerts = alerts_data.get("alerts", [])
        if alerts:
            st.markdown("#### Active Alerts")
            
            # Create table data
            table_data = {
                "Corridor": [a["corridor"] for a in alerts],
                "Severity": [a["severity"] for a in alerts],
                "Breach Risk": [f"{int(a['breach_probability'] * 100)}%" for a in alerts],
                "Affected Shipments": [a["shipment_count"] for a in alerts],
            }
            
            st.dataframe(table_data, use_container_width=True)
            
            # Severity breakdown
            severity_counts = {}
            for alert in alerts:
                severity = alert["severity"]
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            st.markdown("#### Severity Breakdown")
            st.table({
                "Severity": list(severity_counts.keys()),
                "Count": list(severity_counts.values()),
            })
    
    except Exception as e:
        st.error(f"❌ Error loading alerts data: {str(e)}")


# ==================================================
# SECTION 5: COMPLIANCE EXPORT SECTION
# ==================================================

def _render_compliance_export_section():
    """Render compliance export section."""
    st.subheader("📥 Compliance Export Section")
    
    st.info(
        "📋 **Export Information**\n\n"
        "All exports are snapshot-based and compliance-ready. "
        "Select a role and format, then download the export."
    )
    
    # Role selection (for audit purposes)
    role = st.selectbox(
        "Select Role (for audit exports)",
        ["SENDER_MANAGER", "RECEIVER_MANAGER", "COO", "VIEWER"],
        help="Role to generate audit exports for"
    )
    
    # Export format
    export_format = st.radio(
        "Export Format",
        [EXPORT_FORMAT_JSON, EXPORT_FORMAT_CSV],
        horizontal=True,
    )
    
    st.divider()
    
    # Export options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🚫 Access Denials")
        if st.button("Generate Access Denials Export", use_container_width=True):
            try:
                export_data = export_audit_denials(role=role)
                serialized = serialize_export(export_data, export_format)
                
                file_ext = "json" if export_format == EXPORT_FORMAT_JSON else "csv"
                filename = f"access_denials_{role}.{file_ext}"
                
                st.download_button(
                    label=f"⬇️ Download {filename}",
                    data=serialized,
                    file_name=filename,
                    mime="application/json" if export_format == EXPORT_FORMAT_JSON else "text/csv",
                    use_container_width=True,
                )
                
                st.success(f"✅ Export ready: {export_data.get('total_denials', 0)} records")
            except Exception as e:
                st.error(f"❌ Export failed: {str(e)}")
    
    with col2:
        st.markdown("#### 📈 Role Activity")
        if st.button("Generate Role Activity Export", use_container_width=True):
            try:
                export_data = export_role_activity(role=role)
                serialized = serialize_export(export_data, export_format)
                
                file_ext = "json" if export_format == EXPORT_FORMAT_JSON else "csv"
                filename = f"role_activity_{role}.{file_ext}"
                
                st.download_button(
                    label=f"⬇️ Download {filename}",
                    data=serialized,
                    file_name=filename,
                    mime="application/json" if export_format == EXPORT_FORMAT_JSON else "text/csv",
                    use_container_width=True,
                )
                
                st.success("✅ Export ready")
            except Exception as e:
                st.error(f"❌ Export failed: {str(e)}")
    
    with col3:
        st.markdown("#### 🌍 Geo Violations")
        if st.button("Generate Geo Violations Export", use_container_width=True):
            try:
                export_data = export_geo_violations(role=role)
                serialized = serialize_export(export_data, export_format)
                
                file_ext = "json" if export_format == EXPORT_FORMAT_JSON else "csv"
                filename = f"geo_violations_{role}.{file_ext}"
                
                st.download_button(
                    label=f"⬇️ Download {filename}",
                    data=serialized,
                    file_name=filename,
                    mime="application/json" if export_format == EXPORT_FORMAT_JSON else "text/csv",
                    use_container_width=True,
                )
                
                st.success(f"✅ Export ready: {export_data.get('total_violations', 0)} violations")
            except Exception as e:
                st.error(f"❌ Export failed: {str(e)}")


# ==================================================
# HEATMAP SUMMARY (OPTIONAL)
# ==================================================

def _render_heatmap_summary():
    """Render heatmap summary (optional section)."""
    st.subheader("🗺️ Geographic Risk Summary")
    
    try:
        heatmap_data = get_heatmap_summary()
        
        if not heatmap_data.get("snapshot_exists"):
            st.warning("⚠️ Heatmap snapshot not available")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "Total Risk Points",
                heatmap_data.get("total_points", 0)
            )
        
        with col2:
            st.metric(
                "High Risk Points",
                heatmap_data.get("high_risk_points", 0),
                delta=None,
                delta_color="inverse"
            )
    
    except Exception as e:
        st.error(f"❌ Error loading heatmap data: {str(e)}")
