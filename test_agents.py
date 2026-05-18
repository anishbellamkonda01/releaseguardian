"""
Test the full agent pipeline with sample data.
Run with: python test_agents.py
"""

from agents.pipeline import run_pipeline

# === SAMPLE TEST DATA ===
sample_pr_diff = """
## PR #247: Update payment timeout configuration
### Files changed:
- src/checkout-service/handlers/payment_handler.py

### Diff:
```diff
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
```

### Notes:
- Changed payment timeout from 3000ms to 5000ms
- No new tests added
- Affects checkout-service payment handler
"""

sample_jira_ticket = """
TICKET: SHOP-1042
Title: Increase payment gateway timeout for international transactions
Priority: High
Reporter: Sarah Chen (Product Manager)
Assignee: Mike Rodriguez (Backend Engineer)

Description:
International customers are experiencing payment failures due to the 3-second
timeout being too short for cross-border payment processing. Payment gateway
provider confirmed that international transactions can take up to 4.5 seconds.
We need to increase the timeout to 5 seconds to accommodate this.

Acceptance Criteria:
- Payment timeout increased to 5000ms
- No degradation in domestic payment performance
- Monitor error rates for 24 hours post-deploy
"""

sample_runbook = """
# Checkout Service Runbook
## Service: checkout-service
## Owner: Payments Team

### Overview:
Handles the purchase flow including cart validation, payment processing,
and order creation.

### Dependencies:
- auth-service (user validation)
- payment-gateway (external - Stripe)
- redis-cache (session and cart data)
- notification-service (order confirmation emails)

### Known Failure Modes:
1. Payment gateway timeout - causes order to hang in "processing" state
2. Redis connection pool exhaustion - causes cart data loss
3. Auth-service token expiry during checkout - causes 401 errors mid-flow

### Recovery Procedures:
1. For payment gateway issues: Check Stripe status page, verify API keys
2. For Redis issues: Restart Redis pod, clear stale connections
3. For auth issues: Restart auth-service, clear token cache

### Health Check:
- Endpoint: /health
- Expected response: 200 OK with {"status": "healthy"}
- Does NOT currently validate payment gateway connectivity
"""

sample_incident = """
INCIDENT REPORT: INC-2024-031
Date: March 15, 2024
Duration: 45 minutes
Severity: SEV-2 (Major)
Services Affected: checkout-service, payment-gateway

Summary:
A timeout configuration change in checkout-service caused cascading failures
during peak traffic. The payment timeout was changed from 2000ms to 4000ms
in PR #198. Under load, the longer timeout caused thread pool exhaustion
in checkout-service, which backed up requests to the payment gateway.

Impact:
- 12% of transactions failed during the incident window
- Estimated revenue loss: $47,000
- 3,200 customers affected

Root Cause:
The increased timeout meant each payment request held a thread for longer.
During peak traffic (>500 requests/second), the thread pool was exhausted
within 8 minutes. No load test was performed before the change.

Resolution:
- Reverted the timeout change
- Added thread pool monitoring alerts
- Updated checkout-service runbook (but rollback steps for timeout changes
  were NOT added to the runbook)

Follow-up Actions:
- [ ] Add load testing requirement for timeout changes (NOT DONE)
- [ ] Add rollback procedure for timeout changes to runbook (NOT DONE)
- [x] Added thread pool monitoring
"""

sample_screenshot = """
Dashboard observation: Grafana checkout-service panel shows p99 latency
has been elevated at 2.1 seconds (normally 0.8 seconds) for the past
2 hours. Error rate is currently at 0.3% (normally 0.1%). Thread pool
utilization is at 68% (normally 40%).
"""

# === RUN THE PIPELINE ===
print("=" * 60)
print("ReleaseGuardian - Full Pipeline Test")
print("=" * 60)

results = run_pipeline(
    pr_diff=sample_pr_diff,
    jira_ticket=sample_jira_ticket,
    runbook=sample_runbook,
    incidents=[sample_incident],
    screenshot_description=sample_screenshot
)

print("\n" + "=" * 60)
print(f"Pipeline Status: {results['status']}")
print(f"Errors: {results['errors']}")
print("=" * 60)

# Show key results
if results["release_profile"]:
    profile = results["release_profile"]
    print(f"\n📋 Release: {profile.get('release_id', 'unknown')}")
    print(f"   Services: {profile.get('services_touched', [])}")
    print(f"   Risky Patterns: {profile.get('risky_patterns', [])}")
    print(f"   Similar Incidents: {len(profile.get('similar_incidents', []))} found")

if results["risk_assessment"]:
    risk = results["risk_assessment"]
    print(f"\n⚠️  Risk Score: {risk.get('risk_score', 'unknown')} ({risk.get('risk_score_numeric', 0)}/100)")
    print(f"   Confidence: {risk.get('confidence', 0)}")
    print(f"   Summary: {risk.get('summary', 'N/A')}")
    print(f"   Failure Modes: {len(risk.get('failure_modes', []))}")

if results["recovery_plan"]:
    plan = results["recovery_plan"]
    print(f"\n🔄 Recovery Plan:")
    print(f"   Pre-deploy steps: {len(plan.get('pre_deploy_checklist', []))}")
    print(f"   Rollback steps: {len(plan.get('rollback_plan', {}).get('steps', []))}")
    print(f"   Metrics to watch: {len(plan.get('monitoring_plan', {}).get('key_metrics', []))}")
    print(f"\n📨 Slack Message Preview:")
    slack = plan.get("slack_message", "N/A")
    print(f"   {slack[:200]}...")

print("\n✅ Full pipeline test complete!")

# Print full JSON for caching
import json
print("\n\n=== COPY EVERYTHING BELOW FOR CACHING ===")
print(json.dumps(results, indent=2))
print("=== END CACHE DATA ===")