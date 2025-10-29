"""
Collector unificado que usa a API apropriada por liga
"""
from data.api_factory import APIFactory
from typing import List, Dict, Any


class DataCollector:
    """Collector unificado que usa a API apropriada por liga"""
    
    def __init__(self, league_key: str = 'brasileirao'):
        """
        Inicializa o collector para uma liga específica
        
        Args:
            league_key: 'brasileirao' ou 'premier_league'
        """
        self.league_key = league_key
        self.api_collector = APIFactory.create_collector(league_key)
    
    def get_matches(self, season: int = None) -> List[Dict]:
        """
        Coleta matches usando a API apropriada
        
        Args:
            season: Temporada específica (opcional)
            
        Returns:
            Lista de matches normalizados
        """
        return self.api_collector.get_matches(season)
    
    def get_teams(self) -> List[Dict]:
        """
        Coleta times usando a API apropriada
        
        Returns:
            Lista de times normalizados
        """
        return self.api_collector.get_teams()
    
    def get_standings(self) -> List[Dict]:
        """
        Coleta standings usando a API apropriada
        
        Returns:
            Lista de standings normalizados
        """
        return self.api_collector.get_standings()