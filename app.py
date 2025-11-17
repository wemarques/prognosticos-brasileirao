import streamlit as st
import os
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
from analysis.prediction import run_prediction, format_report


@st.cache_data(show_spinner="Carregando rodada da Premier League...")
def cached_load_premier_round_matches(round_number: int):
    return load_premier_round_matches(round_number)


@st.cache_data(show_spinner="Executando simulações de partida...")
def cached_run_prediction(match, n_sim: int):
    return run_prediction(match, n_sim=n_sim)

st.set_page_config(page_title="Prognósticos de Futebol", layout="wide")

st.sidebar.header("⚙️ Configurações")

available_leagues = LeagueRegistry.get_available_leagues()
selected_league_key = st.sidebar.selectbox(
    "Liga:",
    options=list(available_leagues.keys()),
    format_func=lambda x: available_leagues[x]
)
selected_round = st.sidebar.selectbox("Rodada:", list(range(1, 39)))
n_sim = st.sidebar.slider("Simulações (n_sim)", 5000, 100000, 50000, step=5000)

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

    if matches:
        for idx, match in enumerate(matches):
            label = f"{match.home_team} vs {match.away_team}"
            with st.expander(f"⚽ {label} (n_sim={n_sim:,})", expanded=(idx == 0)):
                context = match.context or {}
                odds = context.get("odds") or {}
                metadata = context.get("fixture_metadata") or {}

                st.write(f"**Kickoff (UTC):** {match.kickoff_utc}")

                venue = context.get("venue")
                if venue:
                    st.write(f"**Estádio:** {venue}")

                if metadata:
                    status = metadata.get("status") or context.get("status")
                    if status:
                        st.write(f"**Status:** {status}")
                    if metadata.get("stage"):
                        st.write(f"**Fase:** {metadata['stage']}")

                if any(odds.values()):
                    odds_display = ", ".join(
                        f"{key}: {value}" for key, value in odds.items() if value
                    )
                    if odds_display:
                        st.write(f"**Odds:** {odds_display}")

                try:
                    result = cached_run_prediction(match, n_sim=n_sim)
                    report = format_report(match, result)
                    st.text(report)
                except Exception as prediction_error:
                    st.warning(f"⚠️ Não foi possível gerar o prognóstico: {prediction_error}")
    else:
        st.info("Nenhum jogo disponível para essa rodada.")

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

st.sidebar.subheader("💰 Gestão de Banca")
bankroll = st.sidebar.number_input(
    "Valor da Banca (R$)",
    min_value=100.0,
    max_value=100000.0,
    value=1000.0,
    step=100.0,
    help="Valor total disponível para apostas"
)
kelly_fraction = st.sidebar.slider(
    "Fração de Kelly",
    min_value=0.1,
    max_value=0.5,
    value=0.25,
    step=0.05,
    help="Fração do Kelly Criterion a usar (0.25 = Quarter Kelly, conservador)"
)

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
        teams_list = [team['name'] for team in teams] if teams else []
    
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
        st.write(f"- {team['name']}")
else:
    st.warning("Nenhum time encontrado")
