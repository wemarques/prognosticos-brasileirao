"""
Dados de árbitros e suas estatísticas de cartões
"""

REFEREE_STATS = {
    # Árbitros do Brasileirão 2024/2025
    'anderson_daronco': {
        'name': 'Anderson Daronco',
        'matches_total': 156,
        'cards_per_match': 4.8,
        'yellow_cards_avg': 4.2,
        'red_cards_avg': 0.6,
        'leniency_factor': 1.14,  # Rigoroso
        'by_competition': {
            'brasileirao': {'cards_avg': 4.9, 'leniency': 1.17},
            'copa_do_brasil': {'cards_avg': 4.5, 'leniency': 1.07}
        },
        'by_season': {
            2024: {'cards_avg': 4.8, 'leniency': 1.14},
            2023: {'cards_avg': 4.7, 'leniency': 1.12}
        }
    },
    'wilton_pereira_sampaio': {
        'name': 'Wilton Pereira Sampaio',
        'matches_total': 142,
        'cards_per_match': 4.1,
        'yellow_cards_avg': 3.6,
        'red_cards_avg': 0.5,
        'leniency_factor': 0.98,  # Média
        'by_competition': {
            'brasileirao': {'cards_avg': 4.2, 'leniency': 1.0},
            'copa_do_brasil': {'cards_avg': 3.9, 'leniency': 0.93}
        },
        'by_season': {
            2024: {'cards_avg': 4.1, 'leniency': 0.98},
            2023: {'cards_avg': 4.0, 'leniency': 0.95}
        }
    },
    'raphael_claus': {
        'name': 'Raphael Claus',
        'matches_total': 138,
        'cards_per_match': 3.9,
        'yellow_cards_avg': 3.4,
        'red_cards_avg': 0.5,
        'leniency_factor': 0.93,  # Leniente
        'by_competition': {
            'brasileirao': {'cards_avg': 3.8, 'leniency': 0.90},
            'copa_do_brasil': {'cards_avg': 4.1, 'leniency': 0.98}
        },
        'by_season': {
            2024: {'cards_avg': 3.9, 'leniency': 0.93},
            2023: {'cards_avg': 4.0, 'leniency': 0.95}
        }
    },
    'braulio_da_silva_machado': {
        'name': 'Braulio da Silva Machado',
        'matches_total': 135,
        'cards_per_match': 4.5,
        'yellow_cards_avg': 3.9,
        'red_cards_avg': 0.6,
        'leniency_factor': 1.07,  # Rigoroso
        'by_competition': {
            'brasileirao': {'cards_avg': 4.6, 'leniency': 1.10},
            'copa_do_brasil': {'cards_avg': 4.3, 'leniency': 1.02}
        },
        'by_season': {
            2024: {'cards_avg': 4.5, 'leniency': 1.07},
            2023: {'cards_avg': 4.4, 'leniency': 1.05}
        }
    },
    'flavio_rodrigues_de_souza': {
        'name': 'Flavio Rodrigues de Souza',
        'matches_total': 128,
        'cards_per_match': 4.3,
        'yellow_cards_avg': 3.8,
        'red_cards_avg': 0.5,
        'leniency_factor': 1.02,  # Média
        'by_competition': {
            'brasileirao': {'cards_avg': 4.4, 'leniency': 1.05},
            'copa_do_brasil': {'cards_avg': 4.1, 'leniency': 0.98}
        },
        'by_season': {
            2024: {'cards_avg': 4.3, 'leniency': 1.02},
            2023: {'cards_avg': 4.2, 'leniency': 1.0}
        }
    },
    'paulo_roberto_alves_junior': {
        'name': 'Paulo Roberto Alves Junior',
        'matches_total': 125,
        'cards_per_match': 3.7,
        'yellow_cards_avg': 3.2,
        'red_cards_avg': 0.5,
        'leniency_factor': 0.88,  # Leniente
        'by_competition': {
            'brasileirao': {'cards_avg': 3.6, 'leniency': 0.86},
            'copa_do_brasil': {'cards_avg': 3.9, 'leniency': 0.93}
        },
        'by_season': {
            2024: {'cards_avg': 3.7, 'leniency': 0.88},
            2023: {'cards_avg': 3.8, 'leniency': 0.90}
        }
    },
    'rodolpho_toski': {
        'name': 'Rodolpho Toski',
        'matches_total': 120,
        'cards_per_match': 4.6,
        'yellow_cards_avg': 4.0,
        'red_cards_avg': 0.6,
        'leniency_factor': 1.10,  # Rigoroso
        'by_competition': {
            'brasileirao': {'cards_avg': 4.7, 'leniency': 1.12},
            'copa_do_brasil': {'cards_avg': 4.4, 'leniency': 1.05}
        },
        'by_season': {
            2024: {'cards_avg': 4.6, 'leniency': 1.10},
            2023: {'cards_avg': 4.5, 'leniency': 1.07}
        }
    },
    'sandro_meira_ricci': {
        'name': 'Sandro Meira Ricci',
        'matches_total': 118,
        'cards_per_match': 4.2,
        'yellow_cards_avg': 3.7,
        'red_cards_avg': 0.5,
        'leniency_factor': 1.0,  # Média
        'by_competition': {
            'brasileirao': {'cards_avg': 4.3, 'leniency': 1.02},
            'copa_do_brasil': {'cards_avg': 4.0, 'leniency': 0.95}
        },
        'by_season': {
            2024: {'cards_avg': 4.2, 'leniency': 1.0},
            2023: {'cards_avg': 4.1, 'leniency': 0.98}
        }
    },
    'luiz_flavio_de_oliveira': {
        'name': 'Luiz Flavio de Oliveira',
        'matches_total': 115,
        'cards_per_match': 3.8,
        'yellow_cards_avg': 3.3,
        'red_cards_avg': 0.5,
        'leniency_factor': 0.91,  # Leniente
        'by_competition': {
            'brasileirao': {'cards_avg': 3.7, 'leniency': 0.88},
            'copa_do_brasil': {'cards_avg': 4.0, 'leniency': 0.95}
        },
        'by_season': {
            2024: {'cards_avg': 3.8, 'leniency': 0.91},
            2023: {'cards_avg': 3.9, 'leniency': 0.93}
        }
    },
    'denis_da_silva_serafim': {
        'name': 'Denis da Silva Serafim',
        'matches_total': 110,
        'cards_per_match': 4.4,
        'yellow_cards_avg': 3.8,
        'red_cards_avg': 0.6,
        'leniency_factor': 1.05,  # Rigoroso
        'by_competition': {
            'brasileirao': {'cards_avg': 4.5, 'leniency': 1.07},
            'copa_do_brasil': {'cards_avg': 4.2, 'leniency': 1.0}
        },
        'by_season': {
            2024: {'cards_avg': 4.4, 'leniency': 1.05},
            2023: {'cards_avg': 4.3, 'leniency': 1.02}
        }
    }
}

