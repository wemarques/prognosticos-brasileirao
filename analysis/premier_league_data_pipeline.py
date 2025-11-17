"""Premier League CSV → MatchInputs pipeline.

This module converts the static Premier League CSV files into `MatchInputs`
objects that can be consumed by the generic prediction layer
(`analysis.prediction`).
"""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from analysis.prediction import MatchInputs

# Paths -----------------------------------------------------------------------
DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "csv" / "premier_league"
MATCHES_CSV = DATA_DIR / "2025_matches.csv"
TEAMS_CSV = DATA_DIR / "2025_teams.csv"

# Baseline constants ---------------------------------------------------------
PREMIER_AVG_GOALS_PER_MATCH = 2.69
PREMIER_TEAM_AVG_GOALS = PREMIER_AVG_GOALS_PER_MATCH / 2  # per-team baseline
DEFAULT_HOME_XG = 1.65
DEFAULT_AWAY_XG = 1.30
DEFAULT_HOME_XGC = 1.20
DEFAULT_AWAY_XGC = 1.35
DEFAULT_FORM_POINTS = 7.5
DEFAULT_MATCHES_PLAYED = 10
DEFAULT_CARDS_PER_MATCH = 3.8
DEFAULT_CORNERS_PER_MATCH = 10.0


# Public API -----------------------------------------------------------------
def load_premier_round_matches(round_id: int) -> List[MatchInputs]:
    """
    Load all Premier League matches for a given round from the existing CSV files
    and return a list of MatchInputs compatible with run_prediction().
    """
    if not MATCHES_CSV.exists():
        raise FileNotFoundError(f"Premier League matches CSV not found: {MATCHES_CSV}")
    if not TEAMS_CSV.exists():
        raise FileNotFoundError(f"Premier League teams CSV not found: {TEAMS_CSV}")

    team_index = _build_team_index(_load_csv_records(TEAMS_CSV))
    round_rows = _load_round_rows(round_id)

    match_inputs: List[MatchInputs] = []
    for row in round_rows:
        home_team = (row.get("home_team_name") or "").strip()
        away_team = (row.get("away_team_name") or "").strip()

        if not home_team or not away_team:
            # Skip rows with missing mandatory team information
            continue

        home_stats = _build_team_stats(team_index.get(_normalize_team_name(home_team)), is_home=True)
        away_stats = _build_team_stats(team_index.get(_normalize_team_name(away_team)), is_home=False)
        context = _build_context(row)
        context["home_stats"] = home_stats
        context["away_stats"] = away_stats

        pre_match_home_xg = _optional_float(row.get("Home Team Pre-Match xG"))
        pre_match_away_xg = _optional_float(row.get("Away Team Pre-Match xG"))

        lambda_home = _estimate_lambda(
            attack=home_stats.get("xg_for_home"),
            opponent_defense=away_stats.get("xgc_against_away"),
            pre_match_xg=pre_match_home_xg,
            default=DEFAULT_HOME_XG,
        )
        lambda_away = _estimate_lambda(
            attack=away_stats.get("xg_for_away"),
            opponent_defense=home_stats.get("xgc_against_home"),
            pre_match_xg=pre_match_away_xg,
            default=DEFAULT_AWAY_XG,
        )

        mean_cards = (context["lambda_cards_home"] + context["lambda_cards_away"]) / 2.0
        mean_corners = context["lambda_corners"]

        match_inputs.append(
            MatchInputs(
                home_team=home_team,
                away_team=away_team,
                round_number=round_id,
                kickoff_utc=_parse_timestamp(row.get("timestamp"), row.get("date_GMT")),
                lambda_home=lambda_home,
                lambda_away=lambda_away,
                mean_cards=mean_cards,
                mean_corners=mean_corners,
                context=context,
                raw_row=row,
            )
        )

    if not match_inputs:
        raise ValueError(f"No Premier League fixtures found for round {round_id}")

    return match_inputs


