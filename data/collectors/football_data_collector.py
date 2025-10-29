"""
Collector para Football-Data.org API
"""
import requests
from typing import Dict, List, Any
from data.adapters.data_adapter import FootballDataAdapter


class FootballDataCollector:
    """Collector para Football-Data.org API"""
    
    def __init__(self, league_key: str, api_config: Dict[str, Any]):
        self.league_key = league_key
        self.api_config = api_config
        self.base_url = api_config['base_url']
        self.league_id = api_config['league_id']
        self.api_key = api_config['api_key']
        self.adapter = FootballDataAdapter()
        self.headers = {'X-Auth-Token': self.api_key}
    
    def get_matches(self, season: int = None) -> List[Dict]:
        """Coleta matches da liga"""
        url = f"{self.base_url}/competitions/{self.league_id}/matches"
        params = {}
        if season:
            params['season'] = season
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            matches = response.json().get('matches', [])
            return [self.adapter.normalize_match(m) for m in matches]
        except Exception as e:
            print(f"Erro ao coletar matches Football-Data: {e}")
            return []
    
    def get_teams(self) -> List[Dict]:
        """Coleta times da liga"""
        url = f"{self.base_url}/competitions/{self.league_id}/teams"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            teams = response.json().get('teams', [])
            return [self.adapter.normalize_team(t) for t in teams]
        except Exception as e:
            print(f"Erro ao coletar times Football-Data: {e}")
            return []
    
    def get_standings(self) -> List[Dict]:
        """Coleta tabela de classificação"""
        url = f"{self.base_url}/competitions/{self.league_id}/standings"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            standings = response.json().get('standings', [{}])[0].get('table', [])
            return [self.adapter.normalize_stats(s) for s in standings]
        except Exception as e:
            print(f"Erro ao coletar standings Football-Data: {e}")
            return []