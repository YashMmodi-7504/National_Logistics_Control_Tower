"""
FORENSIC DASHBOARD

Purpose:
- Detailed forensic analysis interface
- Internal audit and legal team
- Tamper detection and evidence export

Requirements:
- Tamper checks
- Snapshot verification logs
- Incident timelines
- Evidence export (download only)
"""

import streamlit as st
from datetime import datetime
from app.security.tamper_detector import detect_snapshot_tampering, get_integrity_status
from app.forensics.incident_timeline import (
    build_incident_timeline,
    build_multi_snapshot_timeline,
    get_timeline_summary,
    export_timeline_text,
)
from app.forensics.evidence_exporter import export_evidence, export_multiple_snapshots, EvidenceExportError
from app.policies.regulator_policy import ALLOWED_SNAPSHOTS


def render_forensic_dashboard():
    """
    Render forensic investigation dashboard.
    
    Audience: Internal audit, legal team, forensic investigators
    Focus: Detailed tamper detection, timelines, evidence
    """
    st.header("🔬 Forensic Investigation Dashboard")
    st.caption("Tamper Detection • Timeline Reconstruction • Evidence Export")
    
    st.divider()
    
    # Section 1: Snapshot Verification
    _render_snapshot_verification()
    
    st.divider()
    
    # Section 2: Tamper Detection
    _render_tamper_detection()
    
    st.divider()
    
    # Section 3: Incident Timeline
    _render_incident_timeline()
    
    st.divider()
    
    # Section 4: Evidence Export
    _render_evidence_export()


def _render_snapshot_verification():
    """Render snapshot verification section."""
    st.subheader("✅ Snapshot Verification")
    
    st.info(
        "Verify cryptographic integrity of snapshots. "
        "Each verification checks hash, signature, and chain linkage."
    )
    
    try:
        status = get_integrity_status(ALLOWED_SNAPSHOTS)
        
        # Overall status
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total", status["total"])
        
        with col2:
            st.metric("✅ Intact", status["intact"], delta_color="normal")
        
        with col3:
            st.metric("🚨 Tampered", status["tampered"], delta_color="inverse")
        
        with col4:
            st.metric("❌ Issues", status["missing"] + status["error"], delta_color="inverse")
        
        # Detailed table
        st.markdown("#### Verification Details")
        
        verification_data = []
        for detail in status["details"]:
            snapshot_name = detail.get("violated_rules", ["unknown"])[0] if detail.get("violated_rules") else "N/A"
            
            verification_data.append({
                "Snapshot": snapshot_name,
                "Status": detail["status"],
                "Severity": detail.get("severity", "N/A"),
                "Issues": ", ".join(detail.get("violated_rules", [])) or "None",
            })
        
        if verification_data:
            st.dataframe(verification_data, use_container_width=True)
    
    except Exception as e:
        st.error(f"❌ Verification failed: {str(e)}")


def _render_tamper_detection():
    """Render tamper detection section."""
    st.subheader("🔍 Tamper Detection")
    
    st.markdown(
        "Select a snapshot to run detailed tamper detection analysis. "
        "This includes hash verification, signature validation, and chain integrity."
    )
    
    # Snapshot selector
    snapshot_name = st.selectbox(
        "Select Snapshot",
        ALLOWED_SNAPSHOTS,
        help="Choose a snapshot to analyze"
    )
    
    if st.button("🔍 Run Tamper Detection", use_container_width=True):
        with st.spinner("Running tamper detection..."):
            try:
                result = detect_snapshot_tampering(snapshot_name)
                
                # Display results
                status = result["status"]
                
                if status == "INTACT":
                    st.success(f"✅ Snapshot **{snapshot_name}** is INTACT")
                elif status == "TAMPERED":
                    st.error(f"🚨 Snapshot **{snapshot_name}** has been TAMPERED")
                elif status == "MISSING":
                    st.warning(f"⚠️ Snapshot **{snapshot_name}** is MISSING")
                else:
                    st.error(f"❌ Error verifying **{snapshot_name}**")
                
                # Details
                with st.expander("📋 Detection Details"):
                    st.json(result)
                
                # Violated rules
                if result.get("violated_rules"):
                    st.markdown("#### Violated Rules")
                    for rule in result["violated_rules"]:
                        st.error(f"❌ {rule}")
                
                # Severity
                if result.get("severity"):
                    st.markdown(f"**Severity:** {result['severity']}")
            
            except Exception as e:
                st.error(f"❌ Tamper detection failed: {str(e)}")


