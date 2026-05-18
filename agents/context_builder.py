"""
Agent 1: Context Builder
========================
Takes raw artifacts (PR diff, Jira ticket, runbook, incidents, screenshot)
and produces a structured "release profile" in JSON format.

Uses: Gemini Flash (fast extraction, not deep reasoning)
"""

from utils.gemini_client import call_gemini_json, FLASH_MODEL


def build_release_context(pr_diff, jira_ticket, runbook=None, incidents=None, screenshot_description=None):
    """
    Takes raw release artifacts and returns a structured release profile.

    Parameters:
    - pr_diff: String containing the PR diff or code change
    - jira_ticket: String containing the Jira ticket or release note
    - runbook: String containing the service runbook (optional)
    - incidents: List of strings, each being a past incident report (optional)
    - screenshot_description: String description of dashboard screenshot (optional)

    Returns:
    - Dictionary containing the structured release profile
    """

    # Build the input section — only include what's provided
    artifacts_text = f"""
## PR DIFF / CODE CHANGE:
{pr_diff}

## JIRA TICKET / RELEASE NOTE:
{jira_ticket}
"""

    if runbook:
        artifacts_text += f"""
## SERVICE RUNBOOK:
{runbook}
"""

    if incidents:
        artifacts_text += "\n## PAST INCIDENT REPORTS:\n"
        for i, incident in enumerate(incidents, 1):
            artifacts_text += f"\n### Incident {i}:\n{incident}\n"

    if screenshot_description:
        artifacts_text += f"""
## DASHBOARD/MONITORING OBSERVATION:
{screenshot_description}
"""

    # The prompt — this is the most important part
    prompt = f"""You are a Release Context Builder for an engineering team. Your job is to read all the release artifacts provided below and extract structured information into a JSON format.

Read every artifact carefully. Extract facts, don't make assumptions.

ARTIFACTS:
{artifacts_text}

INSTRUCTIONS:
Analyze all the artifacts above and produce a JSON object with exactly this structure:

{{
    "release_id": "a short identifier based on the PR or ticket, e.g. checkout-v2.4.1",
    "summary": "one sentence describing what this release does",
    "services_touched": ["list of service names that this change directly modifies"],
    "files_modified": ["list of key files or modules changed based on the PR diff"],
    "dependencies": ["list of other services, databases, or external systems that the touched services depend on"],
    "affected_user_flows": ["list of user-facing flows that could be impacted, e.g. checkout, login, payment"],
    "risky_patterns": ["list of risky patterns found, e.g. timeout change, missing tests, database migration, API contract change, retry logic change, feature flag toggle"],
    "test_delta": {{
        "added": 0,
        "removed": 0,
        "modified": 0,
        "notes": "brief description of test coverage situation"
    }},
    "similar_incidents": [
        {{
            "incident_id": "ID or name of the past incident",
            "similarity": "brief explanation of why this is similar to the current change",
            "severity": "how bad was the past incident (minor/major/critical)"
        }}
    ],
    "current_system_signals": "any observations about current system health from dashboard screenshots or monitoring data, or 'No monitoring data provided' if none",
    "missing_items": ["list of things that are missing or concerning, e.g. no runbook, no tests, no rollback plan, no load test results"]
}}

IMPORTANT:
- Only include facts you can find in the artifacts. Do not invent information.
- If an artifact wasn't provided (e.g. no runbook), note it in missing_items.
- If no past incidents are similar, return an empty list for similar_incidents.
- Respond with ONLY the JSON object. No markdown, no explanation, no code blocks.
"""

    # Call Gemini
    result = call_gemini_json(prompt, model=FLASH_MODEL, temperature=0.2)

    # If Gemini fails, return a basic error profile
    if result is None:
        return {
            "error": "Failed to build release context. Gemini did not return valid JSON.",
            "release_id": "unknown",
            "summary": "Context building failed",
            "services_touched": [],
            "dependencies": [],
            "affected_user_flows": [],
            "risky_patterns": [],
            "test_delta": {"added": 0, "removed": 0, "modified": 0, "notes": "unknown"},
            "similar_incidents": [],
            "current_system_signals": "unknown",
            "missing_items": ["Context building failed - check Gemini API connection"]
        }

    return result