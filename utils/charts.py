"""
Charts and Visualizations for ReleaseGuardian
Professional-grade Plotly charts for the demo dashboard.
"""

import math
import plotly.graph_objects as go


# Color palette
COLORS = {
    "CRITICAL": "#DC2626",
    "HIGH": "#EA580C",
    "MEDIUM": "#D97706",
    "LOW": "#059669",
    "UNKNOWN": "#6B7280",
    "bg_green": "#D1FAE5",
    "bg_yellow": "#FEF3C7",
    "bg_orange": "#FED7AA",
    "bg_red": "#FECACA",
    "primary": "#1A56DB",
    "gray": "#6B7280",
    "light_gray": "#F3F4F6",
    "dark": "#111827",
}


def get_risk_color(score):
    """Return color hex based on risk level string."""
    if isinstance(score, str):
        return COLORS.get(score.upper(), COLORS["UNKNOWN"])
    return COLORS["UNKNOWN"]


def create_risk_gauge(score_numeric, risk_label):
    """
    Creates a professional risk score gauge chart.

    Parameters:
    - score_numeric: Integer 0-100
    - risk_label: String like "HIGH", "LOW", etc.
    """
    color = get_risk_color(risk_label)

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score_numeric,
        title={
            "text": f"<b>RISK LEVEL: {risk_label}</b>",
            "font": {"size": 18, "color": color}
        },
        number={
            "suffix": "<span style='font-size:20px; color:#6B7280'>/100</span>",
            "font": {"size": 48, "color": color},
        },
        gauge={
            "axis": {
                "range": [0, 100],
                "tickwidth": 2,
                "tickcolor": "#D1D5DB",
                "dtick": 25,
                "tickfont": {"size": 12, "color": "#6B7280"},
            },
            "bar": {"color": color, "thickness": 0.7},
            "bgcolor": "#F9FAFB",
            "borderwidth": 2,
            "bordercolor": "#E5E7EB",
            "steps": [
                {"range": [0, 25], "color": "#D1FAE5"},
                {"range": [25, 50], "color": "#FEF3C7"},
                {"range": [50, 75], "color": "#FED7AA"},
                {"range": [75, 100], "color": "#FECACA"},
            ],
            "threshold": {
                "line": {"color": "#111827", "width": 3},
                "thickness": 0.8,
                "value": score_numeric,
            },
        },
    ))

    fig.update_layout(
        height=300,
        margin=dict(l=30, r=30, t=60, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        font={"family": "Arial"},
    )
    return fig


def create_blast_radius_graph(services_affected, all_services=None, dependencies=None):
    """
    Creates a network graph showing service dependencies and blast radius.
    Affected services are shown in red, unaffected in gray.

    Parameters:
    - services_affected: List of service names that are impacted
    - all_services: Optional list of all services (affected + unaffected)
    - dependencies: Optional list of tuples (source, target) showing connections
    """

    if not services_affected:
        return None

    # Default: build a realistic service map if not provided
    if all_services is None:
        all_services = list(set(services_affected + [
            "auth-service",
            "checkout-service",
            "notification-service",
            "payment-gateway",
            "redis-cache",
            "inventory-service",
        ]))

    if dependencies is None:
        # Default dependency map for ShopFlow
        dependencies = [
            ("checkout-service", "auth-service"),
            ("checkout-service", "payment-gateway"),
            ("checkout-service", "redis-cache"),
            ("checkout-service", "inventory-service"),
            ("notification-service", "checkout-service"),
            ("auth-service", "redis-cache"),
        ]

    # Add edges for any affected services not in default map
    for svc in services_affected:
        svc_lower = svc.lower()
        has_edge = False
        for source, target in dependencies:
            if source.lower() == svc_lower or target.lower() == svc_lower:
                has_edge = True
                break
        if not has_edge and len(all_services) > 1:
            # Connect to the first service in the list as a fallback
            other = [s for s in all_services if s != svc][0]
            dependencies.append((svc, other))

    # Position nodes in a circle layout
    n = len(all_services)
    positions = {}
    for i, svc in enumerate(all_services):
        angle = 2 * math.pi * i / n
        positions[svc] = (math.cos(angle) * 2, math.sin(angle) * 2)

    # Build edges
    edge_x = []
    edge_y = []

    for source, target in dependencies:
        if source in positions and target in positions:
            x0, y0 = positions[source]
            x1, y1 = positions[target]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

    # Edge trace
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=2, color="#D1D5DB"),
        hoverinfo="none",
        mode="lines",
    )

    # Build nodes
    node_x = []
    node_y = []
    node_colors = []
    node_sizes = []
    node_text = []
    node_labels = []

    affected_set = set(s.lower() for s in services_affected)

    for svc in all_services:
        x, y = positions[svc]
        node_x.append(x)
        node_y.append(y)

        is_affected = svc.lower() in affected_set
        node_colors.append("#DC2626" if is_affected else "#D1D5DB")
        node_sizes.append(45 if is_affected else 30)
        node_labels.append(svc)

        status = "🔴 AFFECTED" if is_affected else "⚪ Unaffected"
        node_text.append(f"<b>{svc}</b><br>{status}")

    # Node trace
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text",
        hoverinfo="text",
        hovertext=node_text,
        text=node_labels,
        textposition="top center",
        textfont=dict(size=11, color="#111827", family="Arial"),
        marker=dict(
            size=node_sizes,
            color=node_colors,
            line=dict(width=2, color="white"),
        ),
    )

    fig = go.Figure(data=[edge_trace, node_trace])

    fig.update_layout(
        title=dict(
            text="Service Dependency Graph — Blast Radius",
            font=dict(size=16, color="#111827"),
        ),
        showlegend=False,
        height=400,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        hovermode="closest",
    )

    return fig


