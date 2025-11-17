"""League-agnostic prediction helpers used by the Streamlit UI and pipelines."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any, Dict, Optional

import numpy as np

DEFAULT_HOME_LAMBDA = 1.45
DEFAULT_AWAY_LAMBDA = 1.20
MIN_LAMBDA = 0.05
MAX_LAMBDA = 5.0
TOP_SCORELINES = 5


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


def _coerce_float(value: Any) -> Optional[float]:
    try:
        val = float(value)
    except (TypeError, ValueError):
        return None
    if not np.isfinite(val):
        return None
    return val


def _coalesce_float(*values: Any, positive: bool = False) -> Optional[float]:
    for value in values:
        if positive:
            candidate = _coerce_float(value)
            if candidate is not None and candidate > 0:
                return candidate
        else:
            candidate = _coerce_float(value)
            if candidate is not None:
                return candidate
    return None


def _resolve_lambda(match: MatchInputs, side: str) -> float:
    """
    Attempt to retrieve a positive lambda value for the given side, falling back
    to contextual league defaults when explicit values are missing.
    """

    side_key = "home" if side == "home" else "away"
    context = getattr(match, "context", {}) or {}
    raw_row = getattr(match, "raw_row", {}) or {}
    expected = context.get("expected_goals") or {}

    candidates = [
        getattr(match, f"lambda_{side}", None),
        (expected.get("model") or {}).get(side_key),
        (expected.get("pre_match") or {}).get(side_key),
    ]

    pre_match_xg = context.get("pre_match_xg")
    if isinstance(pre_match_xg, dict):
        candidates.append(pre_match_xg.get(side_key))

    candidates.extend(
        [
            context.get(f"lambda_{side}"),
            context.get(f"{side}_lambda"),
        ]
    )

    lambdas_bucket = context.get("lambdas")
    if isinstance(lambdas_bucket, dict):
        candidates.append(lambdas_bucket.get(side_key))

    if isinstance(raw_row, dict):
        for key in (
            f"{side_key}_lambda",
            f"lambda_{side_key}",
            f"{side_key}_xg",
            f"{side_key}_expected_goals",
        ):
            if key in raw_row:
                candidates.append(raw_row.get(key))

    default_value = DEFAULT_HOME_LAMBDA if side == "home" else DEFAULT_AWAY_LAMBDA
    lambda_value = _coalesce_float(*candidates, positive=True)
    if lambda_value is None:
        lambda_value = default_value

    return float(min(MAX_LAMBDA, max(MIN_LAMBDA, lambda_value)))


def _match_time_label(match: MatchInputs) -> Optional[str]:
    if hasattr(match, "kickoff_str") and getattr(match, "kickoff_str"):
        return str(getattr(match, "kickoff_str"))

    context = getattr(match, "context", {}) or {}
    if context.get("kickoff_label"):
        return str(context["kickoff_label"])

    kickoff_value = getattr(match, "kickoff_utc", None)
    if hasattr(kickoff_value, "strftime"):
        return kickoff_value.strftime("%d %b %Y %H:%M UTC")
    if kickoff_value:
        return str(kickoff_value)
    return None


def _trend_summary(
    p_home: float, p_draw: float, p_away: float, home_team: str, away_team: str
) -> tuple[str, str]:
    dominance_threshold = 0.07
    if p_home - max(p_draw, p_away) >= dominance_threshold:
        return (
            "mandante",
            f"{home_team} lidera o modelo ({p_home*100:.1f}% vs {p_away*100:.1f}% do visitante).",
        )
    if p_away - max(p_draw, p_home) >= dominance_threshold:
        return (
            "visitante",
            f"{away_team} aparece como favorito ({p_away*100:.1f}%) fora de casa.",
        )
    return (
        "equilibrado",
        "Distribuição equilibrada entre 1X2; atenção ao peso do empate "
        f"({p_draw*100:.1f}%).",
    )


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
    lambda_home = _resolve_lambda(match, "home")
    lambda_away = _resolve_lambda(match, "away")

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
    clean_sheet_home = float(np.mean(away_goals == 0))
    clean_sheet_away = float(np.mean(home_goals == 0))

    score_counter = Counter(zip(home_goals.tolist(), away_goals.tolist()))
    scoreline_top = [
        {"score": f"{hg}-{ag}", "probability": count / n_sim}
        for (hg, ag), count in score_counter.most_common(TOP_SCORELINES)
    ]

    result = {
        "p_home_win": p_home_win,
        "p_draw": p_draw,
        "p_away_win": p_away_win,
        "p_over_2_5": p_over_2_5,
        "p_under_2_5": float(1.0 - p_over_2_5),
        "p_btts": p_btts,
        "p_clean_sheet_home": clean_sheet_home,
        "p_clean_sheet_away": clean_sheet_away,
        "lambda_home": lambda_home,
        "lambda_away": lambda_away,
        "exp_goals_home": mean_home_goals,
        "exp_goals_away": mean_away_goals,
        "exp_goals_total": mean_home_goals + mean_away_goals,
        "scoreline_top": scoreline_top,
        "probabilities": {
            "1x2": {
                "home": p_home_win,
                "draw": p_draw,
                "away": p_away_win,
            },
            "totals": {
                "over_2_5": p_over_2_5,
                "under_2_5": float(1.0 - p_over_2_5),
            },
            "btts": {
                "yes": p_btts,
                "no": float(1.0 - p_btts),
            },
        },
        "n_sim": n_sim,
        "seed": seed,
    }

    return result


def format_report(match: MatchInputs, result: Dict[str, Any]) -> str:
    """
    Produce a Markdown summary consumed by Streamlit and CLI outputs.
    """

    def pct(value: float) -> str:
        return f"{value * 100:.1f}%"

    home_team = getattr(match, "home_team", "Mandante")
    away_team = getattr(match, "away_team", "Visitante")
    round_label = getattr(match, "round_number", None)
    kickoff_label = _match_time_label(match)

    p_home = float(result.get("p_home_win", 0.0))
    p_draw = float(result.get("p_draw", 0.0))
    p_away = float(result.get("p_away_win", 0.0))
    p_over = float(result.get("p_over_2_5", 0.0))
    p_btts = float(result.get("p_btts", 0.0))

    exp_home = _coalesce_float(
        result.get("exp_goals_home"),
        result.get("mean_home_goals"),
        result.get("lambda_home"),
        getattr(match, "lambda_home", None),
    )
    exp_away = _coalesce_float(
        result.get("exp_goals_away"),
        result.get("mean_away_goals"),
        result.get("lambda_away"),
        getattr(match, "lambda_away", None),
    )
    exp_total = (
        _coerce_float(result.get("exp_goals_total"))
        or (exp_home + exp_away if exp_home is not None and exp_away is not None else None)
    )

    lambda_home = _coalesce_float(result.get("lambda_home"), getattr(match, "lambda_home", None))
    lambda_away = _coalesce_float(result.get("lambda_away"), getattr(match, "lambda_away", None))
    n_sim = result.get("n_sim")

    trend_key, trend_text = _trend_summary(p_home, p_draw, p_away, home_team, away_team)

    scoreline_top = result.get("scoreline_top") or []
    top_score_line = ""
    if scoreline_top:
        top_item = scoreline_top[0]
        top_score_line = f"- Placar mais provável: **{top_item['score']}** ({pct(top_item['probability'])})"

    header_meta: list[str] = []
    if round_label is not None:
        header_meta.append(f"Rodada {round_label}")
    if kickoff_label:
        header_meta.append(str(kickoff_label))

    lines = [
        f"### {home_team} vs {away_team}",
    ]
    if header_meta:
        lines.append(f"*{' · '.join(header_meta)}*")
    lines.append("")

    lines.append("#### Probabilidades 1X2")
    lines.append(f"- 1 ({home_team}): **{pct(p_home)}**")
    lines.append(f"- X (Empate): **{pct(p_draw)}**")
    lines.append(f"- 2 ({away_team}): **{pct(p_away)}**")
    lines.append(f"*Over 2.5: {pct(p_over)} · BTTS Sim: {pct(p_btts)}*")
    lines.append("")

    lines.append("#### Expected Goals")
    lines.append(f"- {home_team}: **{exp_home:.2f}**" if exp_home is not None else f"- {home_team}: n/d")
    lines.append(f"- {away_team}: **{exp_away:.2f}**" if exp_away is not None else f"- {away_team}: n/d")
    if exp_total is not None:
        lines.append(f"- Total: **{exp_total:.2f}**")
    lines.append("")

    lines.append("#### Tendência Geral")
    lines.append(f"- Classificação: **{trend_key.capitalize()}**")
    lines.append(f"- Leitura: {trend_text}")
    if top_score_line:
        lines.append(top_score_line)
    lines.append("")

    lines.append("#### Modelo")
    if n_sim:
        lines.append(f"- Simulações (n_sim): **{int(n_sim):,}**")
    if lambda_home is not None and lambda_away is not None:
        lines.append(
            f"- λ mandante / visitante: **{lambda_home:.2f} · {lambda_away:.2f}**"
        )
    else:
        if lambda_home is not None:
            lines.append(f"- λ mandante: **{lambda_home:.2f}**")
        if lambda_away is not None:
            lines.append(f"- λ visitante: **{lambda_away:.2f}**")

    lines.append("- Cobertura: ±5 p.p. para probabilidades 1X2")

    return "\n".join(lines)
