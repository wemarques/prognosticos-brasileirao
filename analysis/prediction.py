"""League-agnostic prediction helpers used by the Streamlit UI and pipelines."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

import numpy as np


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


def run_prediction(match: MatchInputs, n_sim: int = 50_000, seed: int | None = None) -> Dict[str, Any]:
    """
    Run a Monte Carlo Poisson simulation to generate league-agnostic forecasts.

    Args:
        match: MatchInputs containing prepared model inputs.
        n_sim: Number of Monte Carlo draws (default: 50k for stability).
        seed: Optional RNG seed for reproducibility.

    Returns:
        Dict with win/draw probabilities, totals, BTTS, expected goals, and metadata.
    """
    if n_sim <= 0:
        raise ValueError("n_sim must be positive")

    rng = np.random.default_rng(seed)
    lambda_home = float(match.lambda_home)
    lambda_away = float(match.lambda_away)

    home_goals = rng.poisson(lam=lambda_home, size=n_sim)
    away_goals = rng.poisson(lam=lambda_away, size=n_sim)
    total_goals = home_goals + away_goals

    p_home_win = float(np.mean(home_goals > away_goals))
    p_draw = float(np.mean(home_goals == away_goals))
    p_away_win = float(np.mean(home_goals < away_goals))
    p_over_2_5 = float(np.mean(total_goals >= 3))
    p_btts = float(np.mean((home_goals >= 1) & (away_goals >= 1)))

    mean_home_goals = float(np.mean(home_goals))
    mean_away_goals = float(np.mean(away_goals))

    return {
        "p_home_win": p_home_win,
        "p_draw": p_draw,
        "p_away_win": p_away_win,
        "p_over_2_5": p_over_2_5,
        "p_btts": p_btts,
        "mean_home_goals": mean_home_goals,
        "mean_away_goals": mean_away_goals,
        "n_sim": n_sim,
    }


def format_report(match: MatchInputs, result: Dict[str, Any]) -> str:
    """
    Produce a textual summary that can be displayed in Streamlit or CLI outputs.
    """

    def pct(value: float, width: int = 5) -> str:
        return f"{value * 100:>{width}.1f}%"

    def tendency() -> str:
        home = result["p_home_win"]
        away = result["p_away_win"]
        draw = result["p_draw"]
        if home >= 0.55:
            return "Favoritismo do mandante"
        if away >= 0.55:
            return "Pressão do visitante"
        if abs(home - away) <= 0.08 and draw >= 0.25:
            return "Jogo equilibrado e propenso a empate"
        if home > away:
            return "Leve preferência pelo mandante"
        return "Leve preferência pelo visitante"

    def market_recommendation() -> str:
        # Edge vs neutral baselines (1X2 = 1/3; Overs = 0.5)
        candidates = [
            ("Vitória do mandante (1)", result["p_home_win"] - (1 / 3)),
            ("Empate (X)", result["p_draw"] - (1 / 3)),
            ("Vitória do visitante (2)", result["p_away_win"] - (1 / 3)),
            ("Over 2.5 gols", result["p_over_2_5"] - 0.5),
            ("Under 2.5 gols", (1 - result["p_over_2_5"]) - 0.5),
        ]
        pick = max(candidates, key=lambda item: item[1])
        if pick[1] <= 0:
            return "Nenhum mercado apresenta vantagem clara."
        return f"Mercado sugerido: {pick[0]} (edge ≈ {pick[1] * 100:+.1f} pp)."

    lines = [
        f"{match.home_team} vs {match.away_team} – Round {match.round_number}",
        "",
        "Probabilidades:",
        f"  • Mandante: {pct(result['p_home_win'])}",
        f"  • Empate:   {pct(result['p_draw'])}",
        f"  • Visitante:{pct(result['p_away_win'])}",
        f"  • Over 2.5: {pct(result['p_over_2_5'])}",
        f"  • BTTS:     {pct(result['p_btts'])}",
        "",
        "Expected Goals:",
        f"  • λ_home: {match.lambda_home:.2f}",
        f"  • λ_away: {match.lambda_away:.2f}",
        "",
        "Prognóstico – Resumo Final:",
        f"  • Tendência: {tendency()}",
        f"  • {market_recommendation()}",
        "  • Faixa de confiança: ±5 pp",
    ]

    return "\n".join(lines)
