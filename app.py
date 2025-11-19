import os
from datetime import datetime
from pathlib import Path
from typing import Literal, Any

import pandas as pd
import streamlit as st

from ui.league_selector import render_league_selector, get_league_info
from data.collectors.hybrid_collector import HybridDataCollector
from utils.leagues_config import get_api_config
from collectors.fixtures_collector import FixturesCollector
from collectors.teams_collector import get_teams_list
from modules.roi.kelly_criterion import KellyCriterion
from modules.roi.roi_simulator import ROISimulator
from leagues.league_registry import LeagueRegistry
from models.dixon_coles import DixonColesModel
from analysis.premier_league_data_pipeline import load_premier_round_matches
from analysis.prediction import run_prediction, format_report, MatchInputs

st.set_page_config(
    page_title="Prognósticos – Premier League & Brasileirão",
    page_icon="⚽",
    layout="wide",
)

THEME = {
    "bg_page": "#020617",
    "bg_card": "#0b1120",
    "bg_card_soft": "#020617",
    "border_soft": "#1f2937",
    "primary": "#38bdf8",
    "success": "#22c55e",
    "danger": "#f97316",
    "text_main": "#e5e7eb",
    "text_muted": "#9ca3af",
    "accent": "#facc15",
}

BASE_DIR = Path(__file__).resolve().parent
BR_DATA_DIR = BASE_DIR / "data" / "csv" / "brasileirao"
BR_MATCHES_CSV = BR_DATA_DIR / "2025_matches.csv"

# Fallback averages when CSV rows are missing richer context for Brasileirão fixtures.
DEFAULT_BR_HOME_LAMBDA = 1.45
DEFAULT_BR_AWAY_LAMBDA = 1.15
DEFAULT_BR_CARDS = 4.5
DEFAULT_BR_CORNERS = 9.2

st.markdown(
    f"""
    <style>
    body {{
        background: {THEME["bg_page"]};
    }}

    .match-card {{
        background: linear-gradient(135deg, {THEME["bg_card"]}, {THEME["bg_card_soft"]});
        border-radius: 18px;
        border: 1px solid {THEME["border_soft"]};
        padding: 1.1rem 1.3rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 18px 35px rgba(0,0,0,0.45);
    }}

    .match-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.7rem;
    }}

    .match-title {{
        font-size: 1.05rem;
        font-weight: 600;
        color: {THEME["text_main"]};
    }}

    .match-subtitle {{
        font-size: 0.78rem;
        color: {THEME["text_muted"]};
    }}

    .badge-trend {{
        padding: 0.15rem 0.6rem;
        border-radius: 999px;
        font-size: 0.7rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
    }}

    .badge-green {{
        background: rgba(34,197,94,0.16);
        color: {THEME["success"]};
    }}

    .badge-red {{
        background: rgba(239,68,68,0.16);
        color: #f97373;
    }}

    .badge-blue {{
        background: rgba(56,189,248,0.16);
        color: {THEME["primary"]};
    }}

    .pill-metric {{
        font-size: 0.76rem;
        color: {THEME["text_muted"]};
        margin-bottom: 0.15rem;
    }}

    .pill-metric strong {{
        color: {THEME["text_main"]};
    }}

    .metric-label {{
        font-size: 0.7rem;
        color: {THEME["text_muted"]};
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}

    .metric-value {{
        font-size: 0.95rem;
        font-weight: 600;
        color: {THEME["text_main"]};
    }}

    .ev-positive {{
        color: {THEME["success"]};
        font-weight: 600;
    }}

    .ev-negative {{
        color: {THEME["danger"]};
        font-weight: 500;
    }}

    .section-title {{
        font-size: 1.1rem;
        font-weight: 700;
        color: {THEME["text_main"]};
        margin: 0.4rem 0 0.3rem 0;
    }}

    .section-sub {{
        font-size: 0.8rem;
        color: {THEME["text_muted"]};
        margin-bottom: 0.6rem;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner="Carregando rodada da Premier League...")
def cached_load_premier_round_matches(round_number: int):
    return load_premier_round_matches(round_number)


@st.cache_data(show_spinner="Executando simulações de partida...")
def cached_run_prediction(match, n_sim: int):
    return run_prediction(match, n_sim=n_sim)

@st.cache_data(show_spinner="Carregando rodada do Brasileirão...")
def cached_load_brasileirao_round_matches(round_number: int):
    return load_brasileirao_round_matches(round_number)

@st.cache_data(show_spinner="Lendo rodadas disponíveis do Brasileirão...")
def cached_brasileirao_rounds() -> list[int]:
    if not BR_MATCHES_CSV.exists():
        return []

    try:
        df = pd.read_csv(BR_MATCHES_CSV, usecols=["round"])
    except ValueError:
        df = pd.read_csv(BR_MATCHES_CSV)

    round_series = pd.to_numeric(df.get("round"), errors="coerce").dropna()
    rounds = sorted({int(value) for value in round_series.tolist()})
    return rounds

Trend = Literal["home", "draw", "away"]


def normalize_default_odd(value: float | None) -> float:
    if value is None or value < 1.01:
        return 1.01
    return float(value)


def compute_ev(prob: float, odd_value: float) -> float | None:
    if odd_value <= 1:
        return None
    return prob * odd_value - 1


def compute_kelly_raw(prob: float, odd_value: float) -> float | None:
    if odd_value <= 1:
        return None
    edge_val = prob * odd_value - 1
    if edge_val <= 0:
        return None
    return edge_val / (odd_value - 1)


def get_trend(p_home: float, p_draw: float, p_away: float) -> Trend:
    probs = {"home": p_home, "draw": p_draw, "away": p_away}
    return max(probs, key=probs.get)


def render_trend_badge(p_home: float, p_draw: float, p_away: float) -> str:
    trend = get_trend(p_home, p_draw, p_away)
    if trend == "home":
        label = "Tendência: Mandante"
        cls = "badge-green"
        icon = "🏠"
    elif trend == "away":
        label = "Tendência: Visitante"
        cls = "badge-red"
        icon = "✈️"
    else:
        label = "Tendência: Jogo Equilibrado"
        cls = "badge-blue"
        icon = "⚖️"

    return f'<span class="badge-trend {cls}">{icon} {label}</span>'


def render_market_line(
    label: str,
    fair_odds: float | None,
    book_odds: float | None,
    ev: float | None,
    kelly: float | None,
) -> None:
    """
    Renders a single horizontal market row (label + fair odds + book odds + EV/Kelly)
    inside the current Streamlit container.
    """
    col_m1, col_m2, col_m3, col_m4 = st.columns([1.4, 0.9, 0.9, 0.9])

    with col_m1:
        st.markdown(
            f'<span class="metric-label">{label}</span>',
            unsafe_allow_html=True,
        )

    with col_m2:
        if fair_odds:
            st.markdown(
                f'<div class="metric-value">{fair_odds:.2f}</div>'
                f'<div class="metric-label">Odd Justa</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="metric-label">Odd Justa</div>',
                unsafe_allow_html=True,
            )

    with col_m3:
        if book_odds:
            st.markdown(
                f'<div class="metric-value">{book_odds:.2f}</div>'
                f'<div class="metric-label">Casa</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="metric-label">Casa</div>',
                unsafe_allow_html=True,
            )

    with col_m4:
        if ev is not None and kelly is not None:
            cls = "ev-positive" if ev >= 0 else "ev-negative"
            st.markdown(
                f"""
                <div class="{cls}">{ev:+.1f}%</div>
                <div class="metric-label">EV · Kelly {kelly*100:.1f}%</div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="metric-label">EV · Kelly</div>',
                unsafe_allow_html=True,
            )


