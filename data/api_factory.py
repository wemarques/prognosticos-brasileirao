"""
Factory Pattern para seleção de API apropriada por liga
"""
from typing import Union
from data.collectors.football_data_collector import FootballDataCollector
from data.collectors.footystats_collector import FootyStatsCollector
from utils.leagues_config import get_api_config


class APIFactory:
    """Factory para selecionar o collector correto baseado na API"""
    
    _collectors = {
        'football_data': FootballDataCollector,
        'footystats': FootyStatsCollector,
    }
    
    @staticmethod
    def create_collector(league_key: str) -> Union[FootballDataCollector, FootyStatsCollector]:
        """
        Cria o collector apropriado para a liga
        
        Args:
            league_key: 'brasileirao' ou 'premier_league'
            
        Returns:
            Instância do collector apropriado
            
        Raises:
            ValueError: Se o provider não for suportado
        """
        api_config = get_api_config(league_key)
        provider = api_config['provider']
        
        if provider not in APIFactory._collectors:
            raise ValueError(f"Provider '{provider}' não suportado. Opções: {list(APIFactory._collectors.keys())}")
        
        collector_class = APIFactory._collectors[provider]
        return collector_class(league_key=league_key, api_config=api_config)
    
    @staticmethod
    def get_supported_providers() -> list:
        """Retorna lista de providers suportados"""
        return list(APIFactory._collectors.keys())