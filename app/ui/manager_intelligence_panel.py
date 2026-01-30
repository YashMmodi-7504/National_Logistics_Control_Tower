"""
UNIFIED MANAGER INTELLIGENCE PANEL

Purpose:
- Executive-grade manager dashboard
- AI predictions displayed instantly
- Risk indicators prominently visible
- Priority levels clear
- Override controls accessible
- Notification inbox integrated
- State dashboard embedded

Requirements:
• High signal, no clutter
• Executive-grade UI
• Instant AI visibility
• Clear priority indicators
• One-click override
• Notification center
• National dashboard integration

Author: National Logistics Control Tower
Phase: 9.10 - Unified Manager Intelligence Panel
"""

import streamlit as st
from typing import Dict, Any, List, Optional
from datetime import datetime
import time


def _render_ai_predictions_panel(shipment: Dict[str, Any]):
    """
    Render AI predictions panel for a shipment.
    
    Args:
        shipment: Shipment with ai_predictions metadata
    """
    ai_predictions = shipment.get("ai_predictions", {})
    
    if not ai_predictions:
        st.info("ℹ️ AI predictions not yet available for this shipment.")
        return
    
    st.subheader("🤖 AI Risk Analysis")
    
    # Combined risk score (prominent)
    combined_risk = ai_predictions.get("combined_risk_score", 0)
    combined_level = ai_predictions.get("combined_risk_level", "UNKNOWN")
    
    # Color coding
    risk_colors = {
        "LOW": "normal",
        "MEDIUM": "off",
        "HIGH": "inverse",
        "CRITICAL": "inverse",
    }
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🎯 Combined Risk",
            value=f"{combined_risk}%",
            delta=combined_level,
            delta_color=risk_colors.get(combined_level, "off"),
            help="Overall risk score from AI analysis"
        )
    
    # Individual risk scores
    weather = ai_predictions.get("weather_risk", {})
    route = ai_predictions.get("route_risk", {})
    sla = ai_predictions.get("sla_breach", {})
    
    with col2:
        st.metric(
            label="🌦️ Weather Risk",
            value=f"{weather.get('risk_score', 0)}%",
            delta=weather.get('risk_level', 'N/A'),
            help=weather.get('explanation', 'Weather risk assessment')
        )
    
    with col3:
        st.metric(
            label="🛣️ Route Risk",
            value=f"{route.get('risk_score', 0)}%",
            delta=route.get('risk_level', 'N/A'),
            help=route.get('explanation', 'Route risk assessment')
        )
    
    with col4:
        st.metric(
            label="⏰ SLA Breach Risk",
            value=f"{sla.get('breach_probability', 0)}%",
            delta=sla.get('risk_level', 'N/A'),
            help=sla.get('explanation', 'SLA breach probability')
        )
    
    # AI explanation
    st.divider()
    ai_explanation = ai_predictions.get("ai_explanation", "No explanation available")
    
    if combined_level in ["HIGH", "CRITICAL"]:
        st.error(f"⚠️ **AI Alert**: {ai_explanation}")
    elif combined_level == "MEDIUM":
        st.warning(f"ℹ️ **AI Assessment**: {ai_explanation}")
    else:
        st.success(f"✅ **AI Assessment**: {ai_explanation}")
    
    # AI recommendation
    try:
        from app.intelligence.ai_prediction import get_ai_recommendation
        recommendation = get_ai_recommendation(ai_predictions)
        
        with st.expander("💡 AI Recommendation"):
            st.markdown(recommendation)
    except Exception:
        pass


def _render_priority_indicator(shipment: Dict[str, Any]):
    """
    Render priority level indicator.
    
    Args:
        shipment: Shipment data
    """
    # Determine priority based on risk and flags
    priority = "STANDARD"
    
    ai_predictions = shipment.get("ai_predictions", {})
    combined_risk = ai_predictions.get("combined_risk_score", 0)
    
    if combined_risk >= 80:
        priority = "CRITICAL"
    elif combined_risk >= 60:
        priority = "HIGH"
    elif combined_risk >= 40:
        priority = "MEDIUM"
    
    # Override flag
    is_overridden = shipment.get("is_overridden", False)
    
    # Priority badge
    priority_colors = {
        "CRITICAL": "🔴",
        "HIGH": "🟠",
        "MEDIUM": "🟡",
        "STANDARD": "🟢",
    }
    
    icon = priority_colors.get(priority, "⚪")
    
    st.markdown(f"### {icon} Priority: **{priority}**")
    
    if is_overridden:
        st.warning("⚡ **Manager Override Active**")


