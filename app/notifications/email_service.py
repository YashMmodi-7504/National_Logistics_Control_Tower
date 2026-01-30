"""
EMAIL NOTIFICATION SERVICE (BREVO)

Purpose:
- Send transactional emails via Brevo API
- Template-based email composition
- Event-driven triggers
- Graceful failure handling

Requirements:
• Never hardcode API keys (use os.getenv)
• Timeout protection (10s max)
• Retry logic with backoff
• Log all failures
• Never block event emission

Email Templates:
1. Shipment reached Receiver Manager
2. Shipment out for delivery
3. High-risk / SLA breach warning
4. Manager override notification
5. Daily metrics summary

Author: National Logistics Control Tower
Phase: 10 - External Service Integration
"""

import os
import requests
import logging
import time
from typing import Dict, Any, List, Optional

# Configure logging
logger = logging.getLogger(__name__)

# Brevo configuration
BREVO_API_KEY = os.getenv("BREVO_API_KEY")
BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"
API_TIMEOUT = 10  # seconds
MAX_RETRIES = 2

# Default sender
DEFAULT_SENDER = {
    "email": "noreply@logistics-tower.in",
    "name": "National Logistics Control Tower"
}


def _build_headers() -> Dict[str, str]:
    """Build API request headers."""
    if not BREVO_API_KEY:
        raise ValueError("BREVO_API_KEY not configured")
    
    return {
        "api-key": BREVO_API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def _send_email_request(payload: Dict[str, Any], retry_count: int = 0) -> bool:
    """
    Send email via Brevo API with retry logic.
    
    Args:
        payload: Email payload
        retry_count: Current retry attempt
        
    Returns:
        bool: True if sent successfully
    """
    try:
        headers = _build_headers()
        
        logger.info(f"Sending email to {payload.get('to', [])} (attempt {retry_count + 1})")
        
        response = requests.post(
            BREVO_API_URL,
            json=payload,
            headers=headers,
            timeout=API_TIMEOUT
        )
        
        response.raise_for_status()
        
        logger.info(f"Email sent successfully: {response.json().get('messageId', 'N/A')}")
        return True
    
    except requests.exceptions.Timeout:
        logger.error(f"Email API timeout (attempt {retry_count + 1})")
        
        if retry_count < MAX_RETRIES:
            time.sleep(2 ** retry_count)  # Exponential backoff
            return _send_email_request(payload, retry_count + 1)
        
        return False
    
    except requests.exceptions.HTTPError as e:
        logger.error(f"Email API HTTP error: {e.response.status_code} - {e.response.text}")
        return False
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Email API error: {str(e)}")
        return False
    
    except ValueError as e:
        logger.error(f"Email configuration error: {str(e)}")
        return False
    
    except Exception as e:
        logger.error(f"Unexpected email error: {str(e)}")
        return False


def send_email(
    to_emails: List[str],
    subject: str,
    html_content: str,
    text_content: Optional[str] = None,
    sender: Optional[Dict[str, str]] = None
) -> bool:
    """
    Send email via Brevo.
    
    Args:
        to_emails: List of recipient email addresses
        subject: Email subject
        html_content: HTML email body
        text_content: Plain text fallback (optional)
        sender: Sender info {email, name} (optional)
        
    Returns:
        bool: True if sent successfully
        
    Examples:
        >>> send_email(
        ...     to_emails=["manager@company.in"],
        ...     subject="Shipment Alert",
        ...     html_content="<h1>Alert</h1><p>High risk shipment</p>"
        ... )
    """
    if not BREVO_API_KEY:
        logger.warning("BREVO_API_KEY not configured, skipping email")
        return False
    
    if not to_emails:
        logger.warning("No recipients specified")
        return False
    
    # Build recipient list
    recipients = [{"email": email} for email in to_emails]
    
    # Use default sender if not provided
    if sender is None:
        sender = DEFAULT_SENDER
    
    # Build payload
    payload = {
        "sender": sender,
        "to": recipients,
        "subject": subject,
        "htmlContent": html_content,
    }
    
    if text_content:
        payload["textContent"] = text_content
    
    return _send_email_request(payload)


# ────────────────────────────────────────────────────────────
# EMAIL TEMPLATES
# ────────────────────────────────────────────────────────────


def send_receiver_acknowledgment_email(
    shipment_id: str,
    destination_state: str,
    manager_emails: List[str]
) -> bool:
    """
    Send notification: Shipment reached Receiver Manager.
    
    Args:
        shipment_id: Shipment ID
        destination_state: Destination state
        manager_emails: Sender manager + supervisor emails
        
    Returns:
        bool: Success status
    """
    subject = f"📦 Shipment {shipment_id} Reached Receiver Manager"
    
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6;">
        <h2 style="color: #2563eb;">Shipment Update</h2>
        <p>Your shipment has successfully reached the Receiver Manager.</p>
        
        <table style="border-collapse: collapse; margin: 20px 0;">
            <tr>
                <td style="padding: 8px; font-weight: bold;">Shipment ID:</td>
                <td style="padding: 8px;">{shipment_id}</td>
            </tr>
            <tr>
                <td style="padding: 8px; font-weight: bold;">Destination:</td>
                <td style="padding: 8px;">{destination_state}</td>
            </tr>
            <tr>
                <td style="padding: 8px; font-weight: bold;">Status:</td>
                <td style="padding: 8px; color: #16a34a;">Acknowledged</td>
            </tr>
        </table>
        
        <p>Next step: Warehouse intake and out-for-delivery.</p>
        
        <hr style="margin: 20px 0; border: none; border-top: 1px solid #e5e7eb;">
        <p style="font-size: 12px; color: #6b7280;">
            This is an automated notification from National Logistics Control Tower.
        </p>
    </body>
    </html>
    """
    
    text_content = f"""
    Shipment Update
    
    Your shipment {shipment_id} has successfully reached the Receiver Manager in {destination_state}.
    
    Status: Acknowledged
    Next step: Warehouse intake and out-for-delivery.
    
    ---
    National Logistics Control Tower
    """
    
    return send_email(manager_emails, subject, html_content, text_content)


def send_out_for_delivery_email(
    shipment_id: str,
    eta: str,
    recipient_emails: List[str]
) -> bool:
    """
    Send notification: Shipment out for delivery.
    
    Args:
        shipment_id: Shipment ID
        eta: Estimated delivery time
        recipient_emails: Warehouse + Receiver manager emails
        
    Returns:
        bool: Success status
    """
    subject = f"🚚 Shipment {shipment_id} Out for Delivery"
    
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6;">
        <h2 style="color: #16a34a;">Out for Delivery</h2>
        <p>The shipment is now out for delivery to the customer.</p>
        
        <table style="border-collapse: collapse; margin: 20px 0;">
            <tr>
                <td style="padding: 8px; font-weight: bold;">Shipment ID:</td>
                <td style="padding: 8px;">{shipment_id}</td>
            </tr>
            <tr>
                <td style="padding: 8px; font-weight: bold;">ETA:</td>
                <td style="padding: 8px;">{eta}</td>
            </tr>
            <tr>
                <td style="padding: 8px; font-weight: bold;">Status:</td>
                <td style="padding: 8px; color: #16a34a;">Out for Delivery</td>
            </tr>
        </table>
        
        <p>You will receive another notification upon successful delivery.</p>
        
        <hr style="margin: 20px 0; border: none; border-top: 1px solid #e5e7eb;">
        <p style="font-size: 12px; color: #6b7280;">
            This is an automated notification from National Logistics Control Tower.
        </p>
    </body>
    </html>
    """
    
    text_content = f"""
    Out for Delivery
    
    Shipment {shipment_id} is now out for delivery to the customer.
    
    ETA: {eta}
    Status: Out for Delivery
    
    You will receive another notification upon successful delivery.
    
    ---
    National Logistics Control Tower
    """
    
    return send_email(recipient_emails, subject, html_content, text_content)


def send_high_risk_alert_email(
    shipment_id: str,
    risk_score: int,
    risk_factors: List[str],
    recipient_emails: List[str]
) -> bool:
    """
    Send notification: High-risk shipment / SLA breach warning.
    
    Args:
        shipment_id: Shipment ID
        risk_score: Risk score (0-100)
        risk_factors: List of risk factors
        recipient_emails: Manager + COO emails
        
    Returns:
        bool: Success status
    """
    subject = f"🚨 HIGH RISK ALERT: Shipment {shipment_id}"
    
    risk_bullets = "".join([f"<li>{factor}</li>" for factor in risk_factors])
    
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6;">
        <h2 style="color: #dc2626;">⚠️ High Risk Alert</h2>
        <p style="background: #fef2f2; padding: 15px; border-left: 4px solid #dc2626;">
            <strong>ACTION REQUIRED:</strong> This shipment has been flagged as high risk.
        </p>
        
        <table style="border-collapse: collapse; margin: 20px 0;">
            <tr>
                <td style="padding: 8px; font-weight: bold;">Shipment ID:</td>
                <td style="padding: 8px;">{shipment_id}</td>
            </tr>
            <tr>
                <td style="padding: 8px; font-weight: bold;">Risk Score:</td>
                <td style="padding: 8px; color: #dc2626; font-weight: bold;">{risk_score}/100</td>
            </tr>
        </table>
        
        <h3>Risk Factors:</h3>
        <ul>
            {risk_bullets}
        </ul>
        
        <p><strong>Recommended Action:</strong> Review shipment and consider priority handling or manager override.</p>
        
        <hr style="margin: 20px 0; border: none; border-top: 1px solid #e5e7eb;">
        <p style="font-size: 12px; color: #6b7280;">
            This is an automated risk alert from National Logistics Control Tower.
        </p>
    </body>
    </html>
    """
    
    text_content = f"""
    HIGH RISK ALERT
    
    ACTION REQUIRED: Shipment {shipment_id} has been flagged as high risk.
    
    Risk Score: {risk_score}/100
    
    Risk Factors:
    {chr(10).join(['- ' + f for f in risk_factors])}
    
    Recommended Action: Review shipment and consider priority handling or manager override.
    
    ---
    National Logistics Control Tower
    """
    
    return send_email(recipient_emails, subject, html_content, text_content)


def send_manager_override_notification(
    shipment_id: str,
    manager_name: str,
    override_reason: str,
    recipient_emails: List[str]
) -> bool:
    """
    Send notification: Manager override recorded.
    
    Args:
        shipment_id: Shipment ID
        manager_name: Manager role who overrode
        override_reason: Reason for override
        recipient_emails: COO + audit team emails
        
    Returns:
        bool: Success status
    """
    subject = f"⚡ Manager Override: Shipment {shipment_id}"
    
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6;">
        <h2 style="color: #f59e0b;">Manager Override Recorded</h2>
        <p>A manager has overridden the AI decision for this shipment.</p>
        
        <table style="border-collapse: collapse; margin: 20px 0;">
            <tr>
                <td style="padding: 8px; font-weight: bold;">Shipment ID:</td>
                <td style="padding: 8px;">{shipment_id}</td>
            </tr>
            <tr>
                <td style="padding: 8px; font-weight: bold;">Manager:</td>
                <td style="padding: 8px;">{manager_name}</td>
            </tr>
            <tr>
                <td style="padding: 8px; font-weight: bold;">Reason:</td>
                <td style="padding: 8px;">{override_reason}</td>
            </tr>
        </table>
        
        <p style="background: #fffbeb; padding: 15px; border-left: 4px solid #f59e0b;">
            <strong>Audit Note:</strong> This override has been logged to the immutable audit trail.
        </p>
        
        <hr style="margin: 20px 0; border: none; border-top: 1px solid #e5e7eb;">
        <p style="font-size: 12px; color: #6b7280;">
            This is an automated audit notification from National Logistics Control Tower.
        </p>
    </body>
    </html>
    """
    
    text_content = f"""
    Manager Override Recorded
    
    A manager has overridden the AI decision for shipment {shipment_id}.
    
    Manager: {manager_name}
    Reason: {override_reason}
    
    Audit Note: This override has been logged to the immutable audit trail.
    
    ---
    National Logistics Control Tower
    """
    
    return send_email(recipient_emails, subject, html_content, text_content)


def send_notification(template: str, recipients: List[str], payload: Dict[str, Any]) -> bool:
    """
    Send notification using template name.
    
    Args:
        template: Template name (RECEIVER_ACK, OUT_FOR_DELIVERY, HIGH_RISK, MANAGER_OVERRIDE)
        recipients: List of email addresses
        payload: Template data
        
    Returns:
        bool: Success status
        
    Examples:
        >>> send_notification(
        ...     template="HIGH_RISK",
        ...     recipients=["coo@company.in"],
        ...     payload={
        ...         "shipment_id": "SHIP-20260119-120000-1234",
        ...         "risk_score": 85,
        ...         "risk_factors": ["Severe weather", "Tight SLA"]
        ...     }
        ... )
    """
    if template == "RECEIVER_ACK":
        return send_receiver_acknowledgment_email(
            shipment_id=payload["shipment_id"],
            destination_state=payload.get("destination_state", "Unknown"),
            manager_emails=recipients
        )
    
    elif template == "OUT_FOR_DELIVERY":
        return send_out_for_delivery_email(
            shipment_id=payload["shipment_id"],
            eta=payload.get("eta", "Unknown"),
            recipient_emails=recipients
        )
    
    elif template == "HIGH_RISK":
        return send_high_risk_alert_email(
            shipment_id=payload["shipment_id"],
            risk_score=payload.get("risk_score", 0),
            risk_factors=payload.get("risk_factors", []),
            recipient_emails=recipients
        )
    
    elif template == "MANAGER_OVERRIDE":
        return send_manager_override_notification(
            shipment_id=payload["shipment_id"],
            manager_name=payload.get("manager_name", "Unknown"),
            override_reason=payload.get("override_reason", "Not specified"),
            recipient_emails=recipients
        )
    
    else:
        logger.error(f"Unknown email template: {template}")
        return False
