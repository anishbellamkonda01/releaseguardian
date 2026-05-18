"""
Agent 3: Recovery Planner
=========================
Takes the risk assessment and release profile and generates
actionable recovery artifacts: rollback plan, checklists, and communications.

Uses: Gemini Flash (structured generation, not deep reasoning)
"""

import json
from utils.gemini_client import call_gemini_json, FLASH_MODEL


def generate_recovery_plan(release_profile, risk_assessment, runbook=None):
    """
    Takes the release profile and risk assessment and generates recovery artifacts.

    Parameters:
    - release_profile: Dictionary from Agent 1
    - risk_assessment: Dictionary from Agent 2
    - runbook: Optional string of the original runbook for reference

    Returns:
    - Dictionary containing all recovery artifacts
    """

    profile_text = json.dumps(release_profile, indent=2)
    risk_text = json.dumps(risk_assessment, indent=2)

    runbook_section = ""
    if runbook:
        runbook_section = f"""

EXISTING RUNBOOK (reference this when creating rollback steps):
{runbook}
"""

    prompt = f"""You are a Senior Release Engineer generating a comprehensive recovery plan for a production deployment. You have the release profile and risk assessment. Your job is to generate actionable, specific recovery artifacts.

RELEASE PROFILE:
{profile_text}

RISK ASSESSMENT:
{risk_text}
{runbook_section}

INSTRUCTIONS:
Generate a complete recovery package as a JSON object with this exact structure:

{{
    "pre_deploy_checklist": [
        {{
            "step": 1,
            "action": "specific action to take before deploying",
            "reason": "why this matters",
            "status": "pending"
        }}
    ],
    "rollback_plan": {{
        "trigger_criteria": "specific conditions that should trigger a rollback, e.g. error rate > 5% for 2 minutes",
        "steps": [
            {{
                "step": 1,
                "action": "specific rollback action",
                "expected_result": "what should happen after this step",
                "time_estimate": "how long this step takes"
            }}
        ],
        "verification": "how to verify the rollback was successful",
        "total_estimated_time": "total estimated rollback time"
    }},
    "monitoring_plan": {{
        "dashboards_to_watch": ["list of specific dashboards or panels to monitor"],
        "key_metrics": [
            {{
                "metric": "specific metric name",
                "normal_range": "what the value should be normally",
                "alert_threshold": "at what value to start worrying",
                "critical_threshold": "at what value to trigger rollback"
            }}
        ],
        "monitoring_duration": "how long to monitor post-deploy before considering it safe"
    }},
    "slack_message": "a ready-to-paste Slack message for the release channel that summarizes: what's being deployed, risk level, key concerns, what to watch, and who to contact if something goes wrong. Format it with emoji and clear sections. Keep it under 300 words.",
    "email_summary": "a professional email body for the engineering manager summarizing the release risk, key findings, and the plan. Keep it concise and actionable. 200 words max.",
    "oncall_handoff": "a concise handoff note for the on-call engineer covering: what changed, what could go wrong, what metrics to watch, and step-by-step what to do if something breaks. 200 words max."
}}

REQUIREMENTS:
- Pre-deploy checklist should have 4-6 items, specific to THIS release
- Rollback plan should have 4-8 steps, specific to the services and changes involved
- Monitoring plan should have 3-5 key metrics relevant to the failure modes identified
- All communications should reference the actual risk score and specific concerns
- Be specific, not generic. Reference actual service names, metrics, and thresholds.

Respond with ONLY the JSON object. No markdown, no explanation, no code blocks.
"""

    result = call_gemini_json(prompt, model=FLASH_MODEL, temperature=0.3)

    if result is None:
        return {
            "error": "Failed to generate recovery plan. Gemini did not return valid JSON.",
            "pre_deploy_checklist": [],
            "rollback_plan": {
                "trigger_criteria": "Unknown",
                "steps": [],
                "verification": "Unknown",
                "total_estimated_time": "Unknown"
            },
            "monitoring_plan": {
                "dashboards_to_watch": [],
                "key_metrics": [],
                "monitoring_duration": "Unknown"
            },
            "slack_message": "⚠️ Recovery plan generation failed. Please retry the analysis.",
            "email_summary": "Recovery plan generation failed. Please retry the analysis.",
            "oncall_handoff": "Recovery plan generation failed. Please retry the analysis."
        }

    return result