def _render_override_panel(shipment: Dict[str, Any], manager_role: str):
    """
    Render manager override controls.
    
    Args:
        shipment: Shipment data
        manager_role: Current manager's role
    """
    st.subheader("⚡ Manager Override")
    
    shipment_id = shipment.get("shipment_id")
    current_decision = shipment.get("current_state", "PENDING")
    
    # Override form
    with st.form(key=f"override_form_{shipment_id}"):
        st.caption("Override AI decision with explicit reason")
        
        # Override decision
        override_decision = st.selectbox(
            "Override Decision",
            ["APPROVE", "REJECT", "ESCALATE"],
            help="Select the override decision"
        )
        
        # Reason code
        from app.core.manager_override import OverrideReason
        
        reason_codes = [
            OverrideReason.BUSINESS_PRIORITY,
            OverrideReason.CUSTOMER_REQUEST,
            OverrideReason.MANAGEMENT_DIRECTIVE,
            OverrideReason.AI_ERROR,
            OverrideReason.OPERATIONAL_NEED,
            OverrideReason.RISK_ACCEPTABLE,
            OverrideReason.CUSTOM,
        ]
        
        reason_code = st.selectbox(
            "Reason Code",
            reason_codes,
            help="Select the reason for override"
        )
        
        # Reason text
        reason_text = st.text_area(
            "Detailed Explanation",
            placeholder="Provide a detailed explanation for this override (minimum 10 characters)",
            help="Required: Explain why you are overriding the AI decision"
        )
        
        # Submit button
        submitted = st.form_submit_button("🔓 Submit Override", use_container_width=True)
        
        if submitted:
            # Validate and record override
            from app.core.manager_override import record_override
            
            ai_predictions = shipment.get("ai_predictions", {})
            
            success, error, event = record_override(
                shipment_id=shipment_id,
                original_decision=current_decision,
                override_decision=override_decision,
                reason_code=reason_code,
                reason_text=reason_text,
                manager_role=manager_role,
                ai_predictions=ai_predictions,
            )
            
            if success:
                st.success(f"✅ Override recorded successfully!")
                st.info("Override has been logged to audit trail and notifications sent.")
            else:
                st.error(f"❌ Override failed: {error}")


def _render_notification_inbox(manager_role: str):
    """
    Render notification inbox for manager.
    
    Args:
        manager_role: Current manager's role
    """
    st.subheader("📬 Notification Center")
    
    try:
        from app.notifications.notification_store import (
            read_notifications_for_role,
            get_notification_count_by_role,
            mark_notification_read,
        )
        
        # Get notification counts
        counts = get_notification_count_by_role(manager_role)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total", counts["total"])
        
        with col2:
            st.metric("Unread", counts["unread"], delta_color="inverse")
        
        with col3:
            urgent = counts["by_severity"].get("URGENT", 0)
            st.metric("Urgent", urgent, delta_color="inverse")
        
        st.divider()
        
        # Fetch recent notifications
        notifications = read_notifications_for_role(manager_role, limit=10)
        
        if not notifications:
            st.info("No notifications")
            return
        
        # Display notifications
        for notification in notifications:
            is_unread = notification.is_unread_for(manager_role)
            severity = notification.severity
            
            # Severity icon
            severity_icons = {
                "INFO": "ℹ️",
                "WARNING": "⚠️",
                "URGENT": "🚨",
                "CRITICAL": "🔴",
            }
            icon = severity_icons.get(severity, "•")
            
            # Unread indicator
            unread_badge = "🔵 " if is_unread else ""
            
            with st.container(border=True):
                st.markdown(f"{unread_badge}{icon} **{severity}**")
                st.text(notification.message)
                st.caption(f"Shipment: {notification.shipment_id} | {datetime.fromtimestamp(notification.timestamp).strftime('%Y-%m-%d %H:%M:%S')}")
                
                if is_unread:
                    if st.button("Mark Read", key=f"read_{notification.notification_id}"):
                        mark_notification_read(notification.notification_id, manager_role)
                        st.rerun()
    
    except Exception as e:
        st.error(f"Failed to load notifications: {str(e)}")


