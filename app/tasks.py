"""
Task definitions for the AI Customer Support Operations Simulator.
Three difficulty levels: Easy, Medium, Hard.
"""
from typing import Dict, Any

TASKS: Dict[str, Dict[str, Any]] = {
    "easy": {
        "id": "easy",
        "name": "Ticket Classification",
        "difficulty": "Easy",
        "description": "Read a short incoming message and correctly classify it without taking further action.",
        "max_steps": 3,
        "ticket": {
            "id": "TKT-101",
            "priority": "Low",
            "category": "Unclassified",
            "subject": "Need help with my latest invoice",
            "body": "Hi there, I noticed an extra charge on my latest invoice that I don't recognize. Can someone explain this?",
            "customer_name": "Oliver Twist",
            "customer_tier": "Standard",
            "account_age_days": 45,
            "tone": "Polite"
        },
        "expected_actions": [
            "classify_ticket",
            "confirm_resolution"
        ],
        "knowledge_base": {
            "classification_guide": "Tickets mentioning 'invoice', 'charge', or 'payment' must be classified as Billing."
        },
        "escalation_required": False,
    },
    "medium": {
        "id": "medium",
        "name": "Knowledge Retrieval & Response",
        "difficulty": "Medium",
        "description": "Look up the correct policy in the knowledge base and generate an appropriate support response.",
        "max_steps": 5,
        "ticket": {
            "id": "TKT-202",
            "priority": "Medium",
            "category": "Billing",
            "subject": "Requesting a refund for accidental purchase",
            "body": "Hello, my son accidentally purchased the yearly subscription instead of the monthly one. Is it possible to get a refund? I just bought it yesterday.",
            "customer_name": "Mary Jane",
            "customer_tier": "Standard",
            "account_age_days": 12,
            "tone": "Polite"
        },
        "expected_actions": [
            "query_knowledge_base",
            "generate_response",
            "confirm_resolution"
        ],
        "knowledge_base": {
            "refund_policy": "Accidental purchases made within 48 hours are eligible for a full refund. Agents should generate a response acknowledging the refund approval."
        },
        "escalation_required": False,
    },
    "hard": {
        "id": "hard",
        "name": "Multi-Step Resolution",
        "difficulty": "Hard",
        "description": "Handle an angry customer by classifying, retrieving info, responding, and deciding whether to escalate or close.",
        "max_steps": 8,
        "ticket": {
            "id": "TKT-303",
            "priority": "High",
            "category": "Unclassified",
            "subject": "SYSTEM KEEPS CRASHING! FIX IT NOW!",
            "body": "I am so incredibly frustrated! Your software has crashed 5 times today and I lost 3 hours of work. I demand to speak to a manager right now or I'm cancelling my enterprise contract!",
            "customer_name": "Gordon Ramsay",
            "customer_tier": "Enterprise",
            "account_age_days": 800,
            "tone": "Angry"
        },
        "expected_actions": [
            "classify_ticket",
            "lookup_customer",
            "generate_response",
            "escalate_to_l2",
            "confirm_resolution"
        ],
        "knowledge_base": {
            "enterprise_policy": "Enterprise customers experiencing repeated crashes must be prioritized.",
            "escalation_policy": "If an Enterprise customer demands a manager or threatens to cancel due to technical issues, immediately escalate to L2 after generating an empathetic response."
        },
        "escalation_required": True,
    },
}

VALID_ACTIONS = [
    "classify_ticket",
    "lookup_customer",
    "query_knowledge_base",
    "generate_response",
    "escalate_to_l2",
    "escalate_to_l3",
    "close_ticket",
    "confirm_resolution"
]

ACTION_DESCRIPTIONS = {
    "classify_ticket": "Categorize the ticket (Billing / Refund / Technical)",
    "lookup_customer": "Retrieve account details and customer tier",
    "query_knowledge_base": "Search the internal knowledge base for relevant policies",
    "generate_response": "Draft and send an appropriate response to the customer",
    "escalate_to_l2": "Escalate the ticket to a Level 2 human manager or technician",
    "escalate_to_l3": "Escalate the ticket to Level 3 engineering",
    "close_ticket": "Close the ticket without full resolution",
    "confirm_resolution": "Mark the ticket as fully resolved and complete the workflow",
}
