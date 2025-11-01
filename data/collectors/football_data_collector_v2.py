"""
Collector para Football-Data.org API v4 com headers corretos
"""
import requests
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class FootballDataCollectorV2:
    """Collector para Football-Data.org API v4 com suporte a múltiplas ligas"""
    
    def __init__(self, league_key: str, api_config: Dict[str, Any]):
        self.league_key = league_key
        self.api_config = api_config
        self.base_url = api_config['base_url']
        self.league_id = api_config['league_id']
        self.api_key = api_config['api_key']
        
        # Headers corretos para Football-Data.org v4
        self.headers = {
            'X-Auth-Token': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def get_matches(self, season: int = None, status: str = "SCHEDULED") -> List[Dict]:
        """
        Coleta matches da liga
        
        Args:
            season: Temporada específica (opcional)
            status: Status dos jogos (SCHEDULED, LIVE, FINISHED, etc)
            
        Returns:
            Lista de matches normalizados
        """
        try:
            # Usar código da liga (PL, BSA) ao invés de ID numérico
            league_code = self.api_config.get('league_code', str(self.league_id))
            
            url = f"{self.base_url}/competitions/{league_code}/matches"
            params = {
                'status': status
            }
            
            if season:
                params['season'] = season
            
            logger.info(f"Buscando matches de {self.league_key} em {url}")
            
            response = requests.get(
                url,
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            # Verificar status da resposta
            if response.status_code == 401:
                logger.error("Erro 401: Chave de API inválida ou expirada")
                return []
            elif response.status_code == 400:
                logger.error(f"Erro 400: Requisição inválida. Resposta: {response.text}")
                return []
            elif response.status_code == 429:
                logger.error("Erro 429: Limite de requisições atingido")
                return []
            
            response.raise_for_status()
            
            data = response.json()
            matches = data.get('matches', [])
            
            logger.info(f"Encontrados {len(matches)} matches para {self.league_key}")
            
            return self._normalize_matches(matches)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao coletar matches: {e}")
            return []
        except Exception as e:
            logger.error(f"Erro inesperado: {e}")
            return []
    
    def get_teams(self, season: int = None) -> List[Dict]:
        """
        Coleta times da liga
        
        Args:
            season: Temporada específica (opcional)
            
        Returns:
            Lista de times normalizados
        """
        try:
            league_code = self.api_config.get('league_code', str(self.league_id))
            url = f"{self.base_url}/competitions/{league_code}/teams"
            
            params = {}
            if season:
                params['season'] = season
            
            response = requests.get(
                url,
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            response.raise_for_status()
            
            data = response.json()
            teams = data.get('teams', [])
            
            logger.info(f"Encontrados {len(teams)} times para {self.league_key}")
            
            return self._normalize_teams(teams)
            
        except Exception as e:
            logger.error(f"Erro ao coletar times: {e}")
            return []
    
    def get_standings(self, season: int = None) -> List[Dict]:
        """
        Coleta standings da liga
        
        Args:
            season: Temporada específica (opcional)
            
        Returns:
            Lista de standings normalizados
        """
        try:
            league_code = self.api_config.get('league_code', str(self.league_id))
            url = f"{self.base_url}/competitions/{league_code}/standings"
            
            params = {}
            if season:
                params['season'] = season
            
            response = requests.get(
                url,
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            response.raise_for_status()
            
            data = response.json()
            standings = data.get('standings', [])
            
            logger.info(f"Encontrados standings para {self.league_key}")
            
            return self._normalize_standings(standings)
            
        except Exception as e:
            logger.error(f"Erro ao coletar standings: {e}")
            return []
    
    def _normalize_matches(self, matches: List[Dict]) -> List[Dict]:
        """Normaliza dados de matches"""
        normalized = []
        for match in matches:
            try:
                normalized.append({
                    'id': match.get('id'),
                    'date': match.get('utcDate'),
                    'home_team': match.get('homeTeam', {}).get('name'),
                    'away_team': match.get('awayTeam', {}).get('name'),
                    'home_goals': match.get('score', {}).get('fullTime', {}).get('home'),
                    'away_goals': match.get('score', {}).get('fullTime', {}).get('away'),
                    'status': match.get('status'),
                    'competition': match.get('competition', {}).get('name'),
                })
            except Exception as e:
                logger.warning(f"Erro ao normalizar match: {e}")
                continue
        
        return normalized
    
    def _normalize_teams(self, teams: List[Dict]) -> List[Dict]:
        """Normaliza dados de times"""
        normalized = []
        for team in teams:
            try:
                normalized.append({
                    'id': team.get('id'),
                    'name': team.get('name'),
                    'shortName': team.get('shortName'),
                    'tla': team.get('tla'),
                    'crest': team.get('crest'),
                    'address': team.get('address'),
                    'website': team.get('website'),
                    'founded': team.get('founded'),
                    'clubColors': team.get('clubColors'),
                    'venue': team.get('venue'),
                })
            except Exception as e:
                logger.warning(f"Erro ao normalizar time: {e}")
                continue
        
        return normalized
    
    def _normalize_standings(self, standings: List[Dict]) -> List[Dict]:
        """Normaliza dados de standings"""
        normalized = []
        for standing in standings:
            try:
                table = standing.get('table', [])
                for position in table:
                    normalized.append({
                        'position': position.get('position'),
                        'team': position.get('team', {}).get('name'),
                        'playedGames': position.get('playedGames'),
                        'won': position.get('won'),
                        'draw': position.get('draw'),
                        'lost': position.get('lost'),
                        'points': position.get('points'),
                        'goalDifference': position.get('goalDifference'),
                    })
            except Exception as e:
                logger.warning(f"Erro ao normalizar standing: {e}")
                continue
        
        return normalized