# Helpers --------------------------------------------------------------------
def _load_csv_records(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _load_round_rows(round_id: int) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    with MATCHES_CSV.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            row_round = int(_safe_float(row.get("Game Week"), -1))
            if row_round == round_id:
                rows.append(row)
    return rows


def _build_team_index(records: List[Dict[str, str]]) -> Dict[str, Dict[str, str]]:
    index: Dict[str, Dict[str, str]] = {}
    for row in records:
        for key in ("team_name", "common_name"):
            value = row.get(key)
            if value:
                index[_normalize_team_name(value)] = row
    return index


def _build_team_stats(team_row: Optional[Dict[str, str]], is_home: bool) -> Dict[str, float]:
    if not team_row:
        return _default_team_stats(is_home)

    if is_home:
        xg_for = _safe_float(
            team_row.get("xg_for_avg_home"),
            _safe_float(team_row.get("xg_for_avg_overall"), DEFAULT_HOME_XG),
        )
        xgc = _safe_float(
            team_row.get("xg_against_avg_home"),
            _safe_float(team_row.get("xg_against_avg_overall"), DEFAULT_AWAY_XGC),
        )
        goals_scored = _safe_float(
            team_row.get("goals_scored_per_match_home"),
            _safe_float(team_row.get("goals_scored_per_match"), DEFAULT_HOME_XG),
        )
        goals_conceded = _safe_float(
            team_row.get("goals_conceded_per_match_home"),
            _safe_float(team_row.get("goals_conceded_per_match"), DEFAULT_HOME_XGC),
        )
        points_pg = _safe_float(
            team_row.get("points_per_game_home"),
            _safe_float(team_row.get("points_per_game"), DEFAULT_FORM_POINTS / 5),
        )
        matches_played = int(_safe_float(team_row.get("matches_played_home"), DEFAULT_MATCHES_PLAYED))
        xg_key = "xg_for_home"
        xgc_key = "xgc_against_home"
    else:
        xg_for = _safe_float(
            team_row.get("xg_for_avg_away"),
            _safe_float(team_row.get("xg_for_avg_overall"), DEFAULT_AWAY_XG),
        )
        xgc = _safe_float(
            team_row.get("xg_against_avg_away"),
            _safe_float(team_row.get("xg_against_avg_overall"), DEFAULT_HOME_XGC),
        )
        goals_scored = _safe_float(
            team_row.get("goals_scored_per_match_away"),
            _safe_float(team_row.get("goals_scored_per_match"), DEFAULT_AWAY_XG),
        )
        goals_conceded = _safe_float(
            team_row.get("goals_conceded_per_match_away"),
            _safe_float(team_row.get("goals_conceded_per_match"), DEFAULT_AWAY_XGC),
        )
        points_pg = _safe_float(
            team_row.get("points_per_game_away"),
            _safe_float(team_row.get("points_per_game"), DEFAULT_FORM_POINTS / 5),
        )
        matches_played = int(_safe_float(team_row.get("matches_played_away"), DEFAULT_MATCHES_PLAYED))
        xg_key = "xg_for_away"
        xgc_key = "xgc_against_away"

    attack_strength = goals_scored / PREMIER_TEAM_AVG_GOALS if PREMIER_TEAM_AVG_GOALS else 1.0
    defense_strength = goals_conceded / PREMIER_TEAM_AVG_GOALS if PREMIER_TEAM_AVG_GOALS else 1.0

    return {
        xg_key: xg_for,
        xgc_key: xgc,
        "attack_strength": attack_strength,
        "defense_strength": defense_strength,
        "form_points": points_pg * 5,  # approximate last-five form
        "matches_played": matches_played,
        "goals_per_game": goals_scored,
        "goals_conceded_per_game": goals_conceded,
    }


def _build_context(row: Dict[str, Any]) -> Dict[str, Any]:
    avg_cards = _safe_float(row.get("average_cards_per_match_pre_match"), DEFAULT_CARDS_PER_MATCH)
    avg_corners = _safe_float(row.get("average_corners_per_match_pre_match"), DEFAULT_CORNERS_PER_MATCH)

    def _odds(value: Any) -> Optional[float]:
        val = _safe_float(value, 0.0)
        return val if val > 0 else None

    return {
        "round": int(_safe_float(row.get("Game Week"), 0)),
        "status": row.get("status", "SCHEDULED"),
        "venue": row.get("stadium_name") or row.get("home_team_name"),
        "match_type": "normal",
        "distance_km": 0.0,
        "altitude_m": 0.0,
        "lambda_cards_home": max(avg_cards * 0.55, 1.2),
        "lambda_cards_away": max(avg_cards * 0.45, 1.0),
        "lambda_corners": avg_corners,
        "home_pre_match_xg": _safe_float(row.get("Home Team Pre-Match xG"), DEFAULT_HOME_XG),
        "away_pre_match_xg": _safe_float(row.get("Away Team Pre-Match xG"), DEFAULT_AWAY_XG),
        "odds": {
            "home": _odds(row.get("odds_ft_home_team_win")),
            "draw": _odds(row.get("odds_ft_draw")),
            "away": _odds(row.get("odds_ft_away_team_win")),
            "over_15": _odds(row.get("odds_ft_over15")),
            "over_25": _odds(row.get("odds_ft_over25")),
            "btts_yes": _odds(row.get("odds_btts_yes")),
            "btts_no": _odds(row.get("odds_btts_no")),
        },
        "kickoff_label": row.get("date_GMT"),
    }


def _parse_timestamp(timestamp_value: Any, fallback_label: Optional[str] = None) -> datetime:
    if timestamp_value not in (None, "", "N/A"):
        try:
            seconds = int(float(timestamp_value))
            return datetime.fromtimestamp(seconds, tz=timezone.utc)
        except (TypeError, ValueError):
            pass

    if fallback_label:
        cleaned = fallback_label.replace("pm", "PM").replace("am", "AM")
        for fmt in ("%b %d %Y - %I:%M%p", "%b %d %Y - %H:%M%p", "%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(cleaned, fmt).replace(tzinfo=timezone.utc)
            except ValueError:
                continue

    # As a last resort, return "now" so downstream code always has a datetime.
    return datetime.now(timezone.utc)


def _default_team_stats(is_home: bool) -> Dict[str, float]:
    xg_for = DEFAULT_HOME_XG if is_home else DEFAULT_AWAY_XG
    xgc = DEFAULT_AWAY_XGC if is_home else DEFAULT_HOME_XGC
    return {
        ("xg_for_home" if is_home else "xg_for_away"): xg_for,
        ("xgc_against_home" if is_home else "xgc_against_away"): xgc,
        "attack_strength": 1.0,
        "defense_strength": 1.0,
        "form_points": DEFAULT_FORM_POINTS,
        "matches_played": DEFAULT_MATCHES_PLAYED,
        "goals_per_game": xg_for,
        "goals_conceded_per_game": xgc,
    }


def _normalize_team_name(name: str) -> str:
    return name.strip().lower()


def _safe_float(value: Any, default: float) -> float:
    try:
        if value in (None, "", "N/A"):
            return default
        return float(value)
    except (ValueError, TypeError):
        return default


def _optional_float(value: Any) -> Optional[float]:
    try:
        if value in (None, "", "N/A"):
            return None
        return float(value)
    except (ValueError, TypeError):
        return None


def _estimate_lambda(
    attack: Optional[float],
    opponent_defense: Optional[float],
    pre_match_xg: Optional[float],
    default: float,
) -> float:
    """
    Blend team-specific attack metrics with opponent defensive data and, when available,
    the CSV pre-match xG baseline. Keeps values within realistic Poisson bounds.
    """
    base = attack if attack is not None else default
    if opponent_defense is not None:
        base = (base * 0.65) + (opponent_defense * 0.35)
    if pre_match_xg is not None:
        base = (base * 0.7) + (pre_match_xg * 0.3)
    return max(0.2, base)