def create_radar_chart(risk_dimensions):
    """
    Creates a radar/spider chart showing risk scores across all 6 dimensions.

    Parameters:
    - risk_dimensions: Dictionary from risk_assessment["risk_dimensions"]
      Each key maps to {"score": "HIGH", "explanation": "..."}
    """

    if not risk_dimensions:
        return None

    # Convert text scores to numbers
    score_map = {"LOW": 25, "MEDIUM": 50, "HIGH": 75, "CRITICAL": 100}

    categories = []
    values = []

    for dim_name, dim_data in risk_dimensions.items():
        if isinstance(dim_data, dict):
            label = dim_name.replace("_", " ").title()
            # Shorten long labels
            label = label.replace("Historical Pattern Match", "Historical Match")
            label = label.replace("Current System Health", "System Health")
            label = label.replace("Operational Readiness", "Ops Readiness")
            label = label.replace("Code Change Scope", "Code Scope")
            label = label.replace("Test Coverage", "Test Gaps")
            label = label.replace("Dependency Risk", "Dependencies")
            categories.append(label)

            score_text = dim_data.get("score", "LOW").upper()
            values.append(score_map.get(score_text, 25))

    if not categories:
        return None

    # Close the polygon
    categories.append(categories[0])
    values.append(values[0])

    fig = go.Figure()

    # Filled area
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill="toself",
        fillcolor="rgba(220, 38, 38, 0.15)",
        line=dict(color="#DC2626", width=2),
        marker=dict(size=8, color="#DC2626"),
        name="Risk Level",
    ))

    # Reference line for "medium" baseline
    baseline = [50] * len(categories)
    fig.add_trace(go.Scatterpolar(
        r=baseline,
        theta=categories,
        fill=None,
        line=dict(color="#D1D5DB", width=1, dash="dash"),
        marker=dict(size=0),
        name="Medium Baseline",
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickvals=[25, 50, 75, 100],
                ticktext=["Low", "Med", "High", "Critical"],
                tickfont=dict(size=10, color="#6B7280"),
                gridcolor="#E5E7EB",
            ),
            angularaxis=dict(
                tickfont=dict(size=12, color="#111827", family="Arial"),
                gridcolor="#E5E7EB",
            ),
            bgcolor="rgba(0,0,0,0)",
        ),
        title=dict(
            text="Risk Dimension Analysis",
            font=dict(size=16, color="#111827"),
        ),
        showlegend=False,
        height=380,
        margin=dict(l=60, r=60, t=50, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
    )

    return fig


def create_failure_mode_bar_chart(failure_modes):
    """
    Creates a horizontal bar chart ranking failure modes by severity and likelihood.

    Parameters:
    - failure_modes: List of dicts with "description", "likelihood", "severity"
    """

    if not failure_modes:
        return None

    score_map = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
    color_map = {"LOW": "#059669", "MEDIUM": "#D97706", "HIGH": "#EA580C", "CRITICAL": "#DC2626"}

    descriptions = []
    severity_scores = []
    colors = []

    for fm in failure_modes:
        if isinstance(fm, dict):
            desc = fm.get("description", "Unknown")
            # Truncate long descriptions
            if len(desc) > 50:
                desc = desc[:47] + "..."
            descriptions.append(desc)

            sev = fm.get("severity", "LOW").upper()
            severity_scores.append(score_map.get(sev, 1))
            colors.append(color_map.get(sev, "#6B7280"))

    if not descriptions:
        return None

    # Reverse so highest severity is at top
    descriptions.reverse()
    severity_scores.reverse()
    colors.reverse()

    fig = go.Figure(go.Bar(
        x=severity_scores,
        y=descriptions,
        orientation="h",
        marker=dict(
            color=colors,
            line=dict(width=0),
        ),
        text=[["Low", "Medium", "High", "Critical"][s - 1] for s in severity_scores],
        textposition="inside",
        textfont=dict(color="white", size=12, family="Arial"),
    ))

    fig.update_layout(
        title=dict(
            text="Failure Modes by Severity",
            font=dict(size=16, color="#111827"),
        ),
        xaxis=dict(
            tickvals=[1, 2, 3, 4],
            ticktext=["Low", "Medium", "High", "Critical"],
            range=[0, 4.5],
            gridcolor="#E5E7EB",
        ),
        yaxis=dict(
            tickfont=dict(size=11),
        ),
        height=250,
        margin=dict(l=20, r=20, t=50, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    return fig


def create_timeline_chart(checklist_items):
    """
    Creates a simple horizontal timeline showing pre-deploy steps.

    Parameters:
    - checklist_items: List of dicts with "step", "action"
    """

    if not checklist_items:
        return None

    steps = []
    labels = []

    for item in checklist_items:
        if isinstance(item, dict):
            steps.append(item.get("step", 0))
            action = item.get("action", "Unknown")
            if len(action) > 40:
                action = action[:37] + "..."
            labels.append(action)

    if not steps:
        return None

    fig = go.Figure(go.Scatter(
        x=steps,
        y=[1] * len(steps),
        mode="markers+text",
        marker=dict(
            size=25,
            color=COLORS["primary"],
            line=dict(width=2, color="white"),
        ),
        text=[f"Step {s}" for s in steps],
        textposition="top center",
        textfont=dict(size=10, color="#111827"),
        hovertext=labels,
        hoverinfo="text",
    ))

    # Add connecting line
    fig.add_trace(go.Scatter(
        x=steps,
        y=[1] * len(steps),
        mode="lines",
        line=dict(color=COLORS["primary"], width=2),
        hoverinfo="none",
    ))

    fig.update_layout(
        height=150,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0.5, 1.8]),
        showlegend=False,
    )

    return fig