def render_match_card(match, result: dict, odds_ctx: dict, bankroll: float) -> None:
    """
    This is a skeleton for the match card UI.
    In the next step we will wire it to the actual main loop and
    map the correct keys from `result` and `match`.
    """
    # Try to read model probabilities. If the actual keys differ,
    # we will adjust in the next iteration.
    p_home = float(result.get("p_home_win", 0.0))
    p_draw = float(result.get("p_draw", 0.0))
    p_away = float(result.get("p_away_win", 0.0))

    # Basic fair odds from probabilities (we will refine as needed)
    fair_home = 1.0 / p_home if p_home > 0 else None
    fair_draw = 1.0 / p_draw if p_draw > 0 else None
    fair_away = 1.0 / p_away if p_away > 0 else None

    # User-provided odds for 1X2
    odd_home = odds_ctx.get("home")
    odd_draw = odds_ctx.get("draw")
    odd_away = odds_ctx.get("away")

    # Placeholders for EV and Kelly – we will hook in real values
    # once we confirm the structure of `result`.
    edge_home = result.get("edge_home")
    edge_draw = result.get("edge_draw")
    edge_away = result.get("edge_away")

    kelly_home = result.get("kelly_home")
    kelly_draw = result.get("kelly_draw")
    kelly_away = result.get("kelly_away")

    stake_home = bankroll * kelly_home if kelly_home else 0
    stake_draw = bankroll * kelly_draw if kelly_draw else 0
    stake_away = bankroll * kelly_away if kelly_away else 0

    trend_badge_html = render_trend_badge(p_home, p_draw, p_away)

    # Start card container
    st.markdown('<div class="match-card">', unsafe_allow_html=True)

    # Header: teams + league/round + kickoff + trend badge
    col_h1, col_h2 = st.columns([3, 1.7])
    with col_h1:
        # We will assume match has attributes like home_team, away_team,
        # league_name, round_name, kickoff_str; if not, we will adapt.
        home_name = getattr(match, "home_team", "Mandante")
        away_name = getattr(match, "away_team", "Visitante")
        league_name = getattr(match, "league_name", "")
        round_name = getattr(match, "round_name", "")
        kickoff_str = getattr(match, "kickoff_str", "")
        n_simulations = result.get("n_sim")
        sims_label = f" · {n_simulations:,} sims" if n_simulations else ""

        st.markdown(
            f"""
            <div class="match-header">
                <div>
                    <div class="match-title">
                        {home_name} vs {away_name}
                    </div>
                    <div class="match-subtitle">
                        {league_name} · {round_name} · {kickoff_str}{sims_label}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_h2:
        st.markdown(trend_badge_html, unsafe_allow_html=True)

    # Main 3-column layout: probabilities, 1X2 market, stakes
    col1, col2, col3 = st.columns([1.5, 2.2, 1.7])

    with col1:
        st.markdown(
            '<div class="pill-metric">📊 Probabilidades do modelo</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
            <div class="pill-metric"><strong>Mandante</strong> {p_home*100:.1f}%</div>
            <div class="pill-metric"><strong>Empate</strong> {p_draw*100:.1f}%</div>
            <div class="pill-metric"><strong>Visitante</strong> {p_away*100:.1f}%</div>
            """,
            unsafe_allow_html=True,
        )

        lambda_home = result.get("lambda_home")
        lambda_away = result.get("lambda_away")
        if lambda_home is not None and lambda_away is not None:
            st.markdown(
                f"""
                <div class="pill-metric">
                    ⚽ <strong>xG modelo</strong> {lambda_home:.2f} · {lambda_away:.2f}
                </div>
                """,
                unsafe_allow_html=True,
            )

    with col2:
        st.markdown(
            '<div class="metric-label">Mercado 1X2 – Odds, Odd Justa, EV & Kelly</div>',
            unsafe_allow_html=True,
        )
        render_market_line(
            label="1 (Mandante)",
            fair_odds=fair_home,
            book_odds=odd_home,
            ev=edge_home,
            kelly=kelly_home,
        )
        render_market_line(
            label="X (Empate)",
            fair_odds=fair_draw,
            book_odds=odd_draw,
            ev=edge_draw,
            kelly=kelly_draw,
        )
        render_market_line(
            label="2 (Visitante)",
            fair_odds=fair_away,
            book_odds=odd_away,
            ev=edge_away,
            kelly=kelly_away,
        )

    with col3:
        st.markdown(
            '<div class="metric-label">Stake (Kelly Fractional)</div>',
            unsafe_allow_html=True,
        )
        if stake_home > 0:
            st.markdown(
                f'<div class="pill-metric">🏠 1 (Mandante): <strong>R$ {stake_home:.2f}</strong></div>',
                unsafe_allow_html=True,
            )
        if stake_draw > 0:
            st.markdown(
                f'<div class="pill-metric">➖ X (Empate): <strong>R$ {stake_draw:.2f}</strong></div>',
                unsafe_allow_html=True,
            )
        if stake_away > 0:
            st.markdown(
                f'<div class="pill-metric">✈️ 2 (Visitante): <strong>R$ {stake_away:.2f}</strong></div>',
                unsafe_allow_html=True,
            )

    with st.expander("🔍 Análise detalhada & mercados auxiliares"):
        try:
            report_text = format_report(match, result)
            st.markdown(report_text)
        except Exception:
            st.write(
                "Não foi possível gerar o relatório detalhado para esta partida."
            )

    st.markdown("</div>", unsafe_allow_html=True)


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, str):
        cleaned = value.strip()
        if not cleaned:
            return None
        value = cleaned.replace(",", ".")
    if pd.isna(value):
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def _mean_or_default(values: list[float | None], default: float) -> float:
    valid = [v for v in values if v is not None]
    if not valid:
        return default
    return sum(valid) / len(valid)


