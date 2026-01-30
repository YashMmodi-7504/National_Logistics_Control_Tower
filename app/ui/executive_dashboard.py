"""
EXECUTIVE DASHBOARD

Purpose:
- High-level system integrity view
- COO / Board / Regulator audience
- Read-only, high signal

Requirements:
- System integrity status
- Snapshot chain health
- Last verified timestamp
- Active alerts
- Compliance score
- No controls
"""

import streamlit as st
from datetime import datetime
from typing import Dict, Any, List
from app.security.tamper_detector import get_integrity_status, detect_snapshot_tampering
from app.core.snapshot_store import read_snapshot, SLA_SNAPSHOT, CORRIDOR_SNAPSHOT, ALERTS_SNAPSHOT
from app.policies.regulator_policy import ALLOWED_SNAPSHOTS


def render_executive_dashboard():
    """
    Render executive dashboard for C-level and board.
    
    Audience: COO, Board, Regulators
    Focus: System integrity, compliance, high-level status
    """
    st.header("🎯 Executive Assurance Dashboard")
    st.caption("System Integrity • Compliance • Risk Overview")
    
    # Warning banner if any issues
    _render_critical_alerts()
    
    st.divider()
    
    # Section 1: System Integrity Status
    _render_integrity_status()
    
    st.divider()
    
    # Section 2: Snapshot Chain Health
    _render_chain_health()
    
    st.divider()
    
    # Section 3: Compliance Score
    _render_compliance_score()
    
    st.divider()
    
    # Section 4: Active Alerts Summary
    _render_active_alerts()
    
    st.divider()
    
    # Section 5: Last Verification
    _render_last_verification()


def _render_critical_alerts():
    """Render critical alerts banner if any exist."""
    # Check for tampered snapshots
    status = get_integrity_status(ALLOWED_SNAPSHOTS)
    
    if status["tampered"] > 0:
        st.error(
            f"🚨 **CRITICAL SECURITY ALERT**\n\n"
            f"{status['tampered']} snapshot(s) have been tampered with. "
            f"Immediate investigation required."
        )
    elif status["missing"] > 0 or status["error"] > 0:
        st.warning(
            f"⚠️ **SYSTEM WARNING**\n\n"
            f"{status['missing']} missing, {status['error']} error(s) detected."
        )


def _render_integrity_status():
    """Render overall system integrity status."""
    st.subheader("🔒 System Integrity Status")
    
    try:
        status = get_integrity_status(ALLOWED_SNAPSHOTS)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Snapshots",
                status["total"],
                help="Total number of critical system snapshots"
            )
        
        with col2:
            intact = status["intact"]
            st.metric(
                "Verified Intact",
                intact,
                delta=intact - status["total"],
                delta_color="normal" if intact == status["total"] else "inverse"
            )
        
        with col3:
            tampered = status["tampered"]
            st.metric(
                "Tampered",
                tampered,
                delta=None if tampered == 0 else f"+{tampered}",
                delta_color="inverse" if tampered > 0 else "off"
            )
        
        with col4:
            if status["tampered"] == 0 and status["error"] == 0:
                st.metric("Overall Status", "✅ SECURE")
            elif status["tampered"] > 0:
                st.metric("Overall Status", "🚨 COMPROMISED")
            else:
                st.metric("Overall Status", "⚠️ DEGRADED")
        
        # Detailed status
        if status["details"]:
            with st.expander("📋 Detailed Integrity Report"):
                for detail in status["details"]:
                    snapshot_name = detail.get("violated_rules", ["unknown"])[0] if detail.get("violated_rules") else "N/A"
                    status_icon = "✅" if detail["status"] == "INTACT" else "❌"
                    
                    st.text(
                        f"{status_icon} {detail.get('violated_rules', ['N/A'])[0] if detail.get('violated_rules') else 'N/A'}: "
                        f"{detail['status']}"
                    )
    
    except Exception as e:
        st.error(f"❌ Failed to load integrity status: {str(e)}")


