"""
Fixtures Collector - Busca jogos programados de cada rodada a partir de CSV
"""
from datetime import datetime
from utils.logger import setup_logger
from data.collectors.hybrid_collector import HybridDataCollector

logger = setup_logger(__name__)


class FixturesCollector:
    """
    Collect fixtures (scheduled matches) for a league from CSV files.
    """
    
    def __init__(self, league_id=2013):
        """
        Initialize fixtures collector.
        
        Args:
            league_id: Football-Data.org league ID (2013 = Brasileirão Série A)
        """
        self.league_id = league_id
        # Mapear league_id para league_key
        league_key_map = {
            2013: 'brasileirao',
            2021: 'premier_league',
        }
        self.league_key = league_key_map.get(league_id, 'brasileirao')
        self.league_name = "Brasileirão Série A" if league_id == 2013 else "Premier League"
        
        # Usar HybridDataCollector para buscar dados do CSV
        self.collector = HybridDataCollector(league_key=self.league_key)
        
        logger.info(f"📅 Fixtures Collector initialized for {self.league_name} (usando CSV)")
    
    def get_fixtures_by_round(self, round_number):
        """
        Get all fixtures for a specific round from CSV.
        
        Args:
            round_number (int): Round number (1-38)
        
        Returns:
            list: List of fixtures with home/away teams
        """
        logger.info(f"📂 Buscando fixtures da rodada {round_number} do CSV")
        
        try:
            # Buscar matches do CSV
            matches = self.collector.get_matches(round_number=round_number)
            
            fixtures = []
            for match in matches:
                fixture = {
                    'home_team': match.get('home_team', ''),
                    'home_team_id': match.get('home_team_id'),
                    'away_team': match.get('away_team', ''),
                    'away_team_id': match.get('away_team_id'),
                    'round': round_number,
                    'date': match.get('date') or match.get('kickoff_utc', ''),
                    'status': match.get('status', 'SCHEDULED')
                }
                fixtures.append(fixture)
            
            logger.info(f"✅ Encontrados {len(fixtures)} fixtures para a rodada {round_number}")
            
            return fixtures
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar fixtures do CSV: {e}")
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
    