# Mapeamento de IDs para nomes (para compatibilidade com APIs)
REFEREE_ID_MAP = {
    '1': 'anderson_daronco',
    '2': 'wilton_pereira_sampaio',
    '3': 'raphael_claus',
    '4': 'braulio_da_silva_machado',
    '5': 'flavio_rodrigues_de_souza',
    '6': 'paulo_roberto_alves_junior',
    '7': 'rodolpho_toski',
    '8': 'sandro_meira_ricci',
    '9': 'luiz_flavio_de_oliveira',
    '10': 'denis_da_silva_serafim'
}

# Estatísticas gerais da liga
LEAGUE_REFEREE_STATS = {
    'brasileirao': {
        'avg_cards_per_match': 4.2,
        'avg_yellow_cards': 3.7,
        'avg_red_cards': 0.5,
        'total_referees': 10,
        'season': 2024
    }
}


def get_referee_stats(referee_key: str) -> dict:
    """
    Obtém estatísticas de um árbitro
    
    Args:
        referee_key: Chave do árbitro (ex: 'anderson_daronco')
        
    Returns:
        Dict com estatísticas do árbitro ou dict vazio se não encontrado
    """
    return REFEREE_STATS.get(referee_key, {})


def get_referee_by_id(referee_id: str) -> dict:
    """
    Obtém estatísticas de um árbitro pelo ID
    
    Args:
        referee_id: ID do árbitro
        
    Returns:
        Dict com estatísticas do árbitro
    """
    referee_key = REFEREE_ID_MAP.get(referee_id)
    if referee_key:
        return get_referee_stats(referee_key)
    return {}


def get_leniency_factor(referee_key: str, competition: str = 'brasileirao', season: int = 2024) -> float:
    """
    Obtém fator de leniência de um árbitro
    
    Args:
        referee_key: Chave do árbitro
        competition: Competição (brasileirao, copa_do_brasil, etc)
        season: Temporada
        
    Returns:
        Fator de leniência (1.0 = média, >1.0 = rigoroso, <1.0 = leniente)
    """
    referee = get_referee_stats(referee_key)
    
    if not referee:
        return 1.0  # Árbitro desconhecido = média
    
    # Preferir dados específicos da competição
    if competition in referee.get('by_competition', {}):
        return referee['by_competition'][competition].get('leniency', 1.0)
    
    # Preferir dados específicos da temporada
    if season in referee.get('by_season', {}):
        return referee['by_season'][season].get('leniency', 1.0)
    
    # Fallback para média geral
    return referee.get('leniency_factor', 1.0)


def get_avg_cards(referee_key: str, competition: str = 'brasileirao', season: int = 2024) -> float:
    """
    Obtém média de cartões de um árbitro
    
    Args:
        referee_key: Chave do árbitro
        competition: Competição
        season: Temporada
        
    Returns:
        Média de cartões por jogo
    """
    referee = get_referee_stats(referee_key)
    
    if not referee:
        return LEAGUE_REFEREE_STATS['brasileirao']['avg_cards_per_match']
    
    # Preferir dados específicos da competição
    if competition in referee.get('by_competition', {}):
        return referee['by_competition'][competition].get('cards_avg', referee.get('cards_per_match', 4.2))
    
    # Preferir dados específicos da temporada
    if season in referee.get('by_season', {}):
        return referee['by_season'][season].get('cards_avg', referee.get('cards_per_match', 4.2))
    
    # Fallback para média geral
    return referee.get('cards_per_match', 4.2)


def classify_referee_style(leniency_factor: float) -> str:
    """
    Classifica o estilo de arbitragem
    
    Args:
        leniency_factor: Fator de leniência
        
    Returns:
        Classificação (Rigoroso, Médio, Leniente)
    """
    if leniency_factor > 1.08:
        return "🔴 Rigoroso"
    elif leniency_factor < 0.92:
        return "🟢 Leniente"
    else:
        return "🟡 Médio"