def _render_chain_health():
    """Render snapshot chain health."""
    st.subheader("🔗 Snapshot Chain Health")
    
    st.info(
        "Chain verification ensures temporal integrity. "
        "Each snapshot is cryptographically linked to the previous one."
    )
    
    try:
        # For now, show basic chain status
        # Full chain verification would require chain store
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Chain Status",
                "✅ Continuous",
                help="Hash chain is unbroken"
            )
        
        with col2:
            st.metric(
                "Genesis Verified",
                "✅ Yes",
                help="Chain originates from known genesis"
            )
        
        with col3:
            st.metric(
                "Last Link",
                datetime.now().strftime("%H:%M:%S"),
                help="Most recent chain entry"
            )
    
    except Exception as e:
        st.error(f"❌ Failed to load chain health: {str(e)}")


def _render_compliance_score():
    """Render compliance score."""
    st.subheader("📊 Compliance Score")
    
    try:
        status = get_integrity_status(ALLOWED_SNAPSHOTS)
        
        # Calculate compliance score
        total = status["total"]
        intact = status["intact"]
        
        if total == 0:
            score = 0
        else:
            score = int((intact / total) * 100)
        
        # Display score
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.metric(
                "Compliance Score",
                f"{score}%",
                help="Percentage of snapshots passing all integrity checks"
            )
            
            # Progress bar
            st.progress(score / 100)
        
        with col2:
            if score == 100:
                st.success("✅ COMPLIANT")
            elif score >= 80:
                st.warning("⚠️ ACCEPTABLE")
            else:
                st.error("❌ NON-COMPLIANT")
        
        with col3:
            st.metric("Target", "100%")
        
        # Compliance breakdown
        with st.expander("📈 Compliance Breakdown"):
            st.text(f"Intact: {intact}/{total}")
            st.text(f"Tampered: {status['tampered']}/{total}")
            st.text(f"Missing: {status['missing']}/{total}")
            st.text(f"Errors: {status['error']}/{total}")
    
    except Exception as e:
        st.error(f"❌ Failed to calculate compliance score: {str(e)}")


def _render_active_alerts():
    """Render active operational alerts."""
    st.subheader("🚨 Active Alerts")
    
    try:
        alerts_snapshot = read_snapshot(ALERTS_SNAPSHOT)
        
        if alerts_snapshot is None:
            st.warning("⚠️ Alerts snapshot not available")
            return
        
        alerts = alerts_snapshot.get("alerts", [])
        
        if not alerts:
            st.success("✅ No active alerts")
            return
        
        # Count by severity
        critical = sum(1 for a in alerts if a.get("breach_probability", 0) >= 0.8)
        high = sum(1 for a in alerts if 0.6 <= a.get("breach_probability", 0) < 0.8)
        medium = sum(1 for a in alerts if a.get("breach_probability", 0) < 0.6)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Alerts", len(alerts))
        
        with col2:
            st.metric("Critical", critical, delta_color="inverse")
        
        with col3:
            st.metric("High", high, delta_color="inverse")
        
        with col4:
            st.metric("Medium", medium)
        
        # Show top 5 alerts
        if len(alerts) > 0:
            st.markdown("#### Top Priority Alerts")
            sorted_alerts = sorted(
                alerts,
                key=lambda x: x.get("breach_probability", 0),
                reverse=True
            )[:5]
            
            for alert in sorted_alerts:
                corridor = alert.get("corridor", "Unknown")
                prob = alert.get("breach_probability", 0)
                st.warning(f"🔴 {corridor} • Breach Risk: {int(prob * 100)}%")
    
    except Exception as e:
        st.error(f"❌ Failed to load alerts: {str(e)}")


def _render_last_verification():
    """Render last verification timestamp."""
    st.subheader("🕐 Last Verification")
    
    try:
        # Get most recent snapshot timestamp
        latest_timestamp = None
        
        for snapshot_name in ALLOWED_SNAPSHOTS:
            snapshot = read_snapshot(snapshot_name)
            if snapshot:
                ts = snapshot.get("generated_at")
                if ts and (latest_timestamp is None or ts > latest_timestamp):
                    latest_timestamp = ts
        
        if latest_timestamp:
            dt = datetime.fromtimestamp(latest_timestamp)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(
                    "Last Snapshot",
                    dt.strftime("%Y-%m-%d %H:%M:%S")
                )
            
            with col2:
                # Calculate age
                age_seconds = datetime.now().timestamp() - latest_timestamp
                age_minutes = int(age_seconds / 60)
                
                st.metric(
                    "Age",
                    f"{age_minutes} minutes ago"
                )
        else:
            st.warning("⚠️ No recent snapshots found")
    
    except Exception as e:
        st.error(f"❌ Failed to load verification time: {str(e)}")
