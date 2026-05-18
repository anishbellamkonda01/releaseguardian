"""
Agent 2: Risk Analyst
=====================
Takes the structured release profile from Agent 1 and produces
a risk assessment with score, blast radius, and failure modes.

Uses: Gemini Pro (or Flash) for deeper reasoning
"""

import json
from utils.gemini_client import call_gemini_json, PRO_MODEL


def analyze_risk(release_profile, raw_artifacts=None):
    """
    Takes a structured release profile and returns a risk assessment.

    Parameters:
    - release_profile: Dictionary from Agent 1 (the release profile)
    - raw_artifacts: Optional string of all original artifacts for evidence citing

    Returns:
    - Dictionary containing the risk assessment
    """

    profile_text = json.dumps(release_profile, indent=2)

    # Include raw artifacts for evidence if available
    evidence_section = ""
    if raw_artifacts:
        evidence_section = f"""

ORIGINAL ARTIFACTS (use these to cite specific evidence for your claims):
{raw_artifacts}
"""

    prompt = f"""You are a Senior Site Reliability Engineer performing a release risk assessment. You have been given a structured release profile extracted from the release artifacts. Your job is to evaluate the risk and provide a detailed, evidence-based assessment.

RELEASE PROFILE:
{profile_text}
{evidence_section}

INSTRUCTIONS:
Evaluate risk across these six dimensions:
1. CODE CHANGE SCOPE - How many files, how critical is the code path?
2. DEPENDENCY RISK - How many downstream services could be affected?
3. HISTORICAL PATTERN MATCH - Does this look like a change that caused problems before?
4. TEST COVERAGE - Are there tests for the changed code? Were tests removed?
5. OPERATIONAL READINESS - Does a runbook exist? Does it cover this scenario?
6. CURRENT SYSTEM HEALTH - Is the system already showing stress?

Then produce a JSON object with exactly this structure:

{{
    "risk_score": "LOW or MEDIUM or HIGH or CRITICAL",
    "risk_score_numeric": 0,
    "confidence": 0.0,
    "summary": "2-3 sentence explanation of the overall risk assessment",
    "risk_dimensions": {{
        "code_change_scope": {{
            "score": "LOW/MEDIUM/HIGH/CRITICAL",
            "explanation": "why this score"
        }},
        "dependency_risk": {{
            "score": "LOW/MEDIUM/HIGH/CRITICAL",
            "explanation": "why this score"
        }},
        "historical_pattern_match": {{
            "score": "LOW/MEDIUM/HIGH/CRITICAL",
            "explanation": "why this score"
        }},
        "test_coverage": {{
            "score": "LOW/MEDIUM/HIGH/CRITICAL",
            "explanation": "why this score"
        }},
        "operational_readiness": {{
            "score": "LOW/MEDIUM/HIGH/CRITICAL",
            "explanation": "why this score"
        }},
        "current_system_health": {{
            "score": "LOW/MEDIUM/HIGH/CRITICAL",
            "explanation": "why this score"
        }}
    }},
    "blast_radius": {{
        "services_affected": ["list of services that would be impacted if this release fails"],
        "user_flows_affected": ["list of user-facing flows that would break"],
        "estimated_user_impact": "description of how many users would be affected and how",
        "sla_risk": "which SLAs are at risk, if any"
    }},
    "failure_modes": [
        {{
            "description": "what could go wrong",
            "likelihood": "LOW/MEDIUM/HIGH",
            "severity": "LOW/MEDIUM/HIGH/CRITICAL",
            "evidence": "specific evidence from the artifacts that supports this failure mode"
        }}
    ],
    "missing_safeguards": ["list of things that should exist but don't, e.g. missing load test, missing rollback procedure, missing health check"]
}}

SCORING GUIDE:
- risk_score_numeric: 1-25 for LOW, 26-50 for MEDIUM, 51-75 for HIGH, 76-100 for CRITICAL
- confidence: 0.0 to 1.0, how confident you are in this assessment (higher = more evidence available)
- List at least 2 failure modes, ranked by likelihood
- Every claim in "evidence" must reference something specific from the artifacts

Respond with ONLY the JSON object. No markdown, no explanation, no code blocks.
"""

    result = call_gemini_json(prompt, model=PRO_MODEL, temperature=0.2)

    if result is None:
        return {
            "error": "Failed to analyze risk. Gemini did not return valid JSON.",
            "risk_score": "UNKNOWN",
            "risk_score_numeric": 0,
            "confidence": 0.0,
            "summary": "Risk analysis failed. Please retry.",
            "risk_dimensions": {},
            "blast_radius": {
                "services_affected": [],
                "user_flows_affected": [],
                "estimated_user_impact": "Unknown",
                "sla_risk": "Unknown"
            },
            "failure_modes": [],
            "missing_safeguards": ["Risk analysis failed - check Gemini API connection"]
        }

    return result