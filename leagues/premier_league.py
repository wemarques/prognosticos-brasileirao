"""
Premier League configuration
"""
from leagues.base_league import BaseLeague

class PremierLeague(BaseLeague):
    """Configuration for English Premier League"""

    def get_league_name(self) -> str:
        return "Premier League"

    def get_country(self) -> str:
        return "GB-ENG"

    def get_dixon_coles_params(self) -> dict:
        """
        Dixon-Coles parameters calibrated for Premier League.
        Based on historical data.
        """
        return {
            'hfa': 1.28,  # Home field advantage
            'ava': 0.95,  # Away venue adjustment
            'league_avg_goals': 2.82,  # Average goals per game
            'rho': -0.13  # Correlation between home and away goals
        }

    def get_fallback_stats(self) -> dict:
        """
        Fallback statistics from Premier League.
        """
        return {
            'corners': {
                'home_avg': 5.8,
                'away_avg': 5.2,
                'std_dev': 2.3,
                'over_8_5_prob': 0.72,
                'over_9_5_prob': 0.65,
                'over_10_5_prob': 0.58,
                'over_11_5_prob': 0.50
            },
            'cards': {
                'home_avg': 2.1,
                'away_avg': 2.3,
                'std_dev': 1.2,
                'over_3_5_prob': 0.58,
                'over_4_5_prob': 0.45,
                'over_5_5_prob': 0.32,
                'over_6_5_prob': 0.20
            }
        }

    def get_api_league_id(self, provider: str) -> str:
        """
        Get league ID for different API providers.
        """
        ids = {
            'football-data': 'PL',  # Código da Premier League
            'footystats': '2',     # ID do FootyStats
            'odds-api': 'soccer_epl'  # The Odds API
        }
        return ids.get(provider, '')

    def get_num_teams(self) -> int:
        return 20

    def get_num_rounds(self) -> int:
        return 38  # 20 times, todos contra todos ida e volta
