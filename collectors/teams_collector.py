"""
Teams Collector - Busca lista de times de uma liga dos arquivos CSV
"""
import pandas as pd
from pathlib import Path
from utils.logger import setup_logger

logger = setup_logger(__name__)

def get_teams_list(league_key='brasileirao', season=2025):
    """
    Get list of teams in a league from CSV file.

    Args:
        league_key: League identifier ('brasileirao', 'premier_league')
        season: Season year (default: 2025)

    Returns:
        list: List of team names
    """
    csv_path = Path(__file__).parent.parent / 'data' / 'csv' / league_key
    teams_file = csv_path / f'{season}_teams.csv'

    try:
        if not teams_file.exists():
            logger.warning(f"⚠️ Teams file not found: {teams_file}. Using fallback.")
            return get_fallback_teams_2025() if league_key == 'brasileirao' else []

        df = pd.read_csv(teams_file)
        teams = df['team_name'].tolist()

        logger.info(f"✅ Found {len(teams)} teams in {league_key} {season}")

        return sorted(teams)

    except Exception as e:
        logger.error(f"❌ Error reading teams from CSV: {e}. Using fallback.")
        return get_fallback_teams_2025() if league_key == 'brasileirao' else []

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
