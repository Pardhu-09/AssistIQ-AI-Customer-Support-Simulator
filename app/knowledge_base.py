"""
Enterprise Knowledge Base
--------------------------
Simulates a real-world tiered support knowledge base with articles
covering billing, technical issues, refunds, and account management.
"""

from typing import List, Dict

KNOWLEDGE_BASE: List[Dict] = [
    # ─── BILLING ──────────────────────────────────────────────────────────────
    {
        "id": "KB-BILL-001",
        "category": "billing",
        "title": "How to update your payment method",
        "keywords": ["payment", "credit card", "billing", "update", "charge", "invoice"],
        "content": (
            "To update your payment method, navigate to Settings → Billing → Payment Methods. "
            "Click 'Add Payment Method' and enter your new card details. "
            "Ensure the card is not expired and the billing address matches your bank records. "
            "Changes take effect immediately for the next billing cycle."
        ),
        "policy": "Customers may update payment methods at any time with no fee.",
        "escalate_if": "Payment update fails repeatedly after 3 attempts.",
    },
    {
        "id": "KB-BILL-002",
        "category": "billing",
        "title": "Understanding your invoice",
        "keywords": ["invoice", "charge", "statement", "line item", "tax", "receipt"],
        "content": (
            "Your monthly invoice lists all active subscriptions, add-ons, and prorated charges. "
            "Taxes are calculated based on your registered billing address. "
            "Invoice PDFs can be downloaded from Settings → Billing → Invoice History. "
            "Invoices are generated on the 1st of every month."
        ),
        "policy": "Invoices are retained for 7 years per financial compliance requirements.",
        "escalate_if": "Customer disputes a charge older than 90 days.",
    },
    {
        "id": "KB-BILL-003",
        "category": "billing",
        "title": "Handling duplicate charges",
        "keywords": ["duplicate", "double charge", "charged twice", "billing error", "overcharge"],
        "content": (
            "Duplicate charges can occur due to payment processor errors. "
            "Verify by checking Settings → Billing → Transaction History. "
            "If a duplicate is confirmed, initiate a refund from the admin panel "
            "within 5 business days. Notify the customer via email with the refund ETA."
        ),
        "policy": "Confirmed duplicate charges must be refunded within 5 business days.",
        "escalate_if": "Duplicate charge exceeds $500 or customer threatens chargeback.",
    },
    # ─── REFUND ───────────────────────────────────────────────────────────────
    {
        "id": "KB-REF-001",
        "category": "refund",
        "title": "Standard refund policy",
        "keywords": ["refund", "money back", "cancel", "return", "reimbursement"],
        "content": (
            "Customers are eligible for a full refund within 30 days of purchase "
            "if the product has not been used beyond the trial limit. "
            "Pro-rated refunds apply for annual plans cancelled after 30 days. "
            "Refunds are processed to the original payment method within 5–10 business days."
        ),
        "policy": "Full refund within 30 days; pro-rated thereafter.",
        "escalate_if": "Customer requests refund after 90 days or claims product defect.",
    },
    {
        "id": "KB-REF-002",
        "category": "refund",
        "title": "Expedited refund for billing errors",
        "keywords": ["refund", "billing error", "urgent", "expedite", "fast refund"],
        "content": (
            "In cases of confirmed billing errors, an expedited refund can be processed "
            "within 1–2 business days. Submit a refund request to the Billing Team "
            "with the transaction ID and error description. "
            "Customer should receive a confirmation email within 4 hours."
        ),
        "policy": "Billing errors qualify for expedited 1–2 day refund processing.",
        "escalate_if": "Expedited refund not processed within 2 business days.",
    },
    # ─── TECHNICAL ────────────────────────────────────────────────────────────
    {
        "id": "KB-TECH-001",
        "category": "technical",
        "title": "Troubleshooting login issues",
        "keywords": ["login", "sign in", "password", "access", "locked", "authentication", "2FA", "MFA"],
        "content": (
            "Step 1: Clear browser cache and cookies. "
            "Step 2: Try an incognito/private window. "
            "Step 3: Reset your password via the 'Forgot Password' link. "
            "Step 4: If MFA is enabled, ensure your authenticator app is time-synced. "
            "Step 5: Check service status at status.ourplatform.com for outages."
        ),
        "policy": "Accounts are locked after 10 failed login attempts for 15 minutes.",
        "escalate_if": "Account locked due to suspected breach or customer cannot receive MFA codes.",
    },
    {
        "id": "KB-TECH-002",
        "category": "technical",
        "title": "API rate limiting and error codes",
        "keywords": ["API", "rate limit", "429", "error", "throttle", "quota", "developer"],
        "content": (
            "Our API enforces rate limits of 1,000 requests/minute per API key. "
            "HTTP 429 (Too Many Requests) is returned when the limit is exceeded. "
            "Implement exponential backoff: wait 2^n seconds between retries (max 32s). "
            "Enterprise plans have custom rate limits — contact sales for upgrades."
        ),
        "policy": "Rate limits are enforced per API key, not per account.",
        "escalate_if": "Customer reports 429 errors below documented rate limits.",
    },
    {
        "id": "KB-TECH-003",
        "category": "technical",
        "title": "Data sync failures and troubleshooting",
        "keywords": ["sync", "data", "integration", "webhook", "missing data", "not updating"],
        "content": (
            "Data sync issues are commonly caused by: (1) expired OAuth tokens, "
            "(2) webhook endpoint timeouts (must respond within 30s), "
            "(3) schema mismatches after API version upgrades. "
            "Re-authenticate the integration from Settings → Integrations. "
            "Check webhook delivery logs for error payloads."
        ),
        "policy": "Webhooks retry up to 3 times with exponential backoff over 24 hours.",
        "escalate_if": "Data loss suspected or sync failure affects production data pipeline.",
    },
    # ─── ACCOUNT ──────────────────────────────────────────────────────────────
    {
        "id": "KB-ACC-001",
        "category": "account",
        "title": "How to cancel your subscription",
        "keywords": ["cancel", "subscription", "unsubscribe", "downgrade", "stop service"],
        "content": (
            "To cancel your subscription, go to Settings → Subscription → Cancel Plan. "
            "You will retain access until the end of the current billing period. "
            "Data is retained for 30 days after cancellation before permanent deletion. "
            "You can reactivate within 30 days without data loss."
        ),
        "policy": "Customers retain access through end of paid period; data held 30 days post-cancellation.",
        "escalate_if": "Customer requests immediate data deletion (GDPR right to erasure).",
    },
    {
        "id": "KB-ACC-002",
        "category": "account",
        "title": "Account compromise and security incidents",
        "keywords": ["hacked", "compromised", "unauthorized", "security", "breach", "suspicious"],
        "content": (
            "Immediately: (1) Reset password using a trusted email. "
            "(2) Revoke all active sessions from Settings → Security → Active Sessions. "
            "(3) Enable MFA if not already active. "
            "(4) Review audit logs for unauthorized actions. "
            "Escalate to the Security Team if unauthorized data access is confirmed."
        ),
        "policy": "Security incidents must be escalated to the Security Team within 1 hour of confirmation.",
        "escalate_if": "Always escalate confirmed account compromises to Security Team.",
    },
]


def retrieve_documents(query: str, top_k: int = 3) -> List[Dict]:
    """
    BM25-style keyword retrieval over the knowledge base.
    Returns the top_k most relevant articles for the given query.
    """
    query_terms = set(query.lower().split())
    scores = []

    for article in KNOWLEDGE_BASE:
        score = 0
        article_terms = " ".join(
            [article["title"], article["content"], " ".join(article["keywords"])]
        ).lower()

        for term in query_terms:
            if term in article_terms:
                # Keyword match is weighted higher
                if term in [kw.lower() for kw in article["keywords"]]:
                    score += 3
                else:
                    score += 1

        scores.append((score, article))

    scores.sort(key=lambda x: x[0], reverse=True)
    return [art for score, art in scores[:top_k] if score > 0]
