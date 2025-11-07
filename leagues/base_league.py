"""
Base class for league configurations
"""
from abc import ABC, abstractmethod
from utils.logger import setup_logger

logger = setup_logger(__name__)

class BaseLeague(ABC):
    """
    Abstract base class for league configurations.
    All leagues must implement this interface.
    """
    
    def __init__(self):
        self.name = self.get_league_name()
        self.country = self.get_country()
        self.params = self.get_dixon_coles_params()
        self.fallback_stats = self.get_fallback_stats()
        
        logger.info(f"⚽ {self.name} initialized")
    
    @abstractmethod
    def get_league_name(self) -> str:
        """Return league name"""
        pass
    
    @abstractmethod
    def get_country(self) -> str:
        """Return country code"""
        pass
    
    @abstractmethod
    def get_dixon_coles_params(self) -> dict:
        """
        Return Dixon-Coles parameters calibrated for this league.
        
        Returns:
            dict: {
                'hfa': Home field advantage,
                'ava': Away venue adjustment,
                'league_avg_goals': Average goals per game,
                'rho': Correlation parameter
            }
        """
        pass
    
    @abstractmethod
    def get_fallback_stats(self) -> dict:
        """
        Return fallback statistics for corners and cards.
        
        Returns:
            dict: {
                'corners': {...},
                'cards': {...}
            }
        """
        pass
    
    @abstractmethod
    def get_api_league_id(self, provider: str) -> str:
        """
        Return league ID for specific API provider.
        
        Args:
            provider: 'football-data', 'footystats', or 'odds-api'
        
        Returns:
            str: League ID for that provider
        """
        pass
    
    def get_num_teams(self) -> int:
        """Return number of teams in league"""
        return 20  # Default, pode ser sobrescrito
    
    def get_num_rounds(self) -> int:
        """Return number of rounds in season"""
        return (self.get_num_teams() - 1) * 2  # Default: todos contra todos ida e volta
