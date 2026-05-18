"""
Pre-cached results for live demo fallback.
Run the pipeline once, copy the output, and paste it here.
If Gemini is slow or down during the demo, use these instead.
"""

CACHED_HIGH_RISK = None  # We'll fill this in


def get_cached_results(scenario_name):
    """Return cached results if available."""
    if scenario_name == "High Risk: Payment Timeout Change" and CACHED_HIGH_RISK:
        return CACHED_HIGH_RISK
    return None