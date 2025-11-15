"""
League registry for managing available leagues
"""
from leagues.base_league import BaseLeague
from leagues.brasileirao import BrasileiraoSerieA
from utils.logger import setup_logger

logger = setup_logger(__name__)

class LeagueRegistry:
    """
    Registry of available leagues.
    """
    
    _leagues = {
        'brasileirao': BrasileiraoSerieA,
    }
    
    @classmethod
    def get_league(cls, league_key: str):
        """
        Get league instance by key.
        
        Args:
            league_key: League identifier (e.g., 'brasileirao', 'premier_league')
        
        Returns:
            BaseLeague: League instance
        
        Raises:
            ValueError: If league not found
        """
        if league_key not in cls._leagues:
            available = ', '.join(cls._leagues.keys())
            raise ValueError(f"Liga '{league_key}' não encontrada. Disponíveis: {available}")
        
        league_class = cls._leagues[league_key]
        return league_class()
    
    @classmethod
    def get_available_leagues(cls) -> dict:
        """
        Get all available leagues.
        
        Returns:
            dict: {key: league_name}
        """
        leagues = {}
        for key, league_class in cls._leagues.items():
            instance = league_class()
            leagues[key] = instance.get_league_name()
        
        return leagues
    
    @classmethod
    def register_league(cls, key: str, league_class):
        """
        Register a new league.
        
        Args:
            key: Unique identifier for the league
            league_class: Class that inherits from BaseLeague
        """
        if not issubclass(league_class, BaseLeague):
            raise TypeError("League class must inherit from BaseLeague")
        
        cls._leagues[key] = league_class
        logger.info(f"✅ League registered: {key}")
