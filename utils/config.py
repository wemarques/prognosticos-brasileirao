"""
Configurações gerais do sistema de prognósticos
"""

import os
from dotenv import load_dotenv

load_dotenv()

# APIs
API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY", "")
ODDS_API_KEY = os.getenv("ODDS_API_KEY", "")

# IDs das Ligas
BRASILEIRAO_SERIE_A = 71
CURRENT_SEASON = 2025

# Configurações de Modelos
DIXON_COLES_PARAMS = {
    'rho': 0.0,  # Correlação entre gols
    'home_advantage': 0.3,  # Vantagem de jogar em casa
}

# Calibrações específicas do Brasileirão
BRASILEIRAO_CALIBRATION = {
    'home_boost': 1.15,  # Multiplicador para mandante
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

# Times do Brasileirão 2025 (IDs da API-Football)
BRASILEIRAO_TEAMS = {
    'Flamengo': 127,
    'Palmeiras': 128,
    'São Paulo': 126,
    'Corinthians': 131,
    'Santos': 124,
    'Grêmio': 136,
    'Internacional': 134,
    'Atlético Mineiro': 133,
    'Fluminense': 125,
    'Botafogo': 129,
    'Athletico Paranaense': 149,
    'Cruzeiro': 132,
    'Vasco': 130,
    'Bahia': 159,
    'Fortaleza': 160,
    'Bragantino': 1371,
    'Cuiabá': 1193,
    'Criciúma': 1207,
    'Vitória': 154,
    'Juventude': 1188,
}

# Mapeamento reverso
TEAM_ID_TO_NAME = {v: k for k, v in BRASILEIRAO_TEAMS.items()}