def _parse_brasileirao_datetime(label: str):
    if not label:
        return None
    cleaned = str(label).strip()
    if not cleaned:
        return None
    iso_candidate = cleaned.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(iso_candidate)
    except ValueError:
        pass
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(cleaned, fmt)
        except ValueError:
            continue
    return cleaned


def load_brasileirao_round_matches(round_number: int) -> list[MatchInputs]:
    """
    Carrega partidas do Brasileirão a partir de data/csv/brasileirao/2025_matches.csv.

    O CSV é gerado por scripts/update_csv_from_api.py e contém as colunas:
        round, home_team, away_team, kickoff_utc, lambda_home, lambda_away,
        mean_cards, mean_corners, além de metadados opcionais.

    Para manter compatibilidade com versões antigas, o loader também aceita
    colunas legadas (home_xg, home_cards etc).
    """
    if not BR_MATCHES_CSV.exists():
        raise FileNotFoundError(f"Brasileirão matches CSV não encontrado: {BR_MATCHES_CSV}")

    df = pd.read_csv(BR_MATCHES_CSV)
    df["round"] = pd.to_numeric(df.get("round"), errors="coerce")
    if "round_number" in df.columns:
        legacy_round = pd.to_numeric(df["round_number"], errors="coerce")
        df["round"] = df["round"].fillna(legacy_round)

    target_round = int(round_number)
    round_df = df[df["round"] == target_round]

    match_inputs: list[MatchInputs] = []
    for _, row in round_df.iterrows():
        home_team = str(row.get("home_team", "")).strip()
        away_team = str(row.get("away_team", "")).strip()
        if not home_team or not away_team:
            continue

        lambda_home = (
            _to_float(row.get("lambda_home"))
            or _to_float(row.get("home_xg"))
            or DEFAULT_BR_HOME_LAMBDA
        )
        lambda_away = (
            _to_float(row.get("lambda_away"))
            or _to_float(row.get("away_xg"))
            or DEFAULT_BR_AWAY_LAMBDA
        )

        mean_cards = (
            _to_float(row.get("mean_cards"))
            or _mean_or_default(
                [_to_float(row.get("home_cards")), _to_float(row.get("away_cards"))],
                DEFAULT_BR_CARDS,
            )
        )
        mean_corners = (
            _to_float(row.get("mean_corners"))
            or _mean_or_default(
                [_to_float(row.get("home_corners")), _to_float(row.get("away_corners"))],
                DEFAULT_BR_CORNERS,
            )
        )

        kickoff_source = row.get("kickoff_utc") or row.get("kickoff") or row.get("date")
        kickoff_dt = _parse_brasileirao_datetime(kickoff_source)
        kickoff_value = kickoff_dt if isinstance(kickoff_dt, datetime) else kickoff_source
        if isinstance(kickoff_value, datetime):
            kickoff_label = kickoff_value.strftime("%d %b %Y %H:%M (UTC)")
        else:
            kickoff_label = str(kickoff_value or "")

        context = {
            "round": target_round,
            "status": row.get("status", "SCHEDULED"),
            "league": "Brasileirão Série A",
            "kickoff_label": kickoff_label,
            "lambda_cards_home": max(mean_cards * 0.55, 1.0),
            "lambda_cards_away": max(mean_cards * 0.45, 0.8),
            "lambda_corners": mean_corners,
            "odds": row.get("odds") or {},
            "fixture_metadata": {
                "match_id": row.get("match_id") or row.get("id"),
                "raw_stage": row.get("stage"),
            },
        }

        match_inputs.append(
            MatchInputs(
                home_team=home_team,
                away_team=away_team,
                round_number=target_round,
                kickoff_utc=kickoff_value,
                lambda_home=lambda_home,
                lambda_away=lambda_away,
                mean_cards=mean_cards,
                mean_corners=mean_corners,
                context=context,
                raw_row=row.to_dict(),
            )
        )

    if not match_inputs:
        raise ValueError(f"Nenhuma partida do Brasileirão encontrada para a rodada {round_number}")

    return match_inputs

