"""
Seletor de Liga para Streamlit
"""
import streamlit as st
from utils.leagues_config import LEAGUES

def render_league_selector():
    """Renderiza o seletor de liga na interface"""
    
    st.sidebar.markdown("## ⚽ Selecione a Liga")
    
    # Opções de liga
    league_options = {
        f"{league_config['icon']} {league_config['name']}": league_key
        for league_key, league_config in LEAGUES.items()
    }
    
    # Seletor
    selected_league_display = st.sidebar.selectbox(
        "Liga",
        options=list(league_options.keys()),
        index=0
    )
    
    # Retorna a chave da liga selecionada
    selected_league = league_options[selected_league_display]
    
    return selected_league

def get_league_info(league_key: str):
    """Retorna informações da liga selecionada"""
    return LEAGUES.get(league_key, LEAGUES['brasileirao'])

def render_league_info(league_key: str):
    """Renderiza informações da liga selecionada"""
    league_info = get_league_info(league_key)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Liga", league_info['name'])
    
    with col2:
        st.metric("País", league_info['country'])
    
    with col3:
        st.metric("Temporada", league_info['season'])