def _render_incident_timeline():
    """Render incident timeline section."""
    st.subheader("📅 Incident Timeline Reconstruction")
    
    st.markdown(
        "Reconstruct the sequence of events from snapshot data. "
        "Timelines are ordered chronologically and include integrity events."
    )
    
    # Timeline type selector
    timeline_type = st.radio(
        "Timeline Type",
        ["Single Snapshot", "All Snapshots"],
        horizontal=True,
    )
    
    if timeline_type == "Single Snapshot":
        snapshot_name = st.selectbox(
            "Select Snapshot",
            ALLOWED_SNAPSHOTS,
            key="timeline_snapshot"
        )
        
        if st.button("🔄 Build Timeline", use_container_width=True):
            with st.spinner("Building timeline..."):
                try:
                    timeline = build_incident_timeline(snapshot_name, include_integrity=True)
                    
                    if not timeline:
                        st.warning("No events found in timeline")
                        return
                    
                    # Display summary
                    summary = get_timeline_summary(timeline)
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Total Events", summary["total_events"])
                    
                    with col2:
                        event_types = summary["event_types"]
                        st.metric("Event Types", len(event_types))
                    
                    with col3:
                        time_span = summary.get("time_span")
                        if time_span:
                            duration = int(time_span["duration_seconds"])
                            st.metric("Duration", f"{duration}s")
                    
                    # Display timeline
                    st.markdown("#### Timeline Events")
                    
                    for entry in timeline:
                        dt = datetime.fromtimestamp(entry.timestamp) if entry.timestamp > 0 else None
                        time_str = dt.strftime("%Y-%m-%d %H:%M:%S") if dt else "N/A"
                        
                        severity_icon = {
                            "CRITICAL": "🔴",
                            "ERROR": "❌",
                            "WARNING": "⚠️",
                            "INFO": "ℹ️",
                        }.get(entry.severity, "•")
                        
                        with st.container(border=True):
                            st.markdown(f"**{severity_icon} {entry.event_type}**")
                            st.text(f"Time: {time_str}")
                            st.text(f"Description: {entry.description}")
                    
                    # Export timeline
                    timeline_text = export_timeline_text(timeline)
                    st.download_button(
                        label="📥 Download Timeline (TXT)",
                        data=timeline_text,
                        file_name=f"timeline_{snapshot_name}.txt",
                        mime="text/plain",
                    )
                
                except Exception as e:
                    st.error(f"❌ Timeline reconstruction failed: {str(e)}")
    
    else:  # All snapshots
        if st.button("🔄 Build Combined Timeline", use_container_width=True):
            with st.spinner("Building combined timeline..."):
                try:
                    timeline = build_multi_snapshot_timeline(ALLOWED_SNAPSHOTS)
                    
                    if not timeline:
                        st.warning("No events found")
                        return
                    
                    # Display summary
                    summary = get_timeline_summary(timeline)
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Total Events", summary["total_events"])
                    
                    with col2:
                        st.metric("Snapshots", len(ALLOWED_SNAPSHOTS))
                    
                    with col3:
                        severity = summary.get("severity_breakdown", {})
                        critical = severity.get("CRITICAL", 0) + severity.get("ERROR", 0)
                        st.metric("Critical/Error", critical, delta_color="inverse")
                    
                    # Show recent events
                    st.markdown("#### Recent Events (Last 10)")
                    
                    for entry in timeline[-10:]:
                        dt = datetime.fromtimestamp(entry.timestamp) if entry.timestamp > 0 else None
                        time_str = dt.strftime("%H:%M:%S") if dt else "N/A"
                        
                        st.text(f"{time_str} | {entry.event_type} | {entry.snapshot_name}")
                    
                    # Export
                    timeline_text = export_timeline_text(timeline)
                    st.download_button(
                        label="📥 Download Combined Timeline",
                        data=timeline_text,
                        file_name="timeline_all_snapshots.txt",
                        mime="text/plain",
                    )
                
                except Exception as e:
                    st.error(f"❌ Timeline failed: {str(e)}")


