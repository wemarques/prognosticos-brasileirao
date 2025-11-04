"""
Teams Collector - Busca lista de times de uma liga
"""
import os
import requests
from utils.logger import setup_logger

logger = setup_logger(__name__)


def get_teams_list(league_id=2013):
    """
    Get list of teams in a league.
    
    Args:
        league_id: Football-Data.org league ID (2013 = Brasileirão Série A)
    
    Returns:
        list: List of team names
    """
    api_key = os.getenv('FOOTBALL_DATA_API_KEY')
    
    try:
        headers = {'X-Auth-Token': api_key}
        url = f"https://api.football-data.org/v4/competitions/{league_id}/teams"
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        teams = [team['name'] for team in data.get('teams', [])]
        
        logger.info(f"✅ Found {len(teams)} teams in Brasileirão Série A")
        
        return sorted(teams)
        
    except Exception as e:
        logger.error(f"❌ Error fetching teams: {e}")
        return [
            "Athletico Paranaense", "Atlético Mineiro", "Bahia", "Botafogo",
            "Corinthians", "Cruzeiro", "Cuiabá", "Flamengo", "Fluminense",
            "Fortaleza", "Grêmio", "Internacional", "Juventude", "Palmeiras",
            "Red Bull Bragantino", "Santos", "São Paulo", "Vasco da Gama",
            "Criciúma", "Vitória"
        ]
