"""
Teams Collector - Busca lista de times de uma liga
Atualizado com Prompt 0.1-0.2: Lista oficial 2025
"""
import os
import requests
from utils.logger import setup_logger

logger = setup_logger(__name__)

def get_teams_list(league_id=2013, season=2025):
    """
    Get list of teams in a league from API.
    
    Args:
        league_id: Football-Data.org league ID (2013 = Brasileirão Série A)
        season: Season year (default: 2025)
    
    Returns:
        list: List of team names (official names from API)
    """
    api_key = os.getenv('FOOTBALL_DATA_API_KEY')
    
    try:
        headers = {'X-Auth-Token': api_key}
        url = f"https://api.football-data.org/v4/competitions/{league_id}/teams"
        params = {'season': season}
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        teams = [team['name'] for team in data.get('teams', [])]
        
        logger.info(f"✅ Found {len(teams)} teams in Brasileirão Série A {season}")
        
        # Validação
        if len(teams) == 20:
            logger.info("✅ Complete list: 20 teams")
        else:
            logger.warning(f"⚠️ Incomplete list: {len(teams)}/20 teams")
        
        return sorted(teams)
        
    except Exception as e:
        logger.error(f"❌ Error fetching teams from API: {e}. Using fallback.")
        return get_fallback_teams_2025()

def get_fallback_teams_2025():
    """
    Fallback list with official Brasileirão Série A 2025 teams.
    Used ONLY if API fails.
    
    Returns:
        list: Sorted list of official team names
    """
    logger.warning("🚨 USING FALLBACK - API FOOTBALL UNAVAILABLE")
    
    # Lista oficial Brasileirão Série A 2025 - FONTE: API FOOTBALL
    # Atualizada em: 05/11/2025 (Prompt 0.1-0.2)
    teams_2025 = [
        "Botafogo FR",
        "CA Mineiro",
        "CR Flamengo",
        "CR Vasco da Gama",
        "Ceará SC",  # PROMOVIDO 2025
        "Cruzeiro EC",
        "EC Bahia",
        "EC Juventude",
        "EC Vitória",  # PROMOVIDO 2025
        "Fluminense FC",
        "Fortaleza EC",
        "Grêmio FBPA",
        "Mirassol FC",  # PROMOVIDO 2025
        "RB Bragantino",
        "SC Corinthians Paulista",
        "SC Internacional",
        "SC Recife",
        "SE Palmeiras",
        "Santos FC",  # PROMOVIDO 2025
        "São Paulo FC",
    ]
    
    logger.info(f"📋 Fallback: {len(teams_2025)} teams (Brasileirão 2025)")
    
    return sorted(teams_2025)
