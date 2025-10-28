"""
Configurações gerais do sistema de prognósticos
Adaptado para Football-Data.org API
"""

import os
from dotenv import load_dotenv

load_dotenv()

# APIs
FOOTBALL_DATA_API_KEY = os.getenv("FOOTBALL_DATA_API_KEY", os.getenv("API_FOOTBALL_KEY", ""))
ODDS_API_KEY = os.getenv("ODDS_API_KEY", "")

# IDs das Ligas (Football-Data.org)
BRASILEIRAO_SERIE_A = 2013  # BSA
CURRENT_SEASON = 2025

# Configurações de Modelos
DIXON_COLES_PARAMS = {
    'rho': -0.11,  # Correlação entre gols
    'home_advantage': 1.53,  # Vantagem de jogar em casa (Brasileirão)
}

# Calibrações específicas do Brasileirão
BRASILEIRAO_CALIBRATION = {
    'home_boost': 1.53,  # Multiplicador para mandante
    'away_penalty': 0.85,  # Penalidade para visitante
    'cards_multiplier': 1.2,  # Brasileirão tem mais cartões
    'corners_adjustment': 0.9,  # Menos escanteios que média europeia
}

# Configurações de Value Bets
VALUE_BET_THRESHOLD = 0.05  # 5% de edge mínimo
MIN_PROBABILITY = 0.15  # Não apostar em eventos < 15% probabilidade
MAX_STAKE_PERCENTAGE = 0.05  # Máximo 5% do bankroll por aposta

# Cache
CACHE_EXPIRY_HOURS = 24
CACHE_DIR = "data/cache"

# Times do Brasileirão 2025
# IDs serão obtidos dinamicamente da API Football-Data.org
# Mapeamento de nomes para facilitar busca
BRASILEIRAO_TEAMS_NAMES = [
    'Flamengo',
    'Palmeiras',
    'São Paulo',
    'Corinthians',
    'Santos',
    'Grêmio',
    'Internacional',
    'Atlético Mineiro',
    'Fluminense',
    'Botafogo',
    'Athletico Paranaense',
    'Cruzeiro',
    'Vasco da Gama',
    'Bahia',
    'Fortaleza',
    'Red Bull Bragantino',
    'Cuiabá',
    'Criciúma',
    'Vitória',
    'Juventude',
]

# Mapeamento de IDs (será preenchido dinamicamente)
BRASILEIRAO_TEAMS = {}
TEAM_ID_TO_NAME = {}

def load_teams_from_api():
    """
    Carrega IDs dos times dinamicamente da API
    Deve ser chamado na inicialização do app
    """
    try:
        from data.collector import FootballDataCollector
        collector = FootballDataCollector()
        teams = collector.get_teams()
        
        global BRASILEIRAO_TEAMS, TEAM_ID_TO_NAME
        
        for team in teams:
            team_name = team['name']
            team_id = team['id']
            BRASILEIRAO_TEAMS[team_name] = team_id
            TEAM_ID_TO_NAME[team_id] = team_name
        
        return True
    except Exception as e:
        print(f"Erro ao carregar times da API: {e}")
        return False

# Mapeamento manual de fallback (caso API falhe)
BRASILEIRAO_TEAMS_FALLBACK = {
    'Flamengo': 1776,
    'Palmeiras': 1777,
    'São Paulo': 1778,
    'Corinthians': 1779,
    'Santos': 1780,
    'Grêmio': 1781,
    'Internacional': 1782,
    'Atlético Mineiro': 1783,
    'Fluminense': 1784,
    'Botafogo': 1785,
    'Athletico Paranaense': 1786,
    'Cruzeiro': 1787,
    'Vasco da Gama': 1788,
    'Bahia': 1789,
    'Fortaleza': 1790,
    'Red Bull Bragantino': 1791,
    'Cuiabá': 1792,
    'Criciúma': 1793,
    'Vitória': 1794,
    'Juventude': 1795,
}

