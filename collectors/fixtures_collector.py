"""
Fixtures Collector - Busca jogos programados de cada rodada
"""
import os
import requests
from datetime import datetime, timedelta
from utils.logger import setup_logger

logger = setup_logger(__name__)


class FixturesCollector:
    """
    Collect and cache fixtures (scheduled matches) for a league.
    """
    
    def __init__(self, league_id=2013):
        """
        Initialize fixtures collector.
        
        Args:
            league_id: Football-Data.org league ID (2013 = Brasileirão Série A)
        """
        self.league_id = league_id
        self.league_name = "Brasileirão Série A"
        self.api_key = os.getenv('FOOTBALL_DATA_API_KEY')
        self.base_url = "https://api.football-data.org/v4"
        
        self._cache = {}
        self._cache_timestamp = {}
        self._cache_duration = timedelta(hours=6)
        
        logger.info(f"📅 Fixtures Collector initialized for {self.league_name}")
    
    def get_fixtures_by_round(self, round_number):
        """
        Get all fixtures for a specific round.
        
        Args:
            round_number (int): Round number (1-38)
        
        Returns:
            list: List of fixtures with home/away teams
        """
        if self._is_cache_valid(round_number):
            logger.info(f"📦 Using cached fixtures for round {round_number}")
            return self._cache[round_number]
        
        logger.info(f"🌐 Fetching fixtures for round {round_number} from API")
        
        try:
            headers = {
                'X-Auth-Token': self.api_key
            }
            
            url = f"{self.base_url}/competitions/{self.league_id}/matches"
            params = {
                'matchday': round_number
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            fixtures = []
            
            for match in data.get('matches', []):
                fixture = {
                    'home_team': match['homeTeam']['name'],
                    'home_team_id': match['homeTeam']['id'],
                    'away_team': match['awayTeam']['name'],
                    'away_team_id': match['awayTeam']['id'],
                    'round': round_number,
                    'date': match.get('utcDate', ''),
                    'status': match.get('status', '')
                }
                fixtures.append(fixture)
            
            self._cache[round_number] = fixtures
            self._cache_timestamp[round_number] = datetime.now()
            
            logger.info(f"✅ Found {len(fixtures)} fixtures for round {round_number}")
            
            return fixtures
            
        except Exception as e:
            logger.error(f"❌ Error fetching fixtures: {e}")
            return []
    
    def find_opponent(self, team_name, round_number, is_home=None):
        """
        Find opponent for a team in a specific round.
        
        Args:
            team_name (str): Team name
            round_number (int): Round number
            is_home (bool): If True, find away team. If False, find home team.
                           If None, find either.
        
        Returns:
            dict: {
                'opponent': opponent name,
                'is_home': True if team is home, False if away,
                'fixture': full fixture data
            } or None if not found
        """
        fixtures = self.get_fixtures_by_round(round_number)
        
        for fixture in fixtures:
            if team_name.lower() in fixture['home_team'].lower():
                if is_home is None or is_home == True:
                    logger.info(f"✅ Found match: {fixture['home_team']} vs {fixture['away_team']}")
                    return {
                        'opponent': fixture['away_team'],
                        'opponent_id': fixture['away_team_id'],
                        'is_home': True,
                        'fixture': fixture
                    }
            
            if team_name.lower() in fixture['away_team'].lower():
                if is_home is None or is_home == False:
                    logger.info(f"✅ Found match: {fixture['home_team']} vs {fixture['away_team']}")
                    return {
                        'opponent': fixture['home_team'],
                        'opponent_id': fixture['home_team_id'],
                        'is_home': False,
                        'fixture': fixture
                    }
        
        logger.warning(f"⚠️ No opponent found for {team_name} in round {round_number}")
        return None
    
    def _is_cache_valid(self, round_number):
        """Check if cache is still valid for a round"""
        if round_number not in self._cache:
            return False
        
        timestamp = self._cache_timestamp.get(round_number)
        if not timestamp:
            return False
        
        age = datetime.now() - timestamp
        return age < self._cache_duration
    
    def clear_cache(self):
        """Clear all cached fixtures"""
        self._cache = {}
        self._cache_timestamp = {}
        logger.info("🗑️ Cache cleared")
