"""
Premier League configuration
"""
from leagues.base_league import BaseLeague


class PremierLeague(BaseLeague):
    """Configuration for Premier League"""

    def get_league_name(self) -> str:
        return "Premier League"

    def get_country(self) -> str:
        return "EN"

    def get_dixon_coles_params(self) -> dict:
        """
        Dixon-Coles parameters calibrated for Premier League.
        Based on 2023-2024 season data.
        """
        return {
            'hfa': 1.42,
            'ava': 0.88,
            'league_avg_goals': 1.58,
            'rho': -0.08
        }

    def get_fallback_stats(self) -> dict:
        """
        Fallback statistics from Premier League 2023-2024.
        """
        return {
            'corners': {
                'home_avg': 5.8,
                'away_avg': 5.2,
                'std_dev': 2.3,
                'over_8_5_prob': 0.68,
                'over_9_5_prob': 0.61,
                'over_10_5_prob': 0.54,
                'over_11_5_prob': 0.47
            },
            'cards': {
                'home_avg': 2.2,
                'away_avg': 2.4,
                'std_dev': 1.2,
                'over_3_5_prob': 0.62,
                'over_4_5_prob': 0.48,
                'over_5_5_prob': 0.35,
                'over_6_5_prob': 0.22
            }
        }

    def get_api_league_id(self, provider: str) -> str:
        """
        Get league ID for different API providers.
        """
        ids = {
            'football-data': 'PL',
            'footystats': '2106',
            'odds-api': 'soccer_epl'
        }
        return ids.get(provider, '')

    def get_num_teams(self) -> int:
        return 20

    def get_num_rounds(self) -> int:
        return 38
