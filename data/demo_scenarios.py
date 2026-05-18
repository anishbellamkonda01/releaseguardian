"""
Demo Scenarios
Pre-built scenarios for quick demos. Each scenario contains all the
artifacts needed to run the pipeline.
"""


def get_demo_scenarios():
    """Returns a dictionary of demo scenario names to their data."""
    return {
        "High Risk: Payment Timeout Change": get_high_risk_scenario(),
        "Medium Risk: New API Field": get_medium_risk_scenario(),
        "Low Risk: Copy Update": get_low_risk_scenario(),
    }


def get_high_risk_scenario():
    """The hero demo scenario — payment timeout change that matches a past incident."""
    return {
        "pr_diff": """## PR #247: Update payment timeout configuration
### Files changed:
- src/checkout-service/handlers/payment_handler.py
- src/checkout-service/config/timeouts.yaml

### Diff:
- PAYMENT_TIMEOUT_MS = 3000
+ PAYMENT_TIMEOUT_MS = 5000

- async def process_payment(self, order_id, amount):
-     response = await self.payment_gateway.charge(
-         order_id, amount, timeout=PAYMENT_TIMEOUT_MS
-     )
+ async def process_payment(self, order_id, amount):
+     response = await self.payment_gateway.charge(
+         order_id, amount, timeout=PAYMENT_TIMEOUT_MS
+     )

### Notes:
- Changed payment timeout from 3000ms to 5000ms
- No new tests added
- 2 existing timeout tests were removed as "flaky"
- Affects checkout-service payment handler
- No load test results attached""",

        "jira_ticket": """TICKET: SHOP-1042
Title: Increase payment gateway timeout for international transactions
Priority: High
Reporter: Sarah Chen (Product Manager)
Assignee: Mike Rodriguez (Backend Engineer)

Description:
International customers are experiencing payment failures due to the 3-second
timeout being too short for cross-border payment processing. Payment gateway
provider (Stripe) confirmed that international transactions can take up to
4.5 seconds. We need to increase the timeout to 5 seconds to accommodate this.

Acceptance Criteria:
- Payment timeout increased to 5000ms
- No degradation in domestic payment performance
- Monitor error rates for 24 hours post-deploy

Linked Issues:
- SHOP-998: International payment failure rate at 4.2%
- SHOP-1001: Customer complaints from EU region""",

        "runbook": """# Checkout Service Runbook
## Service: checkout-service
## Owner: Payments Team
## Last Updated: January 2024

### Overview:
Handles the purchase flow including cart validation, payment processing,
and order creation. Processes ~2,000 transactions per minute at peak.

### Dependencies:
- auth-service (user validation, token verification)
- payment-gateway (external - Stripe API)
- redis-cache (session data, cart data, idempotency keys)
- notification-service (order confirmation emails, SMS)
- inventory-service (stock validation)

### Known Failure Modes:
1. Payment gateway timeout - causes order to hang in "processing" state
2. Redis connection pool exhaustion - causes cart data loss
3. Auth-service token expiry during checkout - causes 401 errors mid-flow
4. Stripe webhook delivery failure - causes order status desync

### Recovery Procedures:
1. For payment gateway issues: Check Stripe status page, verify API keys,
   check network connectivity to api.stripe.com
2. For Redis issues: Restart Redis pod, clear stale connections,
   verify memory usage below 80%
3. For auth issues: Restart auth-service, clear token cache

### Health Check:
- Endpoint: /health
- Expected response: 200 OK with {"status": "healthy"}
- Does NOT currently validate payment gateway connectivity
- Does NOT check thread pool utilization

### Scaling:
- Current: 8 pods, 4 CPU / 8GB RAM each
- Auto-scale trigger: CPU > 70% for 5 minutes
- Max pods: 20

### NOTE: No rollback procedure exists for timeout configuration changes.""",

        "incidents": ["""INCIDENT REPORT: INC-2024-031
Date: March 15, 2024
Duration: 45 minutes
Severity: SEV-2 (Major)
Services Affected: checkout-service, payment-gateway, notification-service

Summary:
A timeout configuration change in checkout-service caused cascading failures
during peak traffic. The payment timeout was changed from 2000ms to 4000ms
in PR #198. Under load, the longer timeout caused thread pool exhaustion
in checkout-service, which backed up requests to the payment gateway and
delayed order confirmation notifications.

Impact:
- 12% of transactions failed during the incident window
- Estimated revenue loss: $47,000
- 3,200 customers affected
- 847 support tickets filed
- Notification delays of up to 30 minutes for successful orders

Timeline:
- 14:00 - PR #198 deployed to production
- 14:12 - First alerts fire: checkout-service p99 latency > 3s
- 14:18 - Error rate crosses 5%
- 14:22 - On-call engineer paged
- 14:31 - Root cause identified as timeout change
- 14:35 - Rollback initiated (manual revert of config)
- 14:42 - Rollback complete, service recovering
- 14:45 - Error rate returns to normal

Root Cause:
The increased timeout meant each payment request held a thread for longer.
During peak traffic (>500 requests/second), the thread pool (max 200 threads)
was exhausted within 8 minutes. No load test was performed before the change.
The health check endpoint did not monitor thread pool utilization.

Resolution:
- Reverted the timeout change
- Added thread pool monitoring alerts
- Updated checkout-service runbook

Follow-up Actions:
- [ ] Add load testing requirement for timeout changes (NOT DONE)
- [ ] Add rollback procedure for timeout changes to runbook (NOT DONE)
- [x] Added thread pool monitoring
- [ ] Add thread pool check to health endpoint (NOT DONE)
- [x] Updated incident response playbook""",

"""INCIDENT REPORT: INC-2024-018
Date: January 22, 2024
Duration: 20 minutes
Severity: SEV-3 (Minor)
Services Affected: auth-service, checkout-service

Summary:
Redis cache corruption caused auth-service to return stale session tokens.
Checkout-service rejected the stale tokens, causing intermittent 401 errors
for users mid-checkout.

Impact:
- 3% of active sessions affected
- ~500 users had to re-login
- No revenue loss (users could retry)

Root Cause:
A Redis failover event caused partial cache corruption. Auth-service
continued serving cached tokens that had been invalidated during failover.

Resolution:
- Flushed Redis cache
- Restarted auth-service pods
- Added cache consistency check on failover"""],

        "screenshot_description": """Dashboard observation from Grafana (checkout-service panel):
- p99 latency: 2.1 seconds (normal baseline: 0.8 seconds) - ELEVATED for 2 hours
- Error rate: 0.3% (normal baseline: 0.05%) - slightly elevated
- Thread pool utilization: 68% (normal baseline: 40%) - trending upward
- Active connections to Stripe API: 145 (normal: 80) - elevated
- Redis connection pool: 72% utilized (normal: 50%)
- Request rate: 1,847 req/min (normal for this time: ~1,500 req/min)
- CPU utilization: 62% across pods"""
    }


