"""
Configuração centralizada de ligas e APIs
"""
import os
from typing import Dict, Any

LEAGUES = {
    'brasileirao': {
        'id': 2013,
        'code': 'BSA',
        'name': 'Brasileirão Série A',
        'country': 'Brasil',
        'season': 2025,
        'icon': '🇧🇷',
        'api': {
            'provider': 'football_data',
            'league_id': 2013,
            'api_key': os.getenv('FOOTBALL_DATA_API_KEY'),
            'base_url': 'https://api.football-data.org/v4'
        },
        'stats': {
            'league_avg_goals': 1.82,
            'league_avg_xg': 1.40,
            'home_advantage': 1.53,
            'away_penalty': 0.85,
            'cards_multiplier': 1.2,
            'corners_adjustment': 0.9,
            'btts_rate': 0.36,
        },
        'dixon_coles': {
            'rho': -0.11,
            'home_advantage': 1.53,
        }
    },
    'premier_league': {
        'id': 2021,
        'code': 'PL',
        'name': 'Premier League',
        'country': 'Inglaterra',
        'season': 2024,  # 2024/25
        'icon': '🏴󠁧󠁢󠁥󠁮󠁧󠁿',
        'api': {
            'provider': 'footystats',  # Gratuito!
            'league_id': 1626,  # 2024/25 season
            'api_key': 'test85g57',
            'base_url': 'https://api.footystats.org/api'
        },
        'stats': {
            'league_avg_goals': 2.69,
            'league_avg_xg': 1.52,
            'home_advantage': 1.38,
            'away_penalty': 0.90,
            'cards_multiplier': 0.85,
            'corners_adjustment': 1.25,
            'btts_rate': 0.52,
        },
        'dixon_coles': {
            'rho': -0.11,
            'home_advantage': 1.38,
        }
    }
}

def get_league_config(league_key: str) -> Dict[str, Any]:
    """Retorna configuração de uma liga específica"""
    if league_key not in LEAGUES:
        raise ValueError(f"Liga '{league_key}' não encontrada. Opções: {list(LEAGUES.keys())}")
    return LEAGUES[league_key]

def get_api_config(league_key: str) -> Dict[str, Any]:
    """Retorna configuração da API para uma liga"""
    league = get_league_config(league_key)
    return league['api']

def get_all_leagues() -> Dict[str, Dict[str, Any]]:
    """Retorna todas as ligas disponíveis"""
    return LEAGUES

def get_league_names() -> Dict[str, str]:
    """Retorna mapeamento de league_key para nome exibível"""
    return {key: f"{config['icon']} {config['name']}" for key, config in LEAGUES.items()}