# 🛡️ ReleaseGuardian

### AI-Powered Deployment Risk Analysis & Rollback Copilot

> **Don't let risky deploys go live without context.**

ReleaseGuardian uses a **3-agent Gemini AI pipeline** to analyze code changes, Jira tickets, incident history, and operational signals before deployment — predicting risk, mapping blast radius, and generating rollback plans in under 60 seconds.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-red?logo=streamlit&logoColor=white)
![Gemini](https://img.shields.io/badge/Google%20Gemini-2.5%20Flash-4285F4?logo=google&logoColor=white)

---

## 🎯 What It Does

Engineering teams push code every day, but **risky deployments slip through** because context is scattered across PRs, tickets, runbooks, and incident history. ReleaseGuardian acts as your pre-deploy safety net:

1. **📄 Ingests deployment artifacts** — PR diffs, Jira tickets, service runbooks, past incident reports, dashboard screenshots
2. **🤖 Runs 3 AI agents sequentially** — each specializing in a different aspect of risk analysis
3. **📊 Produces actionable output** — risk scores, blast radius maps, failure mode predictions, rollback plans, and stakeholder communications

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    INPUT ARTIFACTS                       │
│  PR Diff · Jira Ticket · Runbook · Incidents · Dashboard│
└──────────────────────┬──────────────────────────────────┘
                       │
          ┌────────────▼────────────┐
          │   AGENT 1: CONTEXT      │
          │   BUILDER               │
          │   Extracts services,    │
          │   dependencies, risky   │
          │   patterns, test delta  │
          └────────────┬────────────┘
                       │
          ┌────────────▼────────────┐
          │   AGENT 2: RISK         │
          │   ANALYST               │
          │   6-dimension scoring,  │
          │   blast radius mapping, │
          │   failure mode ranking  │
          └────────────┬────────────┘
                       │
          ┌────────────▼────────────┐
          │   AGENT 3: RECOVERY     │
          │   PLANNER               │
          │   Rollback steps,       │
          │   checklists, Slack/    │
          │   email comms, monitor  │
          └────────────┬────────────┘
                       │
          ┌────────────▼────────────┐
          │   RESULTS DASHBOARD     │
          │   5-tab interactive UI  │
          └─────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Google Gemini API key ([Get one free](https://aistudio.google.com/apikey))

### Setup

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/releaseguardian.git
cd releaseguardian

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Add your API key
cp .env.example .env
# Edit .env and paste your GOOGLE_API_KEY

# Run the app
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## 📁 Project Structure

```
releaseguardian/
├── app.py                      # Main Streamlit application
├── agents/
│   ├── __init__.py
│   ├── context_builder.py      # Agent 1: Extracts structured context
│   ├── risk_analyst.py         # Agent 2: Multi-dimensional risk scoring
│   ├── recovery_planner.py     # Agent 3: Rollback & communication plans
│   └── pipeline.py             # Pipeline orchestration
├── data/
│   ├── __init__.py
│   └── demo_scenarios.py       # 3 pre-built demo scenarios
├── utils/
│   ├── __init__.py
│   ├── gemini_client.py        # Gemini API connection & JSON parsing
│   └── charts.py               # Visualization utilities
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🎮 Demo Scenarios

ReleaseGuardian ships with 3 built-in scenarios for the fictional company **ShopFlow**:

| Scenario | Risk Level | Description |
|----------|-----------|-------------|
| **Payment Timeout Change** | 🔴 HIGH | Timeout increased from 3s→5s in checkout-service. Similar change caused a 45-min outage 3 months ago. |
| **New API Field** | 🟡 MEDIUM | Adding `estimated_delivery_date` to checkout response. New dependency on shipping-service. |
| **Copy Update** | 🟢 LOW | Email template wording change in notification-service. No logic changes. |

---

## 📊 Output Types

ReleaseGuardian generates 5 categories of output:

1. **Risk Overview** — Overall risk score (0-100), confidence level, 6-dimension breakdown with explanations
2. **Blast Radius** — Service dependency map, affected user flows, SLA risk, similar past incidents
3. **Failure Modes** — Ranked failure scenarios with severity, likelihood, and evidence
4. **Recovery Plan** — Pre-deploy checklist, step-by-step rollback procedures with time estimates, monitoring plan with metric thresholds
5. **Communications** — Ready-to-send Slack message, email summary, and on-call handoff note

---

## 🧠 How the Agents Work

### Agent 1: Context Builder
Reads all input artifacts and extracts a structured "release profile" including services touched, files modified, dependencies, affected user flows, risky patterns, test coverage delta, and similar past incidents.

### Agent 2: Risk Analyst
Takes the release profile and scores risk across 6 dimensions:
- **Code Change Scope** — Size and complexity of changes
- **Dependency Risk** — Cross-service dependencies affected
- **Historical Pattern Match** — Similarity to past incidents
- **Test Coverage** — Test additions/gaps
- **Operational Readiness** — Runbook quality, monitoring
- **Current System Health** — Existing system stability

Also maps blast radius and identifies specific failure modes with evidence.

### Agent 3: Recovery Planner
Generates actionable recovery artifacts:
- Pre-deploy checklist with reasons
- Step-by-step rollback plan with time estimates
- Monitoring plan with normal/alert/critical thresholds
- Stakeholder communications (Slack, email, on-call handoff)

---

## 🛠️ Tech Stack

- **Frontend**: Streamlit + Custom HTML/CSS (dark theme)
- **AI**: Google Gemini 2.5 Flash (multi-agent pipeline)
- **Language**: Python 3.10+
- **Design**: Space Grotesk + JetBrains Mono, Linear/Raycast-inspired dark UI

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

Built for the **Google Gemini API Hackathon** — demonstrating multi-agent AI architecture for enterprise DevOps risk management.

---

<p align="center">
  <b>Built with Google Gemini 2.5 Flash · Multi-Agent Architecture · Python + Streamlit</b>
</p>
# releaseguradian
# releaseguardian
