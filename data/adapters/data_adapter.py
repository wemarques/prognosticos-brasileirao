"""
Adaptadores para normalizar dados de diferentes APIs
"""
from typing import Dict, Any
from abc import ABC, abstractmethod


class DataAdapter(ABC):
    """Interface abstrata para adaptadores de dados"""
    
    @abstractmethod
    def normalize_match(self, match_data: Dict) -> Dict[str, Any]:
        """Normaliza dados de um jogo"""
        pass
    
    @abstractmethod
    def normalize_team(self, team_data: Dict) -> Dict[str, Any]:
        """Normaliza dados de um time"""
        pass
    
    @abstractmethod
    def normalize_stats(self, stats_data: Dict) -> Dict[str, Any]:
        """Normaliza dados estatísticos"""
        pass


class FootballDataAdapter(DataAdapter):
    """Adaptador para Football-Data.org"""
    
    def normalize_match(self, match_data: Dict) -> Dict[str, Any]:
        """Converte formato Football-Data para padrão interno"""
        return {
            'id': match_data.get('id'),
            'date': match_data.get('utcDate'),
            'home_team': match_data.get('homeTeam', {}).get('name'),
            'away_team': match_data.get('awayTeam', {}).get('name'),
            'home_goals': match_data.get('score', {}).get('fullTime', {}).get('home'),
            'away_goals': match_data.get('score', {}).get('fullTime', {}).get('away'),
            'status': match_data.get('status'),
            'odds': match_data.get('odds', {}),
        }
    
    def normalize_team(self, team_data: Dict) -> Dict[str, Any]:
        """Normaliza dados de um time"""
        return {
            'id': team_data.get('id'),
            'name': team_data.get('name'),
            'code': team_data.get('code'),
            'crest': team_data.get('crest'),
        }
    
    def normalize_stats(self, stats_data: Dict) -> Dict[str, Any]:
        """Normaliza estatísticas de um time"""
        return {
            'team_id': stats_data.get('team', {}).get('id'),
            'team_name': stats_data.get('team', {}).get('name'),
            'matches_played': stats_data.get('playedGames'),
            'wins': stats_data.get('won'),
            'draws': stats_data.get('draw'),
            'losses': stats_data.get('lost'),
            'goals_for': stats_data.get('goalsFor'),
            'goals_against': stats_data.get('goalsAgainst'),
            'goal_difference': stats_data.get('goalDifference'),
            'points': stats_data.get('points'),
        }


class FootyStatsAdapter(DataAdapter):
    """Adaptador para FootyStats API"""
    
    def normalize_match(self, match_data: Dict) -> Dict[str, Any]:
        """Converte formato FootyStats para padrão interno"""
        return {
            'id': match_data.get('id'),
            'date': match_data.get('date'),
            'home_team': match_data.get('home_team', {}).get('name') if isinstance(match_data.get('home_team'), dict) else match_data.get('home_team'),
            'away_team': match_data.get('away_team', {}).get('name') if isinstance(match_data.get('away_team'), dict) else match_data.get('away_team'),
            'home_goals': match_data.get('goals', {}).get('home') if isinstance(match_data.get('goals'), dict) else match_data.get('home_goals'),
            'away_goals': match_data.get('goals', {}).get('away') if isinstance(match_data.get('goals'), dict) else match_data.get('away_goals'),
            'status': match_data.get('status'),
            'odds': match_data.get('odds', {}),
        }
    
    def normalize_team(self, team_data: Dict) -> Dict[str, Any]:
        """Normaliza dados de um time"""
        return {
            'id': team_data.get('id'),
            'name': team_data.get('name'),
            'code': team_data.get('code'),
            'crest': team_data.get('logo'),
        }
    
    def normalize_stats(self, stats_data: Dict) -> Dict[str, Any]:
        """Normaliza estatísticas de um time"""
        return {
            'team_id': stats_data.get('team_id'),
            'team_name': stats_data.get('team_name'),
            'matches_played': stats_data.get('played'),
            'wins': stats_data.get('wins'),
            'draws': stats_data.get('draws'),
            'losses': stats_data.get('losses'),
            'goals_for': stats_data.get('goals_for'),
            'goals_against': stats_data.get('goals_against'),
            'goal_difference': stats_data.get('goal_difference'),
            'points': stats_data.get('points'),
        }