st.sidebar.header("⚙️ Configurações")

available_leagues = LeagueRegistry.get_available_leagues()
selected_league_key = st.sidebar.selectbox(
    "Liga:",
    options=list(available_leagues.keys()),
    format_func=lambda x: available_leagues[x]
)
selected_round = st.sidebar.selectbox("Rodada:", list(range(1, 39)))
available_rounds_br = cached_brasileirao_rounds()
if not available_rounds_br:
    available_rounds_br = list(range(1, 39))
selected_round_br = st.sidebar.selectbox(
    "Rodada Brasileirão:",
    options=available_rounds_br,
    index=0,
)
n_sim = st.sidebar.slider("Simulações (n_sim)", 5000, 100000, 50000, step=5000)
st.sidebar.subheader("💰 Gestão de Banca")
bankroll = st.sidebar.number_input(
    "Banca (R$)",
    min_value=10.0,
    value=100.0,
    step=10.0,
    help="Valor de referência para cálculo de stake via Kelly Fractional.",
)
kelly_fraction = st.sidebar.slider(
    "Fração de Kelly",
    min_value=0.1,
    max_value=0.5,
    value=0.25,
    step=0.05,
    help="Fração do Kelly Criterion a usar (0.25 = Quarter Kelly, conservador)"
)

try:
    model = DixonColesModel(selected_league_key)
    st.sidebar.success(f"✅ {model.league.name} carregado")
except Exception as e:
    st.sidebar.error(f"❌ Erro ao carregar liga: {e}")
    st.stop()

def display_stake_calculation(probabilities, bankroll, kelly_fraction):
    """Display Kelly Criterion stake calculation for Over 2.5 goals"""
    if probabilities and 'goals' in probabilities and 'over_2.5' in probabilities['goals']:
        probability = probabilities['goals']['over_2.5'] / 100
        odds = 2.10
        
        kelly = KellyCriterion(bankroll, kelly_fraction)
        result = kelly.calculate_stake(probability, odds)
        
        if result['is_value_bet']:
            st.success("💎 VALUE BET IDENTIFICADO!")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("💰 Stake Recomendado", f"R$ {result['stake']:.2f}")
            with col2:
                st.metric("📊 Edge", f"{result['edge']:.2f}%")
            with col3:
                st.metric("📈 Valor Esperado", f"R$ {result['expected_value']:.2f}")
            
            st.info(f"ℹ️ Kelly: {result['kelly_percentage']:.2f}% da banca | Odds: {odds}")
        else:
            st.warning("⚠️ Não é uma value bet (edge negativo)")

