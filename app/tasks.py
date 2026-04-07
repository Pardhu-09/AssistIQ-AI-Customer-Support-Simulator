"""
Task definitions for the AI Customer Support Operations Simulator.
Three difficulty levels: Easy, Medium, Hard.
"""
from typing import Dict, Any

TASKS: Dict[str, Dict[str, Any]] = {
    "easy": {
        "id": "easy",
        "name": "Password Reset Request",
        "difficulty": "Easy",
        "description": "Handle a straightforward password reset request from a customer.",
        "max_steps": 6,
        "ticket": {
            "id": "TKT-001",
            "priority": "Low",
            "category": "Account Access",
            "subject": "Cannot log into my account",
            "body": (
                "Hi, I've been trying to log into my account for the past hour and it keeps saying "
                "'Invalid password'. I have an important meeting in 2 hours and need to access my files. "
                "My email is john.doe@example.com. Please help ASAP!"
            ),
            "customer_name": "John Doe",
            "customer_tier": "Standard",
            "account_age_days": 180,
        },
        "expected_actions": [
            "classify_ticket",
            "lookup_customer",
            "verify_identity",
            "send_password_reset",
            "confirm_resolution",
        ],
        "knowledge_base": {
            "password_reset_policy": "Standard users can reset passwords via email link. Link expires in 24 hours.",
            "sla_low": "Low priority tickets must be resolved within 8 business hours.",
        },
        "correct_resolution": "send_password_reset",
        "escalation_required": False,
    },
    "medium": {
        "id": "medium",
        "name": "Billing Dispute Resolution",
        "difficulty": "Medium",
        "description": "Investigate a billing overcharge complaint with policy verification.",
        "max_steps": 10,
        "ticket": {
            "id": "TKT-042",
            "priority": "High",
            "category": "Billing",
            "subject": "Charged twice for the same subscription - URGENT",
            "body": (
                "I was charged $99.99 twice on March 15th. My bank statement clearly shows two identical "
                "charges from your company. This is unacceptable. I want a full refund of one charge "
                "immediately. My account ID is ACC-78234. I've been a customer for 5 years!"
            ),
            "customer_name": "Sarah Chen",
            "customer_tier": "Premium",
            "account_age_days": 1825,
        },
        "expected_actions": [
            "classify_ticket",
            "lookup_customer",
            "query_billing_records",
            "verify_duplicate_charge",
            "initiate_refund",
            "send_confirmation",
            "confirm_resolution",
        ],
        "knowledge_base": {
            "refund_policy": "Premium users are eligible for same-day refunds for verified overcharges.",
            "billing_error_protocol": "Check transaction logs, verify with payment gateway, issue refund within 24h.",
            "sla_high": "High priority tickets must be acknowledged in 1 hour and resolved within 4 hours.",
        },
        "correct_resolution": "initiate_refund",
        "escalation_required": False,
    },
    "hard": {
        "id": "hard",
        "name": "Critical Service Outage Escalation",
        "difficulty": "Hard",
        "description": (
            "Manage a critical production outage for an enterprise client, coordinating with "
            "engineering while maintaining customer communication."
        ),
        "max_steps": 15,
        "ticket": {
            "id": "TKT-99X",
            "priority": "Critical",
            "category": "Technical - Production Outage",
            "subject": "[CRITICAL] API Gateway completely down - revenue loss every minute",
            "body": (
                "Our entire production environment is down. The API gateway is returning 502 errors. "
                "We are an e-commerce platform with $5,000/minute revenue. This outage started 23 minutes ago. "
                "Our team has tried restarting containers - no luck. "
                "CTO is on the phone. Account ID: ENT-00042. We need L3 engineering support NOW."
            ),
            "customer_name": "Michael Torres (CTO)",
            "customer_tier": "Enterprise",
            "account_age_days": 730,
        },
        "expected_actions": [
            "classify_ticket",
            "lookup_customer",
            "check_system_status",
            "acknowledge_outage",
            "escalate_to_l2",
            "escalate_to_l3",
            "query_logs",
            "identify_root_cause",
            "apply_hotfix",
            "verify_resolution",
            "send_incident_report",
            "confirm_resolution",
        ],
        "knowledge_base": {
            "escalation_policy": "Enterprise clients with outages >10 min must be escalated to L3 immediately.",
            "sla_critical": "Critical tickets must have L3 engaged within 15 minutes. P0 incident protocol applies.",
            "compensation_policy": "Downtime >30 min for Enterprise: issue SLA credit of 10x downtime cost.",
            "incident_protocol": "Create war room, assign incident commander, 15-min status updates.",
        },
        "correct_resolution": "apply_hotfix",
        "escalation_required": True,
    },
}

VALID_ACTIONS = [
    "classify_ticket",
    "lookup_customer",
    "verify_identity",
    "send_password_reset",
    "query_billing_records",
    "verify_duplicate_charge",
    "initiate_refund",
    "send_confirmation",
    "check_system_status",
    "acknowledge_outage",
    "escalate_to_l2",
    "escalate_to_l3",
    "query_logs",
    "identify_root_cause",
    "apply_hotfix",
    "verify_resolution",
    "send_incident_report",
    "confirm_resolution",
    "request_more_info",
    "close_ticket",
]

ACTION_DESCRIPTIONS = {
    "classify_ticket": "Categorize the ticket by type and priority",
    "lookup_customer": "Look up customer account details and history",
    "verify_identity": "Verify the customer's identity via security questions",
    "send_password_reset": "Send a password reset link to the customer's email",
    "query_billing_records": "Query the billing database for transaction history",
    "verify_duplicate_charge": "Cross-reference payment gateway for duplicate transaction",
    "initiate_refund": "Submit a refund request to the billing system",
    "send_confirmation": "Send a confirmation email with resolution details",
    "check_system_status": "Check internal monitoring dashboards for system health",
    "acknowledge_outage": "Send immediate acknowledgement to the customer",
    "escalate_to_l2": "Escalate ticket to Level-2 technical support",
    "escalate_to_l3": "Escalate ticket to Level-3 engineering team",
    "query_logs": "Pull system logs to identify error patterns",
    "identify_root_cause": "Analyze logs to identify the root cause of the issue",
    "apply_hotfix": "Deploy emergency hotfix or configuration change",
    "verify_resolution": "Confirm with customer that the issue is resolved",
    "send_incident_report": "Send a post-incident report to the customer",
    "confirm_resolution": "Mark ticket as resolved and close",
    "request_more_info": "Ask the customer for additional information",
    "close_ticket": "Close the ticket without full resolution",
}