def get_medium_risk_scenario():
    """Medium risk — adding a new field to checkout API response."""
    return {
        "pr_diff": """## PR #251: Add estimated_delivery_date to checkout response
### Files changed:
- src/checkout-service/models/order_response.py
- src/checkout-service/handlers/checkout_handler.py
- src/checkout-service/tests/test_checkout_handler.py

### Diff:
class OrderResponse:
    order_id: str
    total: float
    status: str
+   estimated_delivery_date: Optional[str] = None

# In checkout_handler.py:
+ delivery_estimate = await self.shipping_service.get_estimate(order.address)
+ response.estimated_delivery_date = delivery_estimate.date

### Notes:
- New optional field added to API response
- 3 new tests added
- Calls shipping-service (new dependency for checkout flow)
- Backwards compatible — field is optional""",

        "jira_ticket": """TICKET: SHOP-1055
Title: Show estimated delivery date at checkout
Priority: Medium
Reporter: Product Team
Assignee: Lisa Park

Description:
Customers want to see estimated delivery dates before completing purchase.
Add estimated_delivery_date to the checkout API response by integrating
with the shipping-service estimate endpoint.

Acceptance Criteria:
- New field appears in checkout response
- Field is optional (null if estimate unavailable)
- Does not block checkout if shipping-service is down""",

        "runbook": """# Checkout Service Runbook (abbreviated)
## Dependencies: auth-service, payment-gateway, redis-cache, notification-service
## NOTE: shipping-service is NOT listed as a dependency in this runbook""",

        "incidents": ["""INCIDENT REPORT: INC-2024-025
Date: February 10, 2024
Severity: SEV-3
Summary: shipping-service experienced 10-minute outage due to
third-party API rate limiting. No customer impact because no
critical path depended on it at the time."""],

        "screenshot_description": "All dashboards showing normal. No elevated metrics."
    }


def get_low_risk_scenario():
    """Low risk — simple copy update in notification templates."""
    return {
        "pr_diff": """## PR #253: Update order confirmation email copy
### Files changed:
- src/notification-service/templates/order_confirmation.html

### Diff:
- <h1>Thanks for your order!</h1>
+ <h1>Thank you for your purchase!</h1>

- <p>Your order #{{order_id}} has been received.</p>
+ <p>Your order #{{order_id}} has been confirmed and is being prepared.</p>

### Notes:
- Copy-only change in email template
- No logic changes
- Existing template tests still pass""",

        "jira_ticket": """TICKET: SHOP-1060
Title: Update order confirmation email wording
Priority: Low
Reporter: Marketing Team
Description: Update email copy to match new brand voice guidelines.""",

        "runbook": None,
        "incidents": [],
        "screenshot_description": None
    }