def display_roi_simulation(bankroll, kelly_fraction):
    """Display ROI simulation section with adjustable parameters and Monte Carlo scenarios"""
    with st.expander("📊 Simulação de ROI (Monte Carlo)", expanded=False):
        st.subheader("Simular Retorno sobre Investimento")
        st.info("💡 Simulação com 1000 iterações Monte Carlo para análise estatística")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            avg_bets_per_week = st.number_input(
                "Apostas por Semana",
                min_value=1,
                max_value=50,
                value=5,
                step=1,
                help="Número médio de apostas por semana",
                key="roi_bets_per_week"
            )
        with col2:
            avg_edge = st.number_input(
                "Edge Médio (%)",
                min_value=0.0,
                max_value=20.0,
                value=8.0,
                step=0.5,
                help="Edge médio sobre a casa de apostas",
                key="roi_avg_edge"
            ) / 100
        with col3:
            win_rate = st.number_input(
                "Win Rate (%)",
                min_value=30.0,
                max_value=80.0,
                value=55.0,
                step=1.0,
                help="Taxa de acerto esperada",
                key="roi_win_rate"
            ) / 100
        
        if st.button("🎲 Simular ROI", key="simulate_roi_button"):
            with st.spinner("Executando 1000 simulações Monte Carlo..."):
                try:
                    simulator = ROISimulator(bankroll, kelly_fraction)
                    results = simulator.simulate_multiple_periods(avg_bets_per_week, avg_edge, win_rate)
                    
                    st.markdown("### Resultados da Simulação Monte Carlo")
                    
                    for period_key, period_name in [('4_weeks', '30 dias'), ('8_weeks', '60 dias'), ('12_weeks', '90 dias')]:
                        st.markdown(f"#### {period_name} ({results[period_key]['days']} dias)")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.markdown("**😰 Pessimista (10%)**")
                            st.metric(
                                "Banca Final",
                                f"R$ {results[period_key]['scenarios']['pessimistic']['final_bankroll']:.2f}",
                                f"{results[period_key]['scenarios']['pessimistic']['roi_percent']:+.2f}%"
                            )
                        
                        with col2:
                            st.markdown("**😐 Realista (50%)**")
                            st.metric(
                                "Banca Final",
                                f"R$ {results[period_key]['scenarios']['realistic']['final_bankroll']:.2f}",
                                f"{results[period_key]['scenarios']['realistic']['roi_percent']:+.2f}%"
                            )
                        
                        with col3:
                            st.markdown("**😄 Otimista (90%)**")
                            st.metric(
                                "Banca Final",
                                f"R$ {results[period_key]['scenarios']['optimistic']['final_bankroll']:.2f}",
                                f"{results[period_key]['scenarios']['optimistic']['roi_percent']:+.2f}%"
                            )
                        
                        st.markdown("---")
                    
                    st.success(f"✅ Simulação completa: {avg_bets_per_week} apostas/semana, {avg_edge*100:.1f}% edge, {win_rate*100:.1f}% win rate")
                
                except Exception as e:
                    st.error(f"❌ Erro na simulação: {e}")

# Seletor de liga
selected_league = render_league_selector()
league_info = get_league_info(selected_league)

# Exibir informações da liga
st.title(f"{league_info['icon']} {league_info['name']}")

# Criar collector híbrido (CSV + Odds API)
odds_api_key = os.getenv('ODDS_API_KEY')
collector = HybridDataCollector(league_key=selected_league, odds_api_key=odds_api_key)

if selected_league == 'brasileirao':
    fixtures_collector = FixturesCollector(league_id=2013)
else:
    fixtures_collector = None

if selected_league == 'premier_league':
    st.subheader(f"Premier League – Rodada {selected_round}")
    try:
        matches = cached_load_premier_round_matches(selected_round)
    except Exception as pipeline_error:
        st.error(f"❌ Erro ao carregar rodada: {pipeline_error}")
        matches = []

    total_matches = 0
    total_value_bets = 0
    total_stake_suggested = 0.0
    ev_values_for_avg: list[float] = []

    if matches:
        cols = st.columns(2)
        for idx, match in enumerate(matches):
            if idx != 0 and idx % 2 == 0:
                cols = st.columns(2)

            col = cols[idx % 2]
            context = match.context or {}
            odds_defaults = context.get("odds") or {}

            default_home = normalize_default_odd(odds_defaults.get("home"))
            default_draw = normalize_default_odd(odds_defaults.get("draw"))
            default_away = normalize_default_odd(odds_defaults.get("away"))

            with col:
                odds_col1, odds_col2, odds_col3 = st.columns(3)

                with odds_col1:
                    odd_home = st.number_input(
                        f"Odd Mandante – {idx+1}",
                        value=default_home,
                        min_value=1.01,
                        step=0.01,
                        key=f"odd_home_{selected_round}_{idx}"
                    )

                with odds_col2:
                    odd_draw = st.number_input(
                        f"Odd Empate – {idx+1}",
                        value=default_draw,
                        min_value=1.01,
                        step=0.01,
                        key=f"odd_draw_{selected_round}_{idx}"
                    )

                with odds_col3:
                    odd_away = st.number_input(
                        f"Odd Visitante – {idx+1}",
                        value=default_away,
                        min_value=1.01,
                        step=0.01,
                        key=f"odd_away_{selected_round}_{idx}"
                    )

                odds_ctx = {
                    "home": odd_home,
                    "draw": odd_draw,
                    "away": odd_away,
                }

                try:
                    result = cached_run_prediction(match, n_sim=n_sim)
                    p_home = result["p_home_win"]
                    p_draw = result["p_draw"]
                    p_away = result["p_away_win"]

                    ev_home = compute_ev(p_home, odd_home)
                    ev_draw = compute_ev(p_draw, odd_draw)
                    ev_away = compute_ev(p_away, odd_away)

                    kelly_home_raw = compute_kelly_raw(p_home, odd_home)
                    kelly_draw_raw = compute_kelly_raw(p_draw, odd_draw)
                    kelly_away_raw = compute_kelly_raw(p_away, odd_away)

                    kelly_home_fraction = kelly_home_raw * kelly_fraction if kelly_home_raw is not None else None
                    kelly_draw_fraction = kelly_draw_raw * kelly_fraction if kelly_draw_raw is not None else None
                    kelly_away_fraction = kelly_away_raw * kelly_fraction if kelly_away_raw is not None else None

                    result["edge_home"] = ev_home * 100 if ev_home is not None else None
                    result["edge_draw"] = ev_draw * 100 if ev_draw is not None else None
                    result["edge_away"] = ev_away * 100 if ev_away is not None else None

                    result["kelly_home"] = kelly_home_fraction
                    result["kelly_draw"] = kelly_draw_fraction
                    result["kelly_away"] = kelly_away_fraction

                    result["lambda_home"] = getattr(match, "lambda_home", None)
                    result["lambda_away"] = getattr(match, "lambda_away", None)

                    league_name = league_info.get("name", "Premier League")
                    round_label = f"Rodada {selected_round}"
                    kickoff_value = getattr(match, "kickoff_utc", "")
                    if hasattr(kickoff_value, "strftime"):
                        kickoff_label = kickoff_value.strftime("%d %b %Y %H:%M UTC")
                    else:
                        kickoff_label = str(kickoff_value) if kickoff_value else ""

                    setattr(match, "league_name", league_name)
                    setattr(match, "round_name", round_label)
                    setattr(match, "kickoff_str", kickoff_label)

                    total_matches += 1
                    for ev_percent, kelly_val in [
                        (result.get("edge_home"), result.get("kelly_home")),
                        (result.get("edge_draw"), result.get("kelly_draw")),
                        (result.get("edge_away"), result.get("kelly_away")),
                    ]:
                        if (
                            ev_percent is not None
                            and kelly_val is not None
                            and ev_percent > 0
                            and kelly_val > 0
                        ):
                            total_value_bets += 1
                            stake = bankroll * kelly_val
                            total_stake_suggested += stake
                            ev_values_for_avg.append(ev_percent)

                    render_match_card(match, result, odds_ctx, bankroll)
                except Exception as prediction_error:
                    st.warning(f"⚠️ Não foi possível gerar o prognóstico: {prediction_error}")
    else:
        st.info("Nenhum jogo disponível para essa rodada.")

    st.markdown('<div class="section-title">🎯 Resumo do dia – Premier League</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-sub">Visão geral dos jogos analisados, quantidade de value bets e distribuição de stakes.</div>',
        unsafe_allow_html=True,
    )
    avg_ev = sum(ev_values_for_avg) / len(ev_values_for_avg) if ev_values_for_avg else 0.0

    col_summary_a, col_summary_b, col_summary_c, col_summary_d = st.columns(4)
    with col_summary_a:
        st.metric("Jogos analisados", total_matches)
    with col_summary_b:
        st.metric("Value bets 1X2", total_value_bets)
    with col_summary_c:
        st.metric("Stake total sugerida", f"R$ {total_stake_suggested:.2f}")
    with col_summary_d:
        st.metric("EV médio (seleções positivas)", f"{avg_ev:.1f}%")

    st.markdown("---")