def _render_national_dashboard_summary():
    """Render summary of national dashboard."""
    st.subheader("🗺️ National Overview")
    
    try:
        from app.ui.national_dashboard import get_top_risk_states, get_top_volume_states
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Top Risk States")
            top_risk = get_top_risk_states(limit=3)
            
            for state_metrics in top_risk:
                state = state_metrics["state"]
                risk = state_metrics["avg_sla_breach_probability"]
                st.text(f"• {state}: {risk}% SLA risk")
        
        with col2:
            st.markdown("#### Top Volume States")
            top_volume = get_top_volume_states(limit=3)
            
            for state_metrics in top_volume:
                state = state_metrics["state"]
                total = state_metrics["total_shipments"]
                st.text(f"• {state}: {total} shipments")
        
        st.info("💡 Click 'National Dashboard' tab for detailed state-wise analytics")
    
    except Exception as e:
        st.info("National dashboard summary unavailable")


def render_manager_intelligence_panel(shipment: Dict[str, Any], manager_role: str):
    """
    Render unified manager intelligence panel.
    
    Args:
        shipment: Selected shipment data
        manager_role: Current manager's role (SENDER_MANAGER, etc.)
        
    Features:
    - AI predictions (prominent)
    - Risk indicators
    - Priority level
    - Override controls
    - Notification inbox
    - National dashboard summary
    
    Design:
    - High signal, no clutter
    - Executive-grade
    - Actionable insights
    """
    st.header("🎯 Manager Intelligence Panel")
    st.caption("AI-Powered Decision Support • Real-Time Intelligence")
    
    st.divider()
    
    # Shipment header
    shipment_id = shipment.get("shipment_id", "Unknown")
    st.markdown(f"### 📦 Shipment: `{shipment_id}`")
    
    # Priority indicator
    _render_priority_indicator(shipment)
    
    st.divider()
    
    # AI predictions (prominent)
    _render_ai_predictions_panel(shipment)
    
    st.divider()
    
    # Override panel
    _render_override_panel(shipment, manager_role)
    
    st.divider()
    
    # Notification inbox
    _render_notification_inbox(manager_role)
    
    st.divider()
    
    # National dashboard summary
    _render_national_dashboard_summary()


def render_manager_dashboard_tabs(manager_role: str):
    """
    Render tabbed manager dashboard.
    
    Args:
        manager_role: Current manager's role
        
    Tabs:
    - Intelligence Panel: AI predictions + override
    - National Dashboard: State-wise analytics
    - Notification Center: Full notification list
    - Override History: Audit trail
    """
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 Intelligence Panel",
        "🗺️ National Dashboard",
        "📬 Notifications",
        "📋 Override History"
    ])
    
    with tab1:
        st.info("Select a shipment to view intelligence panel")
        # Shipment selector would go here
        # For now, show placeholder
    
    with tab2:
        from app.ui.national_dashboard import render_national_dashboard
        render_national_dashboard()
    
    with tab3:
        _render_notification_inbox(manager_role)
    
    with tab4:
        st.subheader("📋 Override History")
        
        try:
            from app.core.manager_override import get_override_statistics
            
            stats = get_override_statistics()
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Overrides", stats["total_overrides"])
            
            with col2:
                st.metric("Last 24h", stats["last_24h"])
            
            with col3:
                st.metric("Override Rate", f"{stats['override_rate']}%")
            
            with col4:
                # Most common reason
                if stats["by_reason"]:
                    top_reason = max(stats["by_reason"], key=stats["by_reason"].get)
                    st.metric("Top Reason", top_reason)
            
            st.divider()
            
            # By reason breakdown
            st.markdown("#### Overrides by Reason")
            if stats["by_reason"]:
                for reason, count in stats["by_reason"].items():
                    st.text(f"• {reason}: {count}")
            else:
                st.info("No overrides recorded")
            
            st.divider()
            
            # By manager breakdown
            st.markdown("#### Overrides by Manager")
            if stats["by_manager"]:
                for manager, count in stats["by_manager"].items():
                    st.text(f"• {manager}: {count}")
        
        except Exception as e:
            st.error(f"Failed to load override history: {str(e)}")
