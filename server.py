"""
ReleaseGuardian — FastAPI Backend
Serves the agent pipeline as REST API endpoints.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import json

from agents.context_builder import build_release_context
from agents.risk_analyst import analyze_risk
from agents.recovery_planner import generate_recovery_plan
from data.demo_scenarios import get_demo_scenarios

app = FastAPI(title="ReleaseGuardian API")

# Allow React dev server to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    pr_diff: str
    jira_ticket: str
    runbook: Optional[str] = None
    incidents: Optional[List[str]] = None
    screenshot_description: Optional[str] = None


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "ReleaseGuardian"}


@app.get("/api/scenarios")
def get_scenarios():
    """Return available demo scenarios."""
    scenarios = get_demo_scenarios()
    return {"scenarios": list(scenarios.keys())}


@app.get("/api/scenarios/{scenario_name}")
def get_scenario_data(scenario_name: str):
    """Return data for a specific demo scenario."""
    scenarios = get_demo_scenarios()
    for name, data in scenarios.items():
        if name == scenario_name:
            return {"name": name, "data": data}
    return {"error": "Scenario not found"}


@app.post("/api/analyze")
def analyze_release(req: AnalyzeRequest):
    """Run the full 3-agent pipeline."""

    # Agent 1: Context Builder
    release_profile = build_release_context(
        pr_diff=req.pr_diff,
        jira_ticket=req.jira_ticket,
        runbook=req.runbook,
        incidents=req.incidents,
        screenshot_description=req.screenshot_description,
    )

    # Agent 2: Risk Analyst
    raw_artifacts = f"PR DIFF:\n{req.pr_diff}\n\nJIRA TICKET:\n{req.jira_ticket}"
    if req.runbook:
        raw_artifacts += f"\n\nRUNBOOK:\n{req.runbook}"
    if req.incidents:
        for i, inc in enumerate(req.incidents, 1):
            raw_artifacts += f"\n\nINCIDENT {i}:\n{inc}"
    if req.screenshot_description:
        raw_artifacts += f"\n\nDASHBOARD:\n{req.screenshot_description}"

    risk_assessment = analyze_risk(
        release_profile=release_profile,
        raw_artifacts=raw_artifacts,
    )

    # Agent 3: Recovery Planner
    recovery_plan = generate_recovery_plan(
        release_profile=release_profile,
        risk_assessment=risk_assessment,
        runbook=req.runbook,
    )

    return {
        "release_profile": release_profile,
        "risk_assessment": risk_assessment,
        "recovery_plan": recovery_plan,
    }