st.markdown("## 🇧🇷 Brasileirão – Prognósticos")

try:
    brasileirao_matches = cached_load_brasileirao_round_matches(selected_round_br)
except Exception as brasileirao_error:
    st.error(f"❌ Erro ao carregar rodada do Brasileirão: {brasileirao_error}")
    brasileirao_matches = []

total_matches_br = 0
total_value_bets_br = 0
total_stake_suggested_br = 0.0
ev_values_for_avg_br: list[float] = []

if brasileirao_matches:
    cols_br = st.columns(2)
    for idx, match in enumerate(brasileirao_matches):
        if idx != 0 and idx % 2 == 0:
            cols_br = st.columns(2)

        col = cols_br[idx % 2]
        context = getattr(match, "context", {}) or {}
        odds_defaults = context.get("odds") or {}

        default_home = normalize_default_odd(odds_defaults.get("home"))
        default_draw = normalize_default_odd(odds_defaults.get("draw"))
        default_away = normalize_default_odd(odds_defaults.get("away"))

        with col:
            odds_col1, odds_col2, odds_col3 = st.columns(3)

            with odds_col1:
                odd_home = st.number_input(
                    f"Odd Mandante – BR-{idx+1}",
                    value=default_home,
                    min_value=1.01,
                    step=0.01,
                    key=f"br_odd_home_{selected_round_br}_{idx}",
                )

            with odds_col2:
                odd_draw = st.number_input(
                    f"Odd Empate – BR-{idx+1}",
                    value=default_draw,
                    min_value=1.01,
                    step=0.01,
                    key=f"br_odd_draw_{selected_round_br}_{idx}",
                )

            with odds_col3:
                odd_away = st.number_input(
                    f"Odd Visitante – BR-{idx+1}",
                    value=default_away,
                    min_value=1.01,
                    step=0.01,
                    key=f"br_odd_away_{selected_round_br}_{idx}",
                )

            odds_ctx = {"home": odd_home, "draw": odd_draw, "away": odd_away}

            try:
                result = cached_run_prediction(match, n_sim=n_sim)
                result["n_sim"] = n_sim
                p_home = result["p_home_win"]
                p_draw = result["p_draw"]
                p_away = result["p_away_win"]

                ev_home = compute_ev(p_home, odd_home)
                ev_draw = compute_ev(p_draw, odd_draw)
                ev_away = compute_ev(p_away, odd_away)

                kelly_home_raw = compute_kelly_raw(p_home, odd_home)
                kelly_draw_raw = compute_kelly_raw(p_draw, odd_draw)
                kelly_away_raw = compute_kelly_raw(p_away, odd_away)

                kelly_home = kelly_home_raw * kelly_fraction if kelly_home_raw is not None else None
                kelly_draw = kelly_draw_raw * kelly_fraction if kelly_draw_raw is not None else None
                kelly_away = kelly_away_raw * kelly_fraction if kelly_away_raw is not None else None

                result["edge_home"] = ev_home * 100 if ev_home is not None else None
                result["edge_draw"] = ev_draw * 100 if ev_draw is not None else None
                result["edge_away"] = ev_away * 100 if ev_away is not None else None

                result["kelly_home"] = kelly_home
                result["kelly_draw"] = kelly_draw
                result["kelly_away"] = kelly_away

                result["lambda_home"] = getattr(match, "lambda_home", None)
                result["lambda_away"] = getattr(match, "lambda_away", None)

                league_name = "Brasileirão Série A"
                round_label = f"Rodada {selected_round_br}"
                kickoff_value = getattr(match, "kickoff_utc", None)
                if hasattr(kickoff_value, "strftime"):
                    kickoff_label = kickoff_value.strftime("%d %b %Y %H:%M")
                elif kickoff_value:
                    kickoff_label = str(kickoff_value)
                else:
                    kickoff_label = context.get("kickoff_label", "")

                setattr(match, "league_name", league_name)
                setattr(match, "round_name", round_label)
                setattr(match, "kickoff_str", kickoff_label)

                total_matches_br += 1
                for ev_percent, kelly_val in [
                    (result.get("edge_home"), result.get("kelly_home")),
                    (result.get("edge_draw"), result.get("kelly_draw")),
                    (result.get("edge_away"), result.get("kelly_away")),
                ]:
                    if (
                        ev_percent is not None
                        and kelly_val is not None
                        and ev_percent > 0
                        and kelly_val > 0
                    ):
                        total_value_bets_br += 1
                        stake = bankroll * kelly_val
                        total_stake_suggested_br += stake
                        ev_values_for_avg_br.append(ev_percent)

                render_match_card(match, result, odds_ctx, bankroll)
            except Exception as prediction_error:
                st.warning(
                    f"⚠️ Não foi possível gerar o prognóstico para esta partida do Brasileirão: {prediction_error}"
                )
