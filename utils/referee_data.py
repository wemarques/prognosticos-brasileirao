"""
Dados de árbitros e suas estatísticas de cartões
Suporta múltiplas ligas: Brasileirão e Premier League
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

# PREMIER LEAGUE REFEREES 2024/2025
PREMIER_LEAGUE_REFEREE_STATS = {
    'simon_hooper': {
        'name': 'Simon Hooper',
        'matches_total': 24,
        'cards_per_match': 4.9,
        'yellow_cards_avg': 4.4,
        'red_cards_avg': 0.5,
        'leniency_factor': 1.17,  # Rigoroso
        'accuracy': 94.92,
        'by_competition': {
            'premier_league': {'cards_avg': 4.9, 'leniency': 1.17},
        },
        'by_season': {
            2024: {'cards_avg': 4.9, 'leniency': 1.17}
        }
    },
    'anthony_taylor': {
        'name': 'Anthony Taylor',
        'matches_total': 31,
        'cards_per_match': 4.5,
        'yellow_cards_avg': 4.0,
        'red_cards_avg': 0.5,
        'leniency_factor': 1.07,  # Rigoroso
        'accuracy': 94.74,
        'by_competition': {
            'premier_league': {'cards_avg': 4.5, 'leniency': 1.07},
        },
        'by_season': {
            2024: {'cards_avg': 4.5, 'leniency': 1.07}
        }
    },
    'michael_oliver': {
        'name': 'Michael Oliver',
        'matches_total': 26,
        'cards_per_match': 4.3,
        'yellow_cards_avg': 3.8,
        'red_cards_avg': 0.5,
        'leniency_factor': 1.02,  # Médio
        'accuracy': 94.64,
        'by_competition': {
            'premier_league': {'cards_avg': 4.3, 'leniency': 1.02},
        },
        'by_season': {
            2024: {'cards_avg': 4.3, 'leniency': 1.02}
        }
    },
    'john_brooks': {
        'name': 'John Brooks',
        'matches_total': 16,
        'cards_per_match': 4.4,
        'yellow_cards_avg': 3.9,
        'red_cards_avg': 0.5,
        'leniency_factor': 1.05,  # Rigoroso
        'accuracy': 94.29,
        'by_competition': {
            'premier_league': {'cards_avg': 4.4, 'leniency': 1.05},
        },
        'by_season': {
            2024: {'cards_avg': 4.4, 'leniency': 1.05}
        }
    },
    'jarred_gillett': {
        'name': 'Jarred Gillett',
        'matches_total': 16,
        'cards_per_match': 4.6,
        'yellow_cards_avg': 4.1,
        'red_cards_avg': 0.5,
        'leniency_factor': 1.10,  # Rigoroso
        'accuracy': 92.50,
        'by_competition': {
            'premier_league': {'cards_avg': 4.6, 'leniency': 1.10},
        },
        'by_season': {
            2024: {'cards_avg': 4.6, 'leniency': 1.10}
        }
    },
    'tony_harrington': {
        'name': 'Tony Harrington',
        'matches_total': 18,
        'cards_per_match': 4.2,
        'yellow_cards_avg': 3.7,
        'red_cards_avg': 0.5,
        'leniency_factor': 1.0,  # Médio
        'accuracy': 89.13,
        'by_competition': {
            'premier_league': {'cards_avg': 4.2, 'leniency': 1.0},
        },
        'by_season': {
            2024: {'cards_avg': 4.2, 'leniency': 1.0}
        }
    },
    'chris_kavanagh': {
        'name': 'Chris Kavanagh',
        'matches_total': 25,
        'cards_per_match': 4.7,
        'yellow_cards_avg': 4.2,
        'red_cards_avg': 0.5,
        'leniency_factor': 1.12,  # Rigoroso
        'accuracy': 84.21,
        'by_competition': {
            'premier_league': {'cards_avg': 4.7, 'leniency': 1.12},
        },
        'by_season': {
            2024: {'cards_avg': 4.7, 'leniency': 1.12}
        }
    },
    'sam_barrott': {
        'name': 'Sam Barrott',
        'matches_total': 24,
        'cards_per_match': 4.8,
        'yellow_cards_avg': 4.3,
        'red_cards_avg': 0.5,
        'leniency_factor': 1.14,  # Rigoroso
        'accuracy': 85.45,
        'by_competition': {
            'premier_league': {'cards_avg': 4.8, 'leniency': 1.14},
        },
        'by_season': {
            2024: {'cards_avg': 4.8, 'leniency': 1.14}
        }
    },
    'andy_madley': {
        'name': 'Andy Madley',
        'matches_total': 20,
        'cards_per_match': 4.1,
        'yellow_cards_avg': 3.6,
        'red_cards_avg': 0.5,
        'leniency_factor': 0.98,  # Médio
        'accuracy': 87.76,
        'by_competition': {
            'premier_league': {'cards_avg': 4.1, 'leniency': 0.98},
        },
        'by_season': {
            2024: {'cards_avg': 4.1, 'leniency': 0.98}
        }
    },
    'peter_bankes': {
        'name': 'Peter Bankes',
        'matches_total': 23,
        'cards_per_match': 4.3,
        'yellow_cards_avg': 3.8,
        'red_cards_avg': 0.5,
        'leniency_factor': 1.02,  # Médio
        'accuracy': 88.64,
        'by_competition': {
            'premier_league': {'cards_avg': 4.3, 'leniency': 1.02},
        },
        'by_season': {
            2024: {'cards_avg': 4.3, 'leniency': 1.02}
        }
    },
    'darren_england': {
        'name': 'Darren England',
        'matches_total': 20,
        'cards_per_match': 4.0,
        'yellow_cards_avg': 3.5,
        'red_cards_avg': 0.5,
        'leniency_factor': 0.95,  # Leniente
        'accuracy': 88.89,
        'by_competition': {
            'premier_league': {'cards_avg': 4.0, 'leniency': 0.95},
        },
        'by_season': {
            2024: {'cards_avg': 4.0, 'leniency': 0.95}
        }
    }
}

# Estatísticas por liga
LEAGUE_REFEREE_STATS = {
    'brasileirao': {
        'avg_cards_per_match': 4.2,
        'avg_yellow_cards': 3.8,
        'avg_red_cards': 0.4,
        'referees': REFEREE_STATS
    },
    'premier_league': {
        'avg_cards_per_match': 4.4,
        'avg_yellow_cards': 3.9,
        'avg_red_cards': 0.5,
        'referees': PREMIER_LEAGUE_REFEREE_STATS
    }
}


def get_referee_stats(referee_key: str, league: str = 'brasileirao') -> dict:
    """Obter estatísticas de um árbitro"""
    league_data = LEAGUE_REFEREE_STATS.get(league, {})
    referees = league_data.get('referees', {})
    return referees.get(referee_key, {})


def get_leniency_factor(referee_key: str, competition: str = 'brasileirao', season: int = 2024) -> float:
    """Obter fator de leniência do árbitro"""
    stats = get_referee_stats(referee_key, competition)
    if not stats:
        return 1.0  # Padrão
    
    # Tentar obter por temporada específica
    season_data = stats.get('by_season', {}).get(season)
    if season_data:
        return season_data.get('leniency', stats.get('leniency_factor', 1.0))
    
    return stats.get('leniency_factor', 1.0)


def get_avg_cards(referee_key: str, competition: str = 'brasileirao', season: int = 2024) -> float:
    """Obter média de cartões do árbitro"""
    stats = get_referee_stats(referee_key, competition)
    if not stats:
        league_data = LEAGUE_REFEREE_STATS.get(competition, {})
        return league_data.get('avg_cards_per_match', 4.2)
    
    # Tentar obter por temporada específica
    season_data = stats.get('by_season', {}).get(season)
    if season_data:
        return season_data.get('cards_avg', stats.get('cards_per_match', 4.2))
    
    return stats.get('cards_per_match', 4.2)


def classify_referee_style(leniency_factor: float) -> str:
    """Classificar estilo do árbitro"""
    if leniency_factor > 1.10:
        return "🔴 Muito Rigoroso"
    elif leniency_factor > 1.05:
        return "🔴 Rigoroso"
    elif leniency_factor > 0.95:
        return "🟡 Médio"
    elif leniency_factor > 0.90:
        return "🟢 Leniente"
    else:
        return "🟢 Muito Leniente"


def get_league_referees(league: str = 'brasileirao') -> dict:
    """Obter todos os árbitros de uma liga"""
    league_data = LEAGUE_REFEREE_STATS.get(league, {})
    return league_data.get('referees', {})


def get_top_referees(league: str = 'brasileirao', limit: int = 5) -> list:
    """Obter top árbitros por acurácia"""
    referees = get_league_referees(league)
    sorted_refs = sorted(
        referees.items(),
        key=lambda x: x[1].get('accuracy', 0),
        reverse=True
    )
    return sorted_refs[:limit]