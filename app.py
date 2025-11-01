import streamlit as st
from ui.league_selector import render_league_selector, get_league_info
from data.collectors.football_data_collector_v2 import FootballDataCollectorV2
from utils.leagues_config import get_api_config

st.set_page_config(page_title="Prognósticos de Futebol", layout="wide")

# Seletor de liga
selected_league = render_league_selector()
league_info = get_league_info(selected_league)

# Exibir informações da liga
st.title(f"{league_info['icon']} {league_info['name']}")

# Criar collector com a liga selecionada
api_config = get_api_config(selected_league)
collector = FootballDataCollectorV2(selected_league, api_config)

# Buscar dados
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