else:
    st.info("Nenhum jogo disponível para a rodada selecionada do Brasileirão.")

st.markdown('<div class="section-title">🎯 Resumo do dia – Brasileirão</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-sub">Visão geral das partidas do Brasileirão analisadas, quantidade de value bets e distribuição de stakes.</div>',
    unsafe_allow_html=True,
)

avg_ev_br = (
    sum(ev_values_for_avg_br) / len(ev_values_for_avg_br)
    if ev_values_for_avg_br
    else 0.0
)

col_br_a, col_br_b, col_br_c, col_br_d = st.columns(4)
with col_br_a:
    st.metric("Jogos analisados", total_matches_br)
with col_br_b:
    st.metric("Value bets 1X2", total_value_bets_br)
with col_br_c:
    st.metric("Stake total sugerida", f"R$ {total_stake_suggested_br:.2f}")
with col_br_d:
    st.metric("EV médio (seleções positivas)", f"{avg_ev_br:.1f}%")

st.markdown("---")

st.sidebar.header("⚙️ Configurações")

# Informações sobre fonte de dados
with st.sidebar.expander("📊 Fonte de Dados", expanded=False):
    csv_info = collector.get_csv_info()
    st.write(f"**Liga:** {csv_info['league']}")

    for file_type, info in csv_info['files'].items():
        if info['exists']:
            st.success(f"✅ {file_type.title()}: {info['rows']} registros")
        else:
            st.error(f"❌ {file_type.title()}: Não encontrado")

    if odds_api_key:
        st.info("🎲 Odds: The Odds API")
    else:
        st.warning("⚠️ Odds API não configurada")

st.sidebar.markdown("---")

# Seletor de rodada
if selected_league_key == 'premier_league':
    rodada = selected_round
else:
    rodada = st.sidebar.number_input(
        "Número da Rodada",
        min_value=1,
        max_value=38,
        value=1,
        step=1,
        help="Selecione a rodada para análise"
    )

# Seletor de modo
modo = st.sidebar.radio(
    "Modo de Análise",
    ["🎯 Jogo Específico (Time vs Time)", "📋 Todos os Jogos da Rodada"],
    help="Escolha entre analisar um jogo específico ou todos os jogos da rodada"
)

if 'home_team' not in st.session_state:
    st.session_state.home_team = None
if 'away_team' not in st.session_state:
    st.session_state.away_team = None
if 'last_rodada' not in st.session_state:
    st.session_state.last_rodada = rodada
if 'last_home_selection' not in st.session_state:
    st.session_state.last_home_selection = None
if 'last_away_selection' not in st.session_state:
    st.session_state.last_away_selection = None

if st.session_state.last_rodada != rodada:
    st.session_state.home_team = None
    st.session_state.away_team = None
    st.session_state.last_home_selection = None
    st.session_state.last_away_selection = None
    st.session_state.last_rodada = rodada

