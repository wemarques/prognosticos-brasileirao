"""League-agnostic prediction helpers used by the Streamlit UI and pipelines."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class MatchInputs:
    home_team: str
    away_team: str
    round_number: int
    kickoff_utc: Any  # Accepts datetime or ISO string; kept flexible for now
    lambda_home: float
    lambda_away: float
    mean_cards: float
    mean_corners: float
    context: Optional[Dict[str, Any]] = None
    raw_row: Optional[Dict[str, Any]] = None


def run_prediction(match_inputs: MatchInputs) -> Dict[str, Any]:
    """
    Execute the core prediction logic for a single match.

    This placeholder keeps the interface stable while the integration
    layer is built. The actual logic (model loading, Monte Carlo steps,
    probability calibration, etc.) will be added in a follow-up change.
    """
    raise NotImplementedError("Prediction logic not implemented yet.")


def format_report(prediction: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format the raw prediction output into a structure that the UI can render.

    Keeping it separate from `run_prediction` lets different front-ends
    (CLI, Streamlit, API) reuse the same prediction data while customizing
    presentation needs.
    """
    raise NotImplementedError("Report formatter not implemented yet.")
