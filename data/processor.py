"""
Processador de dados da API-Football para formato dos modelos estatísticos
"""

from typing import Dict, List, Optional
import numpy as np

class DataProcessor:
    """Converte dados da API para formato esperado pelos modelos"""
    
    def __init__(self):
        # Médias da liga para normalização
        self.league_avg_goals = 1.82
        self.league_avg_xg = 1.40

    def process_match_data(
        self,
        home_stats: Dict,
        away_stats: Dict,
        h2h_data: Dict,
        home_team_name: str,
        away_team_name: str
    ) -> Dict:
        """
        Processa dados completos de uma partida para uso nos modelos
        
        Args:
            home_stats: Estatísticas do time mandante
            away_stats: Estatísticas do time visitante
            h2h_data: Dados de confrontos diretos
            home_team_name: Nome do time mandante
            away_team_name: Nome do time visitante
            
        Returns:
            Dict com xG_home, xG_away e outras métricas processadas
        """
        # Processar estatísticas dos times
        home_processed = self.process_team_stats(home_stats, is_home=True)
        away_processed = self.process_team_stats(away_stats, is_home=False)
        
        # Processar H2H se disponível
        if h2h_data:
            h2h_processed = self.process_h2h(h2h_data, home_team_name, away_team_name)
            
            # Mesclar com H2H
            home_final = self.merge_stats(home_processed, h2h_processed, is_home=True)
            away_final = self.merge_stats(away_processed, h2h_processed, is_home=False)
        else:
            home_final = home_processed
            away_final = away_processed
        
        # Extrair xG para retorno
        xg_home = home_final.get('xg_for_home', self.league_avg_goals * 1.15)
        xg_away = away_final.get('xg_for_away', self.league_avg_goals * 0.85)
        
        return {
            'xG_home': xg_home,
            'xG_away': xg_away,
            'home_stats': home_final,
            'away_stats': away_final,
            'attack_strength_home': home_final.get('attack_strength', 1.0),
            'defense_strength_home': home_final.get('defense_strength', 1.0),
            'attack_strength_away': away_final.get('attack_strength', 1.0),
            'defense_strength_away': away_final.get('defense_strength', 1.0),
        }

    def process_team_stats(self, api_stats: Dict, is_home: bool = True) -> Dict:
        """
        Processa estatísticas de um time da API
        
        Args:
            api_stats: Dados brutos da API-Football
            is_home: Se o time está jogando em casa
            
        Returns:
            Dict com xG, xGC e outras métricas processadas
        """
        if not api_stats:
            # Retornar valores padrão se não houver dados
            return self._get_default_stats(is_home)
        
        # Extrair dados relevantes
        if is_home:
            goals_for = float(api_stats.get('goals_for_home', self.league_avg_goals))
            goals_against = float(api_stats.get('goals_against_home', self.league_avg_goals))
            matches_played = max(1, api_stats.get('matches_played', 19))
        else:
            goals_for = float(api_stats.get('goals_for_away', self.league_avg_goals))
            goals_against = float(api_stats.get('goals_against_away', self.league_avg_goals))
            matches_played = max(1, api_stats.get('matches_played', 19))
        
        # Calcular xG estimado (se não disponível na API)
        # Usamos média de gols como proxy para xG
        xg_for = goals_for
        xgc_against = goals_against
        
        # Calcular força ofensiva e defensiva
        attack_strength = xg_for / self.league_avg_xg
        defense_strength = xgc_against / self.league_avg_xg
        
        # Processar forma recente (últimos 5 jogos)
        form = api_stats.get('form', 'DDDDD')
        form_points = self._calculate_form_points(form)
        
        return {
            'xg_for_home' if is_home else 'xg_for_away': xg_for,
            'xgc_against_home' if is_home else 'xgc_against_away': xgc_against,
            'attack_strength': attack_strength,
            'defense_strength': defense_strength,
            'form_points': form_points,
            'matches_played': matches_played,
            'goals_per_game': goals_for,
            'goals_conceded_per_game': goals_against,
        }
    
    def process_h2h(self, h2h_matches: List[Dict], team1_name: str, team2_name: str) -> Dict:
        """
        Processa histórico de confrontos diretos
        
        Args:
            h2h_matches: Lista de partidas do confronto
            team1_name: Nome do time 1
            team2_name: Nome do time 2
            
        Returns:
            Dict com estatísticas do H2H
        """
        if not h2h_matches:
            return {
                'team1_wins': 0,
                'draws': 0,
                'team2_wins': 0,
                'avg_goals_team1': self.league_avg_goals,
                'avg_goals_team2': self.league_avg_goals,
                'avg_total_goals': self.league_avg_goals * 2,
                'btts_rate': 0.36,  # Taxa média do Brasileirão
            }
        
        team1_wins = 0
        team2_wins = 0
        draws = 0
        goals_team1 = []
        goals_team2 = []
        btts_count = 0
        
        for match in h2h_matches:
            home_team = match.get('home_team', '')
            home_goals = match.get('home_goals', 0)
            away_goals = match.get('away_goals', 0)
            
            # Determinar quem é quem
            if home_team == team1_name:
                goals_team1.append(home_goals)
                goals_team2.append(away_goals)
                if home_goals > away_goals:
                    team1_wins += 1
                elif home_goals < away_goals:
                    team2_wins += 1
                else:
                    draws += 1
            else:
                goals_team1.append(away_goals)
                goals_team2.append(home_goals)
                if away_goals > home_goals:
                    team1_wins += 1
                elif away_goals < home_goals:
                    team2_wins += 1
                else:
                    draws += 1
            
            # BTTS
            if home_goals > 0 and away_goals > 0:
                btts_count += 1
        
        total_matches = len(h2h_matches)
        
        return {
            'team1_wins': team1_wins,
            'draws': draws,
            'team2_wins': team2_wins,
            'avg_goals_team1': np.mean(goals_team1) if goals_team1 else self.league_avg_goals,
            'avg_goals_team2': np.mean(goals_team2) if goals_team2 else self.league_avg_goals,
            'avg_total_goals': np.mean([g1 + g2 for g1, g2 in zip(goals_team1, goals_team2)]),
            'btts_rate': btts_count / total_matches if total_matches > 0 else 0.36,
            'total_matches': total_matches,
        }
    
    def calculate_context_adjustments(
        self,
        home_team: str,
        away_team: str,
        venue_altitude: int = 0,
        is_classic: bool = False,
        is_derby: bool = False
    ) -> Dict:
        """
        Calcula ajustes contextuais para a partida
        
        Args:
            home_team: Nome do time mandante
            away_team: Nome do time visitante
            venue_altitude: Altitude do estádio (metros)
            is_classic: Se é um clássico
            is_derby: Se é um derby
            
        Returns:
            Dict com ajustes contextuais
        """
        # Calcular distância (simplificado - usar coordenadas reais seria melhor)
        distance_km = self._estimate_distance(home_team, away_team)
        
        # Determinar tipo de partida
        match_type = 'normal'
        if is_derby:
            match_type = 'derby'
        elif is_classic:
            match_type = 'classic'
        
        return {
            'distance_km': distance_km,
            'altitude_m': venue_altitude,
            'match_type': match_type,
            'home_absences_impact': 0.0,  # Pode ser expandido
            'away_absences_impact': 0.0,
            'lambda_cards_home': 1.5,  # Média brasileirão
            'lambda_cards_away': 1.5,
            'lambda_corners': 6.76,  # Média brasileirão (menor que Europa)
        }
    
    def merge_stats(self, team_stats: Dict, h2h_stats: Dict, is_home: bool) -> Dict:
        """
        Combina estatísticas do time com histórico H2H
        
        Args:
            team_stats: Estatísticas processadas do time
            h2h_stats: Estatísticas do H2H
            is_home: Se o time é mandante
            
        Returns:
            Dict com estatísticas mescladas
        """
        # Dar peso 70% para stats do time, 30% para H2H
        weight_team = 0.70
        weight_h2h = 0.30
        
        if is_home:
            xg_for_key = 'xg_for_home'
            xgc_against_key = 'xgc_against_home'
            h2h_goals = h2h_stats.get('avg_goals_team1', self.league_avg_goals)
        else:
            xg_for_key = 'xg_for_away'
            xgc_against_key = 'xgc_against_away'
            h2h_goals = h2h_stats.get('avg_goals_team2', self.league_avg_goals)
        
        # Mesclar xG
        xg_for = (
            team_stats.get(xg_for_key, self.league_avg_goals) * weight_team +
            h2h_goals * weight_h2h
        )
        
        # xGC mantém do time (H2H não tem essa info separada)
        xgc_against = team_stats.get(xgc_against_key, self.league_avg_goals)
        
        return {
            xg_for_key: xg_for,
            xgc_against_key: xgc_against,
            'attack_strength': team_stats.get('attack_strength', 1.0),
            'defense_strength': team_stats.get('defense_strength', 1.0),
            'form_points': team_stats.get('form_points', 5),
        }
    
    def _calculate_form_points(self, form: str) -> int:
        """
        Calcula pontos da forma recente
        
        Args:
            form: String tipo "WWDLW" (W=win, D=draw, L=loss)
            
        Returns:
            Pontos totais (W=3, D=1, L=0)
        """
        points = 0
        for result in form[-5:]:  # Últimos 5 jogos
            if result == 'W':
                points += 3
            elif result == 'D':
                points += 1
        return points
    
    def _estimate_distance(self, team1: str, team2: str) -> float:
        """
        Estima distância entre cidades dos times (simplificado)
        
        Returns:
            Distância estimada em km
        """
        # Mapeamento simplificado de distâncias
        # Em produção, usar coordenadas GPS reais
        distances = {
            ('Flamengo', 'Fluminense'): 0,  # Mesmo estádio
            ('Flamengo', 'Vasco'): 15,
            ('Flamengo', 'Botafogo'): 10,
            ('São Paulo', 'Corinthians'): 20,
            ('São Paulo', 'Palmeiras'): 25,
            ('São Paulo', 'Santos'): 80,
            ('Grêmio', 'Internacional'): 30,
            ('Atlético Mineiro', 'Cruzeiro'): 15,
            ('Bahia', 'Vitória'): 10,
        }
        
        # Buscar distância (ordem não importa)
        key1 = (team1, team2)
        key2 = (team2, team1)
        
        if key1 in distances:
            return distances[key1]
        elif key2 in distances:
            return distances[key2]
        else:
            # Distância padrão para times de estados diferentes
            return 1000.0
    
    def _get_default_stats(self, is_home: bool) -> Dict:
        """Retorna estatísticas padrão quando não há dados da API"""
        if is_home:
            return {
                'xg_for_home': self.league_avg_goals * 1.15,  # Bônus casa
                'xgc_against_home': self.league_avg_goals * 0.85,
                'attack_strength': 1.0,
                'defense_strength': 1.0,
                'form_points': 5,
                'matches_played': 19,
                'goals_per_game': self.league_avg_goals,
                'goals_conceded_per_game': self.league_avg_goals,
            }
        else:
            return {
                'xg_for_away': self.league_avg_goals * 0.85,  # Penalidade fora
                'xgc_against_away': self.league_avg_goals * 1.15,
                'attack_strength': 1.0,
                'defense_strength': 1.0,
                'form_points': 5,
                'matches_played': 19,
                'goals_per_game': self.league_avg_goals,
                'goals_conceded_per_game': self.league_avg_goals,
            }