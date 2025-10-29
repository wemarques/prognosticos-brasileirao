"""
Gerenciador de Rodadas do Brasileirão
Busca jogos por rodada e organiza informações
"""

from typing import Dict, List, Optional
from datetime import datetime
from data.collector import FootballDataCollector

class RoundManager:
    """Gerencia jogos por rodada do Brasileirão"""
    
    def __init__(self):
        self.collector = FootballDataCollector()
        self.brasileirao_id = 2013
        self.current_season = 2025
        self.total_rounds = 38
    
    def get_round_matches(self, round_number: int) -> List[Dict]:
        """
        Busca todos os jogos de uma rodada específica
        
        Args:
            round_number: Número da rodada (1-38)
            
        Returns:
            Lista de jogos da rodada
        """
        if round_number < 1 or round_number > self.total_rounds:
            raise ValueError(f"Rodada deve estar entre 1 e {self.total_rounds}")
        
        # Buscar partidas da competição
        endpoint = f"{self.collector.base_url}/competitions/{self.brasileirao_id}/matches"
        params = {
            'season': self.current_season,
            'matchday': round_number
        }
        
        try:
            import requests
            response = requests.get(
                endpoint, 
                headers=self.collector.headers, 
                params=params, 
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            matches = data.get('matches', [])
            
            # Processar e organizar dados
            processed_matches = []
            for match in matches:
                processed_matches.append({
                    'id': match['id'],
                    'round': round_number,
                    'date': match['utcDate'],
                    'status': match['status'],
                    'home_team': {
                        'id': match['homeTeam']['id'],
                        'name': match['homeTeam']['name'],
                        'crest': match['homeTeam'].get('crest', '')
                    },
                    'away_team': {
                        'id': match['awayTeam']['id'],
                        'name': match['awayTeam']['name'],
                        'crest': match['awayTeam'].get('crest', '')
                    },
                    'score': {
                        'home': match['score']['fullTime']['home'],
                        'away': match['score']['fullTime']['away'],
                        'half_time_home': match['score']['halfTime']['home'],
                        'half_time_away': match['score']['halfTime']['away']
                    } if match['status'] == 'FINISHED' else None,
                    'venue': match.get('venue', 'N/A'),
                    'referee': match.get('referees', [{}])[0].get('name', 'N/A') if match.get('referees') else 'N/A'
                })
            
            return processed_matches
            
        except Exception as e:
            print(f"Erro ao buscar jogos da rodada {round_number}: {e}")
            return []
    
    def is_round_finished(self, round_number: int) -> bool:
        """
        Verifica se uma rodada já foi completada
        
        Args:
            round_number: Número da rodada
            
        Returns:
            True se todos os jogos foram finalizados
        """
        matches = self.get_round_matches(round_number)
        
        if not matches:
            return False
        
        return all(match['status'] == 'FINISHED' for match in matches)
    
    def get_round_status(self, round_number: int) -> Dict:
        """
        Retorna status completo de uma rodada
        
        Args:
            round_number: Número da rodada
            
        Returns:
            Dict com estatísticas da rodada
        """
        matches = self.get_round_matches(round_number)
        
        if not matches:
            return {
                'round': round_number,
                'total_matches': 0,
                'finished': 0,
                'scheduled': 0,
                'in_play': 0,
                'is_complete': False
            }
        
        status_count = {
            'FINISHED': 0,
            'SCHEDULED': 0,
            'TIMED': 0,
            'IN_PLAY': 0,
            'PAUSED': 0
        }
        
        for match in matches:
            status = match['status']
            status_count[status] = status_count.get(status, 0) + 1
        
        return {
            'round': round_number,
            'total_matches': len(matches),
            'finished': status_count['FINISHED'],
            'scheduled': status_count['SCHEDULED'] + status_count['TIMED'],
            'in_play': status_count['IN_PLAY'] + status_count['PAUSED'],
            'is_complete': status_count['FINISHED'] == len(matches),
            'matches': matches
        }
    
    def get_match_by_teams(
        self, 
        round_number: int, 
        home_team_name: str, 
        away_team_name: str
    ) -> Optional[Dict]:
        """
        Busca um jogo específico por times
        
        Args:
            round_number: Número da rodada
            home_team_name: Nome do time mandante
            away_team_name: Nome do time visitante
            
        Returns:
            Dict com dados do jogo ou None
        """
        matches = self.get_round_matches(round_number)
        
        for match in matches:
            if (match['home_team']['name'] == home_team_name and 
                match['away_team']['name'] == away_team_name):
                return match
        
        return None
    
    def get_current_round(self) -> int:
        """
        Determina a rodada atual baseado em jogos agendados/em andamento
        
        Returns:
            Número da rodada atual
        """
        for round_num in range(1, self.total_rounds + 1):
            status = self.get_round_status(round_num)
            
            # Se tem jogos agendados ou em andamento, é a rodada atual
            if status['scheduled'] > 0 or status['in_play'] > 0:
                return round_num
            
            # Se não está completa, é a rodada atual
            if not status['is_complete']:
                return round_num
        
        # Se todas rodadas terminaram, retornar última
        return self.total_rounds
    
    def get_next_round(self) -> int:
        """
        Retorna número da próxima rodada a ser jogada
        
        Returns:
            Número da próxima rodada
        """
        current = self.get_current_round()
        
        # Se rodada atual já terminou, próxima é +1
        if self.is_round_finished(current):
            return min(current + 1, self.total_rounds)
        
        return current


# Exemplo de uso
if __name__ == "__main__":
    manager = RoundManager()
    
    # Buscar jogos da rodada 30
    print("🔍 Buscando jogos da rodada 30...")
    matches = manager.get_round_matches(30)
    
    if matches:
        print(f"\n✅ {len(matches)} jogos encontrados:")
        for match in matches[:3]:
            print(f"  - {match['home_team']['name']} vs {match['away_team']['name']}")
            print(f"    Status: {match['status']}")
            if match['score']:
                print(f"    Placar: {match['score']['home']}-{match['score']['away']}")
    
    # Verificar rodada atual
    print(f"\n📅 Rodada atual: {manager.get_current_round()}")
    print(f"📅 Próxima rodada: {manager.get_next_round()}")

