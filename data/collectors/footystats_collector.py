"""
Collector para FootyStats API
"""
import requests
from typing import Dict, List, Any
from data.adapters.data_adapter import FootyStatsAdapter


class FootyStatsCollector:
    """Collector para FootyStats API"""
    
    def __init__(self, league_key: str, api_config: Dict[str, Any]):
        self.league_key = league_key
        self.api_config = api_config
        self.base_url = api_config['base_url']
        self.league_id = api_config['league_id']
        self.api_key = api_config['api_key']
        self.adapter = FootyStatsAdapter()
    
    def get_matches(self, season: int = None) -> List[Dict]:
        """Coleta matches da liga"""
        url = f"{self.base_url}/league-matches"
        params = {
            'key': self.api_key,
            'league_id': self.league_id,
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            matches = response.json().get('data', [])
            return [self.adapter.normalize_match(m) for m in matches]
        except Exception as e:
            print(f"Erro ao coletar matches FootyStats: {e}")
            return []
    
    def get_teams(self) -> List[Dict]:
        """Coleta times da liga"""
        url = f"{self.base_url}/league-teams"
        params = {
            'key': self.api_key,
            'league_id': self.league_id,
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            teams = response.json().get('data', [])
            return [self.adapter.normalize_team(t) for t in teams]
        except Exception as e:
            print(f"Erro ao coletar times FootyStats: {e}")
            return []
    
    def get_standings(self) -> List[Dict]:
        """Coleta tabela de classificação"""
        url = f"{self.base_url}/league-table"
        params = {
            'key': self.api_key,
            'league_id': self.league_id,
            'include': 'stats'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            standings = response.json().get('league_table', [])
            return [self.adapter.normalize_stats(s) for s in standings]
        except Exception as e:
            print(f"Erro ao coletar standings FootyStats: {e}")
            return []