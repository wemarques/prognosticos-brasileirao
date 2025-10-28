import requests
import os
from dotenv import load_dotenv
from datetime import datetime
import json
from typing import Dict, List, Optional

load_dotenv()

class FootballDataCollector:
    """Coleta dados de APIs de futebol"""
    
    def __init__(self):
        self.api_key = os.getenv("API_FOOTBALL_KEY")
        self.odds_api_key = os.getenv("ODDS_API_KEY")
        self.base_url = "https://v3.football.api-sports.io"
        self.headers = {"x-apisports-key": self.api_key}
    
    def get_team_stats(self, team_id: int, league_id: int = 71, season: int = 2025) -> Dict:
        """
        Busca estatísticas de um time
        
        Args:
            team_id: ID do time na API
            league_id: 71 = Brasileirão Série A
            season: Ano da temporada
            
        Returns:
            Dict com estatísticas do time
        """
        endpoint = f"{self.base_url}/teams/statistics"
        params = {
            "team": team_id,
            "league": league_id,
            "season": season
        }
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data['results'] > 0:
                stats = data['response']
                
                # Organizar dados importantes
                return {
                    'team_name': stats['team']['name'],
                    'matches_played': stats['fixtures']['played']['total'],
                    'wins_home': stats['fixtures']['wins']['home'],
                    'wins_away': stats['fixtures']['wins']['away'],
                    'goals_for_home': stats['goals']['for']['average']['home'],
                    'goals_for_away': stats['goals']['for']['average']['away'],
                    'goals_against_home': stats['goals']['against']['average']['home'],
                    'goals_against_away': stats['goals']['against']['average']['away'],
                    'clean_sheets_home': stats['clean_sheet']['home'],
                    'clean_sheets_away': stats['clean_sheet']['away'],
                    'form': stats['form'],  # Ex: "WWDLW"
                }
            else:
                return {}
                
        except Exception as e:
            print(f"Erro ao buscar stats do time {team_id}: {e}")
            return {}
    
    def get_h2h(self, team1_id: int, team2_id: int, last: int = 5) -> List[Dict]:
        """
        Busca histórico de confrontos diretos
        
        Args:
            team1_id: ID do primeiro time
            team2_id: ID do segundo time
            last: Número de jogos recentes
            
        Returns:
            Lista com últimos confrontos
        """
        endpoint = f"{self.base_url}/fixtures/headtohead"
        params = {
            "h2h": f"{team1_id}-{team2_id}",
            "last": last
        }
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            matches = []
            for fixture in data['response']:
                matches.append({
                    'date': fixture['fixture']['date'],
                    'home_team': fixture['teams']['home']['name'],
                    'away_team': fixture['teams']['away']['name'],
                    'home_goals': fixture['goals']['home'],
                    'away_goals': fixture['goals']['away'],
                    'home_xg': fixture['score'].get('xg', {}).get('home', 0),
                    'away_xg': fixture['score'].get('xg', {}).get('away', 0),
                })
            
            return matches
            
        except Exception as e:
            print(f"Erro ao buscar H2H: {e}")
            return []
    
    def get_fixture_details(self, fixture_id: int) -> Dict:
        """
        Busca detalhes específicos de uma partida
        
        Args:
            fixture_id: ID da partida
            
        Returns:
            Dict com detalhes completos
        """
        endpoint = f"{self.base_url}/fixtures"
        params = {"id": fixture_id}
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()['response'][0]
            
            return {
                'home_team': data['teams']['home']['name'],
                'away_team': data['teams']['away']['name'],
                'date': data['fixture']['date'],
                'venue': data['fixture']['venue']['name'],
                'referee': data['fixture']['referee'],
                'home_team_id': data['teams']['home']['id'],
                'away_team_id': data['teams']['away']['id'],
            }
            
        except Exception as e:
            print(f"Erro ao buscar detalhes do jogo: {e}")
            return {}
    
    def get_odds(self, fixture_id: int) -> Dict:
        """
        Busca odds de múltiplas casas para uma partida
        
        Args:
            fixture_id: ID da partida
            
        Returns:
            Dict com odds médias por mercado
        """
        endpoint = f"{self.base_url}/odds"
        params = {
            "fixture": fixture_id,
            "bookmaker": 1,  # Bet365
        }
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()['response']
            
            if not data:
                return {}
            
            bookmaker = data[0]['bookmakers'][0]
            odds_dict = {}
            
            for bet in bookmaker['bets']:
                if bet['name'] == 'Match Winner':  # 1X2
                    for value in bet['values']:
                        odds_dict[f"odds_{value['value'].lower()}"] = float(value['odd'])
                
                elif bet['name'] == 'Goals Over/Under':
                    for value in bet['values']:
                        key = f"odds_{value['value'].replace('.', '_').replace(' ', '_').lower()}"
                        odds_dict[key] = float(value['odd'])
            
            return odds_dict
            
        except Exception as e:
            print(f"Erro ao buscar odds: {e}")
            return {}

# Exemplo de uso:
if __name__ == "__main__":
    collector = FootballDataCollector()
    
    # IDs dos times (Flamengo=127, Palmeiras=128 na API-Football)
    stats_flamengo = collector.get_team_stats(127)
    print("Stats Flamengo:", stats_flamengo)

