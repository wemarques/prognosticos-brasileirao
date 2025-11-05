"""
Coletor de dados usando Football-Data.org API
API Base: https://api.football-data.org/v4
Brasileirão ID: 2013 (código: BSA)
"""

import requests
import os
from dotenv import load_dotenv
from datetime import datetime
import json
from typing import Dict, List, Optional

load_dotenv()

# Importar cache
try:
    from utils.cache import (
        matches_cache,
        get_cache_key_matches,
        get_cache_key_team_stats,
        get_cache_key_h2h
    )
    CACHE_ENABLED = True
except ImportError:
    CACHE_ENABLED = False
    print("⚠️ Cache não disponível")

class FootballDataCollector:
    """Coleta dados da API Football-Data.org"""
    
    def __init__(self):
        self.api_key = os.getenv("FOOTBALL_DATA_API_KEY") or os.getenv("API_FOOTBALL_KEY")
        self.base_url = "https://api.football-data.org/v4"
        self.headers = {"X-Auth-Token": self.api_key}
        self.brasileirao_code = "BSA"  # Usar código ao invés de ID numérico
        self.premier_league_code = "PL"  # Código Premier League
        self.current_season = 2025
        
        # Backward compatibility - CORREÇÃO DO BUG brasileiro_id (Prompt 0.1-0.2)
        self.brasileiro_id = self.brasileirao_code
    
    def get_competition_info(self, league_code: str = "BSA") -> Dict:
        """Busca informações da competição
        
        Args:
            league_code: Código da liga (BSA para Brasileirão, PL para Premier League)
        
        Returns:
            Dicionário com informações da competição
        """
        endpoint = f"{self.base_url}/competitions/{league_code}"

        try:
            response = requests.get(endpoint, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Erro ao buscar info da competição: {e}")
            return {}
    
    def get_teams(self, league_code: str = "BSA", season: int = None) -> List[Dict]:
        """
        Busca todos os times da liga
        
        Args:
            league_code: Código da liga (BSA ou PL)
            season: Ano da temporada (ex: 2025)

        Returns:
            Lista de times com IDs e informações
        """
        endpoint = f"{self.base_url}/competitions/{league_code}/teams"
        params = {}
        if season:
            params['season'] = season

        try:
            response = requests.get(endpoint, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('teams', [])
        except Exception as e:
            print(f"Erro ao buscar times: {e}")
            return []
    
    def get_team_info(self, team_id: int) -> Dict:
        """
        Busca informações detalhadas de um time
        
        Args:
            team_id: ID do time na API
            
        Returns:
            Dict com informações do time
        """
        endpoint = f"{self.base_url}/teams/{team_id}"
        
        try:
            response = requests.get(endpoint, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Erro ao buscar info do time {team_id}: {e}")
            return {}
    
    def get_team_matches(
        self, 
        team_id: int, 
        status: str = "FINISHED",
        limit: int = 10
    ) -> List[Dict]:
        """
        Busca partidas de um time (com cache)
        
        Args:
            team_id: ID do time
            status: SCHEDULED | FINISHED | TIMED | IN_PLAY
            limit: Número máximo de partidas
            
        Returns:
            Lista de partidas
        """
        # Verificar cache
        if CACHE_ENABLED:
            cache_key = get_cache_key_matches(team_id, status, limit)
            cached_data = matches_cache.get(cache_key)
            if cached_data is not None:
                return cached_data
        
        # Buscar da API
        endpoint = f"{self.base_url}/teams/{team_id}/matches"
        params = {
            'status': status,
            'limit': limit,
            'competitions': self.brasileirao_id
        }
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            matches = data.get('matches', [])
            
            # Armazenar no cache
            if CACHE_ENABLED and matches:
                matches_cache.set(cache_key, matches)
            
            return matches
        except Exception as e:
            print(f"Erro ao buscar partidas do time {team_id}: {e}")
            return []
    
    def get_h2h(self, team1_id: int, team2_id: int, limit: int = 5) -> List[Dict]:
        """
        Busca histórico de confrontos diretos
        
        Args:
            team1_id: ID do primeiro time
            team2_id: ID do segundo time
            limit: Número de jogos recentes
            
        Returns:
            Lista com últimos confrontos
        """
        # Football-Data.org não tem endpoint direto de H2H
        # Vamos buscar partidas de um time e filtrar pelo oponente
        
        all_matches = self.get_team_matches(team1_id, status="FINISHED", limit=50)
        
        h2h_matches = []
        for match in all_matches:
            home_id = match['homeTeam']['id']
            away_id = match['awayTeam']['id']
            
            # Verificar se é confronto direto
            if (home_id == team1_id and away_id == team2_id) or \
               (home_id == team2_id and away_id == team1_id):
                h2h_matches.append({
                    'date': match['utcDate'],
                    'home_team': match['homeTeam']['name'],
                    'away_team': match['awayTeam']['name'],
                    'home_goals': match['score']['fullTime']['home'],
                    'away_goals': match['score']['fullTime']['away'],
                    'home_xg': 0,  # Football-Data.org não fornece xG
                    'away_xg': 0,
                })
                
                if len(h2h_matches) >= limit:
                    break
        
        return h2h_matches
    
    def get_standings(self, season: int = None) -> Dict:
        """
        Busca classificação do Brasileirão
        
        Args:
            season: Ano da temporada
            
        Returns:
            Dict com tabela de classificação
        """
        endpoint = f"{self.base_url}/competitions/{self.brasileirao_id}/standings"
        params = {}
        if season:
            params['season'] = season
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Extrair standings
            standings = data.get('standings', [])
            if standings:
                return standings[0]  # Retornar primeira tabela (total)
            return {}
        except Exception as e:
            print(f"Erro ao buscar classificação: {e}")
            return {}
    
    def get_match_details(self, match_id: int) -> Dict:
        """
        Busca detalhes de uma partida específica
        
        Args:
            match_id: ID da partida
            
        Returns:
            Dict com detalhes completos
        """
        endpoint = f"{self.base_url}/matches/{match_id}"
        
        try:
            response = requests.get(endpoint, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Erro ao buscar detalhes da partida {match_id}: {e}")
            return {}
    
    def get_scorers(self, season: int = None, limit: int = 10) -> List[Dict]:
        """
        Busca artilheiros do Brasileirão
        
        Args:
            season: Ano da temporada
            limit: Número de artilheiros
            
        Returns:
            Lista de artilheiros
        """
        endpoint = f"{self.base_url}/competitions/{self.brasileirao_id}/scorers"
        params = {'limit': limit}
        if season:
            params['season'] = season
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('scorers', [])
        except Exception as e:
            print(f"Erro ao buscar artilheiros: {e}")
            return []
    
    def calculate_team_stats(self, team_id: int, venue: str = "HOME") -> Dict:
        """
        Calcula estatísticas de um time baseado em partidas recentes
        
        Args:
            team_id: ID do time
            venue: HOME ou AWAY
            
        Returns:
            Dict com estatísticas calculadas
        """
        matches = self.get_team_matches(team_id, status="FINISHED", limit=10)
        
        if not matches:
            return self._get_default_stats()
        
        goals_for = []
        goals_against = []
        wins = 0
        draws = 0
        losses = 0
        clean_sheets = 0
        
        for match in matches:
            home_id = match['homeTeam']['id']
            away_id = match['awayTeam']['id']
            home_goals = match['score']['fullTime']['home']
            away_goals = match['score']['fullTime']['away']
            
            # Verificar se é casa ou fora
            is_home = (home_id == team_id)
            
            # Filtrar por venue se especificado
            if venue == "HOME" and not is_home:
                continue
            if venue == "AWAY" and is_home:
                continue
            
            # Calcular estatísticas
            if is_home:
                goals_for.append(home_goals)
                goals_against.append(away_goals)
                
                if home_goals > away_goals:
                    wins += 1
                elif home_goals == away_goals:
                    draws += 1
                else:
                    losses += 1
                
                if away_goals == 0:
                    clean_sheets += 1
            else:
                goals_for.append(away_goals)
                goals_against.append(home_goals)
                
                if away_goals > home_goals:
                    wins += 1
                elif away_goals == home_goals:
                    draws += 1
                else:
                    losses += 1
                
                if home_goals == 0:
                    clean_sheets += 1
        
        matches_played = len(goals_for)
        
        if matches_played == 0:
            return self._get_default_stats()
        
        return {
            'team_name': matches[0]['homeTeam']['name'] if matches[0]['homeTeam']['id'] == team_id else matches[0]['awayTeam']['name'],
            'matches_played': matches_played,
            'wins_home' if venue == "HOME" else 'wins_away': wins,
            'goals_for_home' if venue == "HOME" else 'goals_for_away': sum(goals_for) / matches_played,
            'goals_against_home' if venue == "HOME" else 'goals_against_away': sum(goals_against) / matches_played,
            'clean_sheets_home' if venue == "HOME" else 'clean_sheets_away': clean_sheets,
            'form': self._calculate_form(matches, team_id),
        }
    
    def _calculate_form(self, matches: List[Dict], team_id: int) -> str:
        """Calcula forma recente (últimos 5 jogos)"""
        form = ""
        
        for match in matches[-5:]:
            home_id = match['homeTeam']['id']
            home_goals = match['score']['fullTime']['home']
            away_goals = match['score']['fullTime']['away']
            
            is_home = (home_id == team_id)
            
            if is_home:
                if home_goals > away_goals:
                    form += "W"
                elif home_goals == away_goals:
                    form += "D"
                else:
                    form += "L"
            else:
                if away_goals > home_goals:
                    form += "W"
                elif away_goals == home_goals:
                    form += "D"
                else:
                    form += "L"
        
        return form
    
    def _get_default_stats(self) -> Dict:
        """Retorna estatísticas padrão quando não há dados"""
        return {
            'team_name': 'Unknown',
            'matches_played': 0,
            'wins_home': 0,
            'wins_away': 0,
            'goals_for_home': 1.82,
            'goals_for_away': 1.82,
            'goals_against_home': 1.82,
            'goals_against_away': 1.82,
            'clean_sheets_home': 0,
            'clean_sheets_away': 0,
            'form': 'DDDDD',
        }


# Exemplo de uso
if __name__ == "__main__":
    collector = FootballDataCollector()
    
    # Buscar times do Brasileirão
    print("🔍 Buscando times do Brasileirão...")
    teams = collector.get_teams()
    
    if teams:
        print(f"\n✅ {len(teams)} times encontrados:")
        for team in teams[:5]:
            print(f"  - {team['name']} (ID: {team['id']})")
    else:
        print("❌ Nenhum time encontrado")
    
    # Buscar classificação
    print("\n🏆 Buscando classificação...")
    standings = collector.get_standings()
    
    if standings:
        print("✅ Classificação obtida")
    else:
        print("❌ Classificação não disponível")