if modo == "🎯 Jogo Específico (Time vs Time)":
    st.subheader(f"🎯 Análise de Jogo Específico - Rodada {rodada}")
    
    if selected_league == 'brasileirao':
        teams_list = get_teams_list(league_id=2013)
    else:
        teams = collector.get_teams()
        teams_list = [team for team in teams] if teams else []
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Seletor de time mandante
        home_team_selected = st.selectbox(
            "🏠 Time Mandante",
            ["Selecione..."] + teams_list,
            key="home_team_selector"
        )
        
        if home_team_selected != "Selecione..." and home_team_selected != st.session_state.last_home_selection:
            st.session_state.last_home_selection = home_team_selected
            
            if fixtures_collector:
                opponent_info = fixtures_collector.find_opponent(home_team_selected, rodada, is_home=True)
                
                if opponent_info:
                    st.session_state.away_team = opponent_info['opponent']
                    st.success(f"✅ Oponente encontrado: {opponent_info['opponent']}")
                else:
                    st.session_state.away_team = None
                    st.warning(f"⚠️ {home_team_selected} não joga como mandante na rodada {rodada}")
    
    with col2:
        # Seletor de time visitante
        away_team_selected = st.selectbox(
            "✈️ Time Visitante",
            ["Selecione..."] + teams_list,
            index=teams_list.index(st.session_state.away_team) + 1 if st.session_state.away_team in teams_list else 0,
            key="away_team_selector"
        )
        
        if away_team_selected != "Selecione..." and away_team_selected != st.session_state.last_away_selection:
            st.session_state.last_away_selection = away_team_selected
            
            if fixtures_collector:
                opponent_info = fixtures_collector.find_opponent(away_team_selected, rodada, is_home=False)
                
                if opponent_info:
                    st.session_state.home_team = opponent_info['opponent']
                    st.success(f"✅ Oponente encontrado: {opponent_info['opponent']}")
                else:
                    st.session_state.home_team = None
                    st.warning(f"⚠️ {away_team_selected} não joga como visitante na rodada {rodada}")
    
    if home_team_selected != "Selecione..." and away_team_selected != "Selecione...":
        if fixtures_collector:
            opponent_info = fixtures_collector.find_opponent(home_team_selected, rodada, is_home=True)
            
            if opponent_info and opponent_info['opponent'].lower() == away_team_selected.lower():
                st.success(f"✅ Jogo válido: {home_team_selected} vs {away_team_selected} (Rodada {rodada})")
                
                if st.button("🔮 GERAR PROGNÓSTICO"):
                    st.info("🚧 Funcionalidade de prognóstico em desenvolvimento...")
                    
                    probabilities = {
                        'goals': {
                            'over_2.5': 45.0,
                            'under_2.5': 55.0
                        }
                    }
                    
                    st.markdown("---")
                    st.subheader("💰 Gestão de Banca")
                    display_stake_calculation(probabilities, bankroll, kelly_fraction)
                    
                    st.markdown("---")
                    display_roi_simulation(bankroll, kelly_fraction)
            else:
                st.error(f"❌ Jogo inválido: {home_team_selected} não enfrenta {away_team_selected} na rodada {rodada}")
        else:
            st.info(f"📊 Jogo selecionado: {home_team_selected} vs {away_team_selected}")
            
            if st.button("🔮 GERAR PROGNÓSTICO"):
                st.info("🚧 Funcionalidade de prognóstico em desenvolvimento...")
                
                probabilities = {
                    'goals': {
                        'over_2.5': 45.0,
                        'under_2.5': 55.0
                    }
                }
                
                st.markdown("---")
                st.subheader("💰 Gestão de Banca")
                display_stake_calculation(probabilities, bankroll, kelly_fraction)
                
                st.markdown("---")
                display_roi_simulation(bankroll, kelly_fraction)

else:
    st.subheader(f"📋 Todos os Jogos da Rodada {rodada}")
    
    if fixtures_collector:
        fixtures = fixtures_collector.get_fixtures_by_round(rodada)
        
        if fixtures:
            st.info(f"📅 {len(fixtures)} jogos encontrados na rodada {rodada}")
            
            for fixture in fixtures:
                with st.expander(f"⚽ {fixture['home_team']} vs {fixture['away_team']}"):
                    st.write(f"**Data:** {fixture['date']}")
                    st.write(f"**Status:** {fixture['status']}")
                    
                    if st.button(f"🔮 Gerar Prognóstico", key=f"prog_{fixture['home_team_id']}_{fixture['away_team_id']}"):
                        st.info("🚧 Funcionalidade de prognóstico em desenvolvimento...")
                        
                        probabilities = {
                            'goals': {
                                'over_2.5': 45.0,
                                'under_2.5': 55.0
                            }
                        }
                        
                        st.markdown("---")
                        st.subheader("💰 Gestão de Banca")
                        display_stake_calculation(probabilities, bankroll, kelly_fraction)
                        
                        st.markdown("---")
                        display_roi_simulation(bankroll, kelly_fraction)
        else:
            st.warning(f"⚠️ Nenhum jogo encontrado para a rodada {rodada}")
    else:
        st.info("📊 Modo de análise por rodada disponível apenas para Brasileirão")

st.markdown("---")

# Buscar dados (seção original mantida)
st.subheader("Próximos Jogos")
matches = collector.get_matches(status="SCHEDULED")

if matches:
    for match in matches[:10]:
        st.write(f"{match['home_team']} vs {match['away_team']} - {match['date']}")
else:
    st.warning("Nenhum jogo encontrado")

st.subheader("Times")
teams = collector.get_teams()
if teams:
    for team in teams[:5]:
        # Extrair nome do time independente da estrutura
        if isinstance(team, dict):
            # Tentar diferentes chaves
            team_name = (
                team.get("name") or
                team.get("team_name") or
                team.get("common_name") or
                str(team)
            )
            st.write(f"- {team_name}")
        else:
            # Se for string direta
            st.write(f"- {team}")
else:
    st.warning("Nenhum time encontrado")
