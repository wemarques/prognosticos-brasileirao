import streamlit as st
from ui.league_selector import render_league_selector, get_league_info
from data.collectors.football_data_collector_v2 import FootballDataCollectorV2
from utils.leagues_config import get_api_config
from collectors.fixtures_collector import FixturesCollector
from collectors.teams_collector import get_teams_list

st.set_page_config(page_title="Prognósticos de Futebol", layout="wide")

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
            else:
                st.error(f"❌ Jogo inválido: {home_team_selected} não enfrenta {away_team_selected} na rodada {rodada}")
        else:
            st.info(f"📊 Jogo selecionado: {home_team_selected} vs {away_team_selected}")
            
            if st.button("🔮 GERAR PROGNÓSTICO"):
                st.info("🚧 Funcionalidade de prognóstico em desenvolvimento...")

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