def _render_evidence_export():
    """Render evidence export section."""
    st.subheader("📦 Evidence Export")
    
    st.warning(
        "⚠️ **LEGAL EVIDENCE EXPORT**\n\n"
        "Exported packages include cryptographic proofs and verification instructions. "
        "Handle with appropriate chain of custody procedures."
    )
    
    # Export type
    export_type = st.radio(
        "Export Type",
        ["Single Snapshot", "All Snapshots"],
        horizontal=True,
        key="export_type"
    )
    
    # Export format
    export_format = st.selectbox(
        "Export Format",
        ["zip", "json"],
        help="ZIP includes all verification materials, JSON is single file"
    )
    
    # Include timeline
    include_timeline = st.checkbox("Include Incident Timeline", value=True)
    
    st.divider()
    
    if export_type == "Single Snapshot":
        snapshot_name = st.selectbox(
            "Select Snapshot",
            ALLOWED_SNAPSHOTS,
            key="export_snapshot"
        )
        
        if st.button("📦 Generate Evidence Package", use_container_width=True):
            with st.spinner("Generating evidence package..."):
                try:
                    evidence_bytes = export_evidence(
                        snapshot_name=snapshot_name,
                        format=export_format,
                        include_timeline=include_timeline,
                    )
                    
                    # Offer download
                    file_ext = "zip" if export_format == "zip" else "json"
                    filename = f"evidence_{snapshot_name}.{file_ext}"
                    
                    st.success(f"✅ Evidence package ready: {len(evidence_bytes)} bytes")
                    
                    st.download_button(
                        label=f"⬇️ Download Evidence Package",
                        data=evidence_bytes,
                        file_name=filename,
                        mime="application/zip" if export_format == "zip" else "application/json",
                        use_container_width=True,
                    )
                    
                    st.info(
                        "📋 **Package Contents:**\n"
                        "- Snapshot payload (JSON)\n"
                        "- Cryptographic hash\n"
                        "- Digital signature\n"
                        "- Integrity report\n"
                        "- Verification instructions\n"
                        + ("- Incident timeline\n" if include_timeline else "")
                    )
                
                except EvidenceExportError as e:
                    st.error(f"❌ Export failed: {str(e)}")
                except Exception as e:
                    st.error(f"❌ Unexpected error: {str(e)}")
    
    else:  # All snapshots
        if st.button("📦 Generate Combined Evidence Package", use_container_width=True):
            with st.spinner("Generating combined evidence package..."):
                try:
                    evidence_bytes = export_multiple_snapshots(
                        snapshot_names=ALLOWED_SNAPSHOTS,
                        include_timeline=include_timeline,
                    )
                    
                    filename = f"evidence_all_snapshots_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
                    
                    st.success(f"✅ Combined evidence ready: {len(evidence_bytes)} bytes")
                    
                    st.download_button(
                        label=f"⬇️ Download Combined Evidence",
                        data=evidence_bytes,
                        file_name=filename,
                        mime="application/zip",
                        use_container_width=True,
                    )
                    
                    st.info(
                        f"📋 **Package includes {len(ALLOWED_SNAPSHOTS)} snapshots** with "
                        f"complete verification materials for each."
                    )
                
                except Exception as e:
                    st.error(f"❌ Export failed: {str(e)}")
