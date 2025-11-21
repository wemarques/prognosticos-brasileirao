"""Minimal smoke test for the prediction helpers."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from analysis.prediction import MatchInputs, format_report, run_prediction


def build_dummy_match() -> MatchInputs:
    """Return a MatchInputs instance with realistic placeholder values."""

    return MatchInputs(
        home_team="Team A",
        away_team="Team B",
        round_number=1,
        kickoff_utc="2025-01-01T18:00:00Z",
        lambda_home=1.4,
        lambda_away=1.1,
        mean_cards=4.5,
        mean_corners=9.0,
        context={"source": "smoke-test"},
        raw_row={},
    )


def main() -> None:
    match = build_dummy_match()
    result = run_prediction(match, n_sim=5_000, seed=42)
    report = format_report(match, result)

    print("=== Smoke Test – Dummy Match ===")
    print(f"{match.home_team} vs {match.away_team}")
    print("p_home_win:", result.get("p_home_win"))
    print("p_draw:", result.get("p_draw"))
    print("p_away_win:", result.get("p_away_win"))
    print("lambda_home:", result.get("lambda_home"))
    print("lambda_away:", result.get("lambda_away"))
    print("\nReport preview:")
    print(f"{report[:400]} ...\n")


if __name__ == "__main__":
    main()

