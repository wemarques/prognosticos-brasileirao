"""
Brasileirão Série A configuration
"""
from leagues.base_league import BaseLeague

class BrasileiraoSerieA(BaseLeague):
    """Configuration for Brasileirão Série A"""
    
    def get_league_name(self) -> str:
        return "Brasileirão Série A"
    
    def get_country(self) -> str:
        return "BR"
    
    def get_dixon_coles_params(self) -> dict:
        """
        Dixon-Coles parameters calibrated for Brasileirão.
        Based on 2023-2024 season data.
        """
        return {
            'hfa': 1.35,  # Home field advantage
            'ava': 0.92,  # Away venue adjustment
            'league_avg_goals': 1.65,  # Average goals per game
            'rho': -0.12  # Correlation between home and away goals
        }
    
    def get_fallback_stats(self) -> dict:
        """
        Fallback statistics from Brasileirão 2023-2024.
        """
        return {
            'corners': {
                'home_avg': 5.2,
                'away_avg': 4.8,
                'std_dev': 2.1,
                'over_8_5_prob': 0.62,
                'over_9_5_prob': 0.55,
                'over_10_5_prob': 0.48,
                'over_11_5_prob': 0.41
            },
            'cards': {
                'home_avg': 2.4,
                'away_avg': 2.6,
                'std_dev': 1.3,
                'over_3_5_prob': 0.65,
                'over_4_5_prob': 0.52,
                'over_5_5_prob': 0.38,
                'over_6_5_prob': 0.25
            }
        }
    
    def get_api_league_id(self, provider: str) -> str:
        """
        Get league ID for different API providers.
        """
        ids = {
            'football-data': 'BSA',  # Código do Brasileirão na Football-Data
            'footystats': '2105',     # ID do FootyStats
            'odds-api': 'soccer_brazil_campeonato'  # The Odds API
        }
        return ids.get(provider, '')
    
    def get_num_teams(self) -> int:
        return 20
    
    def get_num_rounds(self) -> int:
        return 38  # 20 times, todos contra todos ida e volta
