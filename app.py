import streamlit as st
from ui.league_selector import render_league_selector, get_league_info
from data.collectors.football_data_collector_v2 import FootballDataCollectorV2
from utils.leagues_config import get_api_config
from collectors.fixtures_collector import FixturesCollector
from collectors.teams_collector import get_teams_list
from modules.roi.kelly_criterion import KellyCriterion
from modules.roi.roi_simulator import ROISimulator

st.set_page_config(page_title="Prognósticos de Futebol", layout="wide")

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
    """Display ROI simulation section with adjustable parameters"""
    with st.expander("📊 Simulação de ROI", expanded=False):
        st.subheader("Simular Retorno sobre Investimento")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            avg_bets_per_week = st.number_input(
                "Apostas por Semana",
                min_value=1,
                max_value=50,
                value=5,
                step=1,
                help="Número médio de apostas por semana"
            )
        with col2:
            avg_edge = st.number_input(
                "Edge Médio (%)",
                min_value=0.0,
                max_value=20.0,
                value=8.0,
                step=0.5,
                help="Edge médio sobre a casa de apostas"
            ) / 100
        with col3:
            win_rate = st.number_input(
                "Win Rate (%)",
                min_value=30.0,
                max_value=80.0,
                value=55.0,
                step=1.0,
                help="Taxa de acerto esperada"
            ) / 100
        
        if st.button("🎲 Simular ROI"):
            simulator = ROISimulator(bankroll, kelly_fraction)
            results = simulator.simulate_multiple_periods(avg_bets_per_week, avg_edge, win_rate)
            
            st.markdown("### Resultados da Simulação")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    "30 dias (4 semanas)",
                    f"R$ {results['4_weeks']['final_bankroll']:.2f}",
                    f"{results['4_weeks']['roi_percent']:+.2f}%"
                )
            with col2:
                st.metric(
                    "60 dias (8 semanas)",
                    f"R$ {results['8_weeks']['final_bankroll']:.2f}",
                    f"{results['8_weeks']['roi_percent']:+.2f}%"
                )
            with col3:
                st.metric(
                    "90 dias (12 semanas)",
                    f"R$ {results['12_weeks']['final_bankroll']:.2f}",
                    f"{results['12_weeks']['roi_percent']:+.2f}%"
                )
            
            st.info(f"ℹ️ Simulação baseada em: {avg_bets_per_week} apostas/semana, {avg_edge*100:.1f}% edge, {win_rate*100:.1f}% win rate")

# Seletor de liga
selected_league = render_league_selector()
league_info = get_league_info(selected_league)

# Exibir informações da liga
st.title(f"{league_info['icon']} {league_info['name']}")

# Criar collector com a liga selecionada
api_config = get_api_config(selected_league)
collector = FootballDataCollectorV2(selected_league, api_config)

if selected_league == 'brasileirao':
    fixtures_collector = FixturesCollector(league_id=2013)
else:
    fixtures_collector = None

st.sidebar.header("⚙️ Configurações")

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
