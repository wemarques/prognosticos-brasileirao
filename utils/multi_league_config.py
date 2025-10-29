"""
Configuração centralizada para múltiplas ligas
Suporta Brasileirão e Premier League com parâmetros específicos
"""
from typing import Dict, Any


LEAGUES_CONFIG = {
    'brasileirao': {
        'id': 2013,
        'code': 'BSA',
        'name': 'Brasileirão Série A',
        'country': 'Brasil',
        'season': 2025,
        'icon': '🇧🇷',
        'timezone': 'America/Sao_Paulo',
        'api': {
            'provider': 'football_data',
            'league_id': 2013,
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
            'avg_cards_per_match': 4.2,
            'avg_yellow_cards': 3.8,
            'avg_red_cards': 0.4,
        },
        'dixon_coles': {
            'rho': -0.11,
            'home_advantage': 1.53,
        },
        'referees': {
            'total': 10,
            'avg_cards': 4.2,
            'avg_accuracy': 92.5
        }
    },
    'premier_league': {
        'id': 2021,
        'code': 'PL',
        'name': 'Premier League',
        'country': 'Inglaterra',
        'season': 2024,  # 2024/25
        'icon': '🏴󠁧󠁢󠁥󠁮󠁧󠁿',
        'timezone': 'Europe/London',
        'api': {
            'provider': 'footystats',  # Gratuito!
            'league_id': 1626,  # 2024/25 season
            'base_url': 'https://api.footystats.org'
        },
        'stats': {
            'league_avg_goals': 2.69,
            'league_avg_xg': 1.65,
            'home_advantage': 1.38,
            'away_penalty': 0.92,
            'cards_multiplier': 1.05,
            'corners_adjustment': 1.0,
            'btts_rate': 0.52,
            'avg_cards_per_match': 4.4,
            'avg_yellow_cards': 3.9,
            'avg_red_cards': 0.5,
        },
        'dixon_coles': {
            'rho': -0.08,
            'home_advantage': 1.38,
        },
        'referees': {
            'total': 10,
            'avg_cards': 4.4,
            'avg_accuracy': 90.5
        }
    }
}


def get_league_config(league_key: str) -> Dict[str, Any]:
    """
    Obter configuração de uma liga
    
    Args:
        league_key: 'brasileirao' ou 'premier_league'
        
    Returns:
        Configuração da liga
    """
    return LEAGUES_CONFIG.get(league_key, {})


def get_api_config(league_key: str) -> Dict[str, Any]:
    """
    Obter configuração da API para uma liga
    
    Args:
        league_key: 'brasileirao' ou 'premier_league'
        
    Returns:
        Configuração da API
    """
    league_config = get_league_config(league_key)
    return league_config.get('api', {})


def get_league_stats(league_key: str) -> Dict[str, Any]:
    """
    Obter estatísticas de uma liga
    
    Args:
        league_key: 'brasileirao' ou 'premier_league'
        
    Returns:
        Estatísticas da liga
    """
    league_config = get_league_config(league_key)
    return league_config.get('stats', {})


def get_league_names() -> Dict[str, str]:
    """
    Obter mapeamento de chaves para nomes de ligas
    
    Returns:
        Dict com chave -> nome
    """
    return {key: config['name'] for key, config in LEAGUES_CONFIG.items()}


def get_league_icons() -> Dict[str, str]:
    """
    Obter mapeamento de chaves para ícones de ligas
    
    Returns:
        Dict com chave -> ícone
    """
    return {key: config['icon'] for key, config in LEAGUES_CONFIG.items()}


def get_available_leagues() -> list:
    """
    Obter lista de ligas disponíveis
    
    Returns:
        Lista de chaves de ligas
    """
    return list(LEAGUES_CONFIG.keys())


def compare_leagues() -> Dict[str, Any]:
    """
    Comparar estatísticas entre ligas
    
    Returns:
        Comparação de estatísticas
    """
    comparison = {}
    
    for league_key, config in LEAGUES_CONFIG.items():
        stats = config.get('stats', {})
        comparison[league_key] = {
            'name': config['name'],
            'avg_goals': stats.get('league_avg_goals', 0),
            'avg_xg': stats.get('league_avg_xg', 0),
            'home_advantage': stats.get('home_advantage', 0),
            'btts_rate': stats.get('btts_rate', 0),
            'avg_cards': stats.get('avg_cards_per_match', 0),
        }
    
    return comparison


def get_league_by_code(code: str) -> str:
    """
    Obter chave de liga pelo código
    
    Args:
        code: Código da liga (ex: 'BSA', 'PL')
        
    Returns:
        Chave da liga ou None
    """
    for key, config in LEAGUES_CONFIG.items():
        if config.get('code') == code:
            return key
    return None


def get_timezone(league_key: str) -> str:
    """
    Obter timezone de uma liga
    
    Args:
        league_key: 'brasileirao' ou 'premier_league'
        
    Returns:
        Timezone (ex: 'America/Sao_Paulo')
    """
    league_config = get_league_config(league_key)
    return league_config.get('timezone', 'UTC')


# Exemplo de uso
if __name__ == "__main__":
    print("Ligas Disponíveis:")
    for league_key in get_available_leagues():
        config = get_league_config(league_key)
        print(f"  {config['icon']} {config['name']} ({league_key})")
    
    print("\nComparação de Estatísticas:")
    comparison = compare_leagues()
    for league_key, stats in comparison.items():
        print(f"\n{stats['name']}:")
        print(f"  Gols/Jogo: {stats['avg_goals']}")
        print(f"  Vantagem Casa: {stats['home_advantage']}")
        print(f"  BTTS: {stats['btts_rate']:.0%}")
        print(f"  Cartões/Jogo: {stats['avg_cards']}")