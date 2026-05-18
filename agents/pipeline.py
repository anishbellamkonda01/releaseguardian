"""
Pipeline: Connects all three agents in sequence.
Agent 1 (Context Builder) → Agent 2 (Risk Analyst) → Agent 3 (Recovery Planner)
"""

from agents.context_builder import build_release_context
from agents.risk_analyst import analyze_risk
from agents.recovery_planner import generate_recovery_plan


def run_pipeline(pr_diff, jira_ticket, runbook=None, incidents=None, screenshot_description=None):
    """
    Runs the full ReleaseGuardian pipeline.

    Parameters:
    - pr_diff: String containing the PR diff
    - jira_ticket: String containing the Jira ticket
    - runbook: Optional runbook text
    - incidents: Optional list of incident report strings
    - screenshot_description: Optional dashboard observation

    Returns:
    - Dictionary with three keys: release_profile, risk_assessment, recovery_plan
    - Each key contains the output from the corresponding agent
    """

    results = {
        "release_profile": None,
        "risk_assessment": None,
        "recovery_plan": None,
        "status": "running",
        "errors": []
    }

    # ========== AGENT 1: Context Builder ==========
    print("🔍 Agent 1: Building release context...")

    release_profile = build_release_context(
        pr_diff=pr_diff,
        jira_ticket=jira_ticket,
        runbook=runbook,
        incidents=incidents,
        screenshot_description=screenshot_description
    )

    results["release_profile"] = release_profile

    if release_profile is None or "error" in release_profile:
        results["errors"].append("Agent 1 (Context Builder) failed")
        results["status"] = "partial_failure"
        # Don't stop — try to continue with whatever we have

    print("✅ Agent 1 complete.")

    # ========== AGENT 2: Risk Analyst ==========
    print("⚠️  Agent 2: Analyzing risk...")

    # Build raw artifacts string for evidence citing
    raw_artifacts = f"PR DIFF:\n{pr_diff}\n\nJIRA TICKET:\n{jira_ticket}"
    if runbook:
        raw_artifacts += f"\n\nRUNBOOK:\n{runbook}"
    if incidents:
        for i, inc in enumerate(incidents, 1):
            raw_artifacts += f"\n\nINCIDENT {i}:\n{inc}"
    if screenshot_description:
        raw_artifacts += f"\n\nDASHBOARD:\n{screenshot_description}"

    risk_assessment = analyze_risk(
        release_profile=release_profile,
        raw_artifacts=raw_artifacts
    )

    results["risk_assessment"] = risk_assessment

    if risk_assessment is None or "error" in risk_assessment:
        results["errors"].append("Agent 2 (Risk Analyst) failed")
        results["status"] = "partial_failure"

    print("✅ Agent 2 complete.")

    # ========== AGENT 3: Recovery Planner ==========
    print("🔄 Agent 3: Generating recovery plan...")

    recovery_plan = generate_recovery_plan(
        release_profile=release_profile,
        risk_assessment=risk_assessment,
        runbook=runbook
    )

    results["recovery_plan"] = recovery_plan

    if recovery_plan is None or "error" in recovery_plan:
        results["errors"].append("Agent 3 (Recovery Planner) failed")
        results["status"] = "partial_failure"

    print("✅ Agent 3 complete.")

    # Final status
    if not results["errors"]:
        results["status"